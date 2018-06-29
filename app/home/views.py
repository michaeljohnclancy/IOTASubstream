from flask import render_template, flash, redirect, url_for
from flask_login import current_user
import threading
import uuid
from time import sleep, time
from iota import *


from ..forms import SendIotaForm
from .. import tasks
from . import home
from ..models import Transaction
from .. import db

@home.route('/', methods=['GET', 'POST'])
def index():
	form = SendIotaForm()

	if form.validate_on_submit():

		if form.si.data=='ki':
			_value *= 1e3
		elif form.si.data=='Mi':
			_value *= 1e6

		tasks.sendiota(current_user, form.value.data, form.target.data, form.time.data, form.num_payments.data)

		return redirect(url_for('member.yourStats'))
		

	return render_template('/home/index.html', form=form)


@home.route('/topup', methods=['GET', 'POST'])
def topupAccount():

	newAddress = str(current_user.api().get_new_addresses(count=1)['addresses'][0])
	return render_template('/home/topup.html', new_address = newAddress)


@home.route('/signup_success', methods=['GET'])
def signup_success():

	
	return render_template('/home/signup_success.html', title="Signup Success")