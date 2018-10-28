from flask_login import current_user
from . import payments
from app.models import PaymentAgreement
from app.oauth2 import require_oauth
from app.forms import IotaPaymentForm
from app.tasks import execute_agreement
from flask import request
from celery.task.control import revoke

from extensions import db

@payments.route('payments/activateAgreement', methods=['POST'])
@require_oauth('payment_gate')
def activateAgreement():
	try:
		user_id = request.oauth.user.user_id
		client_id = request.oauth.client_id

		payment_agreement = PaymentAgreement.query.filter_by(user_id=user_id, client_id=client_id).first()

		payment_agreement.is_active = 1
		execute_agreement(user_id, client_id)

		db.session.commit()

	except:
		return jsonify({'Status':'Error'}), 404

	return jsonify({'Status':'Success'}), 200

@payments.route('payments/pauseAgreement', methods=['POST'])
@require_oauth('payment_gate')
def pauseAgreement():
	user_id = request.oauth.user.user_id
	client_id = request.oauth.client_id

	try:
		payment_agreement = PaymentAgreement.query.filter_by(user_id=user_id, client_id=client_id).first()
		revoke(payment_agreement.celery_id, terminate=True)
		payment_agreement.is_active = 0
		db.session.commit()
		return jsonify({'Status':'Revocation successful.'}), 200
	except:
		return jsonify({'Status':'Error'}), 404



@payments.route('payments/single_payment', methods=['POST'])
@require_oauth('payment_gate')
def singlePayment():
	#Request a new payment be sent
	
	user_id = request.oauth.user.user_id
	client_id = request.oauth.client_id

	payment_agreement = PaymentAgreement.query.filter_by(user_id=user_id, client_id=client_id).first()

	if payment_agreement.is_valid_session():
		newPayment.identifier = request.oauth.user.identifier
		newPayment.value = payment_agreement.payment_amount
		newPayment.target = payment_agreement.payment_address
		try:
			payment_agreement.send_payment()
		except:
			#Add Error handling
			transaction = None
			return jsonify({'Status':'Error'}), 404


	return jsonify(transaction), 200




	




