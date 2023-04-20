from datetime import datetime, time

from flask import Blueprint, jsonify, request

from app import db
from app.models import Guest
from schemas.guest_schema import GuestSchema

guests_bp = Blueprint('guests', __name__)
guest_schema = GuestSchema()


@guests_bp.route('/', methods=['GET'])
@guests_bp.route('', methods=['GET'])
def get_guests():
    """
    API endpoint for getting a list of guests

    GET /guests?page=<page_number>&per_page=<per_page_number>

    Query Params:
    1. page (int): (Optional, default = 1) The page number of the guest list.
    2. per_page (int): (Optional, default = 10) The number of guests per page
    3. inviter_id (int): (Optional, default = None) The unique ID of inviter
    4. start_date (str): (Optional, default = None) The date where search date starts
    5. end_date (str): (Optional, default = None) The date where search date ends
    6. guest_type_id (int): (Optional, default = None) The unique ID of guest type
    :return: A JSON object with page and additional data about
        list (total number of guests, prev page number and next page number)
    :rtype: dict
    """
    # Getting pagination query params
    page_number = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    # Getting filter query params and add it in SQL query depending on it's value
    select_result = db.select(Guest)
    inviter_id = request.args.get('inviter_id', None, type=int)
    if inviter_id:
        select_result = select_result.where(Guest.inviter_id == inviter_id)

    guest_type_id = request.args.get('guest_type_id', None, type=int)
    if guest_type_id:
        select_result = select_result.where(Guest.guest_type_id == guest_type_id)

    start_date_str = request.args.get('start_date', None, type=str)
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        select_result = select_result.where(Guest.start_date >= start_date)

    end_date_str = request.args.get('end_date', None, type=str)
    if start_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        select_result = select_result.where(Guest.start_date <= end_date)

    # Getting page and additional data from database
    resulting_page = db.paginate(select_result, page=page_number, per_page=per_page)
    guests = resulting_page.items
    total_guests = resulting_page.total
    prev_page = None
    next_page = None
    if resulting_page.has_prev:
        prev_page = resulting_page.prev_num
    if resulting_page.has_next:
        next_page = resulting_page.next_num

    # Translating page from the database to the dictionary
    output = []
    for guest in guests:
        guest_data = guest.to_dict()
        output.append(guest_data)

    # Returning a JSON object with requesting data
    return jsonify({'guests': output, 'total_guests': total_guests, 'prev_page': prev_page, 'next_page': next_page})


@guests_bp.route('/', methods=['POST'])
@guests_bp.route('', methods=['POST'])
def create_guest():
    """
    API endpoint for creating a new guest

    POST /guests

    Request Body Parameters:
    1. guest_type_id (int): The unique ID for guest type
    2. inviter_id (int): The unique ID for guest type
    3. coming_date (str): Coming date of the guest
    4. coming_time (str): Coming time of the guest
    5. stay_time (str): Staying time of the guest
    6. comment (str): Comment for guest


    :return: A JSON object containing data of new guest
    :rtype: dict
    """
    # Getting data from request and validate it
    data = request.get_json()
    errors = guest_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Creating new row in Guest table in the database
    new_guest = Guest(guest_type_id=data['guest_type_id'],
                      inviter_id=data['inviter_id'],
                      coming_date=datetime.strptime(data['coming_date'], '%Y-%m-%d').date(),
                      coming_time=time.fromisoformat(data['coming_time']),
                      stay_time=time.fromisoformat(data['stay_time']),
                      comment=data['comment'])
    db.session.add(new_guest)
    db.session.commit()

    # Serialize object to JSON and return it
    return jsonify(new_guest.to_dict()), 201


@guests_bp.route('/<int:guest_id>', methods=['GET'])
def get_guest(guest_id):
    """
    API endpoint for getting information of a specific guest

    GET /api/guests/<guest_id>
    :param guest_id: The unique ID of the guest to retrieve
    :type guest_id: int
    :return: A JSON object containing data of the guest with the requested ID
    :rtype: dict
    """
    # Retrieve guest with the specified id from the database
    guest = db.session.get(Guest, {"id": guest_id})

    if not guest:
        # If guest doesn't exist return 404 response
        return jsonify({'error': 'Guest not found'}), 404

    # Serialize object to JSON and return it
    return jsonify(guest.to_dict())


