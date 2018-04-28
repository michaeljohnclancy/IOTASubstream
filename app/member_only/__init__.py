from flask import Blueprint

member_only = Blueprint('member_only', __name__)

from . import views