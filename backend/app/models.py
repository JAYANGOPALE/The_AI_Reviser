from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    profile_pic = db.Column(db.String(255), default="https://ui-avatars.com/api/?name=User&background=random")
    level = db.Column(db.String(50)) # e.g. 10th
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50))      # 9th CBSE, BE IT
    subject = db.Column(db.String(100))
    chapter_name = db.Column(db.String(255))
    gdrive_link = db.Column(db.Text)      # The URLs you will provide
    summary_cache = db.Column(db.Text)    # AI Output stored here
