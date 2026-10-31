import asyncio
from datetime import datetime, timezone
from datetime import timedelta
from functools import wraps
import hashlib
from io import BytesIO
import html
import json
import logging
import mimetypes
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import unicodedata
from pathlib import Path
from urllib.parse import quote, urlsplit

from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash, abort, send_file, send_from_directory
import eng_to_ipa
from werkzeug.exceptions import HTTPException, RequestEntityTooLarge
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

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
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=80),
    MAX_CONTENT_LENGTH=12 * 1024 * 1024,
)

CHAT_HISTORY_PATH = Path(app.instance_path) / 'chat_history.jsonl'
CHAT_MEDIA_DIR = Path(app.instance_path) / 'uploads' / 'chat'
CHAT_USERS_DB_PATH = Path(app.instance_path) / 'chat_users.sqlite3'
CHAT_SETTINGS_PATH = Path(app.instance_path) / 'chat_settings.json'
CHAT_SESSION_LIFETIME = timedelta(hours=80)
CHAT_PRESENCE_TIMEOUT = timedelta(seconds=90)
CHAT_UPLOAD_MAX_BYTES = 10 * 1024 * 1024
CHAT_ALLOWED_EXTENSIONS = {
    '.jpg', '.jpeg', '.png', '.webp', '.gif',
    '.mp3', '.wav', '.ogg', '.m4a', '.aac',
    '.mp4', '.webm', '.mov', '.m4v',
    '.pdf', '.txt', '.doc', '.docx', '.ppt', '.pptx',
}
CHAT_VIDEO_EXTENSIONS = {'.mp4', '.webm', '.mov', '.m4v'}
VIDEO_MAX_SECONDS = 60
STUDENT_ID_PATH = Path(app.instance_path) / 'student_ids.json'
SECURITY_LOGGER = logging.getLogger('nizarphonetics.security')
if not SECURITY_LOGGER.handlers:
    security_handler = logging.StreamHandler()
    security_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
    SECURITY_LOGGER.addHandler(security_handler)
SECURITY_LOGGER.setLevel(logging.INFO)
SECURITY_LOGGER.propagate = False

DANGEROUS_INPUT_PATTERNS = (
    re.compile(r'(?is)<\s*(script|iframe|object|embed|svg|math|style)\b'),
    re.compile(r'(?is)javascript\s*:'),
    re.compile(r'(?is)on\w+\s*='),
    re.compile(r'(?is)data\s*:\s*(?:text/html|image/svg\+xml|application/javascript|text/javascript)'),
    re.compile(r'(?is)\b(?:union\s+select|select\s+\*|drop\s+table|insert\s+into|delete\s+from|update\s+.*\s+set)\b'),
    re.compile(r'(?is)(?:;\s*(?:curl|wget|bash|sh|chmod|nc|powershell|cmd)|\$\([^)]*\)|`[^`]+`|\|\|\s*(?:curl|wget|bash|sh))'),
)


class SecurityValidationError(ValueError):
    """Raised when a file or input fails the security validation layer."""


def log_security_event(event_name, detail, **extra):
    summary = detail
    if extra:
        summary += ' ' + ' '.join(f'{key}={value}' for key, value in sorted(extra.items()))
    SECURITY_LOGGER.warning('SECURITY %s: %s', event_name, summary)


def sanitize_file_name(filename):
    raw_name = str(filename or '').replace('\\', '/')
    raw_name = os.path.basename(raw_name)
    raw_name = raw_name.replace('\x00', '')
    raw_name = unicodedata.normalize('NFKC', raw_name)
    raw_name = ''.join(ch for ch in raw_name if ch.isprintable() and ch not in {'/', '\\', ':', '*', '?', '"', '<', '>', '|'} )
    cleaned_name = secure_filename(raw_name) or 'upload'
    cleaned_name = re.sub(r'\s+', ' ', cleaned_name).strip().strip('.')
    return cleaned_name[:160] or 'upload'


def sanitize_user_text(value, field_name='message', max_length=2000):
    if value is None:
        return ''
    text = unicodedata.normalize('NFKC', str(value))
    text = text.replace('\x00', '')
    text = ''.join(ch for ch in text if ch.isprintable() or ch in '\n\r\t')
    text = text.strip()
    text = re.sub(r'[\u202a-\u202e\u2066-\u2069]', '', text)
    if not text:
        return ''
    for pattern in DANGEROUS_INPUT_PATTERNS:
        if pattern.search(text):
            raise SecurityValidationError(f'{field_name} contains dangerous content.')
    if len(text) > max_length:
        raise SecurityValidationError(f'{field_name} exceeds the allowed length.')
    return text


