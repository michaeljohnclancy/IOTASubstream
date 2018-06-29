from flask_login import UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length

import tasks

from passlib.context import CryptContext

from __init__ import db
from . import login_manager

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
	
	def api(self):
		return tasks.create_api(self.seed)

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

# Set up user_loader

@login_manager.user_loader
def load_user(id):
	return User.query.get(str(id))

class Transaction(db.Model):
	__tablename__ = 'transactions'


	transaction_id = db.Column(db.String(128), primary_key=True, unique=True)
	identifier = db.Column(db.String(128))
	value = db.Column(db.Integer(), default=0)
	target = db.Column(db.String(128), nullable=True)
	timestamp = db.Column(db.Integer(), nullable=False)


	def __repr__(self):
		return '<Transaction ID: {}>'.format(self.transaction_id)

