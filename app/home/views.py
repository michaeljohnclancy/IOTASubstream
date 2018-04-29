from flask import render_template, flash, redirect, url_for
from flask_login import current_user
import thread


from ..forms import SendIotaForm
from . import home

@home.route('/', methods=['GET', 'POST'])
def sendiota():
	form = SendIotaForm()

	if form.validate_on_submit():

		if form.si.data=='ki':
			_value *= 1e3
		elif form.si.data=='Mi':
			_value *= 1e6
		
		thread.start_new_thread(current_user.iota_send, (str(form.address.data), int(form.value.data), int(form.time.data), int(form.num_payments.data))) 

				

		return redirect(url_for('member.yourStats'))
		

	return render_template('/home/index.html', form=form)


@home.route('/signup_success', methods=['GET'])
def signup_success():

	
	return render_template('/home/signup_success.html', title="Signup Success")