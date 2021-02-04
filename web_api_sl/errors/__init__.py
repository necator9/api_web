from flask import Blueprint

bp = Blueprint('errors', __name__)

from web_api_sl.errors import handlers