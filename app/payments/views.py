from flask_login import current_user
from . import payments
from app.models import PaymentAgreement
from app.oauth2 import require_oauth
from app.forms import IotaPaymentForm

@payments.route('payments/single_payment', methods=['POST'])
@require_oauth('payment_gate')
def singlePayment():
	#Request a new payment be sent
	newPayment = IotaPaymentForm()
	
	user_id = request.oauth.user.user_id
	client_id = request.oauth.client_id

	payment_agreement = PaymentAgreement.query.filter_by(user_id=user_id, client_id=client_id).first()

	if payment_agreement.is_valid_session():
		newPayment.identifier = request.oauth.user.identifier
		newPayment.value = payment_agreement.payment_amount
		newPayment.target = payment_agreement.payment_address
		try:
			transaction = newPayment.send_payment()
		except:
			#Add Error handling
			print("Error")
			transaction = None

	return jsonify(transaction)




	




