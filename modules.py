import pymysql.cursors
from passlib.context import CryptContext
from random import SystemRandom
import pymysql.cursors
from iota import *

class User:

	"""
	User Attributes:
		node
		userID
		seed
		api

	User Methods:
		iota_send()
		new_address()
		transactionHistory()
	"""
	node = ""
	userID = ""

	def __init__(self, node, userID):
		#Starts database connection
		self.db_connection = sql()


		self.node = node
		self.userID = userID

		#Generates random seed
		alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		generator = SystemRandom()
		self.seed = u''.join(generator.choice(alphabet) for _ in range(81))

		#Password Encryption
		self.pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
        )

		#Creates API instance
		self.api = Iota(node, self.seed)

	def iota_send(self, target, value, time=0, numPayments=1):
		i = 0
		while (i <= numPayments-1):
			tx = ProposedTransaction(address=Address(target), value=value, tag=None, message=TryteString.from_string(self.userID))
			self.api.send_transfer(depth = 100, transfers=[tx])
			
			#Logs transaction to DB
			self.db_connection.addTransaction(self.userID, value, self.seed, target, tx.timestamp)
			
			print("Sent")
			sleep(time)
			i += 1

	def newAddress(self):
		return self.api.get_new_addresses()['addresses'][0]

	def transactionHistory(self):
		return self.db_connection.userTransactionHistory(self.userID)

	def commitUserToDB(self, email, password_hash):
		self.db_connection.newUserAccount(self.userID, password_hash, email, self.seed)

	def password_encrypt(self, password):
		return self.pwd_context.encrypt(password)

	def password_verify(self, password, hashed):
		return self.pwd_context.verify(password, hashed)


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
			result = cursor.fetchone()
		return result

	def userCurrentBalance(self, userID):
		with self.connection.cursor() as cursor:

			sql = "SELECT `timestamp` FROM `transactions` WHERE `userID`=%s"
			cursor.execute(sql, (userID,))
			result = cursor.fetchone()
			print(result)
		return result

	def newUserAccount(self, userID, password_hash, email, seed):
		with self.connection.cursor() as cursor:
			sql = "INSERT INTO `users` (`userID`, `password_hash`, `email`, `seed`, `balance`, `email_confirmed`, `timestamp` ) VALUES (%s, %s, %s, %s, %s, %s, %s)"
			cursor.execute(sql, (userID, password_hash, email, seed, 0, 0, 0))
		self.connection.commit()