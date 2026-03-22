from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    CORS(app) # Allows Frontend to talk to Backend
    
    # Database Configuration (Supabase PostgreSQL or Local SQLite fallback)
    database_url = os.getenv('SUPABASE_DB_URL')
    if database_url and 'your_supabase_password_here' not in database_url:
        # Use Supabase
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Fallback to Local SQLite if Supabase URL is not configured
        app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///../revise_ai.db"
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        from . import routes
        app.register_blueprint(routes.main_bp)
        db.create_all() # Automatically creates MySQL tables
        
    return app
