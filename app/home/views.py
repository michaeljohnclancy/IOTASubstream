from flask import render_template, flash, redirect, url_for, request
import flask
from flask_login import current_user
import threading
import uuid
from time import sleep, time
from iota import *

from . import home
from app.forms import SendIotaForm
from app.models import Transaction, db

import qrcode
import cStringIO

@home.route('/', methods=['GET', 'POST'])
def index():
	form = SendIotaForm()

	if form.validate_on_submit():

		form.send_payment()

		return redirect(url_for('member.yourStats'))
		

	return render_template('/home/index.html', form=form)


@home.route('/topup', methods=['GET', 'POST'])
def topupAccount():

	newAddress = str(current_user.iota_api().get_new_addresses(count=1)['addresses'][0])
	return render_template('/home/topup.html', new_address = newAddress)


@home.route('/signup_success', methods=['GET'])
def signup_success():

	
	return render_template('/home/signup_success.html', title="Signup Success")

def random_qr(s):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(s)
    qr.make(fit=True)
    img = qr.make_image()
    return img

@home.route('/get_qr', methods=['GET'])
def get_qr():
    img_buf = cStringIO.StringIO()
    img = random_qr(request.args.get('s'))
    img.save(img_buf)
    img_buf.seek(0)
    return flask.send_file(img_buf, mimetype='image/png')
