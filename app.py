from flask import Flask, request, render_template, redirect, url_for, flash, jsonify, session
from forms.user_forms import LoginForm, RegistrationForm
from forms.UpdateUserForm import UpdateUserForm
from PIL import Image
import requests
from datetime import timedelta
import base64
from io import BytesIO
import cloudinary.uploader
from cloudinary_handler import config_cloudinary 
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models.models import Users, SelectedUnit, ImageStats
from database import db, cast, func, Integer, Float
from flask_cors import CORS
import json
from fuzzywuzzy import process
import pytesseract
import os
import uuid
from dotenv import load_dotenv

load_dotenv()
bcrypt = Bcrypt() 
login_manager = LoginManager()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = 'static/uploads/'
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_KEY')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False
# app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=6)
openai_api_key = os.getenv('OPEN_AI_KEY')
openai_api_url = "https://api.openai.com/v1/chat/completions"
myApiUser = os.getenv('E7_DB_KEY')

# pytesseract.pytesseract.tesseract_cmd = '/app/.apt/usr/bin/tesseract'
# pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe'
 
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)
bcrypt.init_app(app)
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
jwt = JWTManager(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


@app.route('/')
def home():
    # Render the home page template
    return render_template('home.html')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    # Handle user registration and redirect to home after successful signup
    form = RegistrationForm()
    if form.validate_on_submit():
        user = Users(username=form.username.data, epic_seven_account=form.epic_seven_account.data, streamer_name=form.streamer_name.data, rta_rank=form.rta_rank.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        login_user(user)
        return redirect(url_for('home'))
    return render_template('signup.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # Handle user login and redirect to home after successful login
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('You have been logged in!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route('/api/login', methods=['POST'])
def api_login():
    #Handle login for Electron api to get data for Twitch overlay
    data = request.json
    username = data.get('username')
    password = data.get('password')
    user = Users.query.filter_by(username=username).first()
    if user and user.check_password(password):
        login_user(user)
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad username or password"}), 401

@app.route('/login_status')
def login_status():
    # Setting logged in status for Electron Tabs
    return jsonify(logged_in=current_user.is_authenticated)

@login_manager.user_loader
def load_user(user_id):
    # Load user by user_id
    return Users.query.get(int(user_id))

@app.route('/logout')
@login_required
def logout():
    # Log out the current user and redirect to home page
    logout_user()
    return redirect(url_for('home'))


def load_unit_names(api_url, language_code='en'):
    # Load unit names from an API based on the given language code
    response = requests.get(api_url)
    data = response.json()
    unit_names = [unit['name'] for unit in data[language_code]]
    unit_names.sort()
    return unit_names

api_url = 'https://static.smilegatemegaport.com/gameRecord/epic7/epic7_hero.json'
correct_unit_names = load_unit_names(api_url, 'en')

# def load_unit_names(json_file_path, language_code='en'):
#     # Load unit names from a JSON file based on the given language code
#     with open(json_file_path, 'r', encoding='utf-8') as file:
#         data = json.load(file)
#         unit_names = [unit['name'] for unit in data[language_code]]
#     return unit_names

# base_dir = os.path.dirname(os.path.abspath(__file__))
# json_file_path = os.path.join(base_dir, 'hero.json')
# correct_unit_names = load_unit_names(json_file_path, 'en')

def correct_name(extracted_name, choices):
    # Correct the extracted name by finding the best match from the choices
    best_match, score = process.extractOne(extracted_name, choices)
    if score > 80:
        return best_match
    return None

def call_chatgpt_for_ocr(image_base64):
    # Api call for chatgpt image analysis
    payload = {
        "model": "gpt-4-turbo",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "What is the Name, CP, imprint (which appears right below Lv. max/60. If you see locked is 'None'), attack, defense, health, speed, critical hit chance, critical hit damage, effectiveness, effect resistance, and sets stat of this unit? I do not want to know any bonus or total provided.  In your response always provide the name of the unit as unit name. In your response always call cp or combat power, cp. In your response always call sets or sets equipped, sets. Before any stat name remove the '_'. you little shit"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 300
    }

    headers = {
        'Authorization': f'Bearer {openai_api_key}',
        'Content-Type': 'application/json'
    }

    response = requests.post(openai_api_url, headers=headers, json=payload)
    response_data = response.json()
    print(response_data)

    if 'choices' in response_data:
        message = response_data['choices'][0]['message']['content']

        return parse_chatgpt_response(message)
    else:
        print("Error in OpenAI API response:", response_data)
        return {}

def parse_chatgpt_response(content):
    # Format chatgpt data
    stats = {}
    lines = content.split('\n')
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip().lower().replace(' ', '_').replace('**', '').replace('-', '').replace('(', '').replace(')', '')
            value = value.strip().replace('**', '')
            stats[key] = value
    return stats

def image_to_base64(image):
    # Sets image to base64 to be sent to chapgpt
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    #Sets the local or cloudinary upload to session.
    if request.method == 'POST':
        if 'cloudinaryImage' in request.files:
            session.pop('filenames', None)
            cloudinary_files = request.files.getlist('cloudinaryImage')

            if cloudinary_files:
                image_urls = [cloudinary.uploader.upload(file)['url'] for file in cloudinary_files if file]
                image_urls = [url.replace("%5B'", '').replace("'%5D", '') for url in image_urls]
                session['image_urls'] = image_urls
                return redirect(url_for('display_image'))

        elif 'file' in request.files:
            session.pop('image_urls', None)

            files = request.files.getlist('file')
            filenames = []
            for file in files:
                if file and file.filename:
                    ext = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"{uuid.uuid4().hex}.{ext}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    filenames.append(filename)
            session['filenames'] = filenames
            return redirect(url_for('display_image'))

    return render_template('upload.html')

@app.route('/display')
def display_image():
    #Processes the upload results from chatgp and displays in unit format.
    filenames = session.get('filenames', [])
    image_urls = session.get('image_urls', [])
    username = current_user.username
    rta_rank = current_user.rta_rank

    if not filenames and not image_urls:
        return redirect(url_for('upload_file'))

    results = []

    for filename in filenames:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image = Image.open(image_path)
        process_image(image, results, username, rta_rank)

    for url in image_urls:
        response = requests.get(url)
        image = Image.open(BytesIO(response.content))
        process_image(image, results, username, rta_rank)

    return render_template('display.html', results=results)

def fetch_unit_image(unit_name):
    # Fetch the unit image URL from the new API. Thank you to Epic7db.com
    unit_name = unit_name.replace(' ', '-').lower()
    api_url = f'https://epic7db.com/api/heroes/{unit_name.lower()}/{myApiUser}'
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        return data.get('image', '')
    return ''

def process_image(image, results, username, rta_rank):
    # Set image to base64, grab json from chatgpt, organize for upload to db.
    image_base64 = image_to_base64(image)
    stats = call_chatgpt_for_ocr(image_base64)

    sets = stats.get('sets', '').split(',')
    stats['set1'] = sets[0].strip() if len(sets) > 0 else ''
    stats['set2'] = sets[1].strip() if len(sets) > 1 else ''
    stats['set3'] = sets[2].strip() if len(sets) > 2 else ''

    if 'unit_name' in stats:
        corrected_name = correct_name(stats['unit_name'], correct_unit_names)
        if corrected_name:
            stats['unit_name'] = corrected_name

    unit_image_url = fetch_unit_image(stats['unit_name'])

    new_stats = ImageStats(
        unit=stats.get('unit_name', ''),
        cp=stats.get('cp', ''),
        imprint=stats.get('imprint', ''),
        attack=stats.get('attack', ''),
        defense=stats.get('defense', ''),
        health=stats.get('health', ''),
        speed=stats.get('speed', ''),
        critical_hit_chance=stats.get('critical_hit_chance', ''),
        critical_hit_damage=stats.get('critical_hit_damage', ''),
        effectiveness=stats.get('effectiveness', ''),
        effect_resistance=stats.get('effect_resistance', ''),
        set1=stats.get('set1', ''),
        set2=stats.get('set2', ''),
        set3=stats.get('set3', ''),
        uploaded_by=username,
        user_rank=rta_rank, 
    )

    db.session.add(new_stats)
    db.session.commit()

    results.append({
        'stats': new_stats,
        'unit_image_url': unit_image_url
    })


@app.route('/screen_capture')
def screen_cap():
    # Render the screen capture page template. In development
    return render_template('screen_capture.html')

@app.route('/unit_lookup', methods=['GET', 'POST'])
def unit_lookup():
    # Render page for unit look up
    unit = correct_unit_names

    if request.method == 'POST':
        selected_unit = request.form.get('unit')
        return redirect(url_for('display_unit', unit_name=selected_unit))
    
    return render_template('unit_lookup.html', unit=unit)

def fetch_unit_data(unit_name):
    #Fixes unit name edge case, uses e7db to get needed stats 
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
    
@app.route('/unit_lookup/<unit_name>', methods=['GET'])
def display_unit(unit_name):
    # Displays base stats and information for requested unit 
    unit_data = fetch_unit_data(unit_name)
    if unit_data is None:
        return "Unit not found", 404

    unit_details = {
        'image': unit_data.get('image', ''),
        'name': unit_data.get('name', 'N/A'),
        'element': unit_data.get('element', 'N/A'),
        'class': unit_data.get('class', 'N/A'),
        'zodiac': unit_data.get('zodiac', 'N/A'),
        'stats': unit_data.get('stats', {}),
        'memory_imprints': unit_data.get('memory_imprints', {}),
        'skills': [{'name': skill.get('name', 'N/A'), 'description': skill.get('description', 'N/A')} for skill in unit_data.get('skills', [])]
    }

    return render_template('unit_details.html', unit=unit_details)

@app.route('/build_finder', methods=['GET', 'POST'])
def build_finder():
    #Renders page for build finder and searches db based on unit name and rank to find average stats
    unit = correct_unit_names
    ranks = ["Bronze", "Silver", "Gold", "Master", "Challenger", "Champion", "Emperor", "Legend"]

    if request.method == 'POST':
        selected_unit = request.form['unit']
        selected_rank = request.form['rank'].lower()

        average_stats = db.session.query(
            func.avg(cast(ImageStats.attack, Float)).label('avg_attack'),
            func.avg(cast(ImageStats.defense, Float)).label('avg_defense'),
            func.avg(cast(ImageStats.health, Float)).label('avg_health'),
            func.avg(cast(ImageStats.speed, Float)).label('avg_speed'),
            func.avg(cast(func.replace(ImageStats.critical_hit_chance, '%', ''), Float)).label('avg_crit_chance'),
            func.avg(cast(func.replace(ImageStats.critical_hit_damage, '%', ''), Float)).label('avg_crit_damage'),
            func.avg(cast(func.replace(ImageStats.effectiveness, '%', ''), Float)).label('avg_effectiveness'),
            func.avg(cast(func.replace(ImageStats.effect_resistance, '%', ''), Float)).label('avg_effect_resistance'),
            func.mode().within_group(ImageStats.set1).label('most_common_set1'),
            func.mode().within_group(ImageStats.set2).label('most_common_set2'),
            func.mode().within_group(ImageStats.set3).label('most_common_set3')
        ).filter(
            ImageStats.unit == selected_unit,
            ImageStats.user_rank == selected_rank
        ).first()

        if average_stats.avg_crit_chance == None:
            warning = 'No data found for the selected unit and rank.'

            return render_template('build_finder_results.html', warning=warning)

      
        return render_template('build_finder_results.html', 
                               stats=average_stats, 
                               unit=selected_unit, 
                               rank=selected_rank)

    return render_template('build_finder.html', unit=unit, ranks=ranks)

@app.route('/your_units', methods=['GET', 'POST'])
@login_required
def your_units():
    # Render the user's units and handle unit selection
    units = ImageStats.query.filter_by(uploaded_by=current_user.username).all()
    units.sort(key=lambda x: x.unit)
    selected_unit = request.form.get('unit')
    unit_image_url = None

    if request.method == 'POST':
        if selected_unit:
            selected_unit = ImageStats.query.filter(ImageStats.unit.like(f'%{selected_unit[:7]}%'),
            ImageStats.uploaded_by == current_user.username).first()
            if selected_unit:
                unit_image_url = fetch_unit_image(selected_unit.unit)

  
        return render_template('your_units.html', units=units, unit=selected_unit, unit_image_url=unit_image_url)
    
    return render_template('your_units.html', units=units)

@app.route('/delete_unit', methods=['POST'])
def delete_unit():
    # Delete a unit from the database
    unit_id = request.form.get('unit_to_delete')
    unit = ImageStats.query.get(unit_id)
    
    if unit:
        db.session.delete(unit)
        db.session.commit()
        flash(f'Unit {unit.unit} has been deleted.', 'success')
    else:
        flash('Unit not found.', 'danger')
    
    return redirect(url_for('your_units'))

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    # Handle user profile update and render profile page
    form = UpdateUserForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=current_user.username).first()
        if user:
            user.epic_seven_account = form.epic_seven_account.data
            user.streamer_name = form.streamer_name.data
            new_rta_rank = form.rta_rank.data
            user.rta_rank = new_rta_rank
            
            # Update all units' ranks for the user in the ImageStats table
            ImageStats.query.filter_by(uploaded_by=user.username).update({'user_rank': new_rta_rank})
            
            db.session.commit()
            flash('Your profile has been updated', 'success')
            return redirect(url_for('home'))
    else:
        user = Users.query.filter_by(username=current_user.username).first()
        form.username.data = user.username
        form.epic_seven_account.data = user.epic_seven_account
        form.streamer_name.data = user.streamer_name
        form.rta_rank.data = user.rta_rank

    return render_template('user_profile.html', form=form)

@app.route('/get_unit_data')
@login_required
def get_unit_data():
    # Return JSON data for the units of the current user
    units = ImageStats.query.filter_by(uploaded_by=current_user.username).all()
    units_data = [
        {
            'id': unit.id,
            'name': unit.unit,
            'health': unit.health,
            'attack': unit.attack,
            'defense': unit.defense,
            'speed': unit.speed,
            'critical_hit_chance': unit.critical_hit_chance,
            'critical_hit_damage': unit.critical_hit_damage,
            'effectiveness': unit.effectiveness,
            'effect_resistance': unit.effect_resistance
        }
        for unit in units
    ]
    return jsonify(units_data)

@app.route('/overlay')
def overlay():
    # Fetch and render the video component overlay with unit data
    units = ImageStats.query.filter_by(uploaded_by=current_user.username).all()
    return render_template('video_overlay_unit_select.html', units=units)

@app.route('/update_selected_units', methods=['POST'])
@login_required
def update_selected_units():
    #Api call for twitch overlay to update the units needed for overlay to the db
    data = request.json
    selected_units = data.get('units', [])
    print(selected_units)
    units = selected_units + [{}] * (4 - len(selected_units))

    unit_id1 = units[0].get('id', None)
    unit_id2 = units[1].get('id', None)
    unit_id3 = units[2].get('id', None)
    unit_id4 = units[3].get('id', None)

    # Clear existing selected units for the user
    SelectedUnit.query.filter_by(user_id=current_user.id).delete()
    
    new_unit = SelectedUnit(
        user_id=current_user.id,
        unit_id1=unit_id1,
        unit_id2=unit_id2,
        unit_id3=unit_id3,
        unit_id4=unit_id4
    )
    db.session.add(new_unit)
    db.session.commit()

    return jsonify({'status': 'success'})

@app.route('/api/get_selected_units_data', methods=['GET'])
@jwt_required()
def get_selected_units_data():
    #Electron page calls the db for the selected units 
    # current_user_id = get_jwt_identity()
    # user = Users.query.get(current_user_id)
    units_data = []
    
    selected_units = SelectedUnit.query.filter_by(user_id=1).first()
    
    if not selected_units:
        return jsonify({'error': 'No selected units found'}), 404
    
    unit_ids = [selected_units.unit_id1, selected_units.unit_id2, selected_units.unit_id3, selected_units.unit_id4]
    
    unit_ids = [uid for uid in unit_ids if uid is not None and uid != 0]

    for unit_id in unit_ids:
        unit_obj = ImageStats.query.get(unit_id)
        if unit_obj:
            units_data.append({
                'id': unit_obj.id,
                'name': unit_obj.unit,
                'health': unit_obj.health,
                'attack': unit_obj.attack,
                'defense': unit_obj.defense,
                'speed': unit_obj.speed,
                'critical_hit_chance': unit_obj.critical_hit_chance,
                'critical_hit_damage': unit_obj.critical_hit_damage,
                'effectiveness': unit_obj.effectiveness,
                'effect_resistance': unit_obj.effect_resistance
            })
        else:
            print(f'Unit with id {unit_id} not found in the database')

    print('Units data:', units_data)
    return jsonify(units_data)

@app.route('/generate_token', methods=['GET'])
def generate_token():
    # Specify the identity of the user for whom you want to generate the token
    user_id = 'faugnom1'
    
    # Generate the token
    token = create_access_token(identity=user_id)
    print(token)
    return jsonify(token=token)

if __name__ == '__main__':
    context = ('localhost.pem', 'localhost-key.pem')
    config_cloudinary()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
            #  ssl_context=context)


# For pyTesseract local install only
# @app.route('/display')
# def display_image():
#     # Display the image and extracted stats
#     filenames = session.get('filenames', [])
#     image_urls = session.get('image_urls', [])
#     username = current_user.username
#     rta_rank = current_user.rta_rank

#     print('Filenames:', filenames)
#     print('Image URLs:', image_urls)

#     if not filenames and not image_urls:
#         print('No filenames or image URLs found in session.')
#         return redirect(url_for('upload_file'))

#     results = []

#     regions = {
#         'unit': {'x': 150, 'y': 170, 'width': 700, 'height': 60},
#         'cp': {'x': 207, 'y': 555, 'width': 200, 'height': 50},
#         'imprint': {'x': 275, 'y': 360, 'width': 190, 'height': 100},
#         'attack': {'x': 385, 'y': 620, 'width': 100, 'height': 29},
#         'defense': {'x': 385, 'y': 650, 'width': 100, 'height': 29}, 
#         'health': {'x': 385, 'y': 680, 'width': 100, 'height': 29},
#         'speed': {'x': 385, 'y': 720, 'width': 100, 'height': 29}, 
#         'critical_hit_chance': {'x': 385, 'y': 750, 'width': 100, 'height': 29}, 
#         'critical_hit_damage': {'x': 385, 'y': 785, 'width': 100, 'height': 34},
#         'effectiveness':  {'x': 385, 'y': 820, 'width': 100, 'height': 34}, 
#         'effect_resistance': {'x': 385, 'y': 850, 'width': 100, 'height': 34},
#         'set1': {'x': 210, 'y': 942, 'width': 200, 'height': 34},
#         'set2':  {'x': 210, 'y': 976, 'width': 200, 'height': 34}, 
#         'set3': {'x': 210, 'y': 1010, 'width': 200, 'height': 34}
#     }

#     for filename in filenames:
#         image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#         image = Image.open(image_path)
#         process_image(image, regions, results, username, rta_rank)

#         db.session.commit()

#     for url in image_urls:
#         response = requests.get(url)
#         image = Image.open(BytesIO(response.content))
#         process_image(image, regions, results, username, rta_rank)

#         db.session.commit()

#     return render_template('display.html', results=results)

# def process_image(image, regions, results, username, rta_rank):
#     # Extract stats from the image, correct the unit name, and save to the database
#     stats = {name: pytesseract.image_to_string(image.crop((data['x'], data['y'], data['x'] + data['width'], data['y'] + data['height'])), config='--psm 6') for name, data in regions.items()}

#     if 'unit' in stats:
#         corrected_name = correct_name(stats['unit'], correct_unit_names)
#         if corrected_name:
#             stats['unit'] = corrected_name
#         else:
#             print("No matching unit name found or low confidence match for:", stats['unit'])

#     new_stats = ImageStats(**stats)
#     new_stats.uploaded_by = username
#     new_stats.user_rank = rta_rank

#     db.session.add(new_stats)
#     results.append(new_stats)
