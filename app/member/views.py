from flask import render_template, flash
from flask_login import login_required, current_user

from ..models import Transaction

from . import member
from .. import db

@member.route('/your_stats', methods=['GET'])
@login_required
def yourStats():
	user_transactions = db.session.query(Transaction).filter(Transaction.identifier==current_user.identifier).all()
	
	return render_template('/member/yourstats.html', title="Your Stats", user_transactions=user_transactions)