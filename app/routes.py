from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models import UserProfiles, UserPreferences

#Blueprint organizes routes in a modular way.
bp = Blueprint('main', __name__)

#Default route
@bp.route('/', methods=['GET'])
def index():
    return "Welcome to Nak Muay AI API"

#Debugging route to check if user data can be extracted from mongodb
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

#Method for logged in users to view their profile
@bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user = get_jwt_identity()
    user = UserProfiles.objects(id=current_user).first()
    if not user:
        return jsonify(message="User not found"), 404
    return jsonify(
        email=user.email,
        username=user.username
    ), 200

#Allows logged-in users to update their profile information.
@bp.route('/user/profile', methods=['POST'])
@jwt_required()
def update_profile():
    current_user = get_jwt_identity()
    user = UserProfiles.objects(id=current_user).first()

    if not user:
        return jsonify(message="User not found"), 404

    data = request.get_json()

    # Check if the username or email already exists
    if 'username' in data and UserProfiles.objects(username=data['username']).first() and data['username'] != user.username:
        return jsonify(message="Username already exists"), 400
    if 'email' in data and UserProfiles.objects(email=data['email']).first() and data['email'] != user.email:
        return jsonify(message="Email already exists"), 400
    
    # Update fields if they exist in the request data
    if 'username' in data:
        user.username = data['username']
    if 'email' in data:
        user.email = data['email']
    if 'password' in data:
        user.password = generate_password_hash(data['password'])

    user.save()
    return jsonify(message="Profile updated successfully"), 200

#Method for registering users to add their preferences
@bp.route('/user/preferences/add', methods=['POST'])
@jwt_required()
def add_preferences():
    current_user = get_jwt_identity()
    data = request.get_json()

    preferences = UserPreferences(
        userID=current_user,
        hasBarbell=data['hasBarbell'],
        hasDumbbells=data['hasDumbbells'],
        hasKettlebell=data['hasKettlebell'],
        hasBag=data['hasBag'],
        workoutDays=data['workoutDays']
    )
    preferences.save()
    return jsonify(message="Preferences added successfully"), 201

#Method for users to view their preferences
@bp.route('/user/preferences', methods=['GET'])
@jwt_required()
def get_preferences():
    current_user = get_jwt_identity()
    preferences = UserPreferences.objects(userID=current_user).first()
    if not preferences:
        return jsonify(message="Preferences not found"), 404
    return jsonify(
        hasBarbell=preferences.hasBarbell,
        hasDumbbells=preferences.hasDumbbells,
        hasKettlebell=preferences.hasKettlebell,
        hasBag=preferences.hasBag,
        workoutDays=preferences.workoutDays
    ), 200

#Allows logged-in users to update their equipment and workout day preferences.
@bp.route('/user/preferences', methods=['POST'])
@jwt_required()
def update_preferences():
    current_user = get_jwt_identity()
    preferences = UserPreferences.objects(userID=current_user).first()

    if not preferences:
        return jsonify(message="Preferences not found"), 404

    data = request.get_json()
    preferences.update(**data)
    return jsonify(message="Preferences updated successfully"), 200