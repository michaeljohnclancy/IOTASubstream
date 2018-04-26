import pymysql.cursors
from passlib.context import CryptContext
from random import SystemRandom
import pymysql.cursors
from iota import *
import flask_login as fl
import flask
from time import *

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

		if self.user_exists():
			self.seed = self.db_connection.selectProperty(self.userID, "seed")
			self.is_authenticated = self.get_is_authenticated()
			self.is_active = self.get_is_active() #Need to change to false and only make true when email is confirmed
			self.is_anonymous = self.get_is_anonymous()
		#Generates random seed
		else:
			alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
			generator = SystemRandom()
			self.seed = u''.join(generator.choice(alphabet) for _ in range(81))

			self.is_authenticated = False
			self.is_active = True #Need to change to false and only make true when email is confirmed
			self.is_anonymous = True

		self.db_connection.newUserAccount(self.userID, self.seed)
		self.api = Iota(self.node, self.seed)

		#Required for Flask Login
		self.is_authenticated = False
		self.is_active = True #Need to change to false and only make true when email is confirmed
		self.is_anonymous = True


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
			self.db_connection.addTransaction(self.userID, value, self.seed, target, tx.timestamp)
			self.db_connection.newUserAccount(self.userID, self.seed)
			
			print("Sent")
			sleep(time)
			i += 1

	def newAddress(self):
		return self.api.get_new_addresses()['addresses'][0]

	def transactionHistory(self):
		return self.db_connection.userTransactionHistory(self.userID)

	def commitUserToDB(self, email, password_hash):
		self.db_connection.newUserAccount(self.userID, self.seed, password_hash, email)

	def password_encrypt(self, password):
		return self.pwd_context.encrypt(password)

	def password_verify(self, password, hashed):
		return self.pwd_context.verify(password, hashed)

	def get_password_hash(self):
		return sql().getPasswordHash(self.userID)

	def set_is_authenticated(self, bool_val):
		updateProperty(self.userID, 'is_authenticated', bool_val)
		self.is_authenticated = bool_val

	def set_is_active(self, bool_val):
		self.db_connection.updateProperty(self.userID, 'is_active', bool_val)
		self.is_active = bool_val
	
	def set_is_anonymous(self, bool_val):
		updateProperty(self.userID, 'is_anonymous', bool_val)
		self.is_anonymous = bool_val

	def get_is_authenticated():
		return selectProperty(self.userID, "is_authenticated")

	def get_is_active():
		return selectProperty(self.userID, "is_active")

	def get_is_anonymous():
		return selectProperty(self.userID, "is_anonymous")

	def get_id(self):
		return unicode(self.userID)

	def user_exists(self):
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

	def newUserAccount(self, userID, seed, password_hash="", email=""):
		if password_hash == "" or email == "":
			is_anonymous = True
		else:
			is_anonymous = False

		with self.connection.cursor() as cursor:
			sql = "INSERT INTO `users` (`userID`, `password_hash`, `email`, `seed`, `is_anonymous` ) VALUES (%s, %s, %s, %s, %s)"
			cursor.execute(sql, (userID, password_hash, email, seed, is_anonymous))
		self.connection.commit()

	def getPasswordHash(self, userID):
		with self.connection.cursor() as cursor:

			sql = "SELECT `password_hash` FROM `users` WHERE `userID`=%s"
			cursor.execute(sql, ([userID]))
			result = cursor.fetchone()
		return result

	def updateProperty(self, userID, prop, value):
		with self.connection.cursor() as cursor:
			sql = "UPDATE users set %s = %s WHERE userID = %s"
			print(sql)
			cursor.execute(sql, ( prop, value, userID,))
			self.connection.commit()

	def selectProperty(self, userID, prop):
		with self.connection.cursor() as cursor:

			sql = "SELECT %s FROM users WHERE `userID`=%s"
			cursor.execute(sql, (prop, userID, ))
			result = cursor.fetchone()
		return str(result)

	def userExists(self, userID):
		with self.connection.cursor() as cursor:

			sql = "SELECT EXISTS(SELECT 1. FROM users WHERE. userID=%s"
			cursor.execute(sql, ([userID] ))
			result = cursor.fetchone()
		return bool(result)










