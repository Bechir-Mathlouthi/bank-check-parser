from flask import Flask
from flask_cors import CORS
from .api.routes import api
from .database import init_db
from .config.config import settings

def create_app():
    app = Flask(__name__)
    CORS(app)  # Enable CORS for all routes
    
    # Configure the app
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URL'] = settings.DATABASE_URL
    
    # Initialize the database
    init_db()
    
    # Register blueprints
    app.register_blueprint(api, url_prefix=settings.API_V1_PREFIX)
    
    return app 