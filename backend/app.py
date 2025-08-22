from flask import Flask, request, jsonify, make_response
from flask_bcrypt import Bcrypt
from PIL import Image
import requests
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename
from flask_cors import CORS  # keep if you use it elsewhere
import json
from fuzzywuzzy import fuzz
import pytesseract
import os
import logging
import re
import atexit
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from dotenv import load_dotenv
from pymongo import ReturnDocument
from pathlib import Path

# >>> added: scan blueprint registration
from scripts.scan_manager import register_blueprint as register_scan_blueprint
# <<< added

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-only-secret-change-me'
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
myApiUser = os.getenv('E7_DB_KEY')

# Path to Tesseract inside project (existing)
script_dir = os.path.dirname(os.path.abspath(__file__))
tesseract_path = os.path.join(script_dir, 'Pytesseract', 'tesseract.exe')
pytesseract.pytesseract.tesseract_cmd = tesseract_path

bcrypt = Bcrypt(app)

# ------------------------
# CORS for local dev (HTTP only)
# ------------------------
ALLOWED_ORIGINS = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001",
    "https://epicsevenarmoryserver-1.onrender.com"
}

ALLOWED_HEADERS = "Content-Type, Authorization, username"
ALLOWED_METHODS = "GET, POST, PUT, DELETE, OPTIONS"
MAX_AGE = "86400"

def _origin_allowed(origin: str) -> bool:
    return bool(origin and origin in ALLOWED_ORIGINS)

@app.before_request
def handle_cors_preflight():
    if request.method == "OPTIONS":
        origin = request.headers.get("Origin", "")
        resp = make_response("", 204)
        if _origin_allowed(origin):
            resp.headers["Access-Control-Allow-Origin"] = origin
            resp.headers["Vary"] = "Origin"
        else:
            # allow unknown/null origins in dev to support file:// (Electron)
            resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = ALLOWED_HEADERS
        resp.headers["Access-Control-Allow-Methods"] = ALLOWED_METHODS
        resp.headers["Access-Control-Max-Age"] = MAX_AGE
        return resp

@app.after_request
def add_cors_headers(response):
    origin = request.headers.get("Origin", "")
    if _origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
    else:
        # dev-friendly default for file:// and unknown local tools
        response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = ALLOWED_HEADERS
    response.headers["Access-Control-Allow-Methods"] = ALLOWED_METHODS
    response.headers["Access-Control-Max-Age"] = MAX_AGE
    return response

# Set up logging
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# >>> added: register scan endpoints (provides /scan/status and /scan/toggle)
register_scan_blueprint(app)

# MongoDB connection
uri = "mongodb+srv://michaelfaugnodev:Nt9KZ0ELp0mVbNWb@epic-seven-armory-proje.idpnatp.mongodb.net/?retryWrites=true&w=majority&appName=Epic-Seven-Armory-Project"
client = MongoClient(uri, server_api=ServerApi('1'))
atexit.register(client.close)

# Access the database
db = client['epic_seven_armory']
users_collection = db['Users']
image_stats_collection = db['ImageStats']

# Google OAuth blueprint
from scripts.google_auth_native import register_google_auth_blueprint
register_google_auth_blueprint(app, users_collection=users_collection, db=db)

# Legacy/profile blueprints
from scripts.profile_read_legacy import register_profile_read_legacy
from scripts.hero_images import register_hero_images
from scripts.update_profile_legacy import register_update_profile_legacy

try:
    from bson import ObjectId as BsonObjectId
except Exception:
    BsonObjectId = None
register_profile_read_legacy(app, users_collection=users_collection, object_id_cls=BsonObjectId)
register_hero_images(app)
register_update_profile_legacy(app, users_collection=users_collection, object_id_cls=BsonObjectId)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------------
# Unit ingestion/display (existing)
# ------------------------

@app.route('/get_unit_names', methods=['GET'])
def get_unit_names():
    api_url = 'https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json'
    unit_names = load_unit_names(api_url, 'en')
    unit_names.sort()
    return jsonify(unit_names)

