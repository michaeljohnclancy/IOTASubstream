from flask_login import UserMixin, current_user
from flask_wtf import FlaskForm
import pickle

from sqlalchemy.schema import UniqueConstraint
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length
from passlib.context import CryptContext
from authlib.flask.oauth2.sqla import (
	OAuth2ClientMixin,
	OAuth2AuthorizationCodeMixin,
	OAuth2TokenMixin,
)

from iota import Iota

from extensions import db, login_manager


pwd_context = CryptContext(
		schemes=["pbkdf2_sha256"],
		default="pbkdf2_sha256",
		pbkdf2_sha256__default_rounds=30000
		)

# Set up setters and getters
@login_manager.user_loader
def user_loader(user_id):
	user = User.query.filter_by(id=user_id).first()
	if user:
		return user
	return None

class User(UserMixin, db.Model):

	__tablename__ = 'users'

	id = db.Column(db.Integer(), primary_key=True, index=True)
	username = db.Column(db.String(128), nullable=False, unique=True)
	identifier = db.Column(db.String(128), nullable=False, unique=True)
	password_hash = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(128), unique=True, nullable=False)
	seed = db.Column(db.String(128), unique=True, nullable=False)
	balance = db.Column(db.Integer(), default=0)

	active_agreements = db.relationship('PaymentAgreement', backref='user', lazy=True)
	transactions = db.relationship('Transaction', backref='user', lazy=True)

	@property
	def iota_api(self):
		return Iota("http://192.168.0.12:14600", self.seed)

	def iota_account_data(self, n=0):
		return self.iota_api.get_account_data(n)

	def get_balance(self):
		return self.iota_account_data()['balance']

	def get_bundles(self, n=0):
		return self.iota_account_data()['bundles']

	def get_user_id(self):
		if self.id:
			return self.id
		else:
			return False

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

	def check_balance(self):
		current_user.balance = user.iota_api.get_account_data()['balance']
		db.commit()

	def __repr__(self):
		return '<User: {}>'.format(self.id)

class Transaction(db.Model):
	__tablename__ = 'transactions'

	transaction_id = db.Column(db.String(128), primary_key=True)
	user_identifier = db.Column(
		db.String(128), db.ForeignKey('users.identifier', ondelete='CASCADE')
	)
	payment_amount = db.Column(db.Integer(), default=0)
	payment_address = db.Column(db.String(128), nullable=True)
	timestamp = db.Column(db.Integer(), nullable=False)

	payment_agreement_id = db.Column(db.Integer(), db.ForeignKey('payment_agreement.id'))

	def __repr__(self):
		return '<Transaction ID: {}>'.format(self.transaction_id)

class PaymentAgreement(db.Model):
	#TODO Need to add functions for starting and stopping payments
	#Starting payments needs to check if the token between the users is active

	__tablename__ = "payment_agreement"
	__table_args__ = tuple(UniqueConstraint('user_id', 'client_id'),)

	id = db.Column(db.Integer(), primary_key=True)
	payment_address = db.Column(db.String(128))
	payment_amount = db.Column(db.Integer(), default=0)
	payment_time = db.Column(db.Integer(), default=0)
	user_id = db.Column(db.Integer(), db.ForeignKey('users.id'))
	client_id = db.Column(db.String(128), db.ForeignKey('oauth2_client.client_id'))

	is_active = db.Column(db.Boolean(), default=0)

	transactions = db.relationship('Transaction', backref='payment_agreement', lazy=True)
	token = db.relationship('Token', backref='payment_agreement', lazy=True, uselist=False)


	def set_address(self, new_address):
		self.payment_address = new_address

	def is_valid_session(self):
		#This checks all conditions regarding sending a payment.
		#Checks for:
		#active OAuth Session
		#sufficient balance in account
		#if payment is paused

		remaining_balance = self.user.get_balance() - self.payment_amount
		print(remaining_balance)
		print(bool(not self.token))
		print(self.token.revoked)
		print(not self.is_active)

		if (not self.token) or self.token.revoked or (remaining_balance < 0) or (not self.is_active):
			return False
		else:
			return True

	def info(self):
		return dict(
			username=self.user.username,
			payment_address=self.payment_address,
			payment_amount=self.payment_amount,
			payment_time=self.payment_time
			)

	def send_payment(self):
		#Sends payment based off of payment agreement. Returns Boolean depending on success.
		if self.is_valid_session():
			tx = ProposedTransaction(address=Address(str(self.payment_address)),
					value=int(self.payment_amount),
					tag=None,
					message=TryteString.from_string(self.user.identifier))

			try:
				self.user.iota_api().send_transfer(depth=10, transfers=[tx])
			except:
				print("Transfer Unsuccessful")
				return None

			transaction = Transaction(transaction_id=str(uuid.uuid4()),
				identifier=self.user.identifier,
				payment_amount=self.payment_amount,
				payment_address=self.payment_address,
				timestamp=tx.timestamp)

			db.session.add(transaction)
			db.session.commit()
			return transaction

		else:
			print("Session Invalid")
			return None


	def start_agreement(self):
		execute_agreement.delay()

	def stop_agreement():
		self.is_active = 0

class Client(db.Model, OAuth2ClientMixin):
	__tablename__ = 'oauth2_client'

	id = db.Column(db.Integer(), primary_key=True)
	user_id = db.Column(
		db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE')
	)
	payment_agreements = db.relationship('PaymentAgreement', backref='client', lazy='dynamic')

class AuthorizationCode(db.Model, OAuth2AuthorizationCodeMixin):
	__tablename__ = 'oauth2_code'

	id = db.Column(db.Integer(), primary_key=True)
	client_id = db.Column(
		db.String(128), db.ForeignKey('oauth2_client.client_id', ondelete='CASCADE'))
	user_id = db.Column(
		db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
	

class Token(db.Model, OAuth2TokenMixin):
	__tablename__ = 'oauth2_token'
	__table_args__ = tuple(UniqueConstraint('user_id', 'client_id'),)

	id = db.Column(db.Integer(), primary_key=True)
	user_id = db.Column(
		db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
	client_id = db.Column(
		db.String(128), db.ForeignKey('oauth2_client.client_id', ondelete='CASCADE'))
	payment_agreement_id = db.Column(
		db.Integer(), db.ForeignKey('payment_agreement.id', ondelete='CASCADE'))
	def is_refresh_token_expired(self):
		expires_at = self.issued_at + self.expires_in * 2
		return expires_at < time.time()



