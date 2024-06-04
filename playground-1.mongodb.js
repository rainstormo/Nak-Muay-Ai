use('NakMuay_db');

db.UserPreferences.aggregate([
  {
    $lookup: {
      from: "UserProfiles",
      localField: "userID",
      foreignField: "_id",
      as: "userDetails"
    }
  },
  {
    $unwind: "$userDetails"
  },
  {
    $project: {
      _id: 0,
      username: "$userDetails.username",
      hasBarbell: 1,
      hasDumbbells: 1,
      hasKettlebell: 1,
      hasBag: 1,
      workoutDays: 1
    }
  },
  {
    $limit: 10
  }
]);
