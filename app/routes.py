from flask import Blueprint

api_bp = Blueprint('api', __name__)


@api_bp.route('/hello')
def hello():
    return 'Hello, World!'
