from flask import Flask, render_template, request
from iota import *
from time import *
import thread
import time
import flask_login as fl


from modules import User, sql

app = Flask(__name__)
LoginManager = fl.LoginManager(app)
LoginManager.login_view = "login"
LoginManager.login_message = "Please login"

@LoginManager.user_loader
def load_user(user_id):
    return User.get(user_id)

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

		newUser = User(_userID)
		newUser.setNode("http://node02.iotatoken.nl:14265")
		
		thread.start_new_thread(newUser.iota_send, (_address, _value, _time, _numPayments)) 
		

	return render_template('index.html')

@app.route("/signup",  methods=['GET','POST'])
def userSignup():
	if request.method == 'POST':
		_userID = str(request.form['userID'])
		newUser = User(_userID)
		newUser.setNode("http://node02.iotatoken.nl:14265")

		if str(request.form['password']) == str(request.form['confirm']):
			_password_hash = newUser.password_encrypt(str(request.form['password']))
		
			_email = str(request.form['email'])
			newUser.commitUserToDB(_email, _password_hash)
			newUser.set_is_active(True) #Should wait until email is confirmed in the future, set to 1 in database
			newUser.set_is_anonymous(False)

			print("Done")
	return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Here we use a class of some kind to represent and validate our
    # client-side form data. For example, WTForms is a library that will
    # handle this for us, and we use a custom LoginForm to validate.
	if request.method == 'POST':
		_userID = str(request.form['userID'])
		_password = str(request.form['password'])
		user = User(_userID)
		if (user.password_verify(_password, user.get_password_hash())):
			user.setNode("http://node02.iotatoken.nl:14265")
			user.set_is_authenticated(True)
			
			#Flask login logs in user
			login_user(user)
			print("Hello, %s" % fl.current_user )
			return flask.redirect(next or flask.url_for('index'))
	return flask.render_template('login.html', form=form)




if __name__ == "__main__":
    app.run()
