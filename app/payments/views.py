from flask_login import current_user
from . import payments
from app.oauth2 import require_oauth
from app.forms import IotaPaymentForm

@payments.route('payments/single_payment', methods=['POST'])
@require_oauth('payment_gate')
def singlePayment():
	newPayment = IotaPaymentForm()

	if current_user.is_authenticated:
		newPayment.identifier = current_user.identifier
		newPayment.value = request.args['value']
		newPayment.target = request.args['client_address']
	
	try:
		transaction = newPayment.send_payment()
	except:
		#Add Error handling
		print("Error")
		transaction = None

	return transaction




	




