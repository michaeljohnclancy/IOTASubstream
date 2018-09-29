from flask_login import UserMixin, current_user
from flask_wtf import FlaskForm

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length
from passlib.context import CryptContext
from authlib.flask.oauth2.sqla import (
	OAuth2ClientMixin,
	OAuth2AuthorizationCodeMixin,
	OAuth2TokenMixin,
)

db = SQLAlchemy()
login_manager = LoginManager()

from tasks import create_api

pwd_context = CryptContext(
		schemes=["pbkdf2_sha256"],
		default="pbkdf2_sha256",
		pbkdf2_sha256__default_rounds=30000
		)


class User(UserMixin, db.Model):


	__tablename__ = 'users'

	id = db.Column(db.String(128), unique=True, primary_key=True)
	identifier = db.Column(db.String(128), unique=True, index=True)
	password_hash = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(128), unique=True, nullable=False)
	seed = db.Column(db.String(128), unique=True, nullable=False)

	#user_transactions = db.relationship('Transaction', backref='User', lazy='dynamic')
	
	#MAY BE NECESSARY FOR AUTHLIB BUT NOT SURE(user loader decorator further down)
	def get_user_id(self):
		if self.id:
			return self.id
		else:
			return False
	
	def api(self):
		return create_api(self.seed)

	@property
	def password(self):
		"""
		Prevent pasword_hash from being accessed
		"""
		raise AttributeError('password is not a readable attribute.')

	@password.setter
	def password(self, password):
		"""
		Set password to a hashed password
		"""

		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		"""
		Check if hashed password matches actual password
		"""
		return pwd_context.verify(password, self.password_hash)



	def __repr__(self):
		return '<User: {}>'.format(self.id)

class Transaction(db.Model):
	__tablename__ = 'transactions'

	transaction_id = db.Column(db.String(128), primary_key=True, unique=True)
	user_identifier = db.Column(
		db.String(128), db.ForeignKey('users.identifier', ondelete='CASCADE')
	)
	value = db.Column(db.Integer(), default=0)
	target = db.Column(db.String(128), nullable=True)
	timestamp = db.Column(db.Integer(), nullable=False)

	user = db.relationship('User')


	def __repr__(self):
		return '<Transaction ID: {}>'.format(self.transaction_id)

# Set up setters and getters
@login_manager.user_loader
def load_user(id):
	return User.query.get(str(id))

class Client(db.Model, OAuth2ClientMixin):
	__tablename__ = 'oauth2_client'

	id = db.Column(db.Integer(), primary_key=True)
	user_id = db.Column(
		db.String(128), db.ForeignKey('users.id', ondelete='CASCADE')
	)
	user = db.relationship('User')

class AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
	__tablename__ = 'oauth2_code'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(
		db.String(128), db.ForeignKey('users.id', ondelete='CASCADE'))
	user = db.relationship('User')

class Token(db.Model, OAuth2TokenMixin):
	__tablename__ = 'oauth2_token'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(
		db.String(128), db.ForeignKey('users.id', ondelete='CASCADE'))
	user = db.relationship('User')

	def is_refresh_token_expired(self):
		expires_at = self.issued_at + self.expires_in * 2
		return expires_at < time.time()

