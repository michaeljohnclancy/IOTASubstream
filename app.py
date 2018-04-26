from flask import Flask, render_template, request
from iota import *
from time import *
import thread
import time

from modules import User, sql

app = Flask(__name__)

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/sendiota", methods=['GET','POST'])
def sendIota():
	if request.form['submit']:
		_userID = str(request.form['userID'])
		_value = int(request.form['value'])
		_si = request.form['si']

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

@app.route("/signup",  methods=['GET','POST'])
def userSignup():
	if request.method == 'POST':
		_userID = str(request.form['userID'])
		newUser = User("http://node02.iotatoken.nl:14265", _userID)

		if str(request.form['password']) == str(request.form['confirm']):
			_password_hash = newUser.password_encrypt(str(request.form['password']))
		
			_email = str(request.form['email'])
			newUser.commitUserToDB(_email, _password_hash)
			print("Done")
	return render_template('signup.html')




if __name__ == "__main__":
    app.run()