def load_unit_names(api_url, language_code='en'):
    response = requests.get(api_url)
    data = response.json()
    unit_names = [unit['name'] for unit in data[language_code]]
    unit_names.sort()
    return unit_names

api_url = 'https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json'
correct_unit_names = load_unit_names(api_url, 'en')

def fetch_unit_data(unit_name):
    # Fix Python -> replace (was replaceAll)
    if unit_name == "Ainos 2.0":
        formatted_unit_name = "ainos-20"
    else:
        formatted_unit_name = unit_name.replace(' ', '-')

    api_url = f'https://epic7db.com/api/heroes/{formatted_unit_name.lower()}/{myApiUser}'
    response = requests.get(api_url)

    if response.status_code == 200:
        return response.json()
    else:
        return None

def fetch_unit_image(unit_name):
    unit_name = unit_name.replace(' ', '-').lower()
    api_url = f'https://epic7db.com/api/heroes/{unit_name.lower()}/{myApiUser}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get('image', '')
    return ''

def correct_name(extracted_name, choices):
    best_match = None
    best_score = 0
    for choice in choices:
        score = fuzz.token_set_ratio(extracted_name, choice)
        if score > best_score or (score == best_score and len(choice) > len(best_match or '')):
            best_score = score
            best_match = choice
    if best_score > 80:
        return best_match
    return None

