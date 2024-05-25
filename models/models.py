from database import db
from flask_bcrypt import Bcrypt
from flask_login import UserMixin

bcrypt = Bcrypt()

class ImageStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    unit = db.Column(db.String(80))
    cp = db.Column(db.String(80))
    imprint = db.Column(db.String(80))
    attack = db.Column(db.String(80))
    defense = db.Column(db.String(80))
    health = db.Column(db.String(80))
    speed = db.Column(db.String(80))
    critical_hit_chance = db.Column(db.String(80))
    critical_hit_damage = db.Column(db.String(80))
    effectiveness = db.Column(db.String(80))
    effect_resistance = db.Column(db.String(80))
    set1 = db.Column(db.String(80))
    set2 = db.Column(db.String(80))
    set3 = db.Column(db.String(80))
    uploaded_by = db.Column(db.String(80))
    user_rank = db.Column(db.String(80))


    def __repr__(self):
        return f'<ImageStats {self.unit}>'

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    epic_seven_account = db.Column(db.String(100), nullable=False)
    streamer_name = db.Column(db.String(100), nullable=True)
    rta_rank = db.Column(db.String(100), nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
class SelectedUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    unit_id1 = db.Column(db.Integer, nullable=True)
    unit_id2 = db.Column(db.Integer, nullable=True)
    unit_id3 = db.Column(db.Integer, nullable=True)
    unit_id4 = db.Column(db.Integer, nullable=True)   
   
