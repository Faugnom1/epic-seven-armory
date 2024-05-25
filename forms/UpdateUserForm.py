from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

class UpdateUserForm(FlaskForm):
    username = StringField('Username', render_kw={'readonly': True, 'class': 'form-control'})
    epic_seven_account = StringField('Epic Seven Account Name', validators=[DataRequired()], render_kw={'class': 'form-control'})
    streamer_name = StringField('Streamer Name', validators=[DataRequired()], render_kw={'class': 'form-control'})
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
    submit = SubmitField('Update', render_kw={'class': 'btn btn-primary'})