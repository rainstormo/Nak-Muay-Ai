// MongoDB Playground
use('NakMuay_db');

// Verify the current database
db

// Fetch all UserTrainingPlans
db.UserTrainingPlans.find({}).forEach(function(plan) {
    // Fetch the corresponding workout from WorkoutList
    var workout = db.WorkoutList.findOne({ workoutID: plan.workoutID });
    if (workout) {
        // Update the workoutID in UserTrainingPlans to match the _id in WorkoutList
        db.UserTrainingPlans.updateOne(
            { _id: plan._id },
            { $set: { workoutID: workout._id } }
        );
    } else {
        print("Workout not found for plan:", plan);
    }
});



