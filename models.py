from flask_login import UserMixin
from passlib.context import CryptContext

from app import db, login_manager


class User(UserMixin, db.Model):

	#Password Encryption
		self.pwd_context = CryptContext(
		schemes=["pbkdf2_sha256"],
		default="pbkdf2_sha256",
		pbkdf2_sha256__default_rounds=30000
		)


	__tablename__ = 'users'

	userID = db.column(db.String(128), unique=True, primary_key=True,)
	identifier = db.column(db.String(128), unique=True, index=True)
	password_hash = db.Column(db.String(80), nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	seed = db.Column(db.String(120), unique=True, nullable=False)
	is_authenticated = db.Column(db.Boolean, nullable=False, default=False)
	is_active = db.Column(db.Boolean, nullable=False, default=False)
	is_anonymous = db.Column(db.Boolean, nullable=False)
	user_transactions = db.relationship('User', backref='transaction', lazy='dynamic')


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
		self.password_hash = self.pwd_context.encrypt(password)

	def verify_password(self, password):
		"""
		Check if hashed password matches actual password
		"""
		return self.pwd_context.verify(password, self.password_hash)


	def __repr__(self):
		return '<User: {}>'.format(self.username)

# Set up user_loader
@login_manager.user_loader
def load_user(userID):
    return User.query.get(str(userID))

class Transaction(db.model):
	__tablename__ = 'transactions'

	transaction_id = db.column(db.Integer, primary_key=True, unique=True)
	userID = db.column(db.String(128), db.ForeignKey(users.userID))
	value = db.column(db.Integer(), default=0)
	target = db.column(db.String(128), nullable=False)
	timestamp = db.column(db.Integer(), nullable=False)

	 def __repr__(self):
        return '<Transaction ID: {}>'.format(self.transaction_id)






