import eventlet
eventlet.monkey_patch()

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from functools import wraps
import hashlib
import json
import os
import re
import secrets
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, abort
from flask_socketio import SocketIO
from google import genai
from google.genai import types
import eng_to_ipa
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash')
gemini_clients = {}
gemini_key_cursor = 0

app = Flask(__name__)
socketio = SocketIO(app, async_mode='eventlet', cors_allowed_origins='*')
_admin_env_auth = None
_admin_env_credentials = None

def load_session_secret():
    configured_secret = os.environ.get('FLASK_SECRET_KEY')
    if configured_secret:
        return configured_secret
    secret_path = Path(app.instance_path) / 'session_secret.key'
    try:
        secret = secret_path.read_text(encoding='utf-8').strip()
        if len(secret) >= 64:
            return secret
    except OSError:
        pass
    secret_path.parent.mkdir(parents=True, exist_ok=True)
    secret = secrets.token_hex(32)
    secret_path.write_text(secret, encoding='utf-8')
    secret_path.chmod(0o600)
    return secret

app.secret_key = load_session_secret()
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax', MAX_CONTENT_LENGTH=12 * 1024 * 1024)

CHAT_HISTORY_PATH = Path(app.instance_path) / 'chat_history.jsonl'
STUDENT_ID_PATH = Path(app.instance_path) / 'student_ids.json'


def ensure_data_file(path, default_content='[]'):
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(default_content, encoding='utf-8')
    return path


def cleanup_temp_files(root_dir=None):
    target_root = Path(root_dir or app.instance_path)
    patterns = ('*.tmp', '*.temp', '*.bak', '*.log')
    removed = 0
    for pattern in patterns:
        for file_path in target_root.rglob(pattern):
            try:
                if file_path.is_file():
                    file_path.unlink()
                    removed += 1
            except OSError:
                continue
    for file_path in [Path(app.static_folder) / 'uploads', Path(app.static_folder) / 'tmp']:
        if file_path.exists():
            for pattern in ('*.tmp', '*.temp', '*.bak'):
                for temp_file in file_path.rglob(pattern):
                    try:
                        if temp_file.is_file():
                            temp_file.unlink()
                            removed += 1
                    except OSError:
                        continue
    return removed


def load_student_registry():
    ensure_data_file(STUDENT_ID_PATH, '[]')
    try:
        data = json.loads(STUDENT_ID_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return []
    return data if isinstance(data, list) else []


def save_student_registry(entries):
    ensure_data_file(STUDENT_ID_PATH, '[]')
    STUDENT_ID_PATH.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding='utf-8')


def normalize_student_id(student_id):
    if student_id is None:
        return ''
    value = str(student_id).strip().upper()
    return re.sub(r'[^A-Z0-9-]', '', value)


def is_valid_student_id(student_id):
    normalized = normalize_student_id(student_id)
    if not normalized:
        return False
    pattern = r'^[A-Z]{2,5}-\d{4}-\d{4}$'
    return bool(re.fullmatch(pattern, normalized))


def verify_student_in_registry(student_id):
    if not is_valid_student_id(student_id):
        return False
    registry = load_student_registry()
    normalized = normalize_student_id(student_id)
    return normalized in {normalize_student_id(item) for item in registry}


def append_chat_message(message):
    ensure_data_file(CHAT_HISTORY_PATH, '[]')
    with CHAT_HISTORY_PATH.open('a', encoding='utf-8') as chat_file:
        chat_file.write(json.dumps(message, ensure_ascii=False) + '\n')


def load_chat_messages(limit=None, search_term=''):
    ensure_data_file(CHAT_HISTORY_PATH, '[]')
    entries = []
    try:
        lines = CHAT_HISTORY_PATH.read_text(encoding='utf-8').splitlines()
    except OSError:
        return entries
    for line in reversed(lines):
        try:
            entry = json.loads(line)
        except (TypeError, ValueError):
            continue
        if not isinstance(entry, dict):
            continue
        if search_term:
            haystack = ' '.join([
                str(entry.get('student_id', '')),
                str(entry.get('username', '')),
                str(entry.get('message', '')),
            ]).lower()
            if search_term.lower() not in haystack:
                continue
        entries.append(entry)
        if limit and len(entries) >= limit:
            break
    return list(reversed(entries))


def clear_chat_history():
    ensure_data_file(CHAT_HISTORY_PATH, '[]')
    CHAT_HISTORY_PATH.write_text('', encoding='utf-8')


