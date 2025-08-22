from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


class Users():
    def __init__(self, username, epic_seven_account, streamer_name, rta_rank, password_hash, access_token, refresh_token,    _id=None):
        self.username = username
        self.epic_seven_account = epic_seven_account
        self.streamer_name = streamer_name
        self.rta_rank = rta_rank
        self.password_hash = password_hash
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.id = _id  # MongoDB's ObjectId
    
    def get_id(self):
        return str(self.id) 
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    
class SelectedUnit:
    def __init__(self, user_id, unit_id1=None, unit_id2=None, unit_id3=None, unit_id4=None, _id=None):
        self._id = _id
        self.user_id = user_id
        self.unit_id1 = unit_id1
        self.unit_id2 = unit_id2
        self.unit_id3 = unit_id3
        self.unit_id4 = unit_id4

class ImageStats:
    def __init__(self, unit, cp, imprint, attack, defense, health, speed, critical_hit_chance,
                 critical_hit_damage, effectiveness, effect_resistance, set1, set2, set3,
                 uploaded_by, user_rank, _id=None):
        self._id = _id
        self.unit = unit
        self.cp = cp
        self.imprint = imprint
        self.attack = attack
        self.defense = defense
        self.health = health
        self.speed = speed
        self.critical_hit_chance = critical_hit_chance
        self.critical_hit_damage = critical_hit_damage
        self.effectiveness = effectiveness
        self.effect_resistance = effect_resistance
        self.set1 = set1
        self.set2 = set2
        self.set3 = set3
        self.uploaded_by = uploaded_by
        self.user_rank = user_rank

    def to_dict(self):
        return {
            "unit": self.unit,
            "cp": self.cp,
            "imprint": self.imprint,
            "attack": self.attack,
            "defense": self.defense,
            "health": self.health,
            "speed": self.speed,
            "critical_hit_chance": self.critical_hit_chance,
            "critical_hit_damage": self.critical_hit_damage,
            "effectiveness": self.effectiveness,
            "effect_resistance": self.effect_resistance,
            "set1": self.set1,
            "set2": self.set2,
            "set3": self.set3,
            "uploaded_by": self.uploaded_by,
            "user_rank": self.user_rank
        }

    def __repr__(self):
        return f'<ImageStats {self.unit}>'