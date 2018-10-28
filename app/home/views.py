from flask import render_template, flash, redirect, url_for, request
import flask
from flask_login import current_user
import threading
import uuid
from time import sleep, time
from iota import *
import os
import base64

from . import home

from extensions import db
from app.models import Transaction

import qrcode
import cStringIO

@home.route('/', methods=['GET', 'POST'])
def index():
	companies = os.listdir("app/static/banners")

	return render_template('/home/home.html', companies=companies)


@home.route('/topup', methods=['GET', 'POST'])
def topupAccount():
	newAddress = str(current_user.iota_api.get_new_addresses(count=1)['addresses'][0].with_valid_checksum())

	return render_template('/home/topup.html', new_address = newAddress)


@home.route('/signup_success', methods=['GET'])
def signup_success():
	return render_template('/home/signup_success.html', title="Signup Success")
