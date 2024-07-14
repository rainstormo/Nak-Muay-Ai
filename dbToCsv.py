import csv
from pymongo import MongoClient

# MongoDB connection setup (replace with your actual connection string)
connection_string = "mongodb+srv://muhammadalmaery:muaythai@cluster0.yfhb5od.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(connection_string)
db = client['NakMuay_db']

# Fetch all workouts
workouts = db.WorkoutList.find()

# Define the CSV file path
csv_file_path = 'workout_list.csv'

# Define the CSV headers
csv_headers = ['name', 'description', 'equipmentNeeded', 'type', 'videoLink', 'muscleGroups', 'level', 'defaultWeighting']

# Write data to CSV file
with open(csv_file_path, mode='w', newline='', encoding='utf-8') as csv_file:
    writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
    writer.writeheader()
    for workout in workouts:
        # Remove unwanted fields
        workout.pop('_id', None)
        workout.pop('workoutID', None)
        # Flatten the lists into strings
        workout['equipmentNeeded'] = ', '.join(workout['equipmentNeeded'])
        workout['muscleGroups'] = ', '.join(workout['muscleGroups'])
        writer.writerow(workout)

print(f"WorkoutList data has been exported to {csv_file_path}")
