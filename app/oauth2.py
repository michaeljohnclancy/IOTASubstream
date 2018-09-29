from app.models import db, User, AuthorizationCode, Token, Client
from werkzeug.security import gen_salt

from authlib.specs.rfc6749 import grants

from authlib.flask.oauth2 import AuthorizationServer, ResourceProtector
from authlib.flask.oauth2.sqla import (
    create_revocation_endpoint,
    create_bearer_token_validator,
)

#Definitions
authorization = AuthorizationServer()
require_oauth = ResourceProtector()

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def create_authorization_code(self, client, grant_user, request):
        # you can use other method to generate this code
        code = generate_token(48)
        item = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            scope=request.scope,
            user_id=grant_user.get_user_id(),
        )
        db.session.add(item)
        db.session.commit()
        return code

    def parse_authorization_code(self, code, client):
        item = AuthorizationCode.query.filter_by(
            code=code, client_id=client.client_id).first()
        if item and not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        db.session.delete(authorization_code)
        db.session.commit()

    def authenticate_user(self, authorization_code):
        return User.query.get(authorization_code.user_id)



class RefreshTokenGrant(grants.RefreshTokenGrant):
	def authenticate_refresh_token(self, refresh_token):
		item = Token.query.filter_by(refresh_token=refresh_token).first()
		if item and not item.is_refresh_token_expired():
			return item

	def authenticate_user(self, credential):
		return User.query.get(credential.user_id)

def query_client(client_id):
	return Client.query.filter_by(id=client_id).first()

def save_token(token, request):
	if request.user:
		user_id = request.user.get_user_id()
	else:
		# client_credentials grant_type
		user_id = request.client.user_id
	item = Token(
		client_id=request.client.client_id,
		user_id=user_id,
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