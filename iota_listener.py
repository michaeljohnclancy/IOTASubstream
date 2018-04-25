from iota import *
import csv
import thread

#Connects to node and opens API stream with seed
node = "http://node04.iotatoken.nl:14265"
seed = "AAJTNWZJFNGWYMWDPQ9QBSFDTDEXMAGVAYTN9VBWXTQSFZLKYSRMHSSEPSEBBSR9ULHXDEEIRPVSE9YNV"
api = Iota(node, seed)

#GLOBAL DICTIONARY Key is USER, Value is (balance, timestamp, activeStatus)
active_users = {}

def get_bundles(n=None):  #Get all messages from the IOTA network:
		return api.get_transfers(start=n).get(u'bundles')

def print_messages(ms):  #Print raw messages (does not decrypt):
		for m in ms:
				for tx in m:
						print(TryteString.decode(tx.signature_message_fragment))

def interpret_message(m):  #Decrypts and executes instruction:
		tx = m[0]
		userID = TryteString.decode(tx.signature_message_fragment)
		transactionValue = tx.value
		timestamp = tx.timestamp
		return {userID: [transactionValue, timestamp]}

def setMembership():
	for key in active_users.keys():
		#Check if paid, assigns boolean value 1 being subscribed, 0 not subscribed
		if active_users[key][0] >= 0:
			active_users[key][2] = 1
		else:
			active_users[key][2] = 0


def listen_loop():  #Continuously checks the IOTA network for new payments:
	ms = get_bundles()
	n = len(ms)
	print("Found", n, "old message(s).")
	print("------------------------")

	print("Waiting for new messages:")
	while(True):
		ms = get_bundles()  #TODO This is a bottleneck
		if len(ms)==n:
			print("No new messages")
		else:
			print("Received", len(ms)-n, "new message(s) [decrypted]:")

			new_messages = dict([interpret_message(ms[i]).items() for i in range(n, len(ms))])
			userIDs = [new_messages[i][0] for i in range(len(new_messages))]

  

			for userID in UserIDs:
				if userID in active_users.keys():
					#Value of new transaction added to users balance
					active_users[userID][0] += new_messages[userID][0]
					active_users[userID][1] = new_messages[userID][1]
					active_users[userID][2] = 0

				else:
					active_users[userID] = [new_messages[userID][0],  new_messages[userID][0], 0]
			setMembership()

def print_active_users():
	while(True):
		raw_input("Press Enter to list current active users...")
		if active_users == {}:
			continue
		else:
			print(active_users)

thread.start_new_thread(listen_loop, ())
print_active_users()