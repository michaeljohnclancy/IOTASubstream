from flask import render_template, flash, redirect, url_for
from flask_login import current_user
import threading
from iota import *
import uuid
from time import sleep


from ..forms import SendIotaForm
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

		sendiota(form.value.data, form.target.data, form.time.data, form.num_payments.data)

		#thread = threading.Thread(target=sendiota, args=(form.value.data, form.target.data, form.time.data, form.num_payments.data))
		#thread.daemon = True
		#thread.start()


		return redirect(url_for('member.yourStats'))
		

	return render_template('/home/index.html', form=form)

def sendiota(identifier, value, target, time, numPayments):
	api = Iota("http://iota-tangle.io:14265", current_user.seed)

	i = 0

	while (i <= int(numPayments)-1):
		tx = ProposedTransaction(address=Address(str(target)), value=int(value), tag=None, message=TryteString.from_string(current_user.identifier))
		api.send_transfer(depth = 100, transfers=[tx])

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

		sleep(float(form.time.data))
		i += 1
		db.session.commit()




@home.route('/signup_success', methods=['GET'])
def signup_success():

	
	return render_template('/home/signup_success.html', title="Signup Success")