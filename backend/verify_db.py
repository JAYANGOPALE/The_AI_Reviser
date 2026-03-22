from app import create_app
from app.models import Chapter

app = create_app()
with app.app_context():
    count = Chapter.query.count()
    print(f"Total chapters in database: {count}")
    
    levels = [l[0] for l in Chapter.query.with_entities(Chapter.level).distinct().all()]
    print(f"Levels found: {levels}")
