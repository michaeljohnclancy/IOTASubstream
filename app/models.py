from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length
import uuid

from passlib.context import CryptContext

from app import db, login_manager

pwd_context = CryptContext(
		schemes=["pbkdf2_sha256"],
		default="pbkdf2_sha256",
		pbkdf2_sha256__default_rounds=30000
		)


class User(UserMixin, db.Model):


	__tablename__ = 'users'

	id = db.Column(db.String(128), unique=True, primary_key=True,)
	identifier = db.Column(db.String(128), unique=True, index=True)
	password_hash = db.Column(db.String(80), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	seed = db.Column(db.String(120), unique=True, nullable=False)
	#user_transactions = db.relationship('Transaction', backref='User', lazy='dynamic')


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



	"""def iota_send(self, target, value, time=0, numPayments=1):
		i = 0
		while (i <= numPayments-1):
			tx = ProposedTransaction(address=Address(target), value=value, tag=None, message=TryteString.from_string(self.id))
			self.api.send_transfer(depth = 100, transfers=[tx])
			
			#Logs transaction to DB
			self.db_connection.addTransaction(self.identifier, value, self.seed, target, tx.timestamp)
			
			print("Sent")
			sleep(time)
			i += 1
		"""

	def __repr__(self):
		return '<User: {}>'.format(self.username)

# Set up user_loader

@login_manager.user_loader
def load_user(id):
	return User.query.get(str(id))

def is_safe_url(self, target):
		ref_url = urlparse(request.host_url)
		test_url = urlparse(urljoin(request.host_url, target))
		return test_url.scheme in ('http', 'https') and \
		   ref_url.netloc == test_url.netloc

class Transaction(db.Model):
	__tablename__ = 'transactions'

	transaction_id = db.Column(db.Integer(), primary_key=True, unique=True)
	id = db.Column(db.String(128))
	value = db.Column(db.Integer(), default=0)
	target = db.Column(db.String(128), nullable=False)
	timestamp = db.Column(db.Integer(), nullable=False)

	def __repr__(self):
		return '<Transaction ID: {}>'.format(self.transaction_id)



