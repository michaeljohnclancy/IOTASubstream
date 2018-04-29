from flask import render_template
from flask_login import login_required

from . import member

@member.route('/your_stats', methods=['GET'])
@login_required
def yourStats():

	
	return render_template('member/yourstats.html', title="Signup Success")