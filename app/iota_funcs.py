
from models import Transaction
from iota import *
from flask_login import current_user
import threading

def create_api():
	api = Iota("http://node05.iotatoken.nl:16265", current_user.seed)
	return api

def sendiota(value, target, interval, numPayments):
	i = 0

	while (i <= int(numPayments)-1):
		tx = ProposedTransaction(address=Address(str(target)), value=int(value), tag=None, message=TryteString.from_string(current_user.identifier))
		thread = threading.Thread(target=create_api().send_transfer, kwargs = {'depth': 100, 'transfers':[tx]})
		thread.daemon = True
		thread.start()

		current_time = time()
		transaction = Transaction(transaction_id=str(uuid.uuid4()),
		identifier=current_user.identifier,
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

def listen_loop():
	thread = threading.Thread(target=loop)
	thread.daemon = True
	thread.start()

def loop():  #Continuously checks the IOTA network for new payments:
		ms = get_bundles()
		n = len(ms)
		while(True):
			ms = get_bundles(n)  #TODO This is a bottleneck
			if len(ms)==0:
				continue
			else:
				new_messages = {}
				for message in ms:
					transaction = interpret_transaction(message)
					flash(transaction)


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

def get_bundles(n=None):  #Get all messages from the IOTA network:
	return create_api().get_transfers(start=n).get(u'bundles')