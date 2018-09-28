from flask import render_template, flash
from flask_login import login_required, current_user
import datetime

from . import member
from app.models import Transaction, db

@member.route('/your_stats', methods=['GET'])
@login_required
def yourStats():
	user_transactions = db.session.query(Transaction).filter(Transaction.identifier==current_user.identifier).all()
	
	return render_template('/member/yourstats.html', title="Your Stats", user_transactions=user_transactions, from_datetime=fromDatetime)

def fromDatetime(my_datetime):
	return datetime.datetime.fromtimestamp(int(my_datetime)).strftime('%Y-%m-%d %H:%M:%S')