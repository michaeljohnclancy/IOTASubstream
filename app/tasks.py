from iota import TryteString
import uuid
from sqlalchemy import func
from celery import shared_task

#Timekeeping for tasks
from pytz import timezone
from datetime import datetime, timedelta

from app.models import User, Transaction

from app import create_app

from extensions import db

timezone = timezone('Europe/London')

#The functions are called recursively, hence a new app instance being created every time the function is called.
# This works but needs to be fixed, so that the app context can be accessed once.

@shared_task()
def get_balance(user_id):
	user = User.query.filter_by(id=user_id).first()
	if user.is_authenticated:
		user.balance = user.iota_api.get_account_data()['balance']
		print("Users balance is " + str(user.balance))
		db.session.commit()
		return get_balance.apply_async((user_id,), eta=timezone.localize(datetime.now()) + timedelta(seconds=120))
	else:
		return False

@shared_task()
def check_incoming_transactions(user_id, n=0):
	user = User.query.filter_by(id=user_id).first()
	if user.is_authenticated:
		bundles = user.iota_api.get_transfers(start=n).get(u'bundles')
		n = len(bundles)

		#Finds the amount of transactions in the database related
		#to the current user and compares it to the newly retrieved
		#bundle length. If equal, wait 120 seconds, try again. If
		#not equal, new transactions are added to db, then wait 120s.
		transaction_count = db.session.query(User.transactions).filter_by(id=user_id).count()
		print("Number of Transactions is: " + str(transaction_count))
		print("N is equal to: " + str(n))
		if n == transaction_count:
			print("NO NEW TRANSACTIONS")
			print(timezone.localize(datetime.now()) + timedelta(seconds=120))
			check_incoming_transactions.apply_async((user_id, n), eta=timezone.localize(datetime.now()) + timedelta(seconds=120))
		else:
			print("NEW TRANSACTION INCOMING")
			new_messages = {}
			for message in bundles:
				tx = message[0]
				print(tx)
				#user_identifier = TryteString.decode(tx.signature_message_fragment)
				receiving_address = str(tx.address)
				payment_amount = int(tx.value)
				timestamp = tx.timestamp

				incomingTransaction = Transaction(transaction_id=str(uuid.uuid4()),
					user_identifier=user.identifier,
					payment_amount=payment_amount,
					payment_address=receiving_address,
					timestamp=timestamp)

				db.session.add(incomingTransaction)
				db.session.commit()
			check_incoming_transactions.apply_async((user_id, n), eta=timezone.localize(datetime.now()) + timedelta(seconds=120))
	else:
		return False

@shared_task()
def execute_agreement(user_id, client_id):
	payment_agreement = PaymentAgreement.query.filter_by(user_id=user_id, client_id=client_id)
	if payment_agreement.is_valid_session():
		transaction = payment_agreement.send_payment()
		execute_agreement.delay((user_id, client_id), eta=timezone.localize(datetime.now()) + timedelta(seconds=payment_agreement.payment_time))
	else:
		return False








