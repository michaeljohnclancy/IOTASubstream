import pymysql.cursors
from passlib.context import CryptContext
from random import SystemRandom
import pymysql.cursors
from iota import *
import flask_login as fl
import flask
from time import *
import os
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_wtf import FlaskForm
import uuid
from urlparse import urlparse, urljoin
from flask import request, url_for


class User :

	"""
	User Attributes:
		db_connection
		node
		userID
		seed
		api
		is_authenticated
		is_active
		is_anonymous

	User Methods:
		set_node()
		get_node()
		iota_send()
		new_address()
		transactionHistory()
		commitUserToDB()
		password_encrypt()
		password_verify()
		get_password_hash()
		set_is_authenticated()
		set_is_active()
		set_is_anonymous()
		get_id()
		exists()
	"""

	def __init__(self, userID):
		#Starts database connection

		self.db_connection = sql()


		#Password Encryption
		self.pwd_context = CryptContext(
		schemes=["pbkdf2_sha256"],
		default="pbkdf2_sha256",
		pbkdf2_sha256__default_rounds=30000
		)

		self.node = "http://node02.iotatoken.nl:14265"
		self.userID = userID

		if self.exists():
			self.seed = self.db_connection.selectProperty(self.userID, "seed")
			print(self.seed)
			self.identifier = self.db_connection.selectProperty(self.userID, "identifier")
			self.is_authenticated = self.get_is_authenticated()
			self.is_active = self.get_is_active() #Need to change to false and only make true when email is confirmed
			self.is_anonymous = self.get_is_anonymous()

		#Generates random seed
		else:
			alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
			generator = SystemRandom()
			self.seed = u''.join(generator.choice(alphabet) for _ in range(81))

			self.identifier = str(uuid.uuid4())

			self.is_authenticated = False
			self.is_active = True #Need to change to false and only make true when email is confirmed
			self.is_anonymous = True

		self.api = Iota(self.node, self.seed)

	def setNode(self, node):
		self.node=node

	def getNode(self):
		return self.node

	def iota_send(self, target, value, time=0, numPayments=1):
		i = 0
		while (i <= numPayments-1):
			tx = ProposedTransaction(address=Address(target), value=value, tag=None, message=TryteString.from_string(self.userID))
			self.api.send_transfer(depth = 100, transfers=[tx])
			
			#Logs transaction to DB
			self.db_connection.addTransaction(self.identifier, value, self.seed, target, tx.timestamp)
			
			print("Sent")
			sleep(time)
			i += 1

	def newAddress(self):
		return self.api.get_new_addresses()['addresses'][0]

	def transactionHistory(self):
		return self.db_connection.userTransactionHistory(self.userID)

	def registerUser(self):
		self.is_authenticated = False
		self.is_active = True

		if not self.exists():
			self.db_connection.newUserAccount(self.userID, self.identifier, self.password_hash, self.email, self.seed, self.is_authenticated, self.is_active)

	def password_encrypt(self, password):
		return self.pwd_context.encrypt(password)

	def password_verify(self, password, hashed):
		return self.pwd_context.verify(password, hashed)

	def set_password_hash(self, password_hash):
		self.password_hash = password_hash

	def set_email(self, email):
		self.email = email

	def get_password_hash(self):
		return self.db_connection.getPasswordHash(self.userID)

	def set_is_authenticated(self, bool_val):
		self.db_connection.updateProperty(self.userID, 'is_authenticated', bool_val)
		self.is_authentpicated = bool_val

	def set_is_active(self, bool_val):
		self.db_connection.updateProperty(self.userID, 'is_active', bool_val)
		self.is_active = bool_val
	
	def set_is_anonymous(self, bool_val):
		self.db_connection.updateProperty(self.userID, 'is_anonymous', bool_val)
		self.is_anonymous = bool_val

	def get_is_authenticated(self):
		return self.db_connection.selectProperty(self.userID, "is_authenticated")

	def get_is_active(self):
		return self.db_connection.selectProperty(self.userID, "is_active")

	def get_is_anonymous(self):
		return self.db_connection.selectProperty(self.userID, "is_anonymous")

	def get_id(self):
		return unicode(self.userID)

	def exists(self):
		return self.db_connection.userExists(self.userID)


