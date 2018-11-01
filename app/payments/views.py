from flask_login import current_user
from app.models import PaymentAgreement
from app.oauth2 import require_oauth
from app.forms import IotaPaymentForm
from app.tasks import execute_agreement
from flask import request, jsonify
from celery.task.control import revoke
from authlib.flask.oauth2 import current_token

from extensions import db

from . import payments

@payments.route('/payments/info', methods=['GET'])
@require_oauth('payment_gate')
def info():
	agreement = current_token.payment_agreement
	return jsonify(agreement.info())


@payments.route('/payments/activateAgreement', methods=['GET'])
@require_oauth('payment_gate')
def activateAgreement():
	agreement = current_token.payment_agreement
	agreement.is_active = 1
	db.session.commit()
	
	payment_task = execute_agreement.apply_async((current_token.user_id, current_token.client_id,),)
	
	if not payment_task:
		jsonify({'Status':'Payment agreement could not be started.'}), 404

	return jsonify({'Status':'Payment agreement activated'}), 200


@payments.route('/payments/pauseAgreement', methods=['GET'])
@require_oauth('payment_gate')
def pauseAgreement():

	try:
		agreement = current_token.payment_agreement
		agreement.is_active = 0
		db.session.commit()
	except:
		return jsonify({'Status':'Error'})

	return jsonify({'Status':'Agreement paused.'})



@payments.route('/payments/singlePayment', methods=['POST'])
@require_oauth('payment_gate')
def singlePayment():
	#Request a new payment be sent
	try:
		current_token.payment_agreement.send_payment()
	except:
		#Add Error handling
		return jsonify({'Status':'Error'}), 404


	return jsonify(transaction), 200




	




