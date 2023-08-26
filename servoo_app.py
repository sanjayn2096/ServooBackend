# servoo_app.py
from flask import Flask, request, jsonify, session

from google.cloud import firestore
from client.FirestoreClient import db
from controller.MenuController import MenuController
from model.ServooUserInfo import ServooUserInfo
from model.RestaurantInfo import RestaurantInfo
from flask_cors import CORS
from util import uuid_generator
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
        if request.method == 'POST':
            data = request.json
            # The check for valid phone Number and First Name Last Name will be done on UI.
            phone_number = data.get("phone_number")
            f_name = data['first_name']
            l_name = data['last_name']
            # Email will be Optional.
            email = data.get('email', '')
            restaurants_working_at = data.get('restaurants_working_at', [])
            restaurants_owned = data.get('restaurants_owned', [])

            # Create New User from entered Data.
            new_user = ServooUserInfo(phone_number, f_name, l_name, email, restaurants_working_at, restaurants_owned)

            # Generate jwt
            session['phone_number'] = phone_number  # Store the user email in the session
            # Generate Token after User authenticated successfully
            access_token, refresh_token = generate_tokens(phone_number)
            session['access_token'] = access_token
            session['refresh_token'] = refresh_token
            combined_tokens = f"{access_token}:{refresh_token}"
            user_data = new_user.to_dict()
            db.collection("SERVOO_USERS").document(phone_number).set(user_data)
            # Create a response with the user data and set cookies for tokens
            response = jsonify({
                'message': 'User registered successfully!',
                'user': user_data
            })
            response.set_cookie('jwt_tokens', combined_tokens)
            return response, 200
    except Exception as e:
        return jsonify({'error': str(e)})


# This function generates a new access token and refresh token for a given user ID
def generate_tokens(phone_number):
    access_token_payload = {'phone_number': phone_number,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=15)}
    access_token = jwt.encode(access_token_payload, app.secret_key, algorithm='HS256')
    refresh_token_payload = {'phone_number': phone_number,
                             'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=45)}
    refresh_token = jwt.encode(refresh_token_payload, app.secret_key, algorithm='HS256')
    return access_token, refresh_token


# This function validates an access token and returns the user ID associated with it
def validate_token(access_token):
    try:
        print("Access token:", access_token)
        print("Secret key:", app.secret_key)
        payload = jwt.decode(access_token, app.secret_key, algorithms=['HS256'])
        phone_number = payload['phone_number']
        return phone_number
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


@app.route('/api/v1/user', methods=['GET'])
def get_user():
    try:
        jwt_cookie = request.cookies.get('jwt_tokens')
        if jwt_cookie is None:
            return jsonify({'error': 'No JWT token provided'}), 401

        # Split the combined tokens into access and refresh tokens
        access_token, refresh_token = jwt_cookie.split(':')

        # Validate the access token
        phone_number = validate_token(access_token)
        if phone_number is None:
            return jsonify({'error': 'Invalid Token'}), 401

        user_ref = db.collection("SERVOO_USERS").document(phone_number)
        user_doc = user_ref.get()

        if not user_doc.exists:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"User": user_doc.to_dict()}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/v1/updateUser', methods=['PUT'])
def update_user():
    try:
        jwt_cookie = request.cookies.get('jwt_tokens')
        if jwt_cookie is None:
            return jsonify({'error': 'No JWT token provided'}), 401

        # Split the combined tokens into access and refresh tokens
        access_token, refresh_token = jwt_cookie.split(':')

        # Validate the access token
        phone_number = validate_token(access_token)
        if phone_number is None:
            return jsonify({'error': 'Invalid Token'}), 401

        user_ref = db.collection("SERVOO_USERS").document(phone_number)
        user_doc = user_ref.get()

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


# Create a new restaurant object and also update the User's restaurant list.
@app.route('/api/v1/addRestaurant', methods=['POST'])
def add_restaurant():
    try:
        jwt_cookie = request.cookies.get('jwt_tokens')
        data = request.json
        if jwt_cookie is None:
            return jsonify({'error': 'No JWT token provided'}), 401

        # Split the combined tokens into access and refresh tokens
        access_token, refresh_token = jwt_cookie.split(':')

        # Validate the access token
        phone_number = validate_token(access_token)
        if phone_number is None:
            return jsonify({'error': 'Invalid Token'}), 401

        restaurant_id = uuid_generator.generate_random_uuid()

        # The check for valid phone Number and First Name Last Name will be done on UI.
        phone_number = data.get("phone_number")
        restaurant_name = data['restaurant_name']
        # Description will be Optional.
        description = data.get('description', '')
        employees = data.get('employees', [])
        address = data['address']
        theme_color = data['theme_color']

        verification_status = data.get('verification_status', None)
        upi_id = data.get('upi_id', '')
        restaurant_status = data.get('restaurant_status', None)

        # Create New User from entered Data. Enters Blank string or list for items which have not been passed in.
        new_restaurant = RestaurantInfo(restaurant_name=restaurant_name, address=address,
                                        theme_color=theme_color, phone_number=phone_number, employees=employees,
                                        verification_status=verification_status, upi_id=upi_id,
                                        restaurant_status=restaurant_status, description=description)
        new_restaurant_data_dict = new_restaurant.to_dict()
        restaurant_id_str = str(restaurant_id)
        db.collection("SERVOO_RESTAURANTS").document(restaurant_id_str).set(new_restaurant_data_dict)

        print("phone_number of restaurant= " + phone_number)
        # Also add restaurant to the user's restaurant list
        user_doc_ref = db.collection("SERVOO_USERS").document(phone_number)
        user_doc_ref.update({"restaurants_owned": firestore.ArrayUnion([restaurant_id_str])})

        # Create a response with the user data and set cookies for tokens
        return jsonify({
            'message': 'Restaurant registered to successfully!',
            'restaurant': new_restaurant_data_dict
        }), 200
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
