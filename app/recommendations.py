from app.models import UserPreferences, WorkoutList, UserProfiles, UserTrainingPlans, UserWeightings
import random, pandas as pd
from sklearn.neighbors import NearestNeighbors
import bson

def get_workouts_df():
    workouts = list(WorkoutList.objects.only('name', 'type', 'defaultWeighting'))
    workouts_df = pd.DataFrame([{
        'name': w.name,
        'type': w.type,
        'defaultWeighting': w.defaultWeighting
    } for w in workouts])
    return workouts_df

workouts_df = None

def initialize():
    global workouts_df
    workouts_df = get_workouts_df()

#Filters workouts based on equipment
def refine_workouts_for_user(user_id):
    # Retrieve user preferences from the database
    user_preferences = UserPreferences.objects(userID=user_id).first()
    
    if not user_preferences:
        return None, None

    # Extract user equipment preferences
    hasBarbell = user_preferences.hasBarbell
    hasDumbbells = user_preferences.hasDumbbells
    hasKettlebell = user_preferences.hasKettlebell
    hasBag = user_preferences.hasBag

    # Build the query based on user preferences
    query = []
    if hasBarbell:
        query.append({'equipmentNeeded': 'Barbell'})
    if hasDumbbells:
        query.append({'equipmentNeeded': 'Dumbbells'})
    if hasKettlebell:
        query.append({'equipmentNeeded': 'Kettlebell'})
    if hasBag:
        query.append({'equipmentNeeded': 'Bag'})
    
    # Add query to include workouts that need no equipment
    query.append({'equipmentNeeded': []})
    query.append({'equipmentNeeded': 'None'})

    # Perform the query
    refined_workouts = WorkoutList.objects(__raw__={'$or': query}).only('name', 'equipmentNeeded')

    return list(refined_workouts), user_preferences

#Filters days based on days available
def assign_workout_types(available_days):
    base_types = ['Upper Body', 'Lower Body', 'Full Body', 'Flexibility', 'Conditioning']
    
    # Initialize the schedule dictionary and other variables
    type_schedule = {}
    recommended_types = set()  # To track types already recommended
    bag_selected = False  # To ensure 'Bag Work' is selected at least once
    bag_probability = 2  # 'Bag Work' has twice the chance of being selected
    previous_day_main_type = None  # Track the main type recommended on the previous day

    # Loop through each available day to assign workout types
    for i, day in enumerate(available_days):
        selected_types = set()
        
        # Calculate available types based on previous selections
        available_types = list(set(base_types) - recommended_types)
        
        # Ensure 'Bag Work' is selected at least once, preferably by the last day
        if not bag_selected and i == len(available_days) - 1:
            first_type = 'Bag Work'
            bag_selected = True
        else:
            if not available_types:
                # If all base types have been recommended, reset the recommended_types set
                recommended_types.clear()
                available_types = base_types

            # Add 'Bag Work' to the available types with increased probability
            available_types += ['Bag Work'] * bag_probability
            
            # Ensure the selected type is not the same as the previous day's main type if it's 'Upper Body', 'Lower Body', or 'Full Body'
            if previous_day_main_type in ['Upper Body', 'Lower Body', 'Full Body'] and previous_day_main_type in available_types:
                available_types.remove(previous_day_main_type)

            first_type = random.choice(available_types)
        
        # Add the selected type to the day's schedule and update tracking sets
        selected_types.add(first_type)
        type_schedule[day] = [first_type]
        recommended_types.add(first_type)
        if first_type in ['Upper Body', 'Lower Body', 'Full Body']:
            previous_day_main_type = first_type  # Update previous day main type if it's one of the three main types

        # If 'Bag Work' is selected, ensure 'Flexibility' and 'Conditioning' are also added
        if first_type == 'Bag Work':
            type_schedule[day].extend(['Flexibility', 'Conditioning'])
            selected_types.update(['Flexibility', 'Conditioning'])
            recommended_types.update(['Flexibility', 'Conditioning'])
            bag_selected = True

        # 50% chance to select another type, but not the same type as the previous day's main type
        if random.random() < 0.5:
            remaining_types = list(set(base_types) - selected_types)
            if remaining_types:
                if previous_day_main_type in ['Upper Body', 'Lower Body', 'Full Body'] and previous_day_main_type in remaining_types:
                    remaining_types.remove(previous_day_main_type)
                second_type = random.choice(remaining_types)
                type_schedule[day].append(second_type)
                selected_types.add(second_type)
                recommended_types.add(second_type)
                if second_type in ['Upper Body', 'Lower Body', 'Full Body']:
                    previous_day_main_type = second_type  # Update previous day main type if second type is one of the three main types

        # Adjust the probability for 'Bag Work' for the next day
        bag_probability = 2 if 'Bag Work' not in selected_types else 1

    return type_schedule

