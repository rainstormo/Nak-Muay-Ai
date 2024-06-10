from pymongo import MongoClient
from bson import ObjectId

# MongoDB connection setup (replace with your actual connection string)
connection_string = "mongodb+srv://muhammadalmaery:muaythai@cluster0.yfhb5od.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client['NakMuay_db']

# Function to get user preferences and refine workouts based on available equipment
def refine_workouts_for_user(user_id):
    # Retrieve user preferences
    user_preferences = db.UserPreferences.find_one({"userID": ObjectId(user_id)})

    if user_preferences:
        # Extract user equipment preferences
        hasBarbell = user_preferences['hasBarbell']
        hasDumbbells = user_preferences['hasDumbbells']
        hasKettlebell = user_preferences['hasKettlebell']
        hasBag = user_preferences['hasBag']

        # Build the query
        query = {"$or": []}
        
        if hasBarbell:
            query["$or"].append({"equipmentNeeded": "Barbell"})
        if hasDumbbells:
            query["$or"].append({"equipmentNeeded": "Dumbbells"})
        if hasKettlebell:
            query["$or"].append({"equipmentNeeded": "Kettlebell"})
        if hasBag:
            query["$or"].append({"equipmentNeeded": "Bag"})
        
        # Include workouts that require no equipment (None or empty array)
        query["$or"].append({"equipmentNeeded": "None"})
        query["$or"].append({"equipmentNeeded": {"$size": 0}})
        
        # Return refined workouts (name and equipmentNeeded)
        refined_workouts = list(db.WorkoutList.find(query, {"name": 1, "equipmentNeeded": 1, "_id": 0}))
        return refined_workouts
    else:
        return []

# Example usage
sample_user_id = "60d21b4967d0d8992e610c8c"
refined_workouts = refine_workouts_for_user(sample_user_id)
for workout in refined_workouts:
    print(workout)
