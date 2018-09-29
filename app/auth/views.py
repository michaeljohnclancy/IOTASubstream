from flask import flash, redirect, render_template, url_for, request
from flask_login import login_required, login_user, logout_user, current_user
from random import SystemRandom
import uuid
import threading
from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from authlib.specs.rfc6749 import OAuth2Error
from authlib.common.urls import url_encode
import json

#Local
from . import auth
from app.forms import LoginForm, SignupForm, SubmitForm
from app.models import User, Transaction, db, Client
from app.tasks import loop
from app.oauth2 import require_oauth, authorization

@auth.route('/signup', methods=['GET', 'POST'])
def signup():

	form = SignupForm()

	if form.validate_on_submit():
		alphabet = u'9ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		generator = SystemRandom()
		random_seed = u''.join(generator.choice(alphabet) for _ in range(81))

		user = User(id=form.id.data,
				identifier=str(uuid.uuid4()),
				password=form.password.data,
				email=form.email.data,
				seed=random_seed
				)

		db.session.add(user)
		db.session.commit()

		return redirect(url_for('auth.login'))


	return render_template('/auth/signup.html', form=form, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():

	form = LoginForm()

	if form.validate_on_submit():

		user = User.query.filter_by(id=str(form.id.data)).first()

		if user is not None and user.verify_password(form.password.data):
			login_user(user)


			return redirect(url_for('home.index'))

		else:
			flash('Invalid email or password.')

	return render_template('/auth/login.html', form=form, title='Login')

@auth.route('/logout')
@login_required
def logout():
	
	logout_user()
	flash('You have successfully been logged out.')

	return redirect(url_for('auth.login'))

@auth.route('/json_login')
#@require_oauth('payment_gate')
def json_login():
	data = [{'id':0, 'name':'Simple Payment', 'details':'Details...'},{'id':1, 'name':'Flash Payments', 'details':'Details n.2'}]
	return render_template('/auth/json_login.html', title='JSON Login', company_name="Netflix", options=data)



@auth.route('/AJAX_request', methods=['POST'])
@require_oauth('payment_gate')
def ajax_request():
	return render_template('/auth/basic_payment.html', title='Basic Payment', iota=1, time=1)


@auth.route('/auth/authorize', methods=['GET', 'POST'])
def authorize():
	if current_user:
		form = SubmitForm()
	else:
		form = LoginForm()
		
		user = User.query.filter_by(id=str(form.id.data)).first()

		if user is not None and user.verify_password(form.password.data):
			login_user(user)


	if request.method == 'GET':
		try:
			grant = authorization.validate_consent_request(end_user=current_user)
			
			return render_template(
			'auth/authorize.html',
			#grant=grant,
			user=current_user,
			)
		except OAuth2Error as error:
			return url_encode(error.get_body())
	submitted = request.form['submit']
	if submitted:
		# granted by resource owner
		return authorization.create_authorization_response(current_user)
	# denied by resource owner
	return authorization.create_authorization_response(None)

@auth.route('/auth/create_client', methods=('GET', 'POST'))
@login_required
def create_client():
	user = current_user
	if not user:
		return redirect('/')
	if request.method == 'GET':
		return render_template('auth/create_client.html')
	client = Client(**request.form.to_dict(flat=True))
	client.user_id = user.id
	client.client_id = gen_salt(24)
	if client.token_endpoint_auth_method == 'none':
		client.client_secret = ''
	else:
		client.client_secret = gen_salt(48)
	db.session.add(client)
	db.session.commit()
	return redirect('/')

@auth.route('/auth/token', methods=['POST'])
def issue_token():
	return authorization.create_token_response()


@auth.route('/auth/revoke', methods=['POST'])
def revoke_token():
	return authorization.create_endpoint_response('revocation')

