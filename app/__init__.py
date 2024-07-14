from flask import Flask
from flask_mongoengine import MongoEngine
from flask_jwt_extended import JWTManager
import logging

db = MongoEngine()

def create_app():
    app = Flask(__name__)
    
    # Configure MongoDB
    app.config['MONGODB_SETTINGS'] = {
        'db': 'NakMuay_db',
        'host': 'mongodb+srv://muhammadalmaery:UJYuhzTLWjTKd7lK@cluster0.yfhb5od.mongodb.net/NakMuay_db?retryWrites=true&w=majority'
    }
    
    logging.info(f"Connecting to MongoDB at {app.config['MONGODB_SETTINGS']['host']}")
    logging.info(f"Using database: {app.config['MONGODB_SETTINGS']['db']}")

    # Set the JWT secret key
    app.config['JWT_SECRET_KEY'] = 'my_very_secret_key_for_jwt'

    # Configure JWT to store tokens in cookies
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_ACCESS_COOKIE_PATH'] = '/'
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/'
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False  # Disable CSRF protection for simplicity
    
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
