from mongoengine import Document, StringField, BooleanField, ListField, ReferenceField, DateTimeField, IntField, connect

# Ensure the database is connected using MongoEngine
#connect(db='NakMuay_db', host='mongodb+srv://muhammadalmaery:muaythai@cluster0.yfhb5od.mongodb.net/NakMuay_db?retryWrites=true&w=majority')

class UserProfiles(Document):
    meta = {'collection': 'UserProfiles'}
    email = StringField(required=True, unique=True)
    username = StringField(required=True, unique=True)
    password = StringField(required=True)

class UserPreferences(Document):
    meta = {'collection': 'UserPreferences'}
    userID = ReferenceField(UserProfiles, required=True)
    hasBarbell = BooleanField(required=True)
    hasDumbbells = BooleanField(required=True)
    hasKettlebell = BooleanField(required=True)
    hasBag = BooleanField(required=True)
    workoutDays = ListField(StringField(), required=True)

class PerformanceHistory(Document):
    meta = {'collection': 'performanceHistory'}
    userID = ReferenceField(UserProfiles, required=True)
    workoutID = ReferenceField('WorkoutList', required=True)
    date = DateTimeField(required=True)
    setsCompleted = IntField()
    repsCompleted = IntField()
    duration = IntField()
    distance = IntField()
    notes = StringField()

class UserTrainingPlans(Document):
    meta = {'collection': 'UserTrainingPlans'}
    userID = ReferenceField(UserProfiles, required=True)
    workoutID = IntField(required=True)
    dayOfWeek = StringField(required=True)
    sets = IntField()
    reps = IntField()
    duration = IntField()
    distance = IntField()

class WorkoutList(Document):
    meta = {'collection': 'WorkoutList'}
    name = StringField(required=True, unique=True)
    description = StringField()
    equipmentNeeded = ListField(StringField())
    type = StringField()
    videoLink = StringField()
    muscleGroups = ListField(StringField())
    level = StringField()
    defaultWeighting = IntField()
    workoutID = IntField() 

class UserWeightings(Document):
    meta = {'collection': 'UserWeightings'}
    userID = ReferenceField(UserProfiles, required=True)
    workoutID = IntField(required=True)
    weighting = IntField(required=True)
