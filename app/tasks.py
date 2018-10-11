from models import User, db

from app import celery, create_app

@celery.task()
def get_balance(user):
		#user = User.query.filter_by(id=user_id).first()
		if user.is_authenticated:
			user.balance = user.iota_api.get_account_data()['balance']
			return get_balance.delay((user), countdown=120)
		else:
			return False

@celery.task()
def check_incoming_transactions(user, n=0):
		#user = User.query.filter_by(id=user_id).first()
		bundles = user.iota_api.get_transfers(start=n).get(u'bundles')
		n = len(bundles)
		if user.is_authenticated:
			if n == 0:
				return user.check_incoming_transactions.delay((user, n), countdown=120)
			else:
				new_messages = {}
				for message in bundles:
					tx = message[0]
					user_identifier = TryteString.decode(tx.signature_message_fragment)
					payment_amount = tx.value
					timestamp = tx.timestamp

					incomingTransaction = Transaction(transaction_id=str(uuid.uuid4()),
						user_identifier=user_identifier,
						payment_amount=payment_amount,
						payment_address=None,
						timestamp=timestamp)

					db.session.add(incomingTransaction)
				return check_incoming_transactions.delay((user, n), countdown=120)
		else:
			return False