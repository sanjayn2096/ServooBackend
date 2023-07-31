# app.py

from flask import Flask, request, jsonify
from client.BigtableClient import BigtableClient
from controller.MenuController import MenuController
from client.FirestoreClient import db
from model.ServooUserInfo import ServooUserInfo

app = Flask(__name__)

# Configure your Bigtable project ID and instance ID
BIGTABLE_PROJECT_ID = 'servoo-in'
BIGTABLE_INSTANCE_ID = 'servoo-in-menu'

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello Welcome to Servoo APp!'


@app.route('/cart')

@app.route('/api/v1/user', methods=['POST', 'PUT'])
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

            # Check if the user exists in teh Database.
            get_user = db.collection("Users").document(phone_number).get()
            if request.method == 'PUT' and not get_user.exists:
                return jsonify(({'error': 'User not found for Updating'}))

            # Create New User from entered Data.
            new_user = ServooUserInfo(phone_number, f_name, l_name, email)

            db.collection("Users").document(phone_number).set(new_user)

            return 'User registered successfully!'
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/createRestaurant')
@app.route('/checkout')

@app.route('/<int:restaurant_id>/menu', methods=['GET'])
def menu_route(restaurant_id):
    menu = MenuController.get_menu(restaurant_id)
    return jsonify(menu)


if __name__ == '__main__':
    app.run()