SITE_CONTENT_DEFAULTS = {
    'brand_name': 'nizarphonetics',
    'brand_tagline': 'English sound, made clear.',
    'home_heading': 'Hear English with clarity.',
    'home_badge': 'A focused phonetics and pronunciation studio',
    'home_intro': 'Explore English pronunciation, compare British and American speech, and build confidence one sound at a time.',
    'about_eyebrow': 'nizarphonetics · About',
    'about_lead': 'nizarphonetics is a student-centered space for exploring English sounds, pronunciation, and the details that make spoken language clear.',
    'about_story_title': 'Our Story',
    'about_story': 'This platform brings practical phonetics tools into one calm workspace. Its sample story and mission are fully editable from the administration panel.',
    'mission_title': 'Pronunciation Made Clear',
    'mission_text': 'Make English sounds easier to hear, understand, and practice through clear phonetic tools.',
    'vision_title': 'Confidence in Every Sound',
    'vision_text': 'Help learners build a lasting connection between written English and natural spoken language.',
    'values_title': 'Practice, Clarity, Progress',
    'values_text': 'We value accessible practice, careful listening, and steady progress at every level.',
    'founder_name': 'Nizar Sharqi',
    'founder_bio': 'Founder of nizarphonetics, building thoughtful tools for English pronunciation and phonetic learning.',
    'contact_title': 'Contact nizarphonetics',
    'contact_intro': 'Send a question, suggestion, or note to the nizarphonetics team.',
    'contact_email_label': 'Email',
    'contact_hours_label': 'Response Hours',
    'contact_note_title': 'Your Feedback Matters',
    'contact_email': 'hello@example.com',
    'contact_hours': 'Sunday to Thursday, 9:00 AM to 5:00 PM.',
    'contact_note': 'Share an idea or comment with the nizarphonetics team.',
    'contact_accent': '#d5ff3f',
    'contact_decoration': 'minimal',
    'background_enabled': False,
    'faculty': ['Dr. ابراهيم جبريل', 'Dr. نعمة الحاج', 'Dr. محمد علي', 'Dr. سمير الحمادي'],
    'students': [
        'نزار أحمد شرقي', 'عبد العزيز الصغير', 'اية انور', 'ود مجاهد',
        'بنان نصر', 'ربا عياش', 'سمية هيثم', 'نسيبة قطيف', 'جنات',
        'سهام', 'حمزة سيف', 'عبد العزيز', 'زياد وليد العمري',
        'ريم حاتم المالكي', 'أنس جمال الحارثي', 'دانا فواز البلوي',
        'سلمان محمد عبد الله'
    ]
}

SITE_CONTENT_LEGACY_VALUES = {
    'brand_name': {'Nizartra', 'NizarTra', 'Black Spot'},
    'brand_tagline': {
        'Translation tools by Nizartra | Add your tagline here',
        'Fast translation and smart KNX automation by NizarTra',
    },
    'home_heading': {'Translation Platform', 'NIZAR-TRA Translation Platform'},
    'home_badge': {'Lead Developer and Researcher: نزار أحمد شرقي'},
    'home_intro': {
        'Editable introduction: add your message or information as the site creator.',
        'NizarTra delivers fast, accurate translation workflows and a modern control layer for smart automation and KNX-aware operations.',
    },
    'about_eyebrow': {'Nizartra · About', 'NizarTra · About'},
    'about_lead': {
        'We are a digital space that makes translation and learning clearer and easier. This is sample text; replace it with your own introduction and message.',
        'NizarTra combines high-precision translation workflows, clean UX, and smart automation intelligence into one lightweight platform built for speed and clarity.',
    },
    'about_story': {
        "Nizartra began as an idea to bring translation tools together and give students a practical space to experiment and learn. We continue to shape it around users' needs and make every step clearer.",
        'NizarTra was designed to turn language barriers into a more efficient, connected experience. It blends reliable translation tools with modern automation controls and a clear operational dashboard.',
    },
    'founder_bio': {
        'Add a short bio, your field of study, and the idea behind Nizartra.',
        'Add a short introduction, your field of study, and the idea behind Nizartra.',
    },
    'contact_note': {'Help us improve Nizartra by sharing an idea or comment.'},
}

NIZARTRA_CONFIG_DEFAULTS = {
    'default_source_language': 'en',
    'default_target_language': 'ar',
    'translation_mode': 'dual',
    'auto_detect_language': True,
    'enable_knx': True,
    'max_segment_length': 450,
    'api_timeout_seconds': 8,
    'knx_channels': [
        {'name': 'Living Room Lights', 'group_address': '1/0/1', 'room': 'Living Room', 'type': 'Lighting', 'status': 'Off'},
        {'name': 'HVAC Control', 'group_address': '1/0/2', 'room': 'Office', 'type': 'Climate', 'status': 'Auto'},
        {'name': 'Gate Access', 'group_address': '1/0/3', 'room': 'Entrance', 'type': 'Security', 'status': 'Closed'}
    ]
}

def site_content_path():
    return Path(app.instance_path) / 'site_content.json'

def admin_auth_path():
    return Path(app.instance_path) / 'admin_auth.json'

