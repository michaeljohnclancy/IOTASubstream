from . import payments
from app.oauth2 import require_oauth
from app.forms import SendIotaForm

@payments.route('/request_payment', methods=['POST'])
@require_oauth('payment_gate')
def singlePayment():
	return None
	#TODO




