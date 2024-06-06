from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import UserProfiles

#Blueprint organizes routes in a modular way.
bp = Blueprint('main', __name__)

#Default route
@bp.route('/', methods=['GET'])
def index():
    return "Welcome to Nak Muay AI API"

#Debugging route to check if users can be extracted from mongodb
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

@bp.route('/register', methods=['POST'])
def register():
    #Extracts json data entered by the user
    data = request.get_json()
    email = data['email']
    username = data['username']

    # Check if the email or username already exists
    if UserProfiles.objects(email=email).first():
        return jsonify(message="Email already exists"), 400
    if UserProfiles.objects(username=username).first():
        return jsonify(message="Username already exists"), 400

    #Hashes the user-entered password
    hashed_password = generate_password_hash(data['password'])

    #Assigns user entered details to the database
    new_user = UserProfiles(
        email=email,
        username=username,
        password=hashed_password
    )
    new_user.save()

    return jsonify(message="User registered successfully"), 201

@bp.route('/login', methods=['POST'])
def login():

    #Retrieves json data entered by user
    data = request.get_json()

    #Looks the user up in the database then checks if the password matches,
    #if it matches, a JWT token is generated.
    user = UserProfiles.objects(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=str(user.id))
        return jsonify(access_token=access_token), 200
    return jsonify(message="Invalid credentials"), 401

# test route to ensure jwt_required() fn works. Usually '@jwt_required()'
# Will be included within protected routes.
@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200