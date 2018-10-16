# app/__init__.py

# third-party imports
from flask import Flask
from flask_login import user_logged_in
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_qrcode import QRcode

from authlib.specs.rfc6749 import grants

# local imports
from config import app_config, ProductionConfig

def create_app(config_name=None):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(ProductionConfig)
	app.config.from_pyfile('config.py')
	app.config.update(
	CELERY_BROKER_URL='amqp://guest@localhost//',
	CELERY_RESULT_BACKEND='amqp://guest@localhost//'
)

	from app.oauth2 import (
		query_client, save_token, 
		require_oauth, authorization
		)

	from extensions import db, login_manager

	with app.app_context():
		db.init_app(app)
		authorization.init_app(app, query_client, save_token)
		login_manager.init_app(app)
   
	Bootstrap(app)
	QRcode(app)
	login_manager.login_message = "You must be logged in to access this page."
	login_manager.login_view = "auth.login"
	migrate = Migrate(app, db, compare_type=True)


	#DEFINING BLUEPRINTS
	from .home import home as home_blueprint
	app.register_blueprint(home_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from .member import member as member_blueprint
	app.register_blueprint(member_blueprint)

	from .payments import payments as payments_blueprint
	app.register_blueprint(member_blueprint)

	return app