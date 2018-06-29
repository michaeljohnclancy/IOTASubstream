from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, BooleanField, SelectField, SubmitField, ValidationError
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

from .models import User

class SignupForm(FlaskForm):
	id = StringField('User id:', validators=[DataRequired()])
	email = StringField('Email:', validators=[Email(message='Invalid Email')])
	password = PasswordField('Password:', validators=[DataRequired(), Length(min=8, max=80), EqualTo('confirm')])
	confirm = PasswordField('Confirm password:')
	submit = SubmitField("Signup")

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email is already in use.')

	def validate_username(self, field):
		if User.query.filter_by(id=field.data).first():
			raise ValidationError('Username is already in use.')

class LoginForm(FlaskForm):
	id = StringField('User id:', validators=[DataRequired(), Length(min=6, max=24)])
	password = PasswordField('Password:', validators=[DataRequired(), Length(min=8, max=80)])
	remember = BooleanField('Remember me')
	submit = SubmitField("Login")

class SendIotaForm(FlaskForm):
	identifier = StringField('id:', validators=[DataRequired(), Length(max=80)])
	value = IntegerField('Value:', validators=[DataRequired()])
	time = IntegerField('Time:', validators=[DataRequired()])
	target = StringField('Address:', validators=[DataRequired(), Length(min=81, max=81)])
	num_payments = IntegerField('Numer of payments:', validators=[NumberRange(min=0, max=999)])
	si = SelectField(u'si', choices=[('i', 'iota'), ('ki', 'kiota'), ('Mi', 'Miota')], validators=[DataRequired()])
