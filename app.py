from flask import Flask, render_template, request
from iota import *
from time import *
import thread
from random import SystemRandom
import time

app = Flask(__name__)

class User:
	node = ""
	userID = ""

	def __init__(self, node, userID):
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
			print("Sent")
			sleep(time)
			i += 1

	def newAddress(self, amount = 0):
		 return self.api.get_new_addresses(amount)

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/sendiota", methods=['POST'])
def sendIota():
	if request.form['submit']:
		_userID = str(request.form['userID'])
		_value = int(request.form['value'])
		_time = int(request.form['time'])
		_address = str(request.form['address'])
		_numPayments = int(request.form['numPayments'])

		newUser = User("http://node02.iotatoken.nl:14265", _userID)
		
		thread.start_new_thread(newUser.iota_send, (_address, _value, _time, _numPayments)) 

	return render_template('index.html')



if __name__ == "__main__":
    app.run()