from flask_sqlalchemy import SQLAlchemy

class sql:

	def __init__(self, app):
		app.config['SQLALCHEMY_DATABASE_URI'] = \
			'mysql://root:Playbook8003@localhost/transactions_db'
			self.db = SQLAlchemy(app)

	