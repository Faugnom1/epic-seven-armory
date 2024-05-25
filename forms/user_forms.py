from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, Optional

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    epic_seven_account = StringField('Epic Seven Account Name', validators=[DataRequired()])
    streamer_name = StringField('Streamer Name (Optional)', validators=[Optional()])
    rta_rank = SelectField('RTA Rank', choices=[
        ('bronze', 'Bronze'), 
        ('silver', 'Silver'), 
        ('gold', 'Gold'), 
        ('master', 'Master'), 
        ('challenger', 'Challenger'), 
        ('champion', 'Champion'), 
        ('emperor', 'Emperor'), 
        ('legend', 'Legend')
    ], validators=[DataRequired()])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')