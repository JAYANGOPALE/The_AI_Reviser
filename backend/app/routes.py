from flask import Blueprint, jsonify, request
from .models import db, Chapter
from .ai_engine import extract_text_from_large_pdf, generate_professional_summary, generate_engineering_summary

main_bp = Blueprint('main', __name__)

@main_bp.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Online", "message": "Revise-AI Backend is live!"})

# The Main Endpoint for the Frontend to get Notes
@main_bp.route('/api/v1/chapters/<int:id>', methods=['GET'])
def get_chapter(id):
    chapter = Chapter.query.get(id)
    if not chapter:
        return jsonify({"error": "Chapter not found"}), 404
    
    # Check if a summary is already in the database
    if chapter.summary_cache:
        return jsonify({
            "id": chapter.id,
            "title": chapter.chapter_name,
            "subject": chapter.subject,
            "summary": chapter.summary_cache,
            "pdf_url": chapter.gdrive_link
        })
    
    # If no summary exists, trigger the AI Builder
    # 1. Extract text from G-Drive PDF
    text, error = get_pdf_text_from_gdrive(chapter.gdrive_link)
    if error:
        return jsonify({"error": f"Failed to read PDF: {error}"}), 500
    
    # 2. Generate summary using Gemini
    summary = generate_professional_summary(
        text, 
        chapter.level, 
        chapter.subject, 
        chapter.chapter_name
    )
    
    # 3. Save the summary to MySQL for future use
    chapter.summary_cache = summary
    db.session.commit()
    
    return jsonify({
        "id": chapter.id,
        "title": chapter.chapter_name,
        "subject": chapter.subject,
        "summary": summary,
        "pdf_url": chapter.gdrive_link
    })
