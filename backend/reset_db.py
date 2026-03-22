import os
os.environ["GEMINI_API_KEY"] = "dummy"
from app import db, create_app
from app.models import Chapter, User

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset successfully.")
