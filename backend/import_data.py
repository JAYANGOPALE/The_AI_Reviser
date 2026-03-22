import os
import json
from app import db, create_app
from app.models import Chapter

def format_summary(entry):
    """Converts various JSON summary formats into a formatted HTML summary."""
    html_content = ""
    
    # Format 1: detailed_summary (List of strings)
    if 'detailed_summary' in entry:
        html_content += "<ul>"
        for item in entry['detailed_summary']:
            if item.endswith(':'):
                html_content += f"</ul><h3>{item}</h3><ul>"
            else:
                html_content += f"<li>{item}</li>"
        html_content += "</ul>"
    
    # Format 2: detailed_summary_sections (List of objects)
    elif 'detailed_summary_sections' in entry:
        if 'chapter_overview' in entry:
            html_content += f"<p><em>{entry['chapter_overview']}</em></p><br>"
            
        for section in entry['detailed_summary_sections']:
            title = section.get('section_title', '')
            explanation = section.get('explanation', '')
            key_points = section.get('key_points', [])
            
            if title: html_content += f"<h3>{title}</h3>"
            if explanation: html_content += f"<p>{explanation}</p>"
            if key_points:
                html_content += "<ul>"
                for point in key_points:
                    html_content += f"<li>{point}</li>"
                html_content += "</ul>"
    
    return html_content.replace("<ul></ul>", "")

def import_json_files(data_dir):
    app = create_app()
    with app.app_context():
        for filename in os.listdir(data_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(data_dir, filename)
            name_parts = filename.replace('.json', '').split('_')
            level = name_parts[0]
            subject = " ".join(name_parts[1:]).replace('  ', ' ').strip().title()
            if not subject: subject = "General"

            print(f"Importing {filename} (Level: {level}, Subject: {subject})...")

            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # Normalize data to a list
                    entries = data if isinstance(data, list) else [data]
                    
                    for entry in entries:
                        if not isinstance(entry, dict): continue
                        
                        chapter_title = entry.get('chapter_title')
                        if not chapter_title: continue
                        
                        pdf_filename = entry.get('filename')
                        formatted_summary = format_summary(entry)

                        existing = Chapter.query.filter_by(
                            level=level,
                            subject=subject,
                            chapter_name=chapter_title
                        ).first()

                        if existing:
                            existing.summary_cache = formatted_summary
                            print(f"  Updated: {chapter_title}")
                        else:
                            new_chapter = Chapter(
                                level=level,
                                subject=subject,
                                chapter_name=chapter_title,
                                summary_cache=formatted_summary,
                                gdrive_link=f"https://ncert.nic.in/textbook/pdf/{pdf_filename}" if pdf_filename else None
                            )
                            db.session.add(new_chapter)
                            print(f"  Added: {chapter_title}")
                except Exception as e:
                    print(f"Error importing {filename}: {e}")
        
        db.session.commit()
        print("✅ Import complete!")

if __name__ == '__main__':
    import_json_files('data')
