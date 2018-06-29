# app/__init__.py

# third-party imports
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap


# local imports
from config import app_config

login_manager = LoginManager()
db = SQLAlchemy()


def create_app(config_name):
	app = Flask(__name__, instance_relative_config=True)
	app.config.from_object(app_config[config_name])
	app.config.from_pyfile('config.py')

	with app.app_context():
		db.init_app(app)
	
	Bootstrap(app)
	login_manager.init_app(app)
	login_manager.login_message = "You must be logged in to access this page."
	login_manager.login_view = "auth.login"
	migrate = Migrate(app, db, compare_type=True)


	from app import models
	
	from .home import home as home_blueprint
	app.register_blueprint(home_blueprint)

	from .auth import auth as auth_blueprint
	app.register_blueprint(auth_blueprint)

	from .member import member as member_blueprint
	app.register_blueprint(member_blueprint)


	return app
