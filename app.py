import asyncio
from datetime import datetime, timezone
from functools import wraps
import hashlib
from io import BytesIO
import json
import os
import re
import secrets
from pathlib import Path
from urllib.parse import quote, urlsplit

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, abort, send_file, send_from_directory
import eng_to_ipa
from werkzeug.exceptions import HTTPException
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()
app = Flask(__name__)
configured_data_dir = os.environ.get('APP_DATA_DIR')
if configured_data_dir:
    app.instance_path = str(Path(configured_data_dir).expanduser().resolve())
Path(app.instance_path).mkdir(parents=True, exist_ok=True)
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
    'contact_phone': '',
    'facebook_url': '',
    'instagram_url': '',
    'tiktok_url': '',
    'contact_hours': 'Sunday to Thursday, 9:00 AM to 5:00 PM.',
    'contact_note': 'Share an idea or comment with the nizarphonetics team.',
    'contact_accent': '#d5ff3f',
    'contact_decoration': 'minimal',
    'language_prompt_enabled': True,
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
            content[key] = saved[key][:2000]
    return content


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
    return {'site_content': load_site_content()}

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
            if filename == 'feedback_submissions.jsonl':
                entry['is_read'] = bool(entry.get('is_read', False))
            submitted_at = entry.get('submitted_at', '')
            try:
                parsed_date = datetime.fromisoformat(submitted_at.replace('Z', '+00:00'))
                entry['_display_date'] = parsed_date.astimezone().strftime('%Y-%m-%d %H:%M')
            except (AttributeError, TypeError, ValueError):
                entry['_display_date'] = submitted_at or 'Unknown'
            messages.append(entry)
    return messages


def find_feedback_line(lines, feedback_id):
    if len(feedback_id) != 64:
        return None
    return next((
        index for index, line in enumerate(lines)
        if secrets.compare_digest(
            hashlib.sha256(f'{index}:{line}'.encode('utf-8')).hexdigest(), feedback_id
        )
    ), None)


def save_feedback_lines(path, lines):
    temporary_path = path.with_suffix('.tmp')
    temporary_path.write_text('\n'.join(lines) + ('\n' if lines else ''), encoding='utf-8')
    temporary_path.replace(path)


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
        feedback_messages=load_message_file('feedback_submissions.jsonl')
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
        'contact_email': 254, 'contact_phone': 40,
        'facebook_url': 500, 'instagram_url': 500, 'tiktok_url': 500,
        'contact_hours': 300, 'contact_note': 600,
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
    if re.search(r'[^0-9+().\-\s]', content['contact_phone']):
        flash('Please use a valid phone number.')
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
    content['language_prompt_enabled'] = request.form.get('language_prompt_enabled') == 'on'
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

@app.route('/admin/students/<int:student_index>/edit', methods=['POST'])
@admin_required
def admin_edit_student(student_index):
    if not valid_csrf(request.form):
        abort(400)
    content = load_site_content()
    students = content['students']
    if student_index < 0 or student_index >= len(students):
        abort(404)
    name = request.form.get('name', '')
    if not name.strip():
        flash('Enter a name to save.')
    elif len(name) > 100:
        flash('Names must be 100 characters or fewer.')
    elif name.casefold() in {
        student.casefold() for index, student in enumerate(students)
        if index != student_index
    }:
        flash('This name already exists.')
    else:
        students[student_index] = name
        content['students'] = students
        save_site_content(content)
        flash('Name updated.')
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
    feedback_path = Path(app.instance_path) / 'feedback_submissions.jsonl'
    try:
        lines = feedback_path.read_text(encoding='utf-8').splitlines()
    except OSError:
        abort(404)
    matching_index = find_feedback_line(lines, feedback_id)
    if matching_index is None:
        abort(404)
    del lines[matching_index]
    save_feedback_lines(feedback_path, lines)
    flash('Feedback deleted.')
    return redirect(url_for('admin_page') + '#feedback')