class sql:

	def __init__(self):
		self.connection = pymysql.connect(host='localhost',
							user='root',
							password='',
							db='transactions_db',
							charset='utf8',
							cursorclass=pymysql.cursors.DictCursor)

	def addTransaction(self, userID, value, originSeed, destinationAddress, timestamp):
		with self.connection.cursor() as cursor:
			# Create a new record
			sql = "INSERT INTO `transactions` (`userID`, `value`, `origin_seed`, `destination_address`, `timestamp`) VALUES (%s, %s, %s, %s, %s)"
			cursor.execute(sql, (userID, value, originSeed, destinationAddress, timestamp))
		self.connection.commit()

	def userTransactionHistory(self, userID):
		with self.connection.cursor() as cursor:
		# Read a single record
			sql = "SELECT `userID`, `value`, `origin_seed`, `destination_address`, `timestamp` FROM `transactions` WHERE `userID`=%s"
			cursor.execute(sql, (userID))
			result = cursor.fetchall()
		return result

	def userCurrentBalance(self, userID):
		with self.connection.cursor() as cursor:

			sql = "SELECT `timestamp` FROM `transactions` WHERE `userID`=%s"
			cursor.execute(sql, (userID,))
			result = cursor.fetchone()
		self.connection.commit()
		return result

	def newUserAccount(self, userID, identifier, password_hash, email, seed, is_authenticated, is_active):
		if password_hash == "" and email == "":
			is_anonymous = True
		else:
			is_anonymous = False

		with self.connection.cursor() as cursor:
			sql = "INSERT INTO `users` (`userID`, `identifier`, `password_hash`, `email`, `seed`, `is_authenticated`, `is_active`, `is_anonymous` ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			cursor.execute(sql, (userID, identifier, password_hash, email, seed, is_authenticated, is_active, is_anonymous))
		self.connection.commit()

	"""def updateUserAccount(self, userID, identifier, password_hash, email, seed, is_authenticated, is_active, is_authenticated, is_active, is_anonymous):
		if password_hash == "" or email == "":
			is_anonymous = True
		else:
			is_anonymous = False

		with self.connection.cursor() as cursor:
		
			oldkeyList = list([userID, identifier, password_hash, email, seed, is_authenticated, is_active, is_anonymous])
			newKeyList = []
			for key in keyList:
				 placeholder = "{}=".format(key) + "%({})s".format(key)
				 newKeyList.extend([placeholder])
			val_list = ",".join(key_list)
			sql = "UPDATE `{table}` SET {values} WHERE `userID`= %(userID)s;".format(table="users", values=val_list)
			cursor.execute(sql)
			self.connection.commit()
		"""


	def getPasswordHash(self, userID):
		with self.connection.cursor() as cursor:

			sql = "SELECT `password_hash` FROM `users` WHERE `userID`=%s"
			cursor.execute(sql, ([userID]))
			result = cursor.fetchone()
		return str(result['password_hash'])

	def updateProperty(self, userID, prop, value):
		with self.connection.cursor() as cursor:
			sql = "UPDATE users set %s = %s WHERE userID = %s"
			print(sql)
			cursor.execute(sql, ( prop, value, userID,))
			self.connection.commit()

	def selectProperty(self, userID, prop):
		with self.connection.cursor() as cursor:

			sql = "SELECT " + str(prop) + " FROM users WHERE userID=%s"
			cursor.execute(sql, [userID, ] )
			result = cursor.fetchone()
		return str(result[prop])

	def userExists(self, userID):
		with self.connection.cursor() as cursor:

			sql = "SELECT userID FROM users WHERE userID=%s"
			cursor.execute(sql, [userID, ])
			msg = cursor.fetchone()
		if not msg:
			return 0
		return 1

	def emailTaken(self, email):
		with self.connection.cursor() as cursor:

			sql = "SELECT email FROM users WHERE email=%s"
			cursor.execute(sql, ([email, ] ))
			msg = cursor.fetchone()
		if not msg:
			return 0
		return 1

class SendIotaForm(FlaskForm):
	userID = StringField('User id:', validators=[InputRequired(), Length(min=6, max=24)])
	value = StringField('Value:', validators=[InputRequired()])
	time = StringField('Time:', validators=[InputRequired()])
	address = StringField('Address:', validators=[InputRequired(), Length(min=81, max=81)])
	num_payments = StringField('Numer of payments:', validators=[Length(max=3)])
	si = SelectField(u'si', choices=[('i', 'iota'), ('ki', 'kiota'), ('Mi', 'Miota')], validators=[InputRequired()])

class LoginForm(FlaskForm):
	userID = StringField('User id:', validators=[InputRequired(), Length(min=6, max=24)])
	password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('Remember me')

class SignupForm(FlaskForm):
	userID = StringField('User id:', validators=[InputRequired(), Length(min=6, max=24)])
	email = StringField('Email:', validators=[Email(message='Invalid Email'), Length(max=80)])
	password = PasswordField('Password:', validators=[InputRequired(), Length(min=8, max=80)])
	confirm = PasswordField('Confirm password:', validators=[InputRequired(), Length(min=8, max=80)])


class Utils:
	def redirect_back(self, endpoint, **values):
		target = request.form['next']
		if not target or not self.is_safe_url(target):
			target = url_for(endpoint, **values)
		return redirect(target)

	def get_redirect_target(self):
		for target in request.values.get('next'), request.referrer:
			if not target:
				continue
			if self.is_safe_url(target):
				return target

	def is_safe_url(self, target):
		ref_url = urlparse(request.host_url)
		test_url = urlparse(urljoin(request.host_url, target))
		return test_url.scheme in ('http', 'https') and \
		   ref_url.netloc == test_url.netloc


