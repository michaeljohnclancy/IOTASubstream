from flask import flash, redirect, render_template, url_for
from flask_login import login_required, login_user, logout_user, current_user
from random import SystemRandom
import uuid

from . import auth
from ..forms import LoginForm, SignupForm
from .. import db
from ..models import User

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

		user = User.query.filter_by(id=form.id.data).first()

		if user is not None and user.verify_password(form.password.data):
			login_user(user)
			flash("Welcome, %s" % current_user.id)

			return redirect(url_for('home.sendiota'))

		else:
			flash('Invalid email or password.')

	return render_template('/auth/login.html', form=form, title='Login')


@auth.route('/logout')
@login_required
def logout():
	
	logout_user()
	flash('You have successfully been logged out.')

	return redirect(url_for('auth.login'))