#Creates matrix in preparation for KNN model
def create_user_item_matrix(user_id):
    refined_workouts, _ = refine_workouts_for_user(user_id)
    if not refined_workouts:
        return None

    refined_workout_names = [workout.name for workout in refined_workouts]

    # Fetch all user weightings from UserWeightings collection
    user_weightings = list(UserWeightings.objects(userID=user_id))

    # Filter user weightings based on refined workout names
    user_weightings = [w for w in user_weightings if w.workoutID.name in refined_workout_names]

    if not user_weightings:
        user_weightings_df = pd.DataFrame(columns=['userID', 'workoutID', 'weighting'])
    else:
        user_weightings_df = pd.DataFrame([{
            'userID': str(w.userID.id),
            'workoutID': w.workoutID.name,
            'weighting': w.weighting
        } for w in user_weightings])

    # Fetch workout default weightings from WorkoutList collection
    workouts = list(WorkoutList.objects(name__in=refined_workout_names).only('name', 'defaultWeighting'))

    workouts_df = pd.DataFrame([{
        'name': w.name,
        'defaultWeighting': w.defaultWeighting
    } for w in workouts])

    # Create a filtered DataFrame with only the refined workouts
    if not user_weightings_df.empty:
        filtered_weightings_df = user_weightings_df[user_weightings_df['workoutID'].isin(refined_workout_names)]
    else:
        filtered_weightings_df = pd.DataFrame(columns=['userID', 'workoutID', 'weighting'])

    # Add default weightings for workouts not present in user_weightings_df
    missing_workouts = set(refined_workout_names) - set(filtered_weightings_df['workoutID'])
    missing_workouts_df = pd.DataFrame([{
        'userID': str(user_id),
        'workoutID': workout,
        'weighting': workouts_df[workouts_df['name'] == workout]['defaultWeighting'].values[0]
    } for workout in missing_workouts])

    filtered_weightings_df = pd.concat([filtered_weightings_df, missing_workouts_df], ignore_index=True)

    # Pivot the table to create a user-item matrix
    user_item_matrix = filtered_weightings_df.pivot(index='userID', columns='workoutID', values='weighting').fillna(0)
    
    return user_item_matrix

#Uses KNN to recommend workouts
def recommend_workouts_knn(user_id, n_neighbors=5):
    user_item_matrix = create_user_item_matrix(str(user_id))
    if user_item_matrix is None:
        return []

    # Ensure there are enough samples for KNN
    if user_item_matrix.shape[0] < n_neighbors:
        n_neighbors = user_item_matrix.shape[0]

    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(user_item_matrix)

    user_index = user_item_matrix.index.get_loc(str(user_id))
    distances, indices = knn.kneighbors(user_item_matrix.iloc[user_index, :].values.reshape(1, -1), n_neighbors=n_neighbors)

    similar_users_indices = indices.flatten()
    similar_users = user_item_matrix.iloc[similar_users_indices]
    recommended_workouts = similar_users.mean(axis=0).sort_values(ascending=False)

    user_workouts = user_item_matrix.loc[str(user_id)]
    low_rated_workouts = user_workouts[user_workouts < user_workouts.max()]
    recommended_workouts = recommended_workouts[low_rated_workouts.index]

    return recommended_workouts.index.tolist()[:10]

#increases chance of higher weighted workouts to be selected
def weighted_random_choice(workouts, weights):
    total = sum(weights)
    r = random.uniform(0, total)
    upto = 0
    for workout, weight in zip(workouts, weights):
        if upto + weight >= r:
            return workout
        upto += weight
    return workouts[-1]  # Fallback in case of rounding errors

#Generates a fresh weekly training plan for the user
def generate_weekly_plan(user_id):
    # Fetch user preferences
    user_preferences = UserPreferences.objects(userID=user_id).first()
    if not user_preferences:
        return {}

    available_days = user_preferences.workoutDays

    # Get recommended workouts
    recommended_workouts = recommend_workouts_knn(user_id)
    all_workouts = workouts_df['name'].tolist()
    all_weights = workouts_df['defaultWeighting'].tolist()

    # Assign workout types to available days
    type_schedule = assign_workout_types(available_days)

     # Delete existing plans for the user
    UserTrainingPlans.objects(userID=user_id).delete()

    # Map recommended workouts to workout types
    workout_plan = {}
    for day in available_days:
        workout_plan[day] = []
        for workout_type in type_schedule[day]:
            possible_workouts = [workout for workout in recommended_workouts if workouts_df[workouts_df['name'] == workout]['type'].values[0] == workout_type]
            
            if possible_workouts:
                weights = [workouts_df[workouts_df['name'] == workout]['defaultWeighting'].values[0] for workout in possible_workouts]
                selected_workout = weighted_random_choice(possible_workouts, weights)
                workout_plan[day].append(selected_workout)
                recommended_workouts.remove(selected_workout)
            else:
                possible_workouts = [workout for workout in all_workouts if workouts_df[workouts_df['name'] == workout]['type'].values[0] == workout_type]
                weights = [workouts_df[workouts_df['name'] == workout]['defaultWeighting'].values[0] for workout in possible_workouts]
                selected_workout = weighted_random_choice(possible_workouts, weights)
                workout_plan[day].append(selected_workout)

            # Debugging prints
            print(f"Selected Workout: {selected_workout}")
            workout_obj = WorkoutList.objects(name=selected_workout).first()
            if workout_obj:
                print(f"Workout Object: {workout_obj}")
                user_training_plan = UserTrainingPlans(
                    userID=user_id,
                    workoutID=workout_obj.id,
                    dayOfWeek=day
                )
                user_training_plan.save()
            else:
                print(f"Workout {selected_workout} not found in WorkoutList")

#Retrieves the user's weekly training plan
def fetch_weekly_plan(user_id):
    weekly_plan = {}
    training_plans = UserTrainingPlans.objects(userID=user_id)
    
    for plan in training_plans:
        day_of_week = plan.dayOfWeek
        if day_of_week not in weekly_plan:
            weekly_plan[day_of_week] = []

        print(f"Processing plan: {plan.to_json()}")
        print(f"workoutID type: {type(plan.workoutID)}")
        
        # Since workoutID is a ReferenceField, we can directly use it to fetch the workout object
        workout_obj = plan.workoutID  # This is the referenced WorkoutList object
        if workout_obj:
            weekly_plan[day_of_week].append(workout_obj.name)
        else:
            print(f"Workout with workoutID {plan.workoutID} not found.")
    
    return weekly_plan
