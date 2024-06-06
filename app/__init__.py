#Initializes the app, sets up configurations and defines the apps structure.
from flask import Flask
#Mongoengine maps Python objects with MongoDB documents
from flask_mongoengine import MongoEngine
#Authentication
from flask_jwt_extended import JWTManager

# Create a MongoEngine instance
db = MongoEngine()

def create_app():
    app = Flask(__name__)
    
    # Configure MongoDB
    app.config['MONGODB_SETTINGS'] = {
        'db': 'NakMuay_db',
        'host': 'mongodb+srv://muhammadalmaery:muaythai@cluster0.yfhb5od.mongodb.net/NakMuay_db?retryWrites=true&w=majority'
    }
    
    # Set the JWT secret key
    app.config['JWT_SECRET_KEY'] = 'my_very_secret_key_for_jwt'
    
    # Initialize JWTManager which will be used for protected routes
    jwt = JWTManager(app)

    print("Configuring MongoDB...")
    
    # Initialize MongoEngine with the Flask app
    db.init_app(app)
    
    print("MongoEngine initialized.")
    
    # Register the 'main' Blueprint from the routes file
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
