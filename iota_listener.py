from iota import *
import csv
import thread

#Connects to node and opens API stream with seed
node = "http://node02.iotatoken.nl:14265"
seed = "EYPZDLOZBKTECDHCBVGAGOHDIVEDRLGKLWDXXXSBPUBFAJOSSWXUSDYJSRFRYBQK9TMALDCDQHTBGMJRH"
api = Iota(node)
#Random seed for time being

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
		return [userID,  transactionValue, timestamp]

def setMembership(messages):
	for userID in messages.keys():
		#Check if paid, assigns boolean value 1 being subscribed, 0 not subscribed
		if active_users[userID][0] >= 0:
			active_users[userID][2] = 1
		else:
			active_users[userID][2] = 0


def listen_loop():  #Continuously checks the IOTA network for new payments:
	#ms = get_bundles()
	n = 0#len(ms)
	while(True):
		ms = get_bundles()  #TODO This is a bottleneck
		if len(ms)==n:
			print("No new messages")
		else:
			print("Received", len(ms)-n, "new message(s) [decrypted]:")

			new_messages = {}
			for message in ms:
				new_message = interpret_message(message)
				userID = new_message[0]
				new_messages[userID] = [new_message[1], new_message[2]]

			for userID in new_messages.keys():
				if userID in active_users.keys():
					#Value of new transaction added to users balance
					active_users[userID][0] += new_messages[userID][0]
					active_users[userID][1] = new_messages[userID][1]
					active_users[userID][2] = 0

				else:
					active_users[userID] = [new_messages[userID][0],  new_messages[userID][1], 0]
			setMembership(new_messages)

def print_active_users():
	while(True):
		raw_input("Press Enter to list current active users...")
		if active_users == {}:
			continue
		else:
			print(active_users)

thread.start_new_thread(listen_loop, ())
print_active_users()