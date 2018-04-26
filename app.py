from flask import Flask, render_template, request
from iota import *
from time import *
import thread
from random import SystemRandom
import time
import pymysql.cursors
import sql

app = Flask(__name__)

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
		self.db_connection = sql.mysql_connect()


		self.node = node
		self.userID = userID

		#Generates random seed
		alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		generator = SystemRandom()
		self.seed = u''.join(generator.choice(alphabet) for _ in range(81))

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

	def newAddress():
		return self.api.get_new_addresses()['addresses'][0]

	def transactionHistory():
		return self.db_connection.userTransactionHistory(self.userID)

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/sendiota", methods=['POST'])
def sendIota():
	if request.form['submit']:
		_userID = str(request.form['userID'])
		_value = int(request.form['value'])
                _si = int(request.form['si'])

                if _si=='ki':
                    _value *= 1e3
                elif _si=='Mi':
                    _value *= 1e6

		_time = int(request.form['time'])
		_address = str(request.form['address'])
		_numPayments = int(request.form['numPayments'])

		newUser = User("http://node02.iotatoken.nl:14265", _userID)
		
		thread.start_new_thread(newUser.iota_send, (_address, _value, _time, _numPayments)) 
		

	return render_template('index.html')

@app.route("/login",  methods=['GET','POST'])
def userLogin():
	



if __name__ == "__main__":
    app.run()
