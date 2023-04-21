from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import GuestType
from schemas.guest_type_schema import GuestTypeSchema

guest_types_bp = Blueprint('guest_types', __name__)
guest_type_schema = GuestTypeSchema()


@guest_types_bp.route('/', methods=['GET'])
@guest_types_bp.route('', methods=['GET'])
@jwt_required()
def get_guest_types():
    """
    API endpoint for getting a list of guest types

    GET /api/guest_types?page=<page_number>&per_page=<per_page_number>

    Query Params:
    1. page (int): (Optional, default = 1) The page number of the guest types list
    2. per_page (int): (Optional, default = 10) The number of the guest types per page
    :return: A JSON object with page and additional data about
    :rtype: dict
    """
    # Getting query params
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Getting page and additional information
    resulting_page = db.paginate(db.select(GuestType), page=page_number, per_page=per_page)
    guest_types = resulting_page.items
    total_guest_types = resulting_page.total
    prev_page = None
    next_page = None
    if resulting_page.has_prev:
        prev_page = resulting_page.prev_num
    if resulting_page.has_next:
        next_page = resulting_page.next_num

    # Translating page into dict
    output = []
    for gtype in guest_types:
        gtype_data = gtype.to_dict()
        output.append(gtype_data)

    # Return a JSON object with requesting data
    return jsonify({'guest_types': output,
                    'total_guest_types': total_guest_types,
                    'prev_page': prev_page,
                    'next_page': next_page})


@guest_types_bp.route('/', methods=['POST'])
@guest_types_bp.route('', methods=['POST'])
@jwt_required()
def create_guest_type():
    """
    API endpoint for creating a new guest type

    POST /api/guest_types

    Request Body Parameters:
    1. name (str): The name of the new guest type. Should be unique
    :return: A JSON object containing data of the new guest type
    :rtype: dict
    :raises IntegrityError: If the guest type with such name already exist
    """
    # Getting data from request and validate it
    data = request.get_json()
    errors = guest_type_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Creating new row in GuestType table in the database
    new_guest_type = GuestType(name=data['name'])
    db.session.add(new_guest_type)
    try:
        db.session.commit()
    except IntegrityError:
        # If the guest type with such data already exist rollback and return 409
        db.session.rollback()
        return jsonify({'error': 'This type of guest already exists'})

    # Serialize object to JSON and return it
    return jsonify(new_guest_type.to_dict()), 201


@guest_types_bp.route('/<int:guest_id>', methods=['GET'])
@jwt_required()
def get_guest_type(guest_id):
    """
    API endpoint for getting information of a specific guest type

    GET /api/guest_types/<user_id>
    :param guest_id: The unique ID of the guest type to retrieve
    :type guest_id: int
    :return: A JSON object containing data of the guest type with the requested ID
    :rtype: dict
    """
    # Retrieve the guest type from the database
    guest_type = db.session.get(GuestType, {'id': guest_id})

    if not guest_type:
        # If guest type doesn't exist return 404 response
        return jsonify({'error': 'Guest type not found'}), 404

    # Serialize object to JSON and return it
    return jsonify(guest_type.to_dict())


@guest_types_bp.route("/<int:guest_type_id>", methods=['PUT'])
@jwt_required()
def update_guest_type(guest_type_id):
    """
    API endpoint to update the guest type with the requested ID

    PUT /api/guest_types/<guest_type_id>

    Request Body Parameters:
    1. name (str): The name of the guest type. Should be unique

    :param guest_type_id: The unique ID of the guest type to update
    :type guest_type_id: int
    :return: A JSON object containing data of the updated guest type
    :rtype: dict
    :raises IntegrityError: If guest type with this name already exists
    """
    # Get data from request and validate it
    data = request.get_json()
    errors = guest_type_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Get the guest type from the database
    guest_type = db.session.get(GuestType, {'id': guest_type_id})
    if not guest_type:
        # If the guest type doesn't exist return 404 response status code
        return jsonify({'error': 'Guest type not found'}), 404

    # Update the guest type
    guest_type.name = data['name']

    # Try to commit changes to the database
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'This guest type already exists'}), 409

    # Serialize the object and return it
    return jsonify(guest_type.to_dict())


@guest_types_bp.route("/<int:guest_type_id>", methods=['DELETE'])
@jwt_required()
def delete_guest_type(guest_type_id):
    """
       API endpoint to delete the guest type with the requested id

       DELETE /api/guest_type/<guest_type_id>
       :param guest_type_id: The unique id of the guest type to delete
       :type guest_type_id: int
       :return: A JSON containing error message if it is and status code
       :rtype: dict
       """
    # Get the guest type from the database
    guest_type = db.session.get(GuestType, {'id': guest_type_id})

    if not guest_type:
        # If the guest type doesn't exist return 404 response status code
        return jsonify({'error': 'Guest type not found'})

    # Delete the guest type from the database
    db.session.delete(guest_type)
    db.session.commit()

    # Return 204 status code
    from flask import make_response
    return make_response('', 204)
