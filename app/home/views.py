from flask import render_template
from flask_login import current_user

from ..forms import SendIotaForm
from ..models import is_safe_url
from . import home

@home.route('/')
def sendiota():
	form = SendIotaForm()



	if form.validate_on_submit():

		if form.si.data=='ki':
			_value *= 1e3
		elif form.si.data=='Mi':
			_value *= 1e6
		
		thread.start_new_thread(current_user.iota_send, (form.address.data, form.value.data, form.time.data, form.num_payments.data)) 

		return redirect(url_for('success'))
		

	return render_template('/home/index.html', form=form)