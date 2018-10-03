from flask import flash
from flask_wtf import FlaskForm
from flask_login import login_user
from wtforms import PasswordField, StringField, IntegerField, BooleanField, SelectField, SubmitField, ValidationError, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, StopValidation
from werkzeug.security import gen_salt
from uuid import uuid4
from random import SystemRandom


from .models import User, Client, db

class UserForm(FlaskForm):
	username = StringField('User id:', validators=[DataRequired()])
	email = StringField('Email:', validators=[Email(message='Invalid Email')])
	password = PasswordField('Password:', validators=[DataRequired(), Length(min=8, max=80), EqualTo('confirm_pass')])
	confirm_pass = PasswordField('Confirm password:')
	submit = SubmitField("Signup")

	def validate_email(self, field):
		if User.query.filter_by(email=field.data).first():
			raise ValidationError('Email is already in use.')

	def validate_username(self, field):
		if User.query.filter_by(id=field.data).first():
			raise ValidationError('Username is already in use.')

	def save(self):
		alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		generator = SystemRandom()
		random_seed = u''.join(generator.choice(alphabet) for _ in range(81))

		self.validate_email(self.email)
		self.validate_username(self.username)

		user = User(username=self.username.data,
				identifier=str(uuid4()),
				password=self.password.data,
				email=self.email.data,
				seed=random_seed
				)

		db.session.add(user)
		db.session.commit()
		return user


class LoginForm(FlaskForm):
	username = StringField('User id:', validators=[DataRequired(), Length(min=6, max=24)])
	password = PasswordField('Password:', validators=[DataRequired(), Length(min=8, max=80)])
	remember = BooleanField('Remember me')
	submit = SubmitField("Login")

	def login(self):
		user = User.query.filter_by(username=str(self.username.data.lower())).first()

		if user is not None and user.verify_password(self.password.data):
			login_user(user)
		else:
			flash("Username or password is invalid!")

class ConfirmForm(FlaskForm):
	confirm = BooleanField()
	submit = SubmitField("Authorize payment")

class SendIotaForm(FlaskForm):
	identifier = StringField('id:', validators=[DataRequired(), Length(max=80)])
	value = IntegerField('Value:', validators=[DataRequired()])
	time = IntegerField('Time:', validators=[DataRequired()])
	target = StringField('Address:', validators=[DataRequired(), Length(min=81, max=81)])
	num_payments = IntegerField('Numer of payments:', validators=[NumberRange(min=0, max=999)])
	si = SelectField(u'si', choices=[('i', 'iota'), ('ki', 'kiota'), ('Mi', 'Miota')], validators=[DataRequired()])

	def send_payment(self):
		_value = self.value.data
		if form.si.data=='ki':
			_value *= 1e3
		elif form.si.data=='Mi':
			_value *= 1e6

		tx = ProposedTransaction(address=Address(str(self.target.data)),
			value=int(_value),
			tag=None,
			message=TryteString.from_string(self.identifier.data))

		user = User.query.filter_by(identifier=self.identifier.data)
		user.iota_api.send_transfer(depth=10, transfers=[tx])


class ClientForm(FlaskForm):
	client_name = StringField("Client Name", validators=[DataRequired()])
	client_uri = StringField("Client URI", validators=[DataRequired()])
	redirect_uri = StringField("Redirect URI", validators=[DataRequired()])
	grant_type = SelectField("Grant Type", choices=[("authorization_code", "Authorization Code")])
	response_type = SelectField("Response Type", choices=[("code", "Code")])
	scope = StringField()
	submit = SubmitField("Create Client")

	def update(self, client):
		client.client_name = self.client_name.data
		client.client_uri = self.client_uri.data
		client.redirect_uri = self.redirect_uri.data
		client.grant_type = self.grant_type.data
		client.response_type = self.response_type.data
		client.client_scope = self.scope.data

		db.session.add(client)

		db.session.commit()
		return client

	def save(self, user):
		client_id = gen_salt(48)
		client_secret = gen_salt(78)

		client = Client(
			client_id = client_id,
			client_secret = client_secret,
			client_name = self.client_name.data,
			client_uri = self.client_uri.data,
			redirect_uri = self.redirect_uri.data,
			grant_type = self.grant_type.data,
			response_type = self.response_type.data,
			scope = self.scope.data,
			user = user
		)
		db.session.add(client)
		db.session.commit()
		return client
