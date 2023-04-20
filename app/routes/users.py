from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User
from schemas.user_schema import UserSchema

users_bp = Blueprint('users', __name__)
user_schema = UserSchema()


@users_bp.route('/', methods=['GET'])
@users_bp.route('', methods=['GET'])
def get_users():
    """
    API endpoint for getting a list of users

    GET /users?page=<page_number>&per_page=<per_page_number>

    Query Params:
    1. page (int): (Optional, default = 1) The page number of the user list.
    2. per_page (int): (Optional, default = 10) The number of users per page
    :return: A JSON object with page and additional data about
        list (total number of users, prev page number and next page number)
    :rtype: dict
    """
    # Getting query params
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Getting page and additional data from database
    resulting_page = db.paginate(db.select(User), page=page_number, per_page=per_page)
    users = resulting_page.items
    total_users = resulting_page.total
    prev_page = None
    next_page = None
    if resulting_page.has_prev:
        prev_page = resulting_page.prev_num
    if resulting_page.has_next:
        next_page = resulting_page.next_num

    # Translating page from the database to the dictionary
    output = []
    for user in users:
        user_data = user.to_dict()
        output.append(user_data)

    # Returning a JSON object with requesting data
    return jsonify({'users': output, 'total_users': total_users, 'prev_page': prev_page, 'next_page': next_page})


@users_bp.route('/', methods=['POST'])
@users_bp.route('', methods=['POST'])
def create_user():
    """
    API endpoint for creating a new user

    POST /users

    Request Body Parameters:
    1. username (str): The username of the new user. Should be unique
    2. email (str): The email of the new user. Should be unique
    3. password (str): The password of the new user

    :return: A JSON object containing data of new user
    :rtype: dict
    :raises IntegrityError: If the user with such email or username already exists
    """
    # Getting data from request and validate it
    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Creating new row in User table in the database
    new_user = User(username=data['username'], email=data['email'], password=data['password'])
    db.session.add(new_user)
    try:
        db.session.commit()
    except IntegrityError as e:
        # If user with such data already exist, rollback and return 409
        db.session.rollback()
        if "email" in str(e.args):
            return jsonify({'error': 'Email already exists'}), 409
        else:
            return jsonify({'error': 'Username already exists'}), 409

    # Serialize object to JSON and return it
    return jsonify(new_user.to_dict()), 201


@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    API endpoint for getting information of a specific user

    GET /api/users/<user_id>
    :param user_id: The unique ID of the user to retrieve
    :type user_id: int
    :return: A JSON object containing data of the user with the requested ID
    :rtype: dict
    """
    # Retrieve user with the specified id from the database
    user = db.session.get(User, {"id": user_id})

    if not user:
        # If user doesn't exist return 404 response
        return jsonify({'error': 'User not found'}), 404

    # Serialize object to JSON and return it
    return jsonify(user.to_dict())


@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """
    API endpoint to update the user with the requested ID

    PUT /api/users/<user_id>

    Request Body Parameters:
    1. username (str): The username of the user. Should be unique
    2. email (str): The email of the user. Should be unique
    3. password (str): The password of the user

    :param user_id: The unique ID of the user to update
    :type user_id: int
    :return: A JSON object containing data of the updated user
    :rtype: dict
    :raises IntegrityError: If the user with such email or username already exists
    """
    # Retrieve user with the specified id from the database
    user = db.session.get(User, {'id': user_id})

    if not user:
        # If user doesn't exist return 404 response
        return jsonify({'error': 'User not found'}), 404

    # Getting data from request and validate it
    data = request.get_json()
    errors = user_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Update the user
    user.username = data['username']
    user.email = data['email']
    user.password = data['password']

    # Commit the changes to the database
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "email" in str(e.args):
            return jsonify({'error': 'Email already exists'}), 409
        else:
            return jsonify({'error': 'Username already exists'}), 409

    # Serialize the object and return it
    return jsonify(user.to_dict())


@users_bp.route('/<int:user_id>', methods=['PATCH'])
def patch_user(user_id):
    """
       API endpoint to partial update the user with the requested ID

       PATCH /api/users/<user_id>

       Request Body Parameters:
       1. username (str): (Optional) The username of the user. Should be unique
       2. email (str): (Optional) The email of the user. Should be unique
       3. password (str): (Optional) The password of the user

       :param user_id: The unique ID of the user to update
       :type user_id: int
       :return: A JSON object containing data of the updated user
       :rtype: dict
       :raises IntegrityError: If the user with this email or username already exists
    """
    user = db.session.get(User, {'id': user_id})
    if not user:
        # If user doesn't exist return 404 response
        return jsonify({'error': 'User not found'}), 404

    # Getting data from the request and validate it
    data = request.get_json()
    errors = user_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    # Update the user with the provided data
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = data['password']

    # Commit the changes to the database
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "email" in str(e.args):
            return jsonify({'error': 'Email already exists'}), 409
        else:
            return jsonify({'error': 'Username already exists'}), 409

    return jsonify(user.to_dict())


@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    API endpoint to delete the user with the requested id

    DELETE /api/users/<user_id>
    :param user_id: The unique id of the user to delete
    :type user_id: int
    :return: A JSON containing error message if it is and status code
    :rtype: dict
    """
    user = db.session.get(User, {"id": user_id})

    if not user:
        # If user doesn't exist return 404 status code
        return jsonify({'error': 'User not found'}), 404

    # Delete user from database
    db.session.delete(user)
    db.session.commit()

    # Return  204 status code
    from flask import make_response
    return make_response('', 204)
