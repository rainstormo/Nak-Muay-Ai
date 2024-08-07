from flask import Blueprint, request, jsonify, render_template, redirect, url_for, make_response, flash
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
            weekly_plan = {}  # Provide an empty plan to indicate no plan available

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

@bp.route('/preferences', methods=['GET'])
@jwt_required()
def view_preferences():
    current_user_id = get_jwt_identity()  # Retrieve the user ID from JWT
    user_profile = UserProfiles.objects(id=current_user_id).first()

    if not user_profile:
        flash('User not found.', 'danger')
        return redirect(url_for('main.index'))

    user_preferences = UserPreferences.objects(userID=user_profile).first()
    
    if not user_preferences:
        user_preferences = UserPreferences(
            userID=user_profile,
            hasBarbell=False,
            hasDumbbells=False,
            hasKettlebell=False,
            hasBag=False,
            workoutDays=[]
        )
        user_preferences.save()

    return render_template('preferences.html', user=user_preferences)

@bp.route('/update_preferences', methods=['POST'])
@jwt_required()
def update_preferences():
    current_user_id = get_jwt_identity()  # Retrieve the user ID from JWT
    user_profile = UserProfiles.objects(id=current_user_id).first()

    if not user_profile:
        flash('User not found.', 'danger')
        return redirect(url_for('main.index'))

    # Retrieve user preferences from the form
    hasBarbell = 'hasBarbell' in request.form
    hasDumbbells = 'hasDumbbells' in request.form
    hasKettlebell = 'hasKettlebell' in request.form
    hasBag = 'hasBag' in request.form
    workoutDays = request.form.getlist('workoutDays')

    # Find existing preferences or create new ones
    user_preferences = UserPreferences.objects(userID=user_profile).first()
    
    if user_preferences:
        user_preferences.update(
            hasBarbell=hasBarbell,
            hasDumbbells=hasDumbbells,
            hasKettlebell=hasKettlebell,
            hasBag=hasBag,
            workoutDays=workoutDays
        )
    else:
        user_preferences = UserPreferences(
            userID=user_profile,
            hasBarbell=hasBarbell,
            hasDumbbells=hasDumbbells,
            hasKettlebell=hasKettlebell,
            hasBag=hasBag,
            workoutDays=workoutDays
        )
        user_preferences.save()

    flash('Preferences updated successfully.', 'success')
    return redirect(url_for('main.view_preferences'))

@bp.route('/begin_training_day', methods=['GET'])
@jwt_required()
def begin_training_day():
    current_user = get_jwt_identity()
    user = UserProfiles.objects(id=current_user).first()

    if user:
        # Fetch the user's training plan
        user_training_plan = UserTrainingPlans.objects(userID=user.id).order_by('dayOfWeek').first()

        if not user_training_plan:
            return render_template('begin_training_day.html', user=user, workouts=[], message="No training plan found. Please generate a plan.")

        # Determine the first training day
        first_training_day = user_training_plan.dayOfWeek

        # Fetch all workouts for the first training day
        workouts = UserTrainingPlans.objects(userID=user.id, dayOfWeek=first_training_day)
        workout_details = []

        for workout in workouts:
            # Fetch workout information by integer workoutID
            workout_info = WorkoutList.objects(workoutID=workout.workoutID).first()
            if workout_info:
                # Fetch user's personal weighting or use default if none exists
                user_weighting = UserWeightings.objects(userID=user.id, workoutID=workout.workoutID).first()
                weighting = user_weighting.weighting if user_weighting else workout_info.defaultWeighting

                workout_details.append({
                    'name': workout_info.name,
                    'description': workout_info.description,
                    'videoLink': workout_info.videoLink,
                    'workoutID': workout_info.workoutID,
                    'weighting': weighting
                })

        return render_template('begin_training_day.html', user=user, workouts=workout_details, message=None)
    else:
        return jsonify(message="User not found"), 404

@bp.route('/update_weighting', methods=['POST'])
@jwt_required()
def update_weighting():
    current_user_id = get_jwt_identity()
    workout_id = request.form.get('workoutID')
    action = request.form.get('action')

    # Validate inputs
    if not workout_id or action not in ['increase', 'decrease']:
        return redirect(url_for('main.begin_training_day', message="Invalid input: workoutID or action missing or incorrect"))

    # Convert workout_id to int
    try:
        workout_id = int(workout_id)
    except ValueError:
        return redirect(url_for('main.begin_training_day', message="Invalid workout ID"))

    # Determine increment/decrement value
    increment = 1 if action == 'increase' else -1

    # Fetch or create the UserWeighting document
    user_weighting = UserWeightings.objects(userID=current_user_id, workoutID=workout_id).first()
    if user_weighting:
        # Update existing weighting
        new_weighting = max(0, user_weighting.weighting + increment)  # Ensure weighting doesn't go below 0
        user_weighting.weighting = new_weighting
        user_weighting.save()
    else:
        # Create new weighting if it doesn't exist
        new_weighting = max(0, increment)  # If not existing, initialize with increment
        user_weighting = UserWeightings(userID=current_user_id, workoutID=workout_id, weighting=new_weighting)
        user_weighting.save()

    return redirect(url_for('main.begin_training_day'))  # Redirect to the page showing workouts

@bp.route('/complete_day', methods=['POST'])
@jwt_required()
def complete_day():
    current_user_id = get_jwt_identity()

    # Fetch the user's training plan
    user_training_plan = UserTrainingPlans.objects(userID=current_user_id).order_by('dayOfWeek').first()

    if not user_training_plan:
        return jsonify(message="No training plan found."), 404

    # Remove the current day from the user's training plan
    user_training_plan.delete()

    # Redirect to the landing page
    return redirect(url_for('main.landing'))

