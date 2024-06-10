import pandas as pd
from bson import ObjectId
import random

# Generate sample users
users = []
for i in range(1, 21):
    user = {
        "_id": ObjectId(),
        "email": f"user{i}@example.com",
        "username": f"user{i}",
        "password": "scrypt:32768:8:1$vhFYsEfXd4BRf0ZO$878cdc13f521cc7a42776ebfe5d6802e644c…"
    }
    users.append(user)

# Convert to DataFrame
users_df = pd.DataFrame(users)

# Generate sample UserPreferences
user_preferences = []
for user in users:
    entry = {
        "_id": ObjectId(),
        "userID": user["_id"],
        "hasBarbell": random.choice([True, False]),
        "hasDumbbells": random.choice([True, False]),
        "hasKettlebell": random.choice([True, False]),
        "hasBag": random.choice([True, False]),
        "workoutDays": random.sample(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], 
            k=random.randint(1, 7)
        )
    }
    user_preferences.append(entry)

# Convert to DataFrame
user_preferences_df = pd.DataFrame(user_preferences)

# Save to CSV
users_df.to_csv('users.csv', index=False)
user_preferences_df.to_csv('user_preferences.csv', index=False)

# Display the DataFrames
print(users_df.head())
print(user_preferences_df.head())
