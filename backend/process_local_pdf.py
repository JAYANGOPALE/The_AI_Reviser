import os
import json
import fitz  # PyMuPDF
from google import genai
from app import db, create_app
from app.models import Chapter
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_chapter_title_from_ai(first_page_text):
    """Uses Gemini 2.0 to detect Chapter Title."""
    prompt = f"Extract the official Chapter Title from this textbook text. Return ONLY the title (e.g. 'Number Systems').\n\n{first_page_text[:1000]}"
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Title detection error: {e}")
        return None

def generate_summary(text, level, subject, chapter_name):
    """Professional Summary with Gemini 2.0 Flash."""
    prompt = f"""
    You are an expert educator for {level} students.
    Summarize chapter '{chapter_name}' in {subject}.
    1. Concise Summary.
    2. Formulas & Definitions.
    3. 5 'Must-Know' points for exams.
    Format with HTML tags (<h3>, <p>, <ul>, <li>).
    
    CONTENT:
    {text[:20000]}
    """
    try:
        response = client.models.generate_content(model="gemini-2.0-flash", contents=prompt)
        return response.text
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def sync_entire_notes_folder(notes_path):
    app = create_app()
    all_data_for_json = []

    with app.app_context():
        # Iterate Level (9th, 10th...)
        for level_folder in os.listdir(notes_path):
            level_path = os.path.join(notes_path, level_folder)
            if not os.path.isdir(level_path): continue
            
            print(f"\n🚀 SYNCING: {level_folder}")
            
            for root, dirs, files in os.walk(level_path):
                for file_name in files:
                    if not file_name.endswith('.pdf'): continue
                    
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(root, level_path)
                    subject_display = relative_path.replace(os.sep, ' - ')
                    
                    print(f"\n--- {level_folder} | {subject_display} | {file_name} ---")
                    
                    try:
                        text = ""
                        first_page_text = ""
                        with fitz.open(file_path) as doc:
                            if len(doc) > 0: first_page_text = doc[0].get_text()
                            for page in doc[:15]: text += page.get_text()
                        
                        chapter_title = get_chapter_title_from_ai(first_page_text) or file_name.replace('.pdf', '')
                        print(f"Detected: {chapter_title}")
                        
                        summary = generate_summary(text, level_folder, subject_display, chapter_title)
                        
                        if summary:
                            new_chapter = Chapter(
                                level=level_folder,
                                subject=subject_display,
                                chapter_name=chapter_title,
                                summary_cache=summary
                            )
                            db.session.add(new_chapter)
                            db.session.commit()
                            
                            all_data_for_json.append({
                                "level": level_folder,
                                "subject": subject_display,
                                "chapter": chapter_title,
                                "summary": summary
                            })
                            print(f"Success! {chapter_title} saved.")
                            
                    except Exception as e:
                        print(f"Skipping {file_name} due to error: {e}")

        with open('../all_notes.json', 'w', encoding='utf-8') as f:
            json.dump(all_data_for_json, f, indent=4)
        
        print("\n✅ SYNC COMPLETE!")

if __name__ == '__main__':
    sync_entire_notes_folder('../notes')