@app.route('/admin/feedback/<feedback_id>/read', methods=['POST'])
@admin_required
def admin_mark_feedback_read(feedback_id):
    if not valid_csrf(request.form):
        abort(400)
    feedback_path = Path(app.instance_path) / 'feedback_submissions.jsonl'
    try:
        lines = feedback_path.read_text(encoding='utf-8').splitlines()
    except OSError:
        abort(404)
    matching_index = find_feedback_line(lines, feedback_id)
    if matching_index is None:
        abort(404)
    try:
        entry = json.loads(lines[matching_index])
    except ValueError:
        abort(404)
    if not isinstance(entry, dict):
        abort(404)
    entry['is_read'] = True
    lines[matching_index] = json.dumps(entry, ensure_ascii=False)
    save_feedback_lines(feedback_path, lines)
    flash('Feedback marked as read.')
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
        destination = Path(app.instance_path) / 'uploads' / destinations[slot]
        destination.parent.mkdir(parents=True, exist_ok=True)
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
            <a href="/phonetics">IPA Phonetics</a>
            <a href="/thanks">Acknowledgements</a>
        </nav>
    </header>

    <div class="container">
        <div class="welcome-panel">
            <h2 style="margin: 0; font-size: 22px;">English Phonetics Studio</h2>
            <span class="dev-badge">Lead Developer and Researcher: نزار أحمد شرقي</span>

            <div class="search-box-inline">
                <input type="text" id="aboutInp" placeholder="Search (e.g. who created this or who is the developer?)">
                <button onclick="searchAbout()">Search</button>
            </div>
            <div id="aboutRes"></div>
        </div>

        <div class="services-grid">
            <a href="/phonetics" class="service-card">
                <div class="icon">🎙️</div>
                <h3>IPA Phonetics</h3>
                <p>Generate International Phonetic Alphabet (IPA) transcriptions.</p>
            </a>

            <a href="/thanks" class="service-card gold-card" style="grid-column: 1 / -1;">
                <div class="icon">👑</div>
                <h3>Academic Acknowledgements</h3>
                <p>Acknowledgements for the course supervisor, instructors, and colleagues from the phonetics course.</p>
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

@app.route('/phonetics')
def phonetics_page():
    return render_template('phonetics.html')

@app.route('/site-image/<filename>')
def site_image(filename):
    if filename not in {'my_photo.jpg', 'my_photo2.jpg'}:
        abort(404)
    uploads_dir = Path(app.instance_path) / 'uploads'
    if (uploads_dir / filename).is_file():
        return send_from_directory(uploads_dir, filename)
    return send_from_directory(app.static_folder, filename)

@app.route('/thanks')
def thanks_page():
    return render_template('thanks.html')

@app.route('/about')
def about_page():
    return render_template('about.html')

def social_profile_url(platform, account):
    base_urls = {
        'facebook': 'https://www.facebook.com/',
        'instagram': 'https://www.instagram.com/',
        'tiktok': 'https://www.tiktok.com/@',
    }
    if platform not in base_urls:
        return ''
    account = str(account or '').strip()
    if not account:
        return ''
    candidate = account
    if re.match(r'^(?:www\.)?(?:facebook\.com|instagram\.com|tiktok\.com)/', candidate, re.IGNORECASE):
        candidate = f'https://{candidate}'
    if re.match(r'^https?://', candidate, re.IGNORECASE):
        parsed_url = urlsplit(candidate)
        return candidate if parsed_url.netloc and parsed_url.hostname else ''
    username = account.removeprefix('@')
    if not re.fullmatch(r'[A-Za-z0-9._-]{1,100}', username):
        return ''
    profile_url = base_urls[platform] + quote(username, safe='._-')
    return profile_url + '/' if platform == 'instagram' else profile_url

@app.route('/contact')
def contact_page():
    content = load_site_content()
    social_profiles = [
        ('Facebook', 'facebook', content['facebook_url']),
        ('Instagram', 'instagram', content['instagram_url']),
        ('TikTok', 'tiktok', content['tiktok_url']),
    ]
    social_profiles = [
        (label, account, social_profile_url(platform, account))
        for label, platform, account in social_profiles if account
    ]
    whatsapp_number = re.sub(r'\D', '', content['contact_phone'])
    return render_template(
        'contact.html',
        social_profiles=social_profiles,
        whatsapp_url=f'https://wa.me/{whatsapp_number}' if whatsapp_number else '',
    )

@app.route('/feedback', strict_slashes=False)
def feedback_page():
    return render_template('feedback.html')

@app.route('/')
def home():
    return render_template('index.html')


BRITISH_IPA_WORDS = {
    'about': 'əˈbaʊt', 'bird': 'bɜːd', 'car': 'kɑː', 'far': 'fɑː',
    'go': 'ɡəʊ', 'hard': 'hɑːd', 'hot': 'hɒt', 'lot': 'lɒt',
    'near': 'nɪə', 'no': 'nəʊ', 'not': 'nɒt', 'road': 'rəʊd',
    'square': 'skweə', 'thought': 'θɔːt', 'water': 'wɔːtə',
}
AMERICAN_IPA_WORDS = {
    'bird': 'bɝd', 'car': 'kɑr', 'father': 'ˈfɑðɚ', 'far': 'fɑr',
    'go': 'ɡoʊ', 'hard': 'hɑrd', 'hot': 'hɑt', 'lot': 'lɑt',
    'road': 'roʊd', 'thought': 'θɔt', 'water': 'ˈwɔɾɚ',
}


