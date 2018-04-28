from iota import *
from time import *
import thread
import time

from flask import *
from flask_bootstrap import Bootstrap
import flask_login
from flask_security import login_required 



from modules import User, sql, LoginForm, SignupForm, SendIotaForm, Utils
from input_checks import valid_password

app = Flask(__name__)

Bootstrap(app)
LoginManager = flask_login.LoginManager(app)
LoginManager.login_view = "login"

@LoginManager.user_loader
def load_user(userID):
	new_user = User(userID)
	if  new_user.exists():
		return new_user
	else:
		return None

@app.route("/", methods=['GET', 'POST'])
def main():
	form = SendIotaForm()

	if form.validate_on_submit():

		if form.si.data=='ki':
			_value *= 1e3
		elif form.si.data=='Mi':
			_value *= 1e6

		newUser = User(form.userID.data)
		
		thread.start_new_thread(newUser.iota_send, (form.address.data, form.value.data, form.time.data, form.num_payments.data)) 

		flash("Success!")
		

	return render_template('index.html', form=form, next=next)



@app.route("/signup",  methods=['GET','POST'])
def userSignup():
	
	form = SignupForm()
	utils = Utils()
	next = request.args.get('next')
	

	if form.validate_on_submit():
		user = User(form.userID.data)

		passwords_match = (form.password.data == form.confirm.data)

		if not user.exists():
			if passwords_match:
				_password_hash = user.password_encrypt(form.password.data)
				user.set_email(form.email.data)
				user.set_password_hash(_password_hash)

				user.registerUser()
				flask_login.login_user(user)

				if not utils.is_safe_url(next):
					return abort(400)

				return redirect(next or url_for('success'))
			else:
				flash("Passwords don't match!")
				print("Pass bad")
		else:
			flash("UserID taken!")
			print("user bad")

	return render_template('signup.html', form=form, next=next)

@app.route('/login', methods=['GET', 'POST'])

def login():

	form = LoginForm()
	utils = Utils()
	next = request.args.get('next')
	
	if form.validate_on_submit():
		user = User(form.userID.data)

		if user.exists():
			if user.password_verify(form.password.data, user.get_password_hash()):
			#Flask login logs in user
				flask_login.login_user(user)
				print(flask_login.current_user.userID)

				if not utils.is_safe_url(next):
					return abort(400)
				print("Redirecting...")
				return redirect(next or url_for('viewStats'))

		else:
			print("Username or password incorrect! Try again.")
			flash("Username or password incorrect! Try again.")
		

	return render_template('login.html', form=form, next=next)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():

	next = request.args.get('next')
	
	flask_login.logout_user()
		
	return redirect(next or url_for('main'))

@app.route('/yourstats', methods=['GET', 'POST'])
@login_required
def viewStats():
	print(flask_login.current_user.transactionHistory())
	return render_template('yourstats.html')

@app.route('/signup_success', methods=['GET', 'POST'])
@login_required
def success():
	return render_template('signup_success.html')


app.secret_key = ""


if __name__ == "__main__":
	app.run()
