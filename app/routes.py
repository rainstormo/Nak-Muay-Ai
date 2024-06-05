from flask import Blueprint, jsonify
from app.models import UserProfiles

#Blueprint organizes routes in a modular way.
bp = Blueprint('main', __name__)

@bp.route('/users', methods=['GET'])
def get_users():
    try:
        users = UserProfiles.objects()
        print(f"Found users: {users.count()}")  # Debugging: Print the count of users
        for user in users:
            print(user.to_json())  # Debugging: Print each user document
        users_json = users.to_json()
        print(users_json)  # Debugging: Print the JSON serialization
        return users_json
    except Exception as e:
        print(f"Error: {e}")  # Debugging: Print any errors
        return jsonify({"error": str(e)}), 500

@bp.route('/', methods=['GET'])
def index():
    return "Welcome to Nak Muay AI API"
