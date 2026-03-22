from app import create_app
from app.models import Chapter

app = create_app()
with app.app_context():
    levels = [l[0] for l in Chapter.query.with_entities(Chapter.level).distinct().all()]
    for level in levels:
        print(f"Level: {level}")
        subjects = [s[0] for s in Chapter.query.filter_by(level=level).with_entities(Chapter.subject).distinct().all()]
        for subject in subjects:
            chapters = Chapter.query.filter_by(level=level, subject=subject).count()
            print(f"  Subject: {subject} ({chapters} chapters)")
