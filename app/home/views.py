from flask import render_template, flash, redirect, url_for
from flask_login import current_user
import threading
import uuid
from time import sleep, time
from iota import *


from ..forms import SendIotaForm
from .. import iota_funcs
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

		iota_funcs.sendiota(form.value.data, form.target.data, form.time.data, form.num_payments.data)

		#thread = threading.Thread(target=sendiota, args=(form.value.data, form.target.data, form.time.data, form.num_payments.data))
		#thread.daemon = True
		#thread.start()


		return redirect(url_for('member.yourStats'))
		

	return render_template('/home/index.html', form=form)

def sendiota(value, target, interval, numPayments):

	i = 0

	while (i <= int(numPayments)-1):
		tx = ProposedTransaction(address=Address(str(target)), value=int(value), tag=None, message=TryteString.from_string(current_user.identifier))
		thread = threading.Thread(target=current_user.api().send_transfer, kwargs = {'depth': 100, 'transfers':[tx]})
		thread.daemon = True
		thread.start()

		current_time = time()
		transaction = Transaction(transaction_id=str(uuid.uuid4()),
		identifier=current_user.identifier,
			value=value,
			target=target,
			timestamp=tx.timestamp)

		try:
			db.session.add(transaction)
		except Exception, e:
			db.session.rollback()
			print str(e)
		time_taken = time() - current_time

		sleep(float(abs(float(interval)-time_taken)))
		i += 1
	
	db.session.commit()

@home.route('/topup', methods=['GET', 'POST'])
def topupAccount():

	newAddress = str(current_user.api().get_new_addresses(count=1)['addresses'][0])
	return render_template('/home/topup.html', new_address = newAddress)





@home.route('/signup_success', methods=['GET'])
def signup_success():

	
	return render_template('/home/signup_success.html', title="Signup Success")