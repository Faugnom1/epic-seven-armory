import pytesseract
from PIL import Image
from models.models import Users, ImageStats
from database import db

def test_home_page(test_client):
    # Tests homepage rendering
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Welcome to E7 Armory" in response.data

def test_login_correct(test_client):
    # Tests correct login information
    response = test_client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'You have been logged in!' in response.get_data(as_text=True)

def test_login_incorrect(test_client):
    # Tests incorrect login information
    response = test_client.post('/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert 'Login Unsuccessful. Please check username and password' in response.get_data(as_text=True)

def test_display_units(test_client):
    #Tests displaying units associated with user profile.
    test_client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    new_unit = ImageStats(unit='Navy Captain Landy', uploaded_by='testuser')
    db.session.add(new_unit)
    db.session.commit()

    response = test_client.get('/your_units')
    assert response.status_code == 200
    assert 'Navy Captain Landy' in response.get_data(as_text=True)

def test_user_update_rank(test_client):
    #Tests user rank correctly updating. Tests from Silver to Bronze.
    test_client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    response = test_client.post('/profile', data={
        'username': 'testuser',
        'rta_rank': 'Silver',
        'submit': True
    }, follow_redirects=True)

    response = test_client.get('/profile')
    assert response.status_code == 200
    assert 'Silver' in response.get_data(as_text=True)

    response = test_client.post('/profile', data={
        'username': 'testuser',
        'rta_rank': 'Bronze',
        'submit': True
    }, follow_redirects=True)

    response = test_client.get('/profile')
    assert response.status_code == 200
    assert 'Bronze' in response.get_data(as_text=True)

def test_ocr():
    #Test OCR is properly extracting stats from image
    image_path = 'C:\\Users\\Mike\\Documents\\Springy\\epic-seven-armory-main\\static\\uploads\\Test Jenua.png'

    image = Image.open(image_path)

    attack_region = {'x': 385, 'y': 620, 'width': 100, 'height': 29}

    attack_box = (
        attack_region['x'], attack_region['y'], 
        attack_region['x'] + attack_region['width'], 
        attack_region['y'] + attack_region['height'])
    
    attack_image = image.crop(attack_box)
    
    extracted_text = pytesseract.image_to_string(attack_image)

    expected_text = "4178"

    assert expected_text in extracted_text

def test_new_user():
    username = "TestUser2"
    password = "TestPassword123!"
    epic_account = "epic_account"
    streamer_name = "streamer"
    rta_rank = "Gold"

    existing_user = Users.query.filter_by(username=username).first()
    
    if existing_user:
        # If the user exists, delete it first
        db.session.delete(existing_user)
        db.session.commit()

    new_user = Users(username=username, epic_seven_account=epic_account,
                         streamer_name=streamer_name, rta_rank=rta_rank)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    retrieved_user = Users.query.filter_by(username=username).first()

    assert retrieved_user
    assert retrieved_user.username == username
    assert retrieved_user.check_password(password)
    assert retrieved_user.epic_seven_account == epic_account
    assert retrieved_user.streamer_name == streamer_name
    assert retrieved_user.rta_rank == rta_rank
    assert not retrieved_user.check_password('wrongpassword')

    

