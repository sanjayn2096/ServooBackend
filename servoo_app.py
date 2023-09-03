# servoo_app.py
from flask import Flask, request, jsonify, session, Response
from google.cloud import firestore
from client.FirestoreClient import db
from controller.MenuController import MenuController
from model.FoodMenuItem import FoodMenuItem
from model.RestaurantOrders import RestaurantOrders
from model.ServooUserInfo import ServooUserInfo
from model.RestaurantInfo import RestaurantInfo
from flask_cors import CORS
from util import uuid_generator
import jwt
import datetime

app = Flask(__name__)
app.secret_key = 'O9MG5BZGZO5MOCI'
CORS(app, supports_credentials=True)


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
            # Need to do this as set cookie does not have option for sameSite cookie attribute
            response.headers.add('Set-Cookie', f"jwt_tokens={combined_tokens}; SameSite=None; Secure")

            return response, 200
    except Exception as e:
        return jsonify({'error': str(e)})


# This function generates a new access token and refresh token for a given user ID
def generate_tokens(phone_number):
    access_token_payload = {'phone_number': phone_number,
                            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=720)}
    access_token = jwt.encode(access_token_payload, app.secret_key, algorithm='HS256')
    refresh_token_payload = {'phone_number': phone_number,
                             'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=720)}
    refresh_token = jwt.encode(refresh_token_payload, app.secret_key, algorithm='HS256')
    return access_token, refresh_token


# This function validates an access token and returns the user ID associated with it
def validate_token(access_token):
    try:
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


@app.route('/api/v1/foodItem', methods=['POST'])
def add_food_item():
    try:
        if request.method == 'POST':
            data = request.json
            # The check for valid phone Number and First Name Last Name will be done on UI.
            restaurant_id = data.get("restaurant_id")
            item_name = data.get("item_name")
            category = data['category', "DEFAULT"]
            price = data['price']
            description = data['description']
            image_url = data['image_url']
            stock_status = data['stock_status', 'IN_STOCK']
            number_of_times_ordered = data['number_times_ordered', '0']

            # Create New Food Item from entered Data.
            new_food_item = FoodMenuItem(restaurant_id, item_name, price,
                                         description, image_url, stock_status,
                                         number_of_times_ordered)
            new_food_item_data = new_food_item.to_dict()
            db.collection("SERVOO_FOOD_ITEM").document(restaurant_id).collection(category).set(new_food_item_data)

            return jsonify({'message': 'Food item created successfully!', 'food_item': new_food_item_data}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


# Fetches Food Items by Restaurant Id and Category.
# If no category is provided, fetch all the default category items
@app.route('/api/v1/foodItem/<restaurant_id>', methods=['GET'])
def get_food_items(restaurant_id):
    try:
        # Get the category from the query parameters
        category = request.args.get('category', 'DEFAULT')
        food_items = []
        if category == 'DEFAULT':
            # Query the database to get food items for the given restaurant_id from all categories
            food_item_documents = db.collection("SERVOO_FOOD_ITEM").document(restaurant_id).collections()

            for category_collection in food_item_documents:
                for doc in category_collection.stream():
                    food_item_data = doc.to_dict()
                    food_items.append(food_item_data)
        else:
            # Query the database to get food items for the given restaurant_id and category
            food_item_documents = db.collection("SERVOO_FOOD_ITEM").document(restaurant_id). \
                collection(category).stream()

            for doc in food_item_documents:
                food_item_data = doc.to_dict()
                food_items.append(food_item_data)

        for doc in food_item_documents:
            food_item_data = doc.to_dict()
            food_items.append(food_item_data)

        return jsonify({'food_items': food_items}), 200
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
@app.route('/api/v1/restaurant', methods=['POST'])
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


# Check associated restaurant with User, return the restaurants owned.
@app.route('/api/v1/restaurant', methods=['GET'])
def get_restaurant():
    try:
        # get user number
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
            return jsonify({'error': 'Document not found'}), 404

        user_info = ServooUserInfo.from_dict(user_doc.to_dict())
        user_restaurant_id = user_info.restaurants_owned

        user_restaurants = []
        for restaurant_id in user_restaurant_id:
            restaurant_ref = db.collection("SERVOO_RESTAURANTS").document(restaurant_id)
            restaurant_doc = restaurant_ref.get()
            if not restaurant_doc.exists:
                return jsonify({'error': 'Restaurant not found'}), 404
            restaurant_info = RestaurantInfo.from_dict(restaurant_doc.to_dict())
            user_restaurants.append(restaurant_info.to_dict())
        return jsonify({"Restaurants Owned": user_restaurants}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


# Should read any updates to SERVOO_ORDERS table
# How often should the table update ?  HOw many read can it handle. - If too many reads what is the cost.
# Let's populate the table manually
@app.route('/api/v1/orders/<restaurant_id>', methods=['GET'])
def fetch_orders_by_restaurant(restaurant_id):
    try:
        if request.method == 'GET':
            # get user number
            jwt_cookie = request.cookies.get('jwt_tokens')
            if jwt_cookie is None:
                return jsonify({'error': 'No JWT token provided'}), 401

            # Split the combined tokens into access and refresh tokens
            access_token, refresh_token = jwt_cookie.split(':')

            # Validate the access token
            phone_number = validate_token(access_token)

            # Query the Firestore subcollection "orders" under the specified "restaurant_id"
            orders = []
            order_documents = db.collection("SERVOO_ORDERS").document(restaurant_id).collection("ORDERS").stream()

            for doc in order_documents:
                order_data = doc.to_dict()
                orders.append(order_data)

            return jsonify({'orders': orders}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/v1/orders', methods=['POST'])
def create_order():
    # This can be named Checkout - Checkout should create an order entry in the Servoo_Orders Table.
    try:
        if request.method == 'POST':
            data = request.json

            # Extract order details from the request data
            restaurant_id = data.get("restaurant_id")
            order_id = data.get("order_id")
            food_menu_item = data.get("food_menu_item")
            order_instructions = data.get("order_instructions")
            order_total = data.get("order_total")
            transaction_id = data.get("transaction_id")
            order_status = data.get("order_status")
            order_rating = data.get("order_rating")

            # Create a new order instance
            new_order = RestaurantOrders(
                restaurant_id=restaurant_id,
                order_id=order_id,
                food_menu_item=food_menu_item,
                order_instructions=order_instructions,
                order_total=order_total,
                transaction_id=transaction_id,
                order_status=order_status,
                order_rating=order_rating
            )

            # Save the order data to Firestore under the specific restaurant's subcollection
            order_ref = db.collection("SERVOO_ORDERS").document(restaurant_id).collection("ORDERS").document(order_id)
            order_ref.set(new_order.to_dict())  # Convert the object to a dictionary

            return jsonify({'message': 'Order created successfully!', 'order_id': order_id}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/v1/orders/update_status', methods=['PUT'])
def update_order_status():
    try:
        if request.method == 'PUT':
            data = request.json

            # Extract order details from the request data
            restaurant_id = data.get("restaurant_id")
            order_id = data.get("order_id")
            new_status = data.get("new_status")

            # Retrieve the order document
            order_ref = db.collection("SERVOO_ORDERS").document(restaurant_id).collection("ORDERS").document(order_id)
            order_doc = order_ref.get()

            if order_doc.exists:
                # Update the order status
                order_ref.update({"order_status": new_status})

                return jsonify({'message': 'Order status updated successfully!', 'order_id': order_id}), 200
            else:
                return jsonify({'error': 'Order not found'}), 404

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


def menu_route(restaurant_id):
    menu = MenuController.get_menu(restaurant_id)
    return jsonify(menu)


if __name__ == '__main__':
    app.run()
