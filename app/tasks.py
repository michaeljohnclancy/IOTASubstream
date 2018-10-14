from __future__ import absolute_import, unicode_literals
from app.models import User, db, Transaction
from celery import Celery, shared_task
from iota import TryteString
import uuid

celery = Celery(__name__, broker='amqp://guest@localhost//')

#The functions are called recursively, hence a new app instance being created every time the function is called.
# This works but needs to be fixed, so that the app context can be accessed once.

@shared_task()
def get_balance(user_id):
	from app import create_app
	my_app = create_app()
	with my_app.app_context():
		user = User.query.filter_by(id=user_id).first()
		if user.is_authenticated:
			api = user.iota_api()
			print("hello")
			user.balance = api.get_account_data()['balance']
			print("Users balance is " + str(user.balance))
			db.session.commit()
			return get_balance.apply_async((user_id,), countdown=120)
		else:
			return False

@shared_task()
def check_incoming_transactions(user_id, n=0):
	from app import create_app
	my_app = create_app()
	with my_app.app_context():
		user = User.query.filter_by(id=user_id).first()
		if user.is_authenticated:
			api = user.iota_api()
			bundles = api.get_transfers(start=n).get(u'bundles')
			n = len(bundles)
			print(n)
			if n == 0:
				print("NO NEW TRANSACTIONS")
				return check_incoming_transactions.apply_async((user_id, n), countdown=120)
			else:
				print("NEW TRANSACTION INCOMING")
				new_messages = {}
				for message in bundles:
					tx = message[0]
					print(tx)
					user_identifier = TryteString.decode(tx.signature_message_fragment)
					receiving_address = tx.address
					payment_amount = tx.value
					timestamp = tx.timestamp

					incomingTransaction = Transaction(transaction_id=str(uuid.uuid4()),
						user_identifier=user.identifier,
						payment_amount=payment_amount,
						payment_address=receiving_address,
						timestamp=timestamp)

					db.session.add(incomingTransaction)
					db.session.commit()
				return check_incoming_transactions.apply_async((user_id, n), countdown=120)
		else:
			return False