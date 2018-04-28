import re

def valid_password(password):
	if (len(password)<10 or len(password)>24):
		return False
	#elif not re.search("[a-z]", password):
	#	return False
	#elif not re.search("[0-9]", password):
	#	return False
	#elif not re.search("[A-Z]", password):
	#	return False
	#elif not re.search("[$#@]", password):
	#	return False
	else:
		return True

	#def valid_username()