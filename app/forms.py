from models import FlaskForm
from forms import FileField, FileRequired
from config import StringField, TextAreaField, SubmitField, PasswordField
from views import InputRequired, Email, DataRequired

class LoginForm(FlaskForm):
	username = StringField  (u'Username' , validators=[DataRequired()])
	password = PasswordField(u'Password', validators=[DataRequired()])

class RegisterForm(FlaskForm):
	name = StringField  (u'Name'      )
	username = StringField  (u'Username' , validators=[DataRequired()])
	password = PasswordField(u'Password', validators=[DataRequired()])
	email = StringField  (u'Email' , validators=[DataRequired(), Email()])