def sanitize_display_name(value, max_length=60):
    if value is None:
        raise SecurityValidationError('Display name is required.')
    name = sanitize_user_text(value, field_name='display name', max_length=max_length)
    name = re.sub(r'\s+', ' ', name).strip()
    if len(name) < 2:
        raise SecurityValidationError('Display name is too short.')
    if not re.fullmatch(r'[\w\s\-\.]+', name, flags=re.UNICODE):
        raise SecurityValidationError('Display name contains unsupported characters.')
    return name[:max_length]


def is_dangerous_binary_payload(payload):
    sample = payload[:4096].lower()
    if not sample:
        return True
    if b'<' in sample and any(token in sample for token in (b'<script', b'javascript:', b'vbscript:', b'onerror=', b'onload=', b'<!doctype html', b'<html', b'<?php')):
        return True
    if b'#!/bin/' in sample or b'#!/usr/bin/env' in sample:
        return True
    if b'cmd.exe' in sample or b'/bin/sh' in sample or b'powershell' in sample:
        return True
    if sample.startswith((b'<?php', b'<?', b'<!doctype html', b'<html', b'<script')):
        return True
    return False


def is_valid_file_signature(extension, header):
    normalized = extension.lower()
    if normalized in {'.jpg', '.jpeg'}:
        return header.startswith(b'\xff\xd8\xff')
    if normalized == '.png':
        return header.startswith(b'\x89PNG\r\n\x1a\n')
    if normalized == '.gif':
        return header.startswith((b'GIF87a', b'GIF89a'))
    if normalized == '.webp':
        return header.startswith(b'RIFF') and header[8:12] == b'WEBP'
    if normalized in {'.mp3', '.wav'}:
        return (header.startswith(b'ID3') or header.startswith((b'\xff\xfb', b'\xff\xf3', b'\xff\xf2')) or (header.startswith(b'RIFF') and header[8:12] == b'WAVE'))
    if normalized in {'.ogg', '.oga'}:
        return header.startswith(b'OggS')
    if normalized in {'.m4a', '.mp4', '.m4v', '.mov'}:
        return header.startswith(b'\x00\x00\x00') and b'ftyp' in header[4:12] or header.startswith(b'ftyp') or b'ftyp' in header[:32]
    if normalized == '.aac':
        return header.startswith((b'\xff\xf1', b'\xff\xf9', b'\xff\xfa'))
    if normalized == '.pdf':
        return header.startswith(b'%PDF')
    if normalized in {'.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx'}:
        return header.startswith(b'PK') or header.startswith(b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1')
    if normalized == '.txt':
        return not is_dangerous_binary_payload(header)
    return True


def detect_video_duration(path):
    ffprobe_path = shutil.which('ffprobe')
    if not ffprobe_path:
        return None
    try:
        result = subprocess.run(
            [ffprobe_path, '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', str(path)],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    try:
        duration = float(result.stdout.strip().splitlines()[0])
    except ValueError:
        return None
    return duration if duration > 0 else None


def validate_uploaded_media(uploaded, allowed_extensions, max_bytes, *, video_max_seconds=None, mime_map=None):
    if uploaded is None or not getattr(uploaded, 'filename', None):
        raise SecurityValidationError('No file was selected.')

    original_name = sanitize_file_name(uploaded.filename)
    extension = Path(original_name).suffix.lower()
    if extension not in allowed_extensions:
        raise SecurityValidationError('This file type is not allowed.')

    try:
        uploaded.stream.seek(0, os.SEEK_END)
        file_size = uploaded.stream.tell()
        uploaded.stream.seek(0)
    except (AttributeError, OSError):
        raise SecurityValidationError('The file could not be read securely.')
    if file_size <= 0 or file_size > max_bytes:
        raise SecurityValidationError('The file is empty or exceeds the maximum upload size.')

    header = uploaded.stream.read(4096)
    uploaded.stream.seek(0)
    if not header:
        raise SecurityValidationError('The file does not contain any readable data.')
    if is_dangerous_binary_payload(header):
        raise SecurityValidationError('The file content matches a dangerous or executable payload.')
    if not is_valid_file_signature(extension, header):
        raise SecurityValidationError('The file signature does not match the expected format.')

    guessed_mimetype = (uploaded.mimetype or mimetypes.guess_type(original_name)[0] or 'application/octet-stream').lower()
    expected_mimetypes = mime_map.get(extension, {guessed_mimetype}) if mime_map else {guessed_mimetype}
    if guessed_mimetype not in expected_mimetypes:
        raise SecurityValidationError('The file MIME type does not match the allowed list.')

    if extension in CHAT_VIDEO_EXTENSIONS and video_max_seconds is not None:
        temporary_path = Path(app.instance_path) / 'uploads' / 'tmp' / f'{secrets.token_hex(8)}{extension}'
        temporary_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            uploaded.save(temporary_path)
            duration = detect_video_duration(temporary_path)
            if duration is not None and duration > video_max_seconds:
                raise SecurityValidationError('Video files must be 60 seconds or shorter.')
        finally:
            try:
                if temporary_path.exists():
                    temporary_path.unlink()
            except OSError:
                pass

    return {'original_name': original_name, 'extension': extension, 'size': file_size, 'mimetype': guessed_mimetype}


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
    ensure_data_file(CHAT_HISTORY_PATH, '')
    try:
        if CHAT_HISTORY_PATH.stat().st_size == 2 and CHAT_HISTORY_PATH.read_bytes() == b'[]':
            CHAT_HISTORY_PATH.write_text('', encoding='utf-8')
    except OSError:
        pass
    with CHAT_HISTORY_PATH.open('a+', encoding='utf-8') as chat_file:
        chat_file.seek(0, os.SEEK_END)
        if chat_file.tell():
            chat_file.seek(chat_file.tell() - 1)
            if chat_file.read(1) != '\n':
                chat_file.seek(0, os.SEEK_END)
                chat_file.write('\n')
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
        entry['_id'] = str(entry.get('id') or hashlib.sha256(line.encode('utf-8')).hexdigest()[:24])
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


def chat_media_path(filename):
    if not isinstance(filename, str) or not re.fullmatch(r'[a-f0-9]{32}\.[a-z0-9]{1,10}', filename):
        return None
    media_dir = CHAT_MEDIA_DIR.resolve()
    media_path = (media_dir / filename).resolve()
    return media_path if media_path.parent == media_dir else None


def chat_attachments(message):
    attachment = message.get('attachment')
    if isinstance(attachment, dict):
        return [attachment]
    attachments = message.get('attachments')
    return [item for item in attachments if isinstance(item, dict)] if isinstance(attachments, list) else []


def delete_chat_message_media(message):
    deleted_files = 0
    deleted_bytes = 0
    for attachment in chat_attachments(message):
        media_path = chat_media_path(attachment.get('filename'))
        if media_path is None:
            continue
        try:
            if media_path.is_file():
                deleted_bytes += media_path.stat().st_size
                media_path.unlink()
                deleted_files += 1
        except OSError:
            app.logger.exception('Could not remove chat media file %s.', media_path.name)
    return deleted_files, deleted_bytes


def parse_chat_timestamp(value):
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
    except ValueError:
        return None
    return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)


def connect_chat_database():
    CHAT_USERS_DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(CHAT_USERS_DB_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute('''
        CREATE TABLE IF NOT EXISTS chat_users (
            user_id TEXT PRIMARY KEY,
            name_key TEXT NOT NULL UNIQUE,
            display_name TEXT NOT NULL,
            registered_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            typing_until TEXT
        )
    ''')
    user_columns = {row['name'] for row in connection.execute('PRAGMA table_info(chat_users)')}
    if 'typing_until' not in user_columns:
        connection.execute('ALTER TABLE chat_users ADD COLUMN typing_until TEXT')
    connection.commit()
    return connection


def register_chat_user(display_name):
    now = datetime.now(timezone.utc)
    user_id = secrets.token_hex(16)
    name_key = unicodedata.normalize('NFKC', display_name).strip().casefold()
    connection = connect_chat_database()
    try:
        connection.execute('BEGIN IMMEDIATE')
        connection.execute('DELETE FROM chat_users WHERE expires_at <= ?', (now.isoformat(),))
        connection.execute(
            'INSERT INTO chat_users (user_id, name_key, display_name, registered_at, expires_at, last_seen_at) VALUES (?, ?, ?, ?, ?, ?)',
            (user_id, name_key, display_name, now.isoformat(), (now + CHAT_SESSION_LIFETIME).isoformat(), now.isoformat()),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        return None
    finally:
        connection.close()
    return {'user_id': user_id, 'name_key': name_key, 'registered_at': now.isoformat()}


def validate_chat_user_session():
    user_id = session.get('chat_user_id')
    name_key = session.get('chat_name_key')
    if not user_id or not name_key:
        return False
    connection = connect_chat_database()
    try:
        row = connection.execute(
            'SELECT expires_at FROM chat_users WHERE user_id = ? AND name_key = ?',
            (user_id, name_key),
        ).fetchone()
    finally:
        connection.close()
    expires_at = parse_chat_timestamp(row['expires_at']) if row else None
    return bool(expires_at and expires_at > datetime.now(timezone.utc))


def touch_chat_user():
    if not validate_chat_user_session():
        return False
    connection = connect_chat_database()
    try:
        cursor = connection.execute(
            'UPDATE chat_users SET last_seen_at = ? WHERE user_id = ? AND name_key = ?',
            (datetime.now(timezone.utc).isoformat(), session['chat_user_id'], session['chat_name_key']),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def online_chat_presence(exclude_user_id=None):
    now = datetime.now(timezone.utc)
    cutoff = now - CHAT_PRESENCE_TIMEOUT
    connection = connect_chat_database()
    try:
        rows = connection.execute(
            'SELECT user_id, display_name, last_seen_at, expires_at, typing_until FROM chat_users'
        ).fetchall()
    finally:
        connection.close()
    online_users = [
        row for row in rows
        if (parse_chat_timestamp(row['last_seen_at']) or datetime.min.replace(tzinfo=timezone.utc)) >= cutoff
        and (parse_chat_timestamp(row['expires_at']) or now) > now
    ]
    typing_users = sorted(
        (
            row['display_name'] for row in online_users
            if row['user_id'] != exclude_user_id
            and (parse_chat_timestamp(row['typing_until']) or now) > now
        ),
        key=str.casefold,
    )
    return {
        'online_user_ids': {row['user_id'] for row in online_users},
        'online_count': len(online_users),
        'typing_users': typing_users,
    }


def online_chat_user_ids():
    return online_chat_presence()['online_user_ids']


def load_chat_settings():
    try:
        settings = json.loads(CHAT_SETTINGS_PATH.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        settings = {}
    badge_label = settings.get('badge_label', 'HOST') if isinstance(settings, dict) else 'HOST'
    badge_label = ''.join(character for character in str(badge_label) if character.isprintable()).strip()[:16]
    return {'badge_label': badge_label or 'HOST'}


def save_chat_settings(settings):
    CHAT_SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = CHAT_SETTINGS_PATH.with_suffix('.tmp')
    temporary_path.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary_path.replace(CHAT_SETTINGS_PATH)


def clean_chat_history_before(cutoff):
    ensure_data_file(CHAT_HISTORY_PATH, '')
    try:
        lines = CHAT_HISTORY_PATH.read_text(encoding='utf-8').splitlines()
    except OSError:
        return {'messages': 0, 'files': 0, 'bytes': 0}

    retained_lines = []
    removed_messages = 0
    removed_files = 0
    removed_bytes = 0
    for line in lines:
        try:
            entry = json.loads(line)
        except (TypeError, ValueError):
            retained_lines.append(line)
            continue
        timestamp = parse_chat_timestamp(entry.get('submitted_at')) if isinstance(entry, dict) else None
        if isinstance(entry, dict) and timestamp and timestamp < cutoff:
            files, size = delete_chat_message_media(entry)
            removed_messages += 1
            removed_files += files
            removed_bytes += size
        else:
            retained_lines.append(line)

    temporary_path = CHAT_HISTORY_PATH.with_suffix('.tmp')
    temporary_path.write_text('\n'.join(retained_lines) + ('\n' if retained_lines else ''), encoding='utf-8')
    temporary_path.replace(CHAT_HISTORY_PATH)
    return {'messages': removed_messages, 'files': removed_files, 'bytes': removed_bytes}


def clear_chat_history():
    messages = load_chat_messages()
    deleted_files = 0
    deleted_bytes = 0
    for message in messages:
        files, size = delete_chat_message_media(message)
        deleted_files += files
        deleted_bytes += size
    ensure_data_file(CHAT_HISTORY_PATH, '')
    CHAT_HISTORY_PATH.write_text('', encoding='utf-8')
    return {'messages': len(messages), 'files': deleted_files, 'bytes': deleted_bytes}


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
    'founder_name': 'نزار احمد شرقي',
    'founder_bio': 'Founder of nizarphonetics, building thoughtful tools for English pronunciation and phonetic learning.',
    'contact_title': 'Contact nizarphonetics',
    'contact_intro': 'Send a question, suggestion, or note to the nizarphonetics team.',
    'contact_email_label': 'Email',
    'contact_hours_label': 'Response Hours',
    'contact_note_title': 'Your Feedback Matters',
    'contact_email': 'nezarsharqi@hotmail.com',
    'contact_phone': '+967 733694139',
    'facebook_url': 'https://www.facebook.com/share/1BGXh2hsJN/',
    'instagram_url': 'https://www.instagram.com/nizarsharqi?psln=MmpsMW5vanZoNXB5',
    'tiktok_url': 'tiktok.com/@nizarsharqi',
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


def chat_user_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get('is_admin'):
            return view(*args, **kwargs)
        if not active_chat_name():
            if request.endpoint in {'chat_messages_api', 'chat_send_message', 'chat_upload', 'chat_typing'}:
                return jsonify({'error': 'Register your name to enter chat.'}), 401
            return redirect(url_for('chat_page'))
        return view(*args, **kwargs)
    return wrapped


def active_chat_name():
    chat_name = session.get('chat_name')
    registered_at = parse_chat_timestamp(session.get('chat_registered_at'))
    if not chat_name or not registered_at or datetime.now(timezone.utc) - registered_at >= CHAT_SESSION_LIFETIME or not touch_chat_user():
        session.pop('chat_name', None)
        session.pop('chat_registered_at', None)
        session.pop('chat_user_id', None)
        session.pop('chat_name_key', None)
        return None
    return chat_name

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
    if filename == 'feedback_submissions.jsonl':
        messages = sort_entries_by_date(messages)
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


def sort_entries_by_date(entries):
    def parse_sort_value(entry):
        submitted_at = str(entry.get('submitted_at') or '')
        if not submitted_at:
            return datetime.min.replace(tzinfo=timezone.utc)
        try:
            return datetime.fromisoformat(submitted_at.replace('Z', '+00:00')).astimezone(timezone.utc)
        except (AttributeError, TypeError, ValueError):
            return datetime.min.replace(tzinfo=timezone.utc)
    return sorted(entries, key=lambda entry: parse_sort_value(entry), reverse=True)


def serialize_chat_message(entry, online_user_ids=None, badge_label=None):
    is_admin_message = bool(entry.get('is_admin'))
    attachments = []
    for attachment in chat_attachments(entry):
        filename = attachment.get('filename', '')
        if chat_media_path(filename) is None:
            continue
        attachments.append({
            'filename': filename,
            'name': html.escape(str(attachment.get('original_name') or filename), quote=False),
            'kind': str(attachment.get('kind') or 'file'),
            'mimetype': str(attachment.get('mimetype') or 'application/octet-stream'),
            'size': int(attachment.get('size') or 0),
            'url': url_for('chat_media', filename=filename),
            'download_url': url_for('chat_media', filename=filename, download='1'),
        })
    return {
        'id': str(entry.get('_id') or entry.get('id') or ''),
        'name': 'BOSS' if is_admin_message else html.escape(str(entry.get('username') or 'Guest')[:60], quote=False),
        'text': html.escape(str(entry.get('message') or '')[:2000], quote=False),
        'submitted_at': str(entry.get('submitted_at') or ''),
        'reply_to': html.escape(str(entry.get('reply_to') or ''), quote=False),
        'online': bool(not is_admin_message and entry.get('user_id') and entry.get('user_id') in (online_user_ids or set())),
        'is_admin': is_admin_message,
        'badge_label': 'BOSS' if is_admin_message else badge_label or load_chat_settings()['badge_label'],
        'attachments': attachments,
    }


def chat_storage_usage():
    total_bytes = 0
    file_count = 0
    if CHAT_MEDIA_DIR.exists():
        for media_path in CHAT_MEDIA_DIR.iterdir():
            try:
                if media_path.is_file():
                    total_bytes += media_path.stat().st_size
                    file_count += 1
            except OSError:
                continue
    return {'files': file_count, 'bytes': total_bytes}


@app.route('/chat', methods=['GET'])
def chat_page():
    if session.get('is_admin'):
        return render_template('chat.html', csrf_token=csrf_token(), chat_name='BOSS', is_admin=True)
    chat_name = active_chat_name()
    if not chat_name:
        return render_template('chat_register.html', csrf_token=csrf_token(), error='')
    return render_template('chat.html', csrf_token=csrf_token(), chat_name=chat_name, is_admin=False)


@app.route('/chat/register', methods=['POST'])
def chat_register():
    if not valid_csrf(request.form):
        abort(400)
    if active_chat_name():
        return redirect(url_for('chat_page'))
    try:
        chat_name = sanitize_display_name(request.form.get('chat_name', ''))
    except SecurityValidationError as exc:
        log_security_event('chat_name_blocked', str(exc), remote_addr=request.remote_addr)
        return render_template(
            'chat_register.html', csrf_token=csrf_token(),
            error='Choose a printable display name between 2 and 60 characters.',
        ), 400
    registration = register_chat_user(chat_name)
    if registration is None:
        return render_template(
            'chat_register.html', csrf_token=csrf_token(),
            error='That name is already in use. Choose another or return after its 80-hour session expires.',
        ), 409
    session['chat_name'] = chat_name
    session['chat_name_key'] = registration['name_key']
    session['chat_user_id'] = registration['user_id']
    session['chat_registered_at'] = registration['registered_at']
    session.permanent = True
    return redirect(url_for('chat_page'))


@app.route('/chat/messages', methods=['GET'])
@chat_user_required
def chat_messages_api():
    presence = online_chat_presence(exclude_user_id=session.get('chat_user_id'))
    badge_label = load_chat_settings()['badge_label']
    messages = [
        serialize_chat_message(entry, online_user_ids=presence['online_user_ids'], badge_label=badge_label)
        for entry in load_chat_messages(limit=200)
    ]
    return jsonify({
        'messages': messages,
        'online_count': presence['online_count'],
        'typing_users': presence['typing_users'],
    })


@app.route('/chat/typing', methods=['POST'])
@chat_user_required
def chat_typing():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or type(data.get('typing')) is not bool:
        return jsonify({'error': 'Send a valid typing status.'}), 400
    if not valid_csrf(data):
        return jsonify({'error': 'Refresh the page and try again.'}), 400
    if session.get('is_admin'):
        return jsonify({'ok': True})

    now = datetime.now(timezone.utc)
    typing_until = (now + timedelta(seconds=6)).isoformat() if data['typing'] else None
    connection = connect_chat_database()
    try:
        cursor = connection.execute(
            'UPDATE chat_users SET last_seen_at = ?, typing_until = ? WHERE user_id = ? AND name_key = ? AND expires_at > ?',
            (now.isoformat(), typing_until, session['chat_user_id'], session['chat_name_key'], now.isoformat()),
        )
        connection.commit()
    finally:
        connection.close()
    if cursor.rowcount != 1:
        return jsonify({'error': 'Your chat session has expired.'}), 401
    return jsonify({'ok': True})


@app.route('/chat/message', methods=['POST'])
@chat_user_required
def chat_send_message():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'error': 'Send a valid chat message.'}), 400
    if not valid_csrf(data):
        return jsonify({'error': 'Refresh the page and try again.'}), 400
    is_admin_message = bool(session.get('is_admin'))
    username = 'BOSS' if is_admin_message else session['chat_name']
    try:
        message_text = sanitize_user_text(data.get('message', ''), field_name='message', max_length=2000)
        reply_to = sanitize_user_text(data.get('reply_to', ''), field_name='reply', max_length=40)
    except SecurityValidationError as exc:
        log_security_event('chat_message_blocked', str(exc), remote_addr=request.remote_addr, user=username)
        return jsonify({'error': 'Your message contains blocked content.'}), 400
    if not message_text:
        return jsonify({'error': 'Write a message before sending.'}), 400
    entry = {
        'id': secrets.token_hex(12),
        'user_id': None if is_admin_message else session['chat_user_id'],
        'is_admin': is_admin_message,
        'submitted_at': datetime.now(timezone.utc).isoformat(),
        'username': username,
        'message': message_text,
        'reply_to': reply_to,
    }
    append_chat_message(entry)
    entry['_id'] = entry['id']
    return jsonify({'message': serialize_chat_message(entry, online_user_ids=online_chat_user_ids())}), 201


@app.route('/chat/upload', methods=['POST'])
@chat_user_required
def chat_upload():
    if not valid_csrf(request.form):
        return jsonify({'error': 'Refresh the page and try again.'}), 400
    is_admin_message = bool(session.get('is_admin'))
    username = 'BOSS' if is_admin_message else session['chat_name']
    try:
        message_text = sanitize_user_text(request.form.get('message', ''), field_name='message', max_length=1000)
        reply_to = sanitize_user_text(request.form.get('reply_to', ''), field_name='reply', max_length=40)
    except SecurityValidationError as exc:
        log_security_event('chat_upload_blocked', str(exc), remote_addr=request.remote_addr, user=username)
        return jsonify({'error': 'Your message contains blocked content.'}), 400

    uploaded = request.files.get('file')
    if not uploaded or not uploaded.filename:
        return jsonify({'error': 'Choose a file to share.'}), 400

    mime_map = {
        '.jpg': {'image/jpeg'},
        '.jpeg': {'image/jpeg'},
        '.png': {'image/png'},
        '.webp': {'image/webp'},
        '.gif': {'image/gif'},
        '.mp3': {'audio/mpeg', 'audio/mp3', 'audio/x-mpeg-3'},
        '.wav': {'audio/wav', 'audio/x-wav'},
        '.ogg': {'audio/ogg', 'audio/x-ogg'},
        '.m4a': {'audio/mp4', 'audio/x-m4a'},
        '.aac': {'audio/aac', 'audio/mp4'},
        '.mp4': {'video/mp4', 'application/mp4'},
        '.webm': {'video/webm'},
        '.mov': {'video/quicktime', 'video/mp4'},
        '.m4v': {'video/mp4', 'video/x-m4v'},
        '.pdf': {'application/pdf'},
        '.txt': {'text/plain'},
        '.doc': {'application/msword'},
        '.docx': {'application/vnd.openxmlformats-officedocument.wordprocessingml.document'},
        '.ppt': {'application/vnd.ms-powerpoint'},
        '.pptx': {'application/vnd.openxmlformats-officedocument.presentationml.presentation'},
    }
    try:
        safe_file = validate_uploaded_media(
            uploaded,
            CHAT_ALLOWED_EXTENSIONS,
            CHAT_UPLOAD_MAX_BYTES,
            video_max_seconds=VIDEO_MAX_SECONDS,
            mime_map=mime_map,
        )
    except SecurityValidationError as exc:
        log_security_event('chat_upload_rejected', str(exc), remote_addr=request.remote_addr, user=username)
        return jsonify({'error': 'Security check failed. This file was rejected.'}), 400

    extension = safe_file['extension']
    if extension in CHAT_VIDEO_EXTENSIONS:
        kind = 'video'
    elif extension in {'.mp3', '.wav', '.ogg', '.m4a', '.aac'}:
        kind = 'audio'
    elif extension in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
        kind = 'image'
    else:
        kind = 'file'

    stored_name = secrets.token_hex(16) + extension
    CHAT_MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    media_path = chat_media_path(stored_name)
    if media_path is None:
        abort(400)
    uploaded.save(media_path)
    attachment = {
        'filename': stored_name,
        'original_name': safe_file['original_name'] or f'shared-file{extension}',
        'kind': kind,
        'mimetype': safe_file['mimetype'],
        'size': safe_file['size'],
    }
    entry = {
        'id': secrets.token_hex(12),
        'user_id': None if is_admin_message else session['chat_user_id'],
        'is_admin': is_admin_message,
        'submitted_at': datetime.now(timezone.utc).isoformat(),
        'username': username,
        'message': message_text,
        'reply_to': reply_to,
        'attachment': attachment,
    }
    append_chat_message(entry)
    entry['_id'] = entry['id']
    return jsonify({'message': serialize_chat_message(entry, online_user_ids=online_chat_user_ids())}), 201


@app.route('/chat/media/<filename>', methods=['GET'])
@chat_user_required
def chat_media(filename):
    media_path = chat_media_path(filename)
    if media_path is None or not media_path.is_file():
        abort(404)
    download = request.args.get('download') == '1'
    download_name = filename
    if download:
        for entry in load_chat_messages():
            for attachment in chat_attachments(entry):
                if attachment.get('filename') == filename:
                    download_name = secure_filename(str(attachment.get('original_name') or filename)) or filename
                    break
    return send_from_directory(
        CHAT_MEDIA_DIR, filename, as_attachment=download,
        download_name=download_name, conditional=True,
    )


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


@app.route('/admin/chat', methods=['GET'])
@admin_required
def admin_chat_page():
    return render_template(
        'admin_chat.html', csrf_token=csrf_token(),
        chat_messages=load_chat_messages(limit=200),
        storage_usage=chat_storage_usage(),
        chat_settings=load_chat_settings(),
    )


@app.route('/admin/chat/settings', methods=['POST'])
@admin_required
def admin_chat_settings_save():
    if not valid_csrf(request.form):
        abort(400)
    badge_label = ''.join(
        character for character in request.form.get('badge_label', '').strip()
        if character.isprintable()
    )[:16]
    if not badge_label:
        flash('Enter a badge label between 1 and 16 characters.')
        return redirect(url_for('admin_chat_page'))
    save_chat_settings({'badge_label': badge_label})
    flash('Client badge label saved.')
    return redirect(url_for('admin_chat_page'))


@app.route('/admin/chat/cleanup', methods=['POST'])
@admin_required
def admin_chat_cleanup():
    if not valid_csrf(request.form):
        abort(400)
    cleanup_mode = request.form.get('cleanup_mode')
    if cleanup_mode == 'hours':
        try:
            hours = int(request.form.get('hours', ''))
        except ValueError:
            hours = 0
        if hours not in {24, 48}:
            flash('Choose a cleanup window of 24 or 48 hours.')
            return redirect(url_for('admin_chat_page'))
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    elif cleanup_mode == 'date':
        try:
            selected_date = datetime.strptime(request.form.get('before_date', ''), '%Y-%m-%d')
        except ValueError:
            flash('Choose a valid date for cleanup.')
            return redirect(url_for('admin_chat_page'))
        cutoff = selected_date.replace(tzinfo=timezone.utc)
    else:
        abort(400)
    result = clean_chat_history_before(cutoff)
    flash(f"Removed {result['messages']} messages and {result['files']} media files ({result['bytes']:,} bytes).")
    return redirect(url_for('admin_chat_page'))


@app.route('/admin/chat/clear', methods=['POST'])
@admin_required
def admin_chat_clear():
    if not valid_csrf(request.form):
        abort(400)
    result = clear_chat_history()
    flash(f"Removed {result['messages']} messages and {result['files']} media files ({result['bytes']:,} bytes).")
    return redirect(url_for('admin_chat_page'))

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

@app.route('/admin/feedback/bulk-delete', methods=['POST'])
@admin_required
def admin_bulk_delete_feedback():
    if not valid_csrf(request.form):
        abort(400)

    feedback_ids = request.form.getlist('feedback_ids')
    delete_all = request.form.get('delete_all') == '1'

    feedback_path = Path(app.instance_path) / 'feedback_submissions.jsonl'
    try:
        lines = feedback_path.read_text(encoding='utf-8').splitlines()
    except OSError:
        abort(404)

    if delete_all:
        feedback_path.write_text('', encoding='utf-8')
        flash('All suggestions were deleted successfully.')
        return redirect(url_for('admin_page') + '#feedback')

    if not feedback_ids:
        flash('Select at least one suggestion to delete.')
        return redirect(url_for('admin_page') + '#feedback')

    remaining_lines = []
    removed_count = 0
    for index, line in enumerate(lines):
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if isinstance(entry, dict):
            entry_id = hashlib.sha256(f'{index}:{line}'.encode('utf-8')).hexdigest()
            if entry_id in feedback_ids:
                removed_count += 1
                continue
        remaining_lines.append(line)

    save_feedback_lines(feedback_path, remaining_lines)
    flash(f'{removed_count} suggestion(s) deleted successfully.')
    return redirect(url_for('admin_page') + '#feedback')


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

    try:
        allowed_exts = {'.jpg', '.jpeg', '.png', '.webp'}
        safe_file = validate_uploaded_media(
            uploaded,
            allowed_exts,
            5 * 1024 * 1024,
            mime_map={'.jpg': {'image/jpeg'}, '.jpeg': {'image/jpeg'}, '.png': {'image/png'}, '.webp': {'image/webp'}},
        )
    except SecurityValidationError as exc:
        log_security_event('admin_upload_rejected', str(exc), remote_addr=request.remote_addr, slot=slot)
        flash('Security check failed. This upload was rejected.')
        return redirect(url_for('admin_page'))

    try:
        from PIL import Image

        uploaded.stream.seek(0)
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
        log_security_event('admin_upload_deserialization_failed', 'Image decoding failed', remote_addr=request.remote_addr, slot=slot)
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

# The linguistic modules use a consistent dark-mode layout with modular section navigation
# so each area stays readable, focused, and easy to scan without turning into a single wall of text.
@app.route('/phonetics')
def phonetics_page():
    return render_template('phonetics.html', active_module='phonetics')

@app.route('/phonology')
def phonology_page():
    return render_template('phonology.html', active_module='phonology')

@app.route('/morphology')
def morphology_page():
    return render_template('morphology.html', active_module='morphology')

@app.route('/syntax')
def syntax_page():
    return render_template('syntax.html', active_module='syntax')

@app.route('/semantics')
def semantics_page():
    return render_template('semantics.html', active_module='semantics')

@app.route('/discourse')
def discourse_page():
    return render_template('discourse.html', active_module='discourse')

@app.route('/grammar')
def grammar_page():
    return render_template('grammar.html', active_module='grammar')

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

@app.errorhandler(RequestEntityTooLarge)
def handle_large_request(error):
    if request.path.startswith('/chat'):
        return jsonify({'error': 'Files must be 10 MB or smaller.'}), 413
    return error.get_response()


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