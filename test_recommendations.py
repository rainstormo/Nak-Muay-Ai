from app import create_app
from app.recommendations import refine_workouts_for_user, assign_workout_types, create_user_item_matrix, recommend_workouts_knn, generate_weekly_plan, initialize, fetch_weekly_plan
from app.models import UserProfiles

app = create_app()

# with app.app_context():
#     user = UserProfiles.objects(email="sammy@hotmail.com").first()
#     if user:
#         refined_workouts, user_preferences = refine_workouts_for_user(user.id)
        
#         print("Refined Workouts:")
#         for workout in refined_workouts:
#             print(f"Name: {workout.name}, Equipment Needed: {workout.equipmentNeeded}")
        
#         print("\nUser Preferences:")
#         print(f"User ID: {user_preferences.userID}")
#         print(f"Has Barbell: {user_preferences.hasBarbell}")
#         print(f"Has Dumbbells: {user_preferences.hasDumbbells}")
#         print(f"Has Kettlebell: {user_preferences.hasKettlebell}")
#         print(f"Has Bag: {user_preferences.hasBag}")
#         print(f"Workout Days: {user_preferences.workoutDays}")
#     else:
#         print("User not found.")

# with app.app_context():
#     user = UserProfiles.objects(email="sammy@hotmail.com").first()
#     if user:
#         refined_workouts, user_preferences = refine_workouts_for_user(user.id)
        
#         print("Refined Workouts:")
#         for workout in refined_workouts:
#             print(f"Name: {workout.name}, Equipment Needed: {workout.equipmentNeeded}")
        
#         type_schedule = assign_workout_types(user_preferences.workoutDays)
#         print("\nType Schedule:")
#         for day, types in type_schedule.items():
#             print(f"{day}: {types}")
#     else:
#         print("User not found.")

#testing matrix
# with app.app_context():
#     user = UserProfiles.objects(email="sammy@hotmail.com").first()
#     if user:
#         user_item_matrix = create_user_item_matrix(user.id)
#         if user_item_matrix is not None:
#             print("User-Item Matrix:")
#             print(user_item_matrix)
#         else:
#             print("No refined workouts found.")
#     else:
#         print("User not found.")

# #testing KNN model
# with app.app_context():
#     user = UserProfiles.objects(email="sammy@hotmail.com").first()
#     if user:
#         top_recommended_workouts = recommend_workouts_knn(user.id)
#         print("Top Recommended Workouts:", top_recommended_workouts)
#     else:
#         print("User not found.")

# #Testing weekly plan generator
with app.app_context():
    initialize()
    user = UserProfiles.objects(email="justin@rc.hotmail").first()
    if user:
        weekly_plan = generate_weekly_plan(user.id)
        print("Weekly Plan:", weekly_plan)
    else:
        print("User not found.")

#Testing weekly plan outputter
with app.app_context():
    user = UserProfiles.objects(email="justin@rc.hotmail").first()
    if user:
        weekly_plan = fetch_weekly_plan(user.id)
        print("Weekly Plan:", weekly_plan)
    else:
        print("User not found.")