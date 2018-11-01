from iota import TryteString
import uuid
from sqlalchemy import func
from celery import shared_task

#Timekeeping for tasks
from pytz import timezone
from datetime import datetime, timedelta

from app.models import User, Transaction, PaymentAgreement

from extensions import db

timezone = timezone('Europe/London')


@shared_task()
def update_balance(user_id):
	user = User.query.filter_by(id=user_id).first()
	if user.is_authenticated:
		user.balance = user.get_balance()
		print("Users balance is " + str(user.balance))
		db.session.commit()
		update_balance.apply_async((user_id,), eta=timezone.localize(datetime.now()) + timedelta(seconds=120))
	else:
		return False

@shared_task()
def check_incoming_transactions(user_id, n=0):
	user = User.query.filter_by(id=user_id).first()
	if user.is_authenticated:
		bundles = user.get_bundles(n)
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
				print(tx.address)
				#user_identifier = TryteString.decode(tx.signature_message_fragment)
				receiving_address = tx.address
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

	payment_agreement = PaymentAgreement.query.filter_by(user_id=user_id, client_id=client_id).first()

	transaction = payment_agreement.send_payment()

	if type(transaction) is Transaction:
		return execute_agreement.apply_async((user_id, client_id), eta=timezone.localize(datetime.now()) + timedelta(seconds=payment_agreement.payment_time))
	else:
		print("Transaction was not successful.")
		payment_agreement.is_active = 0
		db.session.commit()
		return False








