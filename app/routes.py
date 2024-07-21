from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies, unset_jwt_cookies
from app.models import UserProfiles, UserPreferences
import logging
from app.recommendations import *

#Blueprint organizes routes in a modular way.
bp = Blueprint('main', __name__)

@bp.before_app_first_request
def setup():
    initialize()

# Configure logging
logging.basicConfig(level=logging.INFO)

@bp.route('/', methods=['GET'])
def index():
    return render_template('landing.html')

#Debugging route to check if user data can be extracted from mongodb
@bp.route('/debug/users', methods=['GET'])
def debug_users():
    try:
        users = UserProfiles.objects()
        users_json = users.to_json()
        logging.info(f"Users: {users_json}")
        return users_json, 200
    except Exception as e:
        logging.error(f"Error fetching users: {e}")
        return jsonify(message="Error fetching users"), 500

#Debugging for prefences
@bp.route('/debug/preferences', methods=['GET'])
def debug_preferences():
    try:
        preferences = UserPreferences.objects()
        preferences_json = preferences.to_json()
        logging.info(f"Preferences: {preferences_json}")
        return preferences_json, 200
    except Exception as e:
        logging.error(f"Error fetching preferences: {e}")
        return jsonify(message="Error fetching preferences"), 500

# test route to ensure jwt_required() fn works. Usually '@jwt_required()'
# Will be included within protected routes.
@bp.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

#Registering
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        data = request.form
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')

        existing_user_email = UserProfiles.objects(email=email).first()
        existing_user_username = UserProfiles.objects(username=username).first()
        
        if existing_user_email:
            return jsonify(message="Email already exists"), 400
        if existing_user_username:
            return jsonify(message="Username already exists"), 400

        hashed_password = generate_password_hash(password)
        new_user = UserProfiles(email=email, username=username, password=hashed_password)
        new_user.save()

        logging.info(f'New user saved: {new_user}')

        workout_days = data.getlist('workoutDays')
        
        preferences = UserPreferences(
            userID=new_user,
            hasBarbell='hasBarbell' in data,
            hasDumbbells='hasDumbbells' in data,
            hasKettlebell='hasKettlebell' in data,
            hasBag='hasBag' in data,
            workoutDays=workout_days
        )
        preferences.save()

        logging.info(f'User preferences saved: {preferences}')

        access_token = create_access_token(identity=str(new_user.id))
        response = make_response(redirect(url_for('main.landing')))
        set_access_cookies(response, access_token)

        return response

#Logging in
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    if request.method == 'POST':
        # Retrieves form data entered by user
        email = request.form.get('email')
        password = request.form.get('password')

        # Looks the user up in the database then checks if the password matches,
        # if it matches, a JWT token is generated.
        user = UserProfiles.objects(email=email).first()
        if user and check_password_hash(user.password, password):
            access_token = create_access_token(identity=str(user.id))
            response = make_response(render_template('landing.html'))
            response.set_cookie('access_token_cookie', access_token, httponly=True)
            return response
        return jsonify(message="Invalid credentials"), 401

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

#Landing page
@bp.route('/landing', methods=['GET'])
def landing():
    return render_template('landing.html')

#logging out
@bp.route('/logout', methods=['GET'])
@jwt_required(locations=['cookies'])
def logout():
    response = redirect(url_for('main.login'))
    unset_jwt_cookies(response)  # Clear the JWT cookies to log the user out
    return response

@bp.route('/weekly_plan', methods=['GET'])
@jwt_required()
def weekly_plan():
    current_user = get_jwt_identity()
    user = UserProfiles.objects(id=current_user).first()

    if user:
        weekly_plan = fetch_weekly_plan(user.id)
        print(f"Weekly Plan: {weekly_plan}")  # Debugging statement

        if not weekly_plan:
            return jsonify(message="No weekly plan found"), 404

        return render_template('weekly_plan.html', user=user, weekly_plan=weekly_plan)
    else:
        return jsonify(message="User not found"), 404
    
@bp.route('/generate_new_plan', methods=['POST'])
@jwt_required()
def generate_new_plan():
    current_user = get_jwt_identity()
    user = UserProfiles.objects(id=current_user).first()
    
    if user:
        generate_weekly_plan(user.id)  # Generate the plan, no need to return it here
        return redirect(url_for('main.weekly_plan'))  # Redirect to the weekly_plan view
    else:
        return jsonify(message="User not found"), 404


