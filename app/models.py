from flask_login import UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import DataRequired, Email, Length
from datetime import datetime, timedelta
from passlib.context import CryptContext


import tasks
from app import db
from . import login_manager, oauth


pwd_context = CryptContext(
		schemes=["pbkdf2_sha256"],
		default="pbkdf2_sha256",
		pbkdf2_sha256__default_rounds=30000
		)


class User(UserMixin, db.Model):


	__tablename__ = 'users'

	id = db.Column(db.String(128), unique=True, primary_key=True)
	identifier = db.Column(db.String(128), unique=True, index=True)
	password_hash = db.Column(db.String(128), nullable=False)
	email = db.Column(db.String(128), unique=True, nullable=False)
	seed = db.Column(db.String(128), unique=True, nullable=False)

	#user_transactions = db.relationship('Transaction', backref='User', lazy='dynamic')
	
	def api(self):
		return tasks.create_api(self.seed)

	@property
	def password(self):
		"""
		Prevent pasword_hash from being accessed
		"""
		raise AttributeError('password is not a readable attribute.')

	@password.setter
	def password(self, password):
		"""
		Set password to a hashed password
		"""

		self.password_hash = pwd_context.encrypt(password)

	def verify_password(self, password):
		"""
		Check if hashed password matches actual password
		"""
		return pwd_context.verify(password, self.password_hash)



	def __repr__(self):
		return '<User: {}>'.format(self.id)

class Transaction(db.Model):
	__tablename__ = 'transactions'


	transaction_id = db.Column(db.String(128), primary_key=True, unique=True)
	identifier = db.Column(db.String(128))
	value = db.Column(db.Integer(), default=0)
	target = db.Column(db.String(128), nullable=True)
	timestamp = db.Column(db.Integer(), nullable=False)


	def __repr__(self):
		return '<Transaction ID: {}>'.format(self.transaction_id)

class Client(db.Model):
    # human readable name, not required
    #name = db.Column(db.String(40))

    # human readable description, not required
    #description = db.Column(db.String(400))

    # creator of the client, not required
    user_id = db.Column(db.ForeignKey('users.id'))
    # required if you need to support client credential
    user = db.relationship('User')

    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True,
                              nullable=False)

    # public or confidential
    is_confidential = db.Column(db.Boolean)

    #_redirect_uris = db.Column(db.Text)
    #_default_scopes = db.Column(db.Text)

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

class Grant(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.String(120), db.ForeignKey('users.id', ondelete='CASCADE')
    )
    user = db.relationship('User')

    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)

    #redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)

    #_scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    '''@property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []*/'''

class Token(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.String(40), db.ForeignKey('client.client_id'),
        nullable=False,
    )
    client = db.relationship('Client')

    user_id = db.Column(
        db.String(120), db.ForeignKey('users.id')
    )
    user = db.relationship('User')

    # currently only bearer is supported
    token_type = db.Column(db.String(40))

    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    #_scopes = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    ''' @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()
        return []'''

# Set up setters and getters
@login_manager.user_loader
def load_user(id):
	return User.query.get(str(id))

@oauth.usergetter
def get_user(username, password, *args, **kwargs):
    user = User.query.filter_by(username=username).first()
    if user.verify_password(password):
        return user
    return None

@oauth.clientgetter
def load_client(client_id):
    return Client.query.filter_by(client_id=client_id).first()

@oauth.grantgetter
def load_grant(client_id, code):
    return Grant.query.filter_by(client_id=client_id, code=code).first()

@oauth.grantsetter
def save_grant(client_id, code, request, *args, **kwargs):
    # decide the expires time yourself
    expires = datetime.utcnow() + timedelta(seconds=100)
    grant = Grant(
        client_id=client_id,
        code=code['code'],
        #redirect_uri=request.redirect_uri,
        #_scopes=' '.join(request.scopes),
        user=current_user,
        expires=expires
    )
    db.session.add(grant)
    db.session.commit()
    return grant

@oauth.tokengetter
def load_token(access_token=None, refresh_token=None):
    if access_token:
        return Token.query.filter_by(access_token=access_token).first()
    elif refresh_token:
        return Token.query.filter_by(refresh_token=refresh_token).first()

from datetime import datetime, timedelta

@oauth.tokensetter
def save_token(token, request, *args, **kwargs):
    toks = Token.query.filter_by(client_id=request.client.client_id,
                                 user_id=request.user.id)
    # make sure that every client has only one token connected to a user
    for t in toks:
        db.session.delete(t)

    expires_in = token.get('expires_in')
    expires = datetime.utcnow() + timedelta(seconds=expires_in)

    tok = Token(
        access_token=token['access_token'],
        refresh_token=token['refresh_token'],
        token_type=token['token_type'],
        #_scopes=token['scope'],
        expires=expires,
        client_id=request.client.client_id,
        user_id=request.user.id,
    )
    db.session.add(tok)
    db.session.commit()
    return tok



