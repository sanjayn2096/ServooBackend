# servoo_app.py
from flask import Flask, request, jsonify, session

from client.FirestoreClient import db
from controller.MenuController import MenuController
from model.ServooUserInfo import ServooUserInfo
from flask_cors import CORS
import jwt
import datetime

app = Flask(__name__)
app.secret_key = 'O9MG5BZGZO5MOCI'
CORS(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello Welcome to Servoo App!'


@app.route('/api/v1/user', methods=['POST'])
def create_user():
    try:
        if request.method == 'POST' or request.method == 'PUT':
            data = request.json
            # The check for valid phone Number and First Name Last Name will be done on UI.
            phone_number = data.get("phone_number")
            f_name = data['first_name']
            l_name = data['last_name']
            # Email will be Optional.
            email = data.get('email', '')

            # Create New User from entered Data.
            new_user = ServooUserInfo(phone_number, f_name, l_name, email)

            # Generate jwt
            session['phone_number'] = phone_number  # Store the user email in the session
            # Generate Token after User authenticated successfully
            access_token, refresh_token = generate_tokens(phone_number)
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token

            user_data = {
                "phoneNumber": new_user.phoneNumber,
                "firstName": new_user.firstName,
                "lastName": new_user.lastName,
                "email": new_user.email
            }
            db.collection("SERVOO_USERS").document(phone_number).set(user_data)
            return jsonify({'message': 'User registered successfully!',
                            'access_token': access_token,
                            'refresh_token': refresh_token,
                            'user': user_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)})


# This function generates a new access token and refresh token for a given user ID
def generate_tokens(phone_number):
    access_token_payload = {'phone_number': phone_number, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}
    access_token = jwt.encode(access_token_payload, app.secret_key, algorithm='HS256').decode('utf-8')
    refresh_token_payload = {'phone_number': phone_number, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}
    refresh_token = jwt.encode(refresh_token_payload, app.secret_key, algorithm='HS256').decode('utf-8')
    return access_token, refresh_token


# This function validates an access token and returns the user ID associated with it
def validate_token(access_token):
    try:
        payload = jwt.decode(access_token, app.secret_key, algorithms=['HS256'])
        phone_number = payload['phone_number']
        return phone_number
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


@app.route('/api/updateUser', methods=['PUT'])
def update_user():
    try:
        is_token_valid = validate_token(request.headers.get('x-access-token'))
        phone_number = ""
        if is_token_valid is None:
            return jsonify({'error': 'Invalid Token'}), 401
        else:
            phone_number = is_token_valid

        user_ref = db.collection("SERVOO_USERS").document(phone_number)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        user_data = user_doc.to_dict()
        updated_user_data = {}

        update_fields = request.get_json()
        if 'first_name' in update_fields and update_fields['first_name'] != user_data.get('first_name'):
            updated_user_data['first_name'] = update_fields['first_name']

        if 'last_name' in update_fields and update_fields['last_name'] != user_data.get('last_name'):
            updated_user_data['last_name'] = update_fields['last_name']

        if 'email' in update_fields and update_fields['email'] != user_data.get('email'):
            updated_user_data['email'] = update_fields['email']

        if updated_user_data:
            user_ref.update(updated_user_data)

        return jsonify({"message": "User updated successfully"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/createRestaurant')
@app.route('/checkout')
@app.route('/<int:restaurant_id>/menu', methods=['GET'])
def menu_route(restaurant_id):
    menu = MenuController.get_menu(restaurant_id)
    return jsonify(menu)


if __name__ == '__main__':
    app.run()
