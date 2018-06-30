from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user
from random import SystemRandom
import uuid
import threading

from . import auth
from ..forms import LoginForm, SignupForm
from .. import db, oauth
from ..models import User, Transaction
from ..tasks import loop

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
		flash('You have successfully registered! You may now login.')

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
@login_required
def json_login():
    data = [{'id':0, 'name':'Simple Payment', 'details':'Details...'},{'id':1, 'name':'Flash Payments', 'details':'Details n.2'}]
    return render_template('/auth/json_login.html', title='JSON Login', company_name="Netflix", options=data)

@auth.route('/AJAX_request', methods=['POST'])
@login_required
def ajax_request():
    return render_template('/auth/basic_payment.html', title='Basic Payment', iota=1, time=1)

@auth.route('/auth/authorize', methods=['GET', 'POST'])
@login_required
@oauth.authorize_handler
def authorize(*args, **kwargs):
    if request.method == 'GET':
        client_id = kwargs.get('client_id')
        client = Client.query.filter_by(client_id=client_id).first()
        kwargs['client'] = client
        return render_template('oauthorize.html', **kwargs)

    confirm = request.form.get('confirm', 'no')
    return confirm == 'yes'

@auth.route('/auth/token')
@oauth.token_handler
def access_token():
    return None

