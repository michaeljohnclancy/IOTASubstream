import pymysql.cursors

class mysql_connect:

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

	def userTransactionHistory(self, userID):
		with connection.cursor() as cursor:
		# Read a single record
			sql = "SELECT `userID`, `value`, `origin_seed`, `destination_address`, `timestamp` FROM `transactions` WHERE `userID`=%s"
			cursor.execute(sql, (userID))
			result = cursor.fetchone()
		return result