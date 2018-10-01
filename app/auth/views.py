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
from app.models import User, Transaction, db, Client
from app.oauth2 import authorization, query_client

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(url_for('home.index'))
	userForm = UserForm()

	if userForm.validate_on_submit():
		
		userForm.save()

		return redirect(url_for('auth.login'))

	return render_template('/auth/signup.html', form=userForm, title='Register')


@auth.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home.index'))
	loginForm = LoginForm()

	if loginForm.validate_on_submit():

		loginForm.login()

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
	if current_user:
		form = ConfirmForm()
	else:
		form = LoginForm()

	if form.validate_on_submit():
		if form.confirm.data:
			grant_user = current_user
		else:
			grant_user = None
		return authorization.create_authorization_response(grant_user=grant_user)
	
	try:
		if current_user:
			grant = authorization.validate_consent_request(end_user=current_user)
	except OAuth2Error as error:
		# TODO: add an error page
		payload = dict(error.get_body())
		return jsonify(payload), error.status_code

	client = query_client(request.args['client_id'])
	return render_template(
		'auth/authorize.html',
		grant=grant,
		client=client,
		form=form,
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