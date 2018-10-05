from flask import flash, redirect, render_template, url_for, request, jsonify
from flask_login import login_required, logout_user, current_user

import threading

from werkzeug.security import gen_salt
from authlib.flask.oauth2 import current_token
from authlib.specs.rfc6749 import OAuth2Error
from authlib.common.urls import url_encode
import json

#Local
from . import auth
from app.forms import LoginForm, UserForm, ConfirmForm, ClientForm
from app.models import User, Transaction, db, Client, PaymentAgreement
from app.oauth2 import authorization, query_client

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('home.index'))
	userForm = UserForm()

	if userForm.validate_on_submit():
		userForm.save()
		flash('Account creation successful.')
		return redirect(url_for('auth.login'))

	return render_template('/auth/signup.html', form=userForm, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home.index'))
	loginForm = LoginForm()

	if loginForm.validate_on_submit():
		if not loginForm.login():
			return redirect(url_for('auth.login'))
		return redirect(url_for('home.index'))

	return render_template('/auth/login.html', form=loginForm, title='Login')

@auth.route('/logout')
@login_required
def logout():
	
	logout_user()
	flash('You have successfully been logged out.')

	return redirect(url_for('auth.login'))

@auth.route('/json_login')
def json_login():
	data = [{'id':0, 'name':'Simple Payment', 'details':'Details...'},{'id':1, 'name':'Flash Payments', 'details':'Details n.2'}]
	return render_template('/auth/json_login.html', title='JSON Login', company_name="Netflix", options=data)

@auth.route('/AJAX_request', methods=['POST'])
def ajax_request():
	return render_template('/auth/authorize.html', title='Basic Payment', iota=1, time=1)


@auth.route('/auth/authorize', methods=['GET', 'POST'])
def authorize():
	#Must provide valid OAuth request and the client's 
	#active payment_address and proposed payment_amount.

	#In get request, should be:
	#payment_address, payment_amount, payment_time
	#payment_time is the time between payment requests.

	#This information gets passed to the PaymentAgreement object on creation,
	#and is valid until the Token is destroyed. (TODO destroy agreement on token deletion.)

	#Alternatively, a website may request payment preauthorization here.


	if current_user.is_authenticated:
		form = ConfirmForm()
	else:
		form = LoginForm()


	if form.validate_on_submit():
		if current_user.is_authenticated:
			if form.confirm.data:

				grant_user = current_user

				try:	
					#Need to sanitize the request.args inputs before putting in DB
					payment_agreement = PaymentAgreement(
						payment_address=request.args['payment_address'],
						payment_amount=request.args['payment_amount'],
						payment_time=request.args['payment_time'],
						user_id=grant_user.id,
						client_id=request.args['client_id']
						)


					db.session.add(payment_agreement)
				except:
					#Need to add errors
					print("Error adding new payment agreement")

			else:
				grant_user = None
		else:
			form.login()
			if current_user.is_authenticated:
				grant_user = current_user

				payment_agreement = PaymentAgreement(
					payment_address=request.args['payment_address'],
					payment_amount=request.args['payment_amount'],
					payment_time=request.args['payment_time'],
					user_id=grant_user.id,
					client_id=request.args['client_id']
					)

				db.session.add(payment_agreement)
			else:
				grant_user = None

		db.session.commit()
		return authorization.create_authorization_response(grant_user=grant_user)
	
	try:
		grant = authorization.validate_consent_request(end_user=current_user)
	except OAuth2Error as error:
		# TODO: add an error page
		payload = dict(error.get_body())
		return jsonify(payload), error.status_code

	client = Client.query.filter_by(client_id=request.args['client_id']).first()
	return render_template(
		'auth/authorize.html',
		grant=grant,
		client=client,
		form=form,
		payment_amount=request.args['payment_amount'],
		payment_address=request.args['payment_address'],
		payment_time=request.args['payment_time']
	)


@auth.route('/auth/create_client', methods=('GET', 'POST'))
@login_required
def create_client():
	form = ClientForm()
	if form.validate_on_submit():
		form.save(current_user)
		return redirect(url_for('home.index'))
	return render_template('auth/create_client.html', form=form)

@auth.route('/auth/token', methods=['POST'])
def issue_token():
	try:
		return authorization.create_token_response()
	except OAuth2Error as error:
		# TODO: add an error page
		payload = dict(error.get_body())
		return jsonify(payload), error.status_code

@auth.route('/auth/revoke', methods=['POST'])
def revoke_token():
	return authorization.create_endpoint_response('revocation')