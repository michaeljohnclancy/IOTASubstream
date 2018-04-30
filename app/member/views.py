from flask import render_template
from flask_login import login_required, current_user

from ..models import Transaction

from . import member
from .. import db

@member.route('/your_stats', methods=['GET'])
@login_required
def yourStats():
	user_transactions = db.session.query(Transaction).filter_by(identifier=str(current_user.identifier)).first()
	
	return render_template('/member/yourstats.html', title="Your Stats")