@guests_bp.route('/<int:guest_id>', methods=['PUT'])
def update_guest(guest_id):
    """
    API endpoint to update the guest with the requested ID

    PUT /api/guests/<guest_id>

    Request Body Parameters:
    1. guest_type_id (int): The unique ID for guest type
    2. inviter_id (int): The unique ID for guest type
    3. coming_date (str): Coming date of the guest
    4. coming_time (str): Coming time of the guest
    5. stay_time (str): Staying time of the guest
    6. comment (str): Comment for guest

    :param guest_id: The unique ID of the guest to update
    :type guest_id: int
    :return: A JSON object containing data of the updated guest
    :rtype: dict
    """
    # Retrieve guest with the specified id from the database
    guest = db.session.get(Guest, {'id': guest_id})

    if not guest:
        # If guest doesn't exist return 404 response
        return jsonify({'error': 'Guest not found'}), 404

    # Getting data from request and validate it
    data = request.get_json()
    errors = guest_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    # Update the guest
    guest.guest_type_id = data['guest_type_id']
    guest.inviter_id = data['inviter_id']
    guest.coming_date = datetime.strptime(data['coming_date'], '%Y-%m-%d').date()
    guest.coming_time = time.fromisoformat(data['coming_time'])
    guest.stay_time = time.fromisoformat(data['stay_time'])
    guest.comment = data['comment']

    # Commit the changes to the database
    db.session.commit()

    # Serialize the object and return it
    return jsonify(guest.to_dict())


@guests_bp.route('/<int:guest_id>', methods=['PATCH'])
def patch_guest(guest_id):
    """
       API endpoint to partial update the guest with the requested ID

       PATCH /api/guests/<guest_id>

       Request Body Parameters:
        1. guest_type_id (int): The unique ID for guest type
        2. inviter_id (int): The unique ID for guest type
        3. coming_date (str): Coming date of the guest
        4. coming_time (str): Coming time of the guest
        5. stay_time (str): Staying time of the guest
        6. comment (str): Comment for guest

       :param guest_id: The unique ID of the guest to update
       :type guest_id: int
       :return: A JSON object containing data of the updated guest
       :rtype: dict
    """
    guest = db.session.get(Guest, {'id': guest_id})
    if not guest:
        # If guest doesn't exist return 404 response
        return jsonify({'error': 'guest not found'}), 404

    # Getting data from the request and validate it
    data = request.get_json()
    errors = guest_schema.validate(data, partial=True)
    if errors:
        return jsonify(errors), 400

    # Update the guest with the provided data
    if 'guest_type_id' in data:
        guest.guest_type_id = data['guest_type_id']
    if 'inviter_id' in data:
        guest.inviter_id = data['inviter_id']
    if 'coming_date' in data:
        guest.coming_date = datetime.strptime(data['coming_date'], '%Y-%m-%d').date()
    if 'coming_time' in data:
        guest.coming_time = time.fromisoformat(data['coming_time'])
    if 'stay_time' in data:
        guest.stay_time = time.fromisoformat(data['stay_time'])
    if 'comment' in data:
        guest.comment = data['comment']

    # Commit the changes to the database
    db.session.commit()

    return jsonify(guest.to_dict())


@guests_bp.route('/<int:guest_id>', methods=['DELETE'])
def delete_guest(guest_id):
    """
    API endpoint to delete the guest with the requested id

    DELETE /api/guests/<guest_id>
    :param guest_id: The unique id of the guest to delete
    :type guest_id: int
    :return: A JSON containing error message if it is and status code
    :rtype: dict
    """
    guest = db.session.get(Guest, {"id": guest_id})

    if not guest:
        # If guest doesn't exist return 404 status code
        return jsonify({'error': 'Guest not found'}), 404

    # Delete guest from database
    db.session.delete(guest)
    db.session.commit()

    # Return  204 status code
    from flask import make_response
    return make_response('', 204)