def load_site_content():
    content = dict(SITE_CONTENT_DEFAULTS)
    try:
        saved = json.loads(site_content_path().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return content
    if not isinstance(saved, dict):
        return content
    for key, default in SITE_CONTENT_DEFAULTS.items():
        if key in {'students', 'faculty'}:
            names = saved.get(key)
            if isinstance(names, list):
                limit = 50 if key == 'students' else 30
                content[key] = [str(name)[:100] for name in names[:limit] if str(name).strip()]
        elif isinstance(default, bool) and isinstance(saved.get(key), bool):
            content[key] = saved[key]
        elif isinstance(default, str) and isinstance(saved.get(key), str):
            value = saved[key]
            if value.strip() not in SITE_CONTENT_LEGACY_VALUES.get(key, set()):
                content[key] = value[:2000]
    return content


def nizartra_config_path():
    return Path(app.instance_path) / 'nizartra_config.json'


def load_app_config():
    config = dict(NIZARTRA_CONFIG_DEFAULTS)
    try:
        saved = json.loads(nizartra_config_path().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return config
    if not isinstance(saved, dict):
        return config
    for key, default in NIZARTRA_CONFIG_DEFAULTS.items():
        if key == 'knx_channels':
            channels = saved.get(key)
            if isinstance(channels, list):
                cleaned_channels = []
                for channel in channels[:20]:
                    if not isinstance(channel, dict):
                        continue
                    cleaned_channels.append({
                        'name': str(channel.get('name', 'Unnamed Channel'))[:80],
                        'group_address': str(channel.get('group_address', '0/0/0'))[:40],
                        'room': str(channel.get('room', 'Unknown'))[:60],
                        'type': str(channel.get('type', 'Automation'))[:40],
                        'status': str(channel.get('status', 'Off'))[:20],
                    })
                config[key] = cleaned_channels
        elif isinstance(default, bool) and isinstance(saved.get(key), bool):
            config[key] = saved[key]
        elif isinstance(default, int) and isinstance(saved.get(key), int):
            config[key] = saved[key]
        elif isinstance(default, str) and isinstance(saved.get(key), str):
            config[key] = saved[key][:2000]
    return config


def save_app_config(config):
    path = nizartra_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix('.tmp')
    temp_path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    temp_path.replace(path)


def save_site_content(content):
    path = site_content_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix('.tmp')
    temporary_path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary_path.replace(path)

def load_admin_auth():
    global _admin_env_auth, _admin_env_credentials

    env_username = os.environ.get('ADMIN_USERNAME', 'admin').strip()[:80] or 'admin'
    env_password = os.environ.get('ADMIN_PASSWORD', '')
    if env_password:
        password_fingerprint = hashlib.sha256(env_password.encode('utf-8')).digest()
        credentials = (env_username, password_fingerprint)
        if credentials != _admin_env_credentials:
            _admin_env_auth = {
                'username': env_username,
                'password_hash': generate_password_hash(env_password),
            }
            _admin_env_credentials = credentials
        return _admin_env_auth

    try:
        data = json.loads(admin_auth_path().read_text(encoding='utf-8'))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) and data.get('password_hash') else None

def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return session['csrf_token']

def valid_csrf(form):
    submitted_token = form.get('csrf_token', '')
    stored_token = session.get('csrf_token', '')
    return bool(submitted_token and stored_token and secrets.compare_digest(submitted_token, stored_token))

def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin_page'))
        return view(*args, **kwargs)
    return wrapped

@app.context_processor
def inject_site_content():
    return {'site_content': load_site_content(), 'site_config': load_app_config()}

def load_message_file(filename, limit=40):
    path = Path(app.instance_path) / filename
    try:
        all_lines = path.read_text(encoding='utf-8').splitlines()
    except OSError:
        return []
    lines = all_lines[-limit:]
    messages = []
    first_line_number = len(all_lines) - len(lines)
    for line_number, line in reversed(list(enumerate(lines, start=first_line_number))):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            entry['_id'] = hashlib.sha256(f'{line_number}:{line}'.encode('utf-8')).hexdigest()
            submitted_at = entry.get('submitted_at', '')
            try:
                parsed_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                entry['_display_date'] = parsed_date.astimezone().strftime('%Y-%m-%d %H:%M')
            except (AttributeError, TypeError, ValueError):
                entry['_display_date'] = submitted_at or 'Unknown'
            messages.append(entry)
    return messages


def detect_language(text):
    text = (text or '').strip()
    if not text:
        return 'en'
    arabic_count = sum(1 for char in text if '\u0600' <= char <= '\u06FF')
    alpha_count = sum(1 for char in text if char.isalpha())
    if alpha_count and arabic_count / alpha_count > 0.2:
        return 'ar'
    return 'en'


def segment_text(text, max_length):
    normalized = re.sub(r'\s+', ' ', (text or '').strip())
    if not normalized:
        return []
    if len(normalized) <= max_length:
        return [normalized]

    sentences = re.split(r'(?<=[.!?])\s+|\n+', normalized)
    segments = []
    current = ''
    for sentence in sentences:
        if not sentence.strip():
            continue
        sentence = sentence.strip()
        if len(sentence) <= max_length:
            if len(current) + len(sentence) + 1 <= max_length:
                current = (current + ' ' + sentence).strip() if current else sentence
            else:
                if current:
                    segments.append(current)
                current = sentence
        else:
            words = sentence.split()
            chunk = ''
            for word in words:
                candidate = f'{chunk} {word}'.strip()
                if len(candidate) <= max_length:
                    chunk = candidate
                else:
                    if chunk:
                        segments.append(chunk)
                    chunk = word
            if chunk:
                if current:
                    segments.append(current)
                    current = ''
                segments.append(chunk)
    if current:
        segments.append(current)
    if not segments:
        return [normalized[:max_length]]
    return segments

@app.route('/admin', methods=['GET'])
def admin_page():
    auth = load_admin_auth()
    if auth is None:
        if request.remote_addr not in {'127.0.0.1', '::1'}:
            abort(404)
        mode = 'setup'
    elif not session.get('is_admin'):
        mode = 'login'
    else:
        mode = 'dashboard'
    return render_template(
        'admin.html', mode=mode, csrf_token=csrf_token(),
        contact_messages=load_message_file('contact_messages.jsonl'),
        feedback_messages=load_message_file('feedback_submissions.jsonl'),
        app_config=load_app_config()
    )

@app.route('/admin/setup', methods=['POST'])
def admin_setup():
    if request.remote_addr not in {'127.0.0.1', '::1'}:
        abort(404)
    if load_admin_auth() is not None:
        return redirect(url_for('admin_page'))
    if not valid_csrf(request.form):
        abort(400)
    username = request.form.get('username', 'admin').strip()[:80] or 'admin'
    password = request.form.get('password', '')
    confirmation = request.form.get('confirmation', '')
    if len(password) < 12:
        flash('Choose a password with at least 12 characters.')
        return redirect(url_for('admin_page'))
    if password != confirmation:
        flash('The passwords do not match.')
        return redirect(url_for('admin_page'))

    auth_path = admin_auth_path()
    auth_path.parent.mkdir(parents=True, exist_ok=True)
    auth_path.write_text(json.dumps({
        'username': username,
        'password_hash': generate_password_hash(password),
    }), encoding='utf-8')
    auth_path.chmod(0o600)
    session.clear()
    session['is_admin'] = True
    csrf_token()
    flash('Admin access was set up securely.')
    return redirect(url_for('admin_page'))

@app.route('/admin/login', methods=['POST'])
def admin_login():
    auth = load_admin_auth()
    if auth is None:
        return redirect(url_for('admin_page'))
    if not valid_csrf(request.form):
        abort(400)
    submitted_username = request.form.get('username', '').strip()
    username_matches = secrets.compare_digest(
        submitted_username,
        str(auth.get('username', 'admin')),
    )
    if not username_matches or not check_password_hash(auth['password_hash'], request.form.get('password', '')):
        flash('The admin password is incorrect.')
        return redirect(url_for('admin_page'))
    session.clear()
    session['is_admin'] = True
    csrf_token()
    return redirect(url_for('admin_page'))

@app.route('/admin/logout', methods=['POST'])
@admin_required
def admin_logout():
    if not valid_csrf(request.form):
        abort(400)
    session.clear()
    return redirect(url_for('admin_page'))

@app.route('/admin/settings/save', methods=['POST'])
@admin_required
def admin_settings_save():
    if not valid_csrf(request.form):
        abort(400)
    config = load_app_config()
    config['default_source_language'] = request.form.get('default_source_language', 'en').strip().lower()[:2]
    config['default_target_language'] = request.form.get('default_target_language', 'ar').strip().lower()[:2]
    config['translation_mode'] = request.form.get('translation_mode', 'dual').strip()[:20]
    config['auto_detect_language'] = request.form.get('auto_detect_language') == 'on'
    config['enable_knx'] = request.form.get('enable_knx') == 'on'
    config['max_segment_length'] = max(120, min(900, int(request.form.get('max_segment_length', config['max_segment_length']))))
    config['api_timeout_seconds'] = max(3, min(20, int(request.form.get('api_timeout_seconds', config['api_timeout_seconds']))))
    save_app_config(config)
    flash('Translation settings saved.')
    return redirect(url_for('admin_page'))


@app.route('/admin/save', methods=['POST'])
@admin_required
def admin_save():
    if not valid_csrf(request.form):
        abort(400)
    content = load_site_content()
    field_limits = {
        'brand_name': 80, 'brand_tagline': 180, 'home_heading': 120,
        'home_badge': 160, 'home_intro': 1000, 'about_eyebrow': 100,
        'about_lead': 1200, 'about_story_title': 100, 'about_story': 2000,
        'mission_title': 100, 'mission_text': 700, 'vision_title': 100,
        'vision_text': 700, 'values_title': 100, 'values_text': 700,
        'founder_name': 100, 'founder_bio': 1000, 'contact_title': 120,
        'contact_intro': 1000, 'contact_email_label': 80,
        'contact_hours_label': 80, 'contact_note_title': 100,
        'contact_email': 254, 'contact_hours': 300, 'contact_note': 600,
        'contact_accent': 7, 'contact_decoration': 20
    }
    for field, limit in field_limits.items():
        content[field] = request.form.get(field, '').strip()[:limit]
    if not re.fullmatch(r'#[0-9A-Fa-f]{6}', content['contact_accent']):
        content['contact_accent'] = SITE_CONTENT_DEFAULTS['contact_accent']
    if content['contact_decoration'] not in {'minimal', 'grid', 'glow'}:
        content['contact_decoration'] = 'minimal'
    email = content['contact_email']
    if email and ('@' not in email or '.' not in email.rsplit('@', 1)[-1]):
        flash('Please check the contact email format.')
        return redirect(url_for('admin_page'))
    if 'students' in request.form:
        students = [line.strip()[:100] for line in request.form.get('students', '').splitlines() if line.strip()]
        if len(students) > 50:
            flash('The maximum is 50 names.')
            return redirect(url_for('admin_page'))
        content['students'] = students
    faculty = [line.strip()[:100] for line in request.form.get('faculty', '').splitlines() if line.strip()]
    if len(faculty) > 30:
        flash('The maximum is 30 faculty names.')
        return redirect(url_for('admin_page'))
    content['faculty'] = faculty
    content['background_enabled'] = request.form.get('background_enabled') == 'on'
    save_site_content(content)
    flash('Site content saved.')
    return redirect(url_for('admin_page'))

@app.route('/admin/students/add', methods=['POST'])
@admin_required
def admin_add_student():
    if not valid_csrf(request.form):
        abort(400)
    name = request.form.get('name', '').strip()[:100]
    content = load_site_content()
    students = content['students']
    if not name:
        flash('Enter a name to add.')
    elif len(students) >= 50:
        flash('The maximum of 50 names has been reached.')
    elif name.casefold() in {student.casefold() for student in students}:
        flash('This name already exists.')
    else:
        students.append(name)
        content['students'] = students
        save_site_content(content)
        flash('Name added.')
    return redirect(url_for('admin_page') + '#students')

@app.route('/admin/students/<int:student_index>/delete', methods=['POST'])
@admin_required
def admin_delete_student(student_index):
    if not valid_csrf(request.form):
        abort(400)
    content = load_site_content()
    students = content['students']
    if student_index >= len(students):
        abort(404)
    del students[student_index]
    content['students'] = students
    save_site_content(content)
    flash('Name deleted.')
    return redirect(url_for('admin_page') + '#students')

@app.route('/admin/feedback/<feedback_id>/delete', methods=['POST'])
@admin_required
def admin_delete_feedback(feedback_id):
    if not valid_csrf(request.form):
        abort(400)
    if len(feedback_id) != 64:
        abort(404)
    feedback_path = Path(app.instance_path) / 'feedback_submissions.jsonl'
    try:
        lines = feedback_path.read_text(encoding='utf-8').splitlines()
    except OSError:
        abort(404)
    matching_index = next((
        index for index, line in enumerate(lines)
        if secrets.compare_digest(
            hashlib.sha256(f'{index}:{line}'.encode('utf-8')).hexdigest(), feedback_id
        )
    ), None)
    if matching_index is None:
        abort(404)
    del lines[matching_index]
    temporary_path = feedback_path.with_suffix('.tmp')
    temporary_path.write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')
    temporary_path.replace(feedback_path)
    flash('Feedback deleted.')
    return redirect(url_for('admin_page') + '#feedback')

@app.route('/admin/upload', methods=['POST'])
@admin_required
def admin_upload():
    if not valid_csrf(request.form):
        abort(400)
    uploaded = request.files.get('image')
    slot = request.form.get('slot')
    destinations = {'avatar': 'my_photo.jpg', 'background': 'my_photo2.jpg'}
    if slot not in destinations or not uploaded or not uploaded.filename:
        flash('Choose an image and the image slot to replace.')
        return redirect(url_for('admin_page'))
    if Path(uploaded.filename).suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp'}:
        flash('Supported image formats are JPG, PNG, and WEBP.')
        return redirect(url_for('admin_page'))

    try:
        from PIL import Image

        image = Image.open(uploaded.stream)
        image.verify()
        uploaded.stream.seek(0)
        image = Image.open(uploaded.stream).convert('RGB')
        destination = Path(app.static_folder) / destinations[slot]
        temporary_path = destination.with_name(f'.{destination.stem}.{secrets.token_hex(6)}.tmp')
        image.save(temporary_path, format='JPEG', quality=92, optimize=True)
        temporary_path.replace(destination)
    except (ImportError, OSError, ValueError):
        flash('Unable to read the image. Try a valid JPG, PNG, or WEBP file.')
        return redirect(url_for('admin_page'))

    flash('Image replaced successfully.')
    return redirect(url_for('admin_page'))

# Legacy standalone home-page markup
HTML_INDEX = """
<!DOCTYPE html>
<html lang="en" dir="ltr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>nizarphonetics - English Phonetics Studio</title>
    <style>
        * { box-sizing: border-box; }
        body {
            margin: 0; padding: 0;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            background-color: #07090e;
            color: #ffffff;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header-nav {
            background-color: #0d1322;
            border-bottom: 1px solid #1f2937;
            padding: 12px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand-container {
            display: flex; align-items: center; gap: 12px; text-decoration: none;
        }
        /* Small profile image in the navigation bar */
        .navbar-avatar {
            width: 56px; height: 56px; border-radius: 50%;
            border: 2px solid #38bdf8; object-fit: cover;
        }
        .brand-title { font-size: 16px; font-weight: bold; color: #38bdf8; }
        .nav-menu { display: flex; gap: 15px; list-style: none; margin: 0; padding: 0; }
        .nav-menu a { color: #9ca3af; text-decoration: none; font-size: 14px; padding: 6px 12px; border-radius: 6px; }
        .nav-menu a:hover, .nav-menu a.active { color: #38bdf8; background-color: rgba(56, 189, 248, 0.15); }
        .container { max-width: 900px; margin: 30px auto; padding: 0 20px; width: 100%; }
        .welcome-panel {
            background: #0d1322; border: 1px solid #1f2937; border-radius: 20px;
            padding: 25px; margin-bottom: 25px; text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .dev-badge {
            display: inline-block; background-color: rgba(56, 189, 248, 0.15);
            color: #38bdf8; font-size: 13px; padding: 5px 15px; border-radius: 15px;
            font-weight: bold; margin-top: 8px; border: 1px solid rgba(56, 189, 248, 0.3);
        }
        .search-box-inline {
            width: 100%; max-width: 550px; display: flex; gap: 8px; margin: 18px auto 0 auto;
        }
        .search-box-inline input {
            flex: 1; padding: 10px 15px; border-radius: 8px; border: 1px solid #374151;
            background-color: #050811; color: #ffffff; font-size: 13px;
        }
        .search-box-inline button {
            padding: 10px 20px; background-color: #38bdf8; color: #050811;
            border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 13px;
        }
        #aboutRes { margin-top: 12px; font-size: 14px; color: #fbbf24; font-weight: bold; }
        .services-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; }
        .service-card {
            background: #0d1322; border: 1px solid #1f2937; border-radius: 16px;
            padding: 22px; text-decoration: none; color: #ffffff; display: flex;
            flex-direction: column; align-items: center; text-align: center;
        }
        .service-card:hover { border-color: #38bdf8; transform: translateY(-5px); }
        .service-card .icon { font-size: 34px; margin-bottom: 10px; }
        .service-card h3 { margin: 0 0 6px 0; color: #38bdf8; font-size: 17px; }
        .service-card p { margin: 0; font-size: 12px; color: #9ca3af; line-height: 1.5; }
        .service-card.gold-card h3 { color: #fbbf24; }
        footer {
            margin-top: auto; text-align: center; padding: 15px;
            background-color: #0d1322; border-top: 1px solid #1f2937; font-size: 12px; color: #9ca3af;
        }
    </style>
</head>
<body>

    <header class="header-nav">
        <a href="/" class="brand-container">
            <!-- Profile image in the navigation bar -->
            <img src="/static/my_photo.jpg" class="navbar-avatar" alt="Photo of نزار أحمد شرقي">
            <span class="brand-title">nizarphonetics</span>
        </a>
        <nav class="nav-menu">
            <a href="/" class="active">Home</a>
            <a href="/contextual">Stylistic Translation</a>
            <a href="/standard">Direct Translation</a>
            <a href="/phonetics">IPA Phonetics</a>
            <a href="/thanks">Acknowledgements</a>
        </nav>
    </header>

    <div class="container">
        <div class="welcome-panel">
            <h2 style="margin: 0; font-size: 22px;">Advanced Translation and Research Platform</h2>
            <span class="dev-badge">Lead Developer and Researcher: نزار أحمد شرقي</span>

            <div class="search-box-inline">
                <input type="text" id="aboutInp" placeholder="Search (e.g. who created this or who is the developer?)">
                <button onclick="searchAbout()">Search</button>
            </div>
            <div id="aboutRes"></div>
        </div>

        <div class="services-grid">
            <a href="/contextual" class="service-card">
                <div class="icon">📝</div>
                <h3>Stylistic Translation</h3>
                <p>Choose the text context (academic, literary, technical, or legal) and tone.</p>
            </a>

            <a href="/standard" class="service-card">
                <div class="icon">🔄</div>
                <h3>Direct Paragraph Translation</h3>
                <p>Quickly translate long texts and paragraphs without stylistic processing.</p>
            </a>

            <a href="/phonetics" class="service-card">
                <div class="icon">🎙️</div>
                <h3>IPA Phonetics</h3>
                <p>Generate International Phonetic Alphabet (IPA) transcriptions.</p>
            </a>

            <a href="/thanks" class="service-card gold-card" style="grid-column: 1 / -1;">
                <div class="icon">👑</div>
                <h3>Academic Acknowledgements</h3>
                <p>Acknowledgements for the course supervisor, instructors, and 11 colleagues from the 2026 translation class.</p>
            </a>
        </div>
    </div>

    <footer>
        © 2026 All rights reserved | Developed by *نزار أحمد شرقي*
    </footer>

    <script>
        async function searchAbout() {
            let query = document.getElementById('aboutInp').value;
            if(!query.trim()) return;
            let res = await fetch('/about_query', {
                method: 'POST', 
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({query})
            });
            let data = await res.json();
            document.getElementById('aboutRes').innerText = data.response;
        }
    </script>
</body>
</html>
"""

@app.route('/contextual')
def contextual_page():
    return render_template('contextual.html')

@app.route('/standard')
def standard_page():
    return render_template('standard.html')

@app.route('/phonetics')
def phonetics_page():
    return render_template('phonetics.html')

@app.route('/thanks')
def thanks_page():
    return render_template('thanks.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

@app.route('/contact')
def contact_page():
    return render_template('contact.html')

@app.route('/')
def home():
    return render_template('index.html')

class TranslationServiceError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.status_code = status_code


def get_retry_after_seconds(error):
    response = getattr(error, 'response', None)
    headers = getattr(response, 'headers', {}) or {}
    retry_after = headers.get('retry-after') or headers.get('Retry-After')
    if not retry_after:
        return 1.0

    try:
        return max(0.0, float(retry_after))
    except (TypeError, ValueError):
        try:
            retry_at = parsedate_to_datetime(retry_after)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, (retry_at - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return 1.0


def get_gemini_keys():
    configured_keys = [
        os.environ.get(f'GEMINI_API_KEY_{index}', '').strip()
        for index in range(1, 10)
    ]
    legacy_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if legacy_key:
        configured_keys.append(legacy_key)
    return list(dict.fromkeys(key for key in configured_keys if key))


def get_gemini_client(api_key):
    if api_key not in gemini_clients:
        try:
            gemini_clients[api_key] = genai.Client(api_key=api_key)
        except Exception as error:
            app.logger.exception('Failed to initialize a Gemini client.')
            raise TranslationServiceError(
                'Gemini could not be initialized. Check the server configuration.',
                503,
            ) from error
    return gemini_clients[api_key]


def fetch_translation(text, src, tgt):
    supported_languages = {'en', 'ar'}
    if src.lower() not in supported_languages or tgt.lower() not in supported_languages:
        raise TranslationServiceError('The selected language pair is not supported.', 400)
    if src.lower() == tgt.lower():
        return text

    language_names = {'en': 'English', 'ar': 'Arabic'}
    source_language = language_names[src.lower()]
    target_language = language_names[tgt.lower()]
    system_instruction = (
        'You are a professional contextual translator. Translate the user text '
        f'from {source_language} into {target_language}. Preserve its meaning, '
        'tone, formatting, names, and numbers. Do not summarize, explain, or '
        'add commentary. Return only the translation.'
    )

    api_keys = get_gemini_keys()
    if not api_keys:
        raise TranslationServiceError(
            'Translation is not configured. Set GEMINI_API_KEY_1 through GEMINI_API_KEY_9.',
            503,
        )

    global gemini_key_cursor
    start_index = gemini_key_cursor % len(api_keys)
    gemini_key_cursor = (gemini_key_cursor + 1) % len(api_keys)
    ordered_keys = api_keys[start_index:] + api_keys[:start_index]
    last_error = None
    all_rate_limited = True

    for api_key in ordered_keys:
        try:
            client = get_gemini_client(api_key)
            response = None
            for attempt in range(2):
                try:
                    with app.app_context():
                        response = client.models.generate_content(
                            model=GEMINI_MODEL,
                            contents=text,
                            config=types.GenerateContentConfig(
                                system_instruction=system_instruction,
                            ),
                        )
                    break
                except Exception as error:
                    status_code = getattr(error, 'code', None) or getattr(error, 'status_code', None)
                    error_text = str(error).lower()
                    is_rate_limited = (
                        status_code == 429
                        or '429' in error_text
                        or 'resource_exhausted' in error_text
                    )
                    all_rate_limited = all_rate_limited and is_rate_limited
                    last_error = error
                    retry_after = get_retry_after_seconds(error)
                    if not is_rate_limited or attempt > 0 or retry_after > 5:
                        break
                    eventlet.sleep(retry_after)
            if response is not None:
                translated_text = (response.text or '').strip()
                if translated_text:
                    return translated_text
                raise TranslationServiceError('Gemini returned an empty translation. Please try again.', 503)
        except TranslationServiceError as error:
            last_error = error
            all_rate_limited = False
            app.logger.warning('Gemini client initialization failed; trying the next configured key.')
        except Exception as error:
            last_error = error
            status_code = getattr(error, 'code', None) or getattr(error, 'status_code', None)
            error_text = str(error).lower()
            is_rate_limited = (
                status_code == 429
                or '429' in error_text
                or 'resource_exhausted' in error_text
            )
            all_rate_limited = all_rate_limited and is_rate_limited
            app.logger.warning('Gemini key attempt failed; trying the next configured key.')

    app.logger.warning('All configured Gemini keys failed for model=%s.', GEMINI_MODEL)
    if all_rate_limited:
        raise TranslationServiceError(
            'All configured Gemini keys are temporarily rate-limiting requests. Please try again shortly.',
            503,
        ) from last_error
    raise TranslationServiceError(
        'Gemini translation is temporarily unavailable. Please try again shortly.',
        502,
    ) from last_error

def translate_long_text(text, src, tgt, config=None):
    config = config or load_app_config()
    max_length = int(config.get('max_segment_length', 450))
    segments = segment_text(text, max_length)
    translated_segments = [fetch_translation(segment, src, tgt) for segment in segments]
    return ' '.join(part for part in translated_segments if part)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json(silent=True) or {}
    message = str(data.get('message', '')).strip()
    name = str(data.get('name', '')).strip()[:80]
    if not message:
        return jsonify({'error': 'Enter your feedback before submitting.'}), 400
    if len(message) > 5000:
        return jsonify({'error': 'Feedback must be 5,000 characters or fewer.'}), 400

    feedback_path = Path(app.instance_path) / 'feedback_submissions.jsonl'
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {'submitted_at': datetime.now(timezone.utc).isoformat(), 'name': name, 'message': message}
    with feedback_path.open('a', encoding='utf-8') as feedback_file:
        feedback_file.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return jsonify({'result': 'Your feedback has been received. Thank you for sharing.'})

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get('name', '')).strip()[:80]
    email = str(data.get('email', '')).strip()[:254]
    topic = str(data.get('topic', '')).strip()[:100]
    message = str(data.get('message', '')).strip()
    if not message:
        return jsonify({'error': 'Enter your message before submitting.'}), 400
    if len(message) > 5000:
        return jsonify({'error': 'Your message must be 5,000 characters or fewer.'}), 400
    if email and ('@' not in email or '.' not in email.rsplit('@', 1)[-1]):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    contact_path = Path(app.instance_path) / 'contact_messages.jsonl'
    contact_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        'submitted_at': datetime.now(timezone.utc).isoformat(),
        'name': name,
        'email': email,
        'topic': topic,
        'message': message
    }
    with contact_path.open('a', encoding='utf-8') as contact_file:
        contact_file.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return jsonify({'result': 'Your message has been submitted. Thank you for contacting us.'})

@app.route('/translate_fast', methods=['POST'])
def translate_fast():
    try:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'Request body must be a JSON object.'}), 400

        text = str(data.get('text') or '').strip()
        config = load_app_config()
        requested_src = str(data.get('src') or config.get('default_source_language') or 'en').strip().lower()
        requested_tgt = str(data.get('tgt') or config.get('default_target_language') or 'ar').strip().lower()

        if config.get('auto_detect_language') and requested_src in {'auto', ''}:
            requested_src = detect_language(text)

        if not text:
            return jsonify({'result': 'Enter text to translate.'})

        result = translate_long_text(text, requested_src, requested_tgt, config=config)
    except TranslationServiceError as error:
        return jsonify({'error': str(error)}), error.status_code
    except Exception:
        app.logger.exception('Unexpected error while translating text.')
        return jsonify({'error': 'An unexpected error occurred while translating.'}), 500
    return jsonify({'result': result})


