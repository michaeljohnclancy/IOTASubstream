import pymysql.cursors
from passlib.context import CryptContext

def mysql_connect():

	def __init__(self):
		self.connection = pymysql.connect(host='localhost',
							user='root',
							password='Playbook8003',
							db='transactions_db',
							charset='utf8',
							cursorclass=pymysql.cursors.DictCursor)
		
		self.pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
        )

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

	def password_encrypt(password):
		return pwd_context.encrypt(password)

	def password_decrypt(password, hashed)
		return pwd_context.verify(password, hashed)

	def newUserAccount(self, userID, password_hash, email, seed):
		with self.connection.cursor() as cursor:
			sql = "INSERT INTO `users` (`userID`, `password_hash`, `email`, `seed`) VALUES (%s, %s, %s, %s)"
			cursor.execute(sql, (userID, password_hash, email, seed))
		self.connection.commit()