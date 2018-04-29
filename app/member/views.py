from flask import render_template
from flask_login import login_required, current_user

from ..models import Transaction

from . import member

@member.route('/your_stats', methods=['GET'])
@login_required
def yourStats():
	try:
		user_transactions = Transaction.query.filter_by(identifier=str(current_user.identifier))
	except Exception, e:
		session.rollback()
		print str(e)
	
	return render_template('/member/yourstats.html', title="Signup Success")