@app.route('/upload_files', methods=['POST'])
def upload_files():
    uploaded_files = []
    for key, file in request.files.items():
        if key.startswith('file') and file and file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append(filename)
    if 'file' in request.files and not uploaded_files:
        file = request.files['file']
        if file.filename != '':
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            uploaded_files.append(filename)
    if 'json_file' in request.files:
        json_file = request.files['json_file']
        if json_file.filename != '':
            filename = secure_filename(json_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            json_file.save(file_path)
            uploaded_files.append(filename)
    if uploaded_files:
        return jsonify({"message": "Files uploaded successfully", "filenames": uploaded_files}), 200
    else:
        return jsonify({"error": "No files uploaded"}), 400


def clean_stat(stat, keep_percentage=False):
    stat = re.sub(r'[*:©]', '', stat).strip()
    stat = re.split(r'[.|]', stat)[0].strip()
    if keep_percentage:
        if not stat.endswith('%'):
            stat += '%'
    else:
        stat = stat.rstrip('%')
    return stat

def clean_unit_name(name):
    cleaned_name = re.sub(r'\s*\d+$', '', name)
    return cleaned_name.rstrip()

def process_image(image, username, rta_rank):
    regions = {
        'unit': {'x': 150, 'y': 170, 'width': 700, 'height': 60},
        'cp': {'x': 207, 'y': 555, 'width': 200, 'height': 50},
        'imprint': {'x': 275, 'y': 360, 'width': 190, 'height': 100},
        'attack': {'x': 418, 'y': 620, 'width': 70, 'height': 29},
        'defense': {'x': 418, 'y': 648, 'width': 70, 'height': 34}, 
        'health': {'x': 394, 'y': 683, 'width': 100, 'height': 34},
        'speed': {'x': 385, 'y': 720, 'width': 100, 'height': 29}, 
        'critical_hit_chance': {'x': 385, 'y': 750, 'width': 100, 'height': 29}, 
        'critical_hit_damage': {'x': 385, 'y': 785, 'width': 100, 'height': 34},
        'effectiveness':  {'x': 385, 'y': 820, 'width': 100, 'height': 34}, 
        'effect_resistance': {'x': 385, 'y': 850, 'width': 100, 'height': 34},
        'set1': {'x': 210, 'y': 942, 'width': 200, 'height': 34},
        'set2':  {'x': 210, 'y': 976, 'width': 200, 'height': 34}, 
        'set3': {'x': 210, 'y': 1010, 'width': 200, 'height': 34}
    }

    stats = {name: pytesseract.image_to_string(image.crop((data['x'], data['y'], data['x'] + data['width'], data['y'] + data['height'])), config='--psm 6').strip() for name, data in regions.items()}

    percentage_stats = ["imprint", 'critical_hit_chance', 'critical_hit_damage', 'effectiveness', 'effect_resistance']
    for key in stats:
        if key not in ['unit', 'uploaded_by', 'user_rank']:
            stats[key] = clean_stat(stats[key], keep_percentage=(key in percentage_stats))

    if 'unit' in stats:
        unit_name = clean_unit_name(stats['unit']).lower()
        if "draaon bride senva" in unit_name:
            stats['unit'] = "Dragon Bride Senya"
        elif "new moon luna" in unit_name:
            stats['unit'] = "New Moon Luna"
        else:
            corrected_name = correct_name(unit_name, correct_unit_names)
            if corrected_name:
                stats['unit'] = corrected_name
            else:
                print("No matching unit name found or low confidence match for:", stats['unit'])

    stats['uploaded_by'] = username
    stats['user_rank'] = rta_rank

    result = image_stats_collection.insert_one(stats)
    stats['_id'] = str(result.inserted_id)

    return stats

def process_json(file_path, username, rta_rank):
    with open(file_path, 'r') as json_file:
        data = json.load(json_file)
    
    results = []
    for hero in data['heroes']:
        if hero['atk'] == 0 and hero['hp'] == 0 and hero['def'] == 0:
            continue

        def format_number(num): return f"{num:,}"
        def format_percentage(num): return f"{num:.1f}%"
        def format_set_name(set_name):
            if not set_name:
                return "No set effect"
            words = set_name.split('_')
            return ' '.join(word.capitalize() for word in words)

        stats = {
            'unit': hero['name'],
            'cp': format_number(hero['cp']),
            'imprint': hero.get('imprint', 'Locked'),
            'attack': format_number(hero['atk']),
            'defense': format_number(hero['def']),
            'health': format_number(hero['hp']),
            'speed': str(hero['spd']),
            'critical_hit_chance': format_percentage(hero['cr']),
            'critical_hit_damage': format_percentage(hero['cd']),
            'effectiveness': format_percentage(hero['eff']),
            'effect_resistance': format_percentage(hero['res']),
            'uploaded_by': username,
            'user_rank': rta_rank
        }
        
        equipment = hero.get('equipment', {})
        sets = [format_set_name(item.get('set')) for item in equipment.values() if item and 'set' in item]
        stats['set1'] = sets[0] if len(sets) > 0 else "No set effect"
        stats['set2'] = sets[1] if len(sets) > 1 else "No set effect"
        stats['set3'] = sets[2] if len(sets) > 2 else "No set effect"

        for key, value in stats.items():
            stats[key] = str(value)

        result = image_stats_collection.insert_one(stats)
        stats['_id'] = str(result.inserted_id)
        results.append(stats)

    return results

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        form = request.get_json()
        if form:
            updated_data = {
                "username": form.get('username'),
                "epic_seven_account": form.get('epic_seven_account'),
                "streamer_name": form.get('streamer_name'),
                "rta_rank": form.get('rta_rank')
            }
            result = users_collection.update_one({"username": form.get('username')}, {"$set": updated_data})
            if result.matched_count > 0:
                return jsonify({"message": "Profile updated successfully"}), 200
            else:
                return jsonify({"error": "User not found"}), 404
        return jsonify({"error": "Form data is invalid"}), 400

@app.route('/your_units', methods=['GET', 'POST', 'OPTIONS'])
def your_units():
    if request.method == 'OPTIONS':
        return "", 204

    if request.method == 'GET':
        username = request.headers.get('Username') or request.headers.get('username') or request.args.get('username')
        if not username:
            return jsonify([]), 200
        units = list(image_stats_collection.find({"uploaded_by": username}))
        if not units:
            return jsonify([]), 200
        for unit in units:
            unit['_id'] = str(unit['_id'])
        units = sorted(units, key=lambda x: x.get('unit', ''))
        return jsonify(units), 200

    elif request.method == 'POST':
        form = request.get_json() or {}
        unit_name = form.get('unit')
        username = request.headers.get('Username') or request.headers.get('username') or request.args.get('username')
        if not username:
            return jsonify({"error": "Username not provided"}), 400
        unit = image_stats_collection.find_one({"uploaded_by": username, "unit": unit_name})
        if unit:
            unit['_id'] = str(unit['_id'])
            return jsonify(unit), 200
        return jsonify({"error": "Unit not found"}), 404

@app.route('/delete_unit', methods=['POST'])
def delete_unit():
    data = request.get_json()
    unit_id = data.get('unit_to_delete')
    username = request.headers.get('Username')

    if not username:
        return jsonify({"error": "Username not provided"}), 400

    if unit_id:
        result = image_stats_collection.delete_one({"_id": ObjectId(unit_id), "uploaded_by": username})
        if result.deleted_count > 0:
            return jsonify({"message": f"Unit deleted successfully"}), 200
        else:
            return jsonify({"error": "Unit not found or not authorized to delete"}), 404
    
    return jsonify({"error": "Unit ID not provided"}), 400

@app.route('/update_unit_stats', methods=['POST'])
def update_unit_stats():
    payload = request.get_json(silent=True) or {}
    unit_id = payload.get('unit_id')
    updates = payload.get('updates') or {}
    username = request.headers.get('Username') or request.headers.get('username') or request.args.get('username')

    if not username:
        return jsonify({"error": "Username not provided"}), 400
    if not unit_id:
        return jsonify({"error": "unit_id is required"}), 400

    allowed = {
        "unit", "name", "unit_name",
        "attack", "defense", "health", "speed",
        "imprint",
        "critical_hit_chance", "critical_hit_damage",
        "effectiveness", "effect_resistance",
        "set1", "set2", "set3",
    }
    clean = {k: v for k, v in updates.items() if k in allowed}

    if not clean:
        return jsonify({"error": "No valid fields to update"}), 400

    for f in ("attack", "defense", "health", "speed"):
        if f in clean:
            try:
                if clean[f] in ("", None):
                    clean[f] = None
                else:
                    clean[f] = int(float(clean[f]))
            except Exception:
                pass

    set_doc = {}
    for k, v in clean.items():
        set_doc[k] = v
        set_doc[f"stats.{k}"] = v

    result = image_stats_collection.update_one(
        {"_id": ObjectId(unit_id), "uploaded_by": username},
        {"$set": set_doc}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Unit not found or not authorized to update"}), 404

    updated = image_stats_collection.find_one({"_id": ObjectId(unit_id)})
    if updated:
        updated["_id"] = str(updated["_id"])
    return jsonify({"ok": True, "unit": updated}), 200

@app.route('/update_unit', methods=['POST'])
def update_unit_alias():
    return update_unit_stats()

@app.route('/update_selected_units', methods=['POST'])
def update_selected_units():
    username = request.headers.get('Username')
    if not username:
        return jsonify({"error": "Username not provided"}), 400

    data = request.json
    selected_units = data.get('units', [])
    selected_units = selected_units[:4]
    while len(selected_units) < 4:
        selected_units.append(None)

    result = db.selected_units.update_one(
        {"username": username},
        {"$set": {
            "unit_id1": selected_units[0]['id'] if selected_units[0] else None,
            "unit_id2": selected_units[1]['id'] if selected_units[1] else None,
            "unit_id3": selected_units[2]['id'] if selected_units[2] else None,
            "unit_id4": selected_units[3]['id'] if selected_units[3] else None
        }},
        upsert=True
    )

    if result.acknowledged:
        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Failed to update selected units'}), 500

@app.route('/get_selected_units_data', methods=['GET'])
def get_selected_units_data():
    username = request.headers.get('Username')
    if not username:
        return jsonify({"error": "Username not provided"}), 400
    
    selected_units = db.selected_units.find_one({"username": username})
    if not selected_units:
        return jsonify([]), 200
    
    unit_ids = [selected_units.get(f'unit_id{i}') for i in range(1, 5) if selected_units.get(f'unit_id{i}')]
    
    units_data = []
    for unit_id in unit_ids:
        unit = image_stats_collection.find_one({"_id": ObjectId(unit_id)})
        if unit:
            unit['_id'] = str(unit['_id'])
            units_data.append(unit)

    return jsonify(units_data), 200

def load_unit_names(api_url, language_code='en'):
    response = requests.get(api_url)
    data = response.json()
    unit_names = [unit['name'] for unit in data[language_code]]
    unit_names.sort()
    return unit_names

api_url = 'https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json'
correct_unit_names = load_unit_names(api_url, 'en')

def fetch_unit_data(unit_name):
    if unit_name == "Ainos 2.0":
        formatted_unit_name = "ainos-20"
    else:
        formatted_unit_name = unit_name.replace(' ', '-')
    api_url = f'https://epic7db.com/api/heroes/{formatted_unit_name.lower()}/{myApiUser}'
    response = requests.get(api_url)
    if response.status_code == 200:
        return response.json()
    return None

def fetch_unit_image(unit_name):
    unit_name = unit_name.replace(' ', '-').lower()
    api_url = f'https://epic7db.com/api/heroes/{unit_name.lower()}/{myApiUser}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get('image', '')
    return ''

def correct_name(extracted_name, choices):
    best_match = None
    best_score = 0
    for choice in choices:
        score = fuzz.token_set_ratio(extracted_name, choice)
        if score > best_score or (score == best_score and len(choice) > len(best_match or '')):
            best_score = score
            best_match = choice
    if best_score > 80:
        return best_match
    return None

@app.route('/display', methods=['POST'])
def display_image():
    data = request.json or {}
    filenames = data.get('filenames')
    username = data.get('username')
    rta_rank = data.get('rank')
    is_json = data.get('isJson', False)

    if not filenames:
        return jsonify({"error": "No filenames provided"}), 400
    if isinstance(filenames, str):
        filenames = [filenames]

    results = []
    for filename in filenames:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(file_path):
            return jsonify({"error": f"File not found: {filename}"}), 404

        if is_json:
            result = process_json(file_path, username, rta_rank)
            results.extend(result)
        else:
            image = Image.open(file_path)
            result = process_image(image, username, rta_rank)
            results.append(result)

        os.remove(file_path)
    
    return jsonify(results), 200

def clean_stat(stat, keep_percentage=False):
    stat = re.sub(r'[*:Â©]', '', stat or '').strip()
    stat = re.split(r'[.|]', stat)[0].strip()
    if keep_percentage:
        if stat and not stat.endswith('%'):
            stat += '%'
    else:
        stat = stat.rstrip('%')
    return stat

def clean_unit_name(name):
    cleaned_name = re.sub(r'\s*\d+$', '', name or '')
    return cleaned_name.rstrip()

def process_image(image, username, rta_rank):
    regions = {
        'unit': {'x': 150, 'y': 170, 'width': 700, 'height': 60},
        'cp': {'x': 207, 'y': 555, 'width': 200, 'height': 50},
        'imprint': {'x': 275, 'y': 360, 'width': 190, 'height': 100},
        'attack': {'x': 418, 'y': 620, 'width': 70, 'height': 29},
        'defense': {'x': 418, 'y': 648, 'width': 70, 'height': 34}, 
        'health': {'x': 394, 'y': 683, 'width': 100, 'height': 34},
        'speed': {'x': 385, 'y': 720, 'width': 100, 'height': 29}, 
        'critical_hit_chance': {'x': 385, 'y': 750, 'width': 100, 'height': 29}, 
        'critical_hit_damage': {'x': 385, 'y': 785, 'width': 100, 'height': 34},
        'effectiveness':  {'x': 385, 'y': 820, 'width': 100, 'height': 34}, 
        'effect_resistance': {'x': 385, 'y': 850, 'width': 100, 'height': 34},
        'set1': {'x': 210, 'y': 942, 'width': 200, 'height': 34},
        'set2':  {'x': 210, 'y': 976, 'width': 200, 'height': 34}, 
        'set3': {'x': 210, 'y': 1010, 'width': 200, 'height': 34}
    }

    stats = {name: pytesseract.image_to_string(
        image.crop((data['x'], data['y'], data['x'] + data['width'], data['y'] + data['height'])),
        config='--psm 6'
    ).strip() for name, data in regions.items()}

    percentage_stats = ["imprint", 'critical_hit_chance', 'critical_hit_damage', 'effectiveness', 'effect_resistance']
    for key in stats:
        if key not in ['unit', 'uploaded_by', 'user_rank']:
            stats[key] = clean_stat(stats[key], keep_percentage=(key in percentage_stats))

    if 'unit' in stats:
        unit_name = clean_unit_name(stats['unit']).lower()
        if "draaon bride senva" in unit_name:
            stats['unit'] = "Dragon Bride Senya"
        elif "new moon luna" in unit_name:
            stats['unit'] = "New Moon Luna"
        else:
            corrected_name = correct_name(unit_name, correct_unit_names)
            if corrected_name:
                stats['unit'] = corrected_name
            else:
                print("No matching unit name found or low confidence match for:", stats['unit'])

    stats['uploaded_by'] = username
    stats['user_rank'] = rta_rank

    result = image_stats_collection.insert_one(stats)
    stats['_id'] = str(result.inserted_id)

    return stats

def process_json(file_path, username, rta_rank):
    with open(file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)
    
    results = []
    for hero in data.get('heroes', []):
        if hero.get('atk') == 0 and hero.get('hp') == 0 and hero.get('def') == 0:
            continue

        def format_number(num): return f"{num:,}"
        def format_percentage(num): return f"{num:.1f}%"
        def format_set_name(set_name):
            if not set_name:
                return "No set effect"
            words = str(set_name).split('_')
            return ' '.join(word.capitalize() for word in words)

        stats = {
            'unit': hero.get('name', ''),
            'cp': format_number(hero.get('cp', 0)),
            'imprint': hero.get('imprint', 'Locked'),
            'attack': format_number(hero.get('atk', 0)),
            'defense': format_number(hero.get('def', 0)),
            'health': format_number(hero.get('hp', 0)),
            'speed': str(hero.get('spd', '')),
            'critical_hit_chance': format_percentage(hero.get('cr', 0.0)),
            'critical_hit_damage': format_percentage(hero.get('cd', 0.0)),
            'effectiveness': format_percentage(hero.get('eff', 0.0)),
            'effect_resistance': format_percentage(hero.get('res', 0.0)),
            'uploaded_by': username,
            'user_rank': rta_rank
        }
        
        equipment = hero.get('equipment', {})
        sets = [format_set_name(item.get('set')) for item in equipment.values() if item and 'set' in item]
        stats['set1'] = sets[0] if len(sets) > 0 else "No set effect"
        stats['set2'] = sets[1] if len(sets) > 1 else "No set effect"
        stats['set3'] = sets[2] if len(sets) > 2 else "No set effect"

        for key, value in stats.items():
            stats[key] = str(value)

        result = image_stats_collection.insert_one(stats)
        stats['_id'] = str(result.inserted_id)
        results.append(stats)

    return results

# ------------------------
# Scanning Routes (existing)
# ------------------------
@app.route("/ingest_unit_ocr", methods=["POST"])
def ingest_unit_ocr():
    payload = request.get_json(force=True, silent=True) or {}
    username = request.headers.get("username") or request.args.get("username")
    if not username:
        return jsonify({"error": "missing username"}), 400

    hero_name = (payload.get("hero_name") or "").strip()
    cp_in = payload.get("cp")
    stats_in = payload.get("stats") or {}
    sig = payload.get("sig")
    if not hero_name or not sig:
        return jsonify({"error": "missing hero_name or sig"}), 400

    def _fmt_int(n):   return f"{int(n):,}" if n is not None else ""
    def _fmt_pct(p):   return f"{float(p):.1f}%" if p is not None else ""

    nice_name = hero_name
    unit_lower = nice_name.lower()

    doc = {
        "unit": nice_name,
        "unit_lower": unit_lower,
        "cp": _fmt_int(cp_in),
        "imprint": "Locked",
        "attack": _fmt_int(stats_in.get("attack")),
        "defense": _fmt_int(stats_in.get("defense")),
        "health": _fmt_int(stats_in.get("health")),
        "speed": str(stats_in.get("speed") or ""),
        "critical_hit_chance": _fmt_pct(stats_in.get("crit_chance")),
        "critical_hit_damage": _fmt_pct(stats_in.get("crit_damage")),
        "effectiveness": _fmt_pct(stats_in.get("effectiveness")),
        "effect_resistance": _fmt_pct(stats_in.get("effect_resistance")),
        "set1": "No set effect",
        "set2": "No set effect",
        "set3": "No set effect",
        "uploaded_by": username,
        "user_rank": "",
        "source": "ocr_auto",
        "sig": sig,
        "updated_at": datetime.utcnow(),
    }

    units = db["units"]
    existing = units.find_one({"username": username, "unit_lower": unit_lower})
    if existing:
        if existing.get("sig") == sig:
            event = "duplicate"
            updated = existing
        else:
            event = "updated"
            updated = units.find_one_and_update(
                {"_id": existing["_id"]},
                {"$set": doc},
                return_document=ReturnDocument.AFTER
            )
    else:
        event = "added"
        doc["created_at"] = datetime.utcnow()
        doc["username"] = username
        inserted_id = units.insert_one(doc).inserted_id
        updated = units.find_one({"_id": inserted_id})

    return jsonify({"ok": True, "unit_id": str(updated.get("_id")), "event": event})

@app.route("/scan_event", methods=["POST"])
def scan_event():
    payload = request.get_json(force=True, silent=True) or {}
    username = request.headers.get("username") or request.args.get("username")
    if not username:
        return jsonify({"error": "missing username"}), 400

    event = {
        "username": username,
        "event_type": payload.get("event_type") or "info",
        "hero_name": payload.get("hero_name") or "",
        "cp": payload.get("cp"),
        "sig": payload.get("sig") or "",
        "message": payload.get("message") or "",
        "created_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(days=14),
    }
    db["scan_events"].insert_one(event)
    return jsonify({"ok": True})

@app.route("/scan_events", methods=["GET"])
def scan_events():
    username = request.headers.get("username") or request.args.get("username")
    if not username:
        return jsonify({"error": "missing username"}), 400
    limit = min(int(request.args.get("limit", 100)), 500)

    cur = db["scan_events"].find({"username": username}).sort("created_at", -1).limit(limit)
    rows = [{
        "ts": doc.get("created_at").isoformat() + "Z",
        "event_type": doc.get("event_type"),
        "hero_name": doc.get("hero_name"),
        "cp": doc.get("cp"),
        "sig": doc.get("sig"),
        "message": doc.get("message")
    } for doc in cur]

    return jsonify({"ok": True, "events": rows})

@app.route("/monitor_status", methods=["GET"])
def monitor_status():
    status_dir  = Path(os.environ.get("E7_STATUS_DIR", r"C:\Projects\EpicSevenArmory"))
    status_path = status_dir / "monitor_status.json"
    if status_path.exists():
        try:
            return jsonify(json.loads(status_path.read_text(encoding="utf-8")))
        except Exception:
            pass
    return jsonify({})

@app.route("/scanner", methods=["POST"])
def scanner_toggle():
    data = request.get_json(force=True, silent=True) or {}
    enabled  = bool(data.get("enabled"))
    username = request.headers.get("username") or data.get("username") or request.args.get("username")

    if username:
        import hero_scanner
        hero_scanner.USERNAME_VALUE = username

    if enabled:
        import hero_scanner
        hero_scanner.start_scanner()
    else:
        import hero_scanner
        hero_scanner.stop_scanner()

    return jsonify({"enabled": enabled})

if __name__ == '__main__':
    # Serve HTTP locally for development
    app.logger.info("Starting HTTP dev server on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=True, threaded=True)