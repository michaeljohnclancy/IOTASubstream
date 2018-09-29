from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, IntegerField, BooleanField, SelectField, SubmitField, ValidationError, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from werkzeug.security import gen_salt

from .models import User, Client, db

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

class SubmitForm(FlaskForm):
	submit = BooleanField()

class SendIotaForm(FlaskForm):
	identifier = StringField('id:', validators=[DataRequired(), Length(max=80)])
	value = IntegerField('Value:', validators=[DataRequired()])
	time = IntegerField('Time:', validators=[DataRequired()])
	target = StringField('Address:', validators=[DataRequired(), Length(min=81, max=81)])
	num_payments = IntegerField('Numer of payments:', validators=[NumberRange(min=0, max=999)])
	si = SelectField(u'si', choices=[('i', 'iota'), ('ki', 'kiota'), ('Mi', 'Miota')], validators=[DataRequired()])

class ClientForm(FlaskForm):
	name = StringField(validators=[DataRequired()])
	redirect_uri = StringField(validators=[DataRequired()])
	scope = StringField()
	submit = SubmitField("Create Client")

	def update(self, client):
		client.name = self.name.data
		client.redirect_uri = self.redirect_uri.data
		client.scope = self.scope.data
		
		db.session.add(client)

		db.session.commit()
		return client

	def save(self, user):
		client_id = gen_salt(48)
		client_secret = gen_salt(78)

		client = Client(
			client_id=client_id,
			client_secret=client_secret,
			name=self.name.data,
			user=user,
			redirect_uri=self.redirect_uri.data,
			scope=self.scope.data,
		)
		db.session.add(client)
		db.session.commit()
		return client
