from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, create_access_token, jwt_required, create_refresh_token

from app import db
from app.models import User

authentication_bp = Blueprint('authentication', __name__)


@authentication_bp.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    user = db.session.scalar(db.select(User).where(User.username == username))
    # Check if password is correct
    if user is not None and user.check_password(password):
        # Create access and refresh tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Return tokens in response
        return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200
    else:
        return jsonify({'error': 'Invalid username or password'}), 401


@authentication_bp.route('/refresh', methods=['GET'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    refresh_token = create_refresh_token(identity=current_user)
    return jsonify({'access_token': access_token, 'refresh_token': refresh_token}), 200


@authentication_bp.route('/logout', methods=['POST'])
@jwt_required(refresh=True)
def logout():
    current_user = get_jwt_identity()
    user = db.session.get(User, current_user)

    if user:
        return jsonify({'message': 'Successfully logged out.'}), 200
    else:
        return jsonify({'message': 'User not found.'}), 404
