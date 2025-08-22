from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
bcrypt = Bcrypt(app)

# MongoDB connection
uri = "mongodb+srv://michaelfaugnodev:GfY7h6QqkOR1PIgx@epic-seven-armory-proje.idpnatp.mongodb.net/?retryWrites=true&w=majority&appName=Epic-Seven-Armory-Project"

client = MongoClient(uri, server_api=ServerApi('1'))

# Access the database
db = client['epic_seven_armory']

# Sample user data
sample_users = [
    {
        "username": "testuser1",
        "password": bcrypt.generate_password_hash("password123").decode('utf-8')
    },
    {
        "username": "testuser2",
        "password": bcrypt.generate_password_hash("mypassword").decode('utf-8')
    }
]

# Insert sample data into the 'users' collection
db.Users.insert_many(sample_users)

print("Sample users inserted.")