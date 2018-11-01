from werkzeug.security import gen_salt
from flask_login import current_user

from authlib.specs.rfc6749 import grants
from authlib.common.security import generate_token

from authlib.flask.oauth2 import AuthorizationServer, ResourceProtector
from authlib.flask.oauth2.sqla import (
	create_revocation_endpoint,
	create_bearer_token_validator,
	create_query_client_func,
	create_save_token_func
)

from extensions import db
from app.models import User, AuthorizationCode, Token, Client, PaymentAgreement

#Definitions
authorization = AuthorizationServer()
require_oauth = ResourceProtector()

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
	def create_authorization_code(self, client, grant_user, request):
		# you can use other method to generate this code
		print(client.client_id)
		print(grant_user.id)
		code = generate_token(48)
		item = AuthorizationCode(
			code=code,
			client_id=client.client_id,
			redirect_uri=request.redirect_uri,
			scope=client.scope,
			user_id=grant_user.id,
			)
		db.session.add(item)
		db.session.commit()
		return code

	def parse_authorization_code(self, code, client):
		item = AuthorizationCode.query.filter_by(
			code=code, client_id=client.client_id).first()
		if item and not item.is_expired():
			return item
		else:
			return None

	def delete_authorization_code(self, authorization_code):
		db.session.delete(authorization_code)
		db.session.commit()

	def authenticate_user(self, authorization_code):
		return User.query.filter_by(id=authorization_code.user_id).first()

class RefreshTokenGrant(grants.RefreshTokenGrant):
	def authenticate_refresh_token(self, refresh_token):
		item = Token.query.filter_by(refresh_token=refresh_token).first()
		if item and not item.is_refresh_token_expired():
			return item

	def authenticate_user(self, credential):
		return User.query.filter_by(id=credential.user_id).first()

query_client = create_query_client_func(db.session, Client)

#def query_client(client_id):
#	return Client.query.filter_by(client_id=client_id).first()

def save_token(token, request):
	authCode = AuthorizationCode.query.filter_by(
			code=request.code, client_id=request.client.client_id).first()

	print(authCode)
	if authCode and not authCode.is_expired():
		payment_agreement = PaymentAgreement.query.filter_by(user_id=authCode.user_id, client_id=authCode.client_id).first()
		item = Token(
			client_id = authCode.client_id,
			user_id = authCode.user_id,
			payment_agreement_id=payment_agreement.id,
			**token

		)
		db.session.add(item)
		db.session.commit()

#Registering grants
authorization.register_grant(AuthorizationCodeGrant)
authorization.register_grant(RefreshTokenGrant)

# support revocation
revocation_cls = create_revocation_endpoint(db.session, Token)
authorization.register_endpoint(revocation_cls)

#Resourse Protector
bearer_cls = create_bearer_token_validator(db.session, Token)
require_oauth.register_token_validator(bearer_cls())