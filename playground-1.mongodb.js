// Switch to the NakMuay_db database
use('NakMuay_db');

// Aggregate to group by userID and show all training plans
db.UserTrainingPlans.aggregate([
    {
        $group: {
            _id: "$userID",
            trainingPlans: { $push: "$$ROOT" } // Store all training plans for each user
        }
    }
]);
