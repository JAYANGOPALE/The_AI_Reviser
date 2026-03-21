import os
import google.auth
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from app import db, create_app
from app.models import Chapter

# Path to your Google Cloud credentials.json file
SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def get_drive_service():
    """Sets up the Google Drive API service."""
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        return None, "credentials.json not found"
    
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    return build('drive', 'v3', credentials=creds), None

def sync_grade_folder(folder_id, level_name):
    """
    Crawls a Google Drive folder and populates the MySQL database.
    Folder Structure: Level Folder > Subject Folder > Chapter PDF
    """
    service, error = get_drive_service()
    if error:
        print(f"Error: {error}")
        return

    app = create_app()
    with app.app_context():
        # 1. List all Subject Folders inside the Grade Folder
        results = service.files().list(
            q=f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'",
            fields="files(id, name)"
        ).execute()
        
        subjects = results.get('files', [])
        
        for subject in subjects:
            subject_name = subject['name']
            subject_id = subject['id']
            print(f"--- Processing Subject: {subject_name} ---")
            
            # 2. List all PDF Chapters inside each Subject Folder
            chapter_results = service.files().list(
                q=f"'{subject_id}' in parents and mimeType = 'application/pdf'",
                fields="files(id, name, webViewLink)"
            ).execute()
            
            chapters = chapter_results.get('files', [])
            
            for chapter in chapters:
                chapter_title = chapter['name'].replace('.pdf', '')
                gdrive_link = chapter['webViewLink']
                
                # 3. Check if chapter already exists in MySQL to avoid duplicates
                existing = Chapter.query.filter_by(
                    level=level_name, 
                    subject=subject_name, 
                    chapter_name=chapter_title
                ).first()
                
                if not existing:
                    new_chapter = Chapter(
                        level=level_name,
                        subject=subject_name,
                        chapter_name=chapter_title,
                        gdrive_link=gdrive_link
                    )
                    db.session.add(new_chapter)
                    print(f"Added: {chapter_title}")
                else:
                    print(f"Skipped (Exists): {chapter_title}")
        
        db.session.commit()
        print(f"Sync complete for {level_name}!")