@app.errorhandler(HTTPException)
def handle_translation_http_error(error):
    if request.path == '/translate_fast':
        return jsonify({'error': error.description}), error.code
    return error.get_response()

@app.route('/phonetics_process', methods=['POST'])
def phonetics_process():
    data = request.get_json(silent=True) or {}
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'result': 'Enter some text first.'})

    ipa_result = f'/{eng_to_ipa.convert(text)}/'
    return jsonify({'result': ipa_result, 'ipa': ipa_result})


@app.route('/knx')
def knx_dashboard():
    config = load_app_config()
    return render_template('knx.html', channels=config.get('knx_channels', []), config=config)


@app.route('/admin/knx/save', methods=['POST'])
@admin_required
def admin_knx_save():
    if not valid_csrf(request.form):
        abort(400)
    config = load_app_config()
    channel_names = request.form.getlist('channel_name')
    group_addresses = request.form.getlist('group_address')
    rooms = request.form.getlist('room')
    types = request.form.getlist('type')
    statuses = request.form.getlist('status')
    channels = []

    for name, ga, room, channel_type, status in zip(channel_names, group_addresses, rooms, types, statuses):
        name = name.strip()[:80]
        if not name and not ga.strip():
            continue
        channels.append({
            'name': name or 'Unnamed Channel',
            'group_address': ga.strip() or '0/0/0',
            'room': room.strip() or 'Unknown',
            'type': channel_type.strip() or 'Automation',
            'status': status.strip() or 'Off',
        })

    if channels:
        config['knx_channels'] = channels
    save_app_config(config)
    flash('KNX channels updated.')
    return redirect(url_for('admin_page'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)