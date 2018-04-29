# config.py

class Config(object):
	"""
	Common configurations
	"""
	MYSQL_DATABASE_CHARSET = 'utf8mb4'
	# Put any configurations here that are common across all environments

class DevelopmentConfig(Config):
	"""
	Development configurations
	"""
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	DEBUG = True
	SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
	"""
	Production configurations
	"""

	DEBUG = False

app_config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig
}
