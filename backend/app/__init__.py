from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
db = SQLAlchemy()

def create_app():
    # Set frontend folder as static folder
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    CORS(app) # Allows Frontend to talk to Backend
    
    # Database Configuration (Supabase PostgreSQL or Local SQLite fallback)
    database_url = os.getenv('SUPABASE_DB_URL')
    if database_url and 'your_supabase_password_here' not in database_url:
        # Fix for SQLAlchemy 1.4+ which requires 'postgresql://' instead of 'postgres://'
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
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