def transcribe_ipa(text, accent):
    if accent not in {'en-GB', 'en-US'}:
        raise ValueError('Choose British or American English.')

    transcription = []
    for token in re.findall(r"[A-Za-z]+(?:['’][A-Za-z]+)?|[^A-Za-z]+", text):
        if not token[0].isalpha():
            transcription.append(token)
            continue
        word = token.lower().replace('’', "'")
        ipa = eng_to_ipa.convert(token)
        if accent == 'en-GB':
            ipa = BRITISH_IPA_WORDS.get(word, ipa)
            ipa = re.sub(r'(?<=[ɑɔəɜɛɪʊu])r$', '', ipa)
        else:
            ipa = AMERICAN_IPA_WORDS.get(word, ipa)
        transcription.append(ipa)
    return ''.join(transcription)


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.get_json(silent=True) or {}
    message = str(data.get('message', '')).strip()
    name = str(data.get('name', '')).strip()[:80]
    email = str(data.get('email', '')).strip()[:254]
    phone = str(data.get('phone', '')).strip()[:40]
    if not name:
        return jsonify({'error': 'Enter your name before submitting.'}), 400
    if not re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email):
        return jsonify({'error': 'Enter a valid email address before submitting.'}), 400
    if not message:
        return jsonify({'error': 'Enter your feedback before submitting.'}), 400
    if len(message) > 5000:
        return jsonify({'error': 'Feedback must be 5,000 characters or fewer.'}), 400
    if email and ('@' not in email or '.' not in email.rsplit('@', 1)[-1]):
        return jsonify({'error': 'Please enter a valid email address.'}), 400
    if re.search(r'[^0-9+().\-\s]', phone):
        return jsonify({'error': 'Please enter a valid phone number.'}), 400

    feedback_path = Path(app.instance_path) / 'feedback_submissions.jsonl'
    feedback_path.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        'submitted_at': datetime.now(timezone.utc).isoformat(),
        'name': name,
        'email': email,
        'phone': phone,
        'message': message,
        'is_read': False,
    }
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

@app.errorhandler(HTTPException)
def handle_http_error(error):
    return error.get_response()

@app.route('/phonetics_process', methods=['POST'])
def phonetics_process():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object.'}), 400
    text = str(data.get('text', '')).strip()
    if not text:
        return jsonify({'result': 'Enter some text first.'})
    if len(text) > 4000:
        return jsonify({'error': 'Text must be 4,000 characters or fewer.'}), 400
    accent = str(data.get('accent', 'en-GB'))
    if accent not in {'en-GB', 'en-US'}:
        return jsonify({'error': 'Choose British or American English.'}), 400

    ipa_result = f'/{transcribe_ipa(text, accent)}/'
    return jsonify({'result': ipa_result, 'ipa': ipa_result})


@app.route('/speech_download', methods=['POST'])
def speech_download():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Request body must be a JSON object.'}), 400

    text = str(data.get('text', '')).strip()
    accent = str(data.get('accent', 'en-GB'))
    voices = {'en-GB': 'en-GB-SoniaNeural', 'en-US': 'en-US-AriaNeural'}
    if not text:
        return jsonify({'error': 'Enter text before downloading audio.'}), 400
    if len(text) > 4000:
        return jsonify({'error': 'Text must be 4,000 characters or fewer.'}), 400
    if accent not in voices:
        return jsonify({'error': 'Choose British or American English.'}), 400
    volume = data.get('volume', 100)
    if not isinstance(volume, int) or not 0 <= volume <= 100:
        return jsonify({'error': 'Volume must be between 0 and 100.'}), 400

    audio = BytesIO()

    async def synthesize():
        import edge_tts

        communicator = edge_tts.Communicate(
            text,
            voices[accent],
            volume=f'{volume - 100:+d}%',
        )
        async for chunk in communicator.stream():
            if chunk.get('type') == 'audio':
                audio.write(chunk['data'])

    try:
        asyncio.run(asyncio.wait_for(synthesize(), timeout=45))
    except Exception:
        app.logger.exception('Speech audio generation failed for accent %s.', accent)
        return jsonify({'error': 'Audio could not be generated. Try again shortly.'}), 502

    if not audio.getbuffer().nbytes:
        return jsonify({'error': 'The speech service returned no audio.'}), 502
    audio.seek(0)
    return send_file(
        audio,
        mimetype='audio/mpeg',
        as_attachment=True,
        download_name=f'pronunciation-{accent}.mp3',
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)