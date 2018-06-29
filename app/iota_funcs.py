
from models import Transaction
from iota import *
from flask_login import current_user
import threading
from flask import jsonify

import celery

def create_api(seed):
	api = Iota("http://node02.iotatoken.nl:14265", seed)
	return api


@celery.task()
def sendiota(user, value, target, interval, numPayments):
	i = 0

	while (i <= int(numPayments)-1):
		current_time = time()

		tx = ProposedTransaction(address=Address(str(target)), value=int(value), tag=None, message=TryteString.from_string(user.identifier))
		user.create_api(user.seed).send_transfer(depth=10, transfers=[tx])
		print(tx)

		transaction = Transaction(transaction_id=str(uuid.uuid4()),
		identifier=user.identifier,
			value=value,
			target=target,
			timestamp=tx.timestamp)

		try:
			db.session.add(transaction)
		except Exception, e:
			db.session.rollback()
			print str(e)
		time_taken = time() - current_time

		sleep(float(abs(float(interval)-time_taken)))
		i += 1

	db.session.commit()


@celery.task()
def loop(seed):  #Continuously checks the IOTA network for new payments:
	ms = get_bundles(seed)
	n = len(ms)
	while(True):
		ms = get_bundles(seed, n)  #TODO This is a bottleneck
		if len(ms)==0:
			continue
		else:
			new_messages = {}
			for message in ms:
				transaction = interpret_transaction(message)
				print(transaction)
	return jsonify({"Status":1})


def interpret_transaction(m):  #Decrypts and executes instruction:
	tx = m[0]
	identifier = TryteString.decode(tx.signature_message_fragment)
	transactionValue = tx.value
	timestamp = tx.timestamp

	incomingTransaction = Transaction(transaction_id=str(uuid.uuid4()),
		identifier=identifier,
		value=transaction_value,
		target=None,
		timestamp=timestamp)

	db.session.add(incomingTransaction)
	db.session.commit()

	return incomingTransaction

def get_bundles(seed, n=None):  #Get all messages from the IOTA network:
	return create_api(seed).get_transfers(start=n).get(u'bundles')