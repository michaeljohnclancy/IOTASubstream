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
	DEBUG = 1
	SQLALCHEMY_ECHO = True
	AUTHLIB_INSECURE_TRANSPORT = True

class ProductionConfig(Config):
	"""
	Production configurations

	"""
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	AUTHLIB_INSECURE_TRANSPORT = True

app_config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig
}
