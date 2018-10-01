from iota import *
from flask_login import current_user
import threading
from flask import jsonify, current_app


"""def loop(seed):  #Continuously checks the IOTA network for new payments:
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
	return jsonify({"Status":1})"""


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