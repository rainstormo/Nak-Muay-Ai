// Use the correct database
use('NakMuay_db');

// Find the preferences for the specific user
db.UserPreferences.find({ userID: ObjectId("66612a0a2f15fc482efbd7c1") }).pretty();
