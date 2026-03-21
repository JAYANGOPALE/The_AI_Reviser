from . import db

class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(50))      # 9th CBSE, BE IT
    subject = db.Column(db.String(100))
    chapter_name = db.Column(db.String(255))
    gdrive_link = db.Column(db.Text)      # The URLs you will provide
    summary_cache = db.Column(db.Text)    # AI Output stored here
