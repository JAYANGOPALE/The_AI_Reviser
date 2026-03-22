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

import re

def get_ncert_link(level, subject, chapter_title, filename):
    """Generates an NCERT PDF link based on level, subject and chapter number."""
    if filename:
        return f"https://ncert.nic.in/textbook/pdf/{filename}"
    
    # Try to extract chapter/unit number
    match = re.search(r'(?:Chapter|Unit)\s*(\d+)', chapter_title, re.IGNORECASE)
    if not match:
        return None
    
    num = int(match.group(1))
    # Standardize to 2 digits for the PDF filename (e.g., 01, 02)
    chapter_code = f"{num:02d}"
    
    prefix_map = {
        ('9th', 'Science'): 'iesc1',
        ('9th', 'Maths'): 'iemh1',
        ('10th', 'Science'): 'jesc1',
        ('10th', 'Maths'): 'jemh1',
        ('11th', 'Physics'): 'keph1',
        ('11th', 'Chemistry'): 'kech1',
        ('11th', 'Maths'): 'kemh1',
    }

    # Handle class 11 Parts (Usually Part 1 is 1xx, Part 2 is 2xx in some schemes, 
    # but NCERT often just uses keph1 and keph2 prefixes)
    # Check if the filename itself (from which subject was derived) had '1' or '2'
    # This info is lost here, but we can check the num if it's class 11
    prefix = prefix_map.get((level, subject))
    
    if level == '11th':
        if subject == 'Physics':
            prefix = 'keph1' if num <= 8 else 'keph2'
            if num > 8: chapter_code = f"{num-8:02d}" # Adjust for part 2
        elif subject == 'Chemistry':
            prefix = 'kech1' if num <= 7 else 'kech2'
            if num > 7: chapter_code = f"{num-7:02d}" # Adjust for part 2

    if prefix:
        return f"https://ncert.nic.in/textbook/pdf/{prefix}{chapter_code}.pdf"
    
    return None

def import_json_files(data_dir):
    app = create_app()
    with app.app_context():
        subject_map = {
            'phy': 'Physics',
            'phys': 'Physics',
            'physics': 'Physics',
            'chem': 'Chemistry',
            'chemistry': 'Chemistry',
            'maths': 'Maths',
            'math': 'Maths',
            'mathematics': 'Maths',
            'science': 'Science',
            'bio': 'Biology',
            'biology': 'Biology',
            'eng': 'English',
            'english': 'English'
        }

        for filename in os.listdir(data_dir):
            if not filename.endswith('.json'):
                continue
            
            file_path = os.path.join(data_dir, filename)
            name_parts = filename.replace('.json', '').split('_')
            level = name_parts[0]
            
            # Extract subject and merge Part 1/2 into the main subject
            raw_subject_parts = name_parts[1:]
            subject_parts = []
            for part in raw_subject_parts:
                part_lower = part.lower()
                if not part: continue
                if part.isdigit():
                    continue
                if part_lower in ['p1', 'p2', 'part1', 'part2']:
                    continue
                else:
                    subject_parts.append(subject_map.get(part_lower, part.title()))
            
            # Use only the first valid subject part to avoid "Maths Maths" or similar
            if subject_parts:
                subject = subject_parts[0]
            else:
                subject = "General"

            print(f"Importing {filename} (Level: {level}, Subject: {subject})...")

            with open(file_path, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    # Normalize data to a list of chapters
                    if isinstance(data, dict):
                        if 'study_guide' in data:
                            entries = data['study_guide']
                        elif 'chapters' in data:
                            entries = data['chapters']
                        else:
                            entries = [data]
                    else:
                        entries = data
                    
                    if not isinstance(entries, list):
                        print(f"  Warning: Could not find list of chapters in {filename}")
                        continue

                    for entry in entries:
                        if not isinstance(entry, dict): continue
                        
                        chapter_title = entry.get('chapter_title')
                        if not chapter_title: continue
                        
                        pdf_filename = entry.get('filename')
                        formatted_summary = format_summary(entry)
                        
                        # Generate PDF URL
                        pdf_url = get_ncert_link(level, subject, chapter_title, pdf_filename)

                        existing = Chapter.query.filter_by(
                            level=level,
                            subject=subject,
                            chapter_name=chapter_title
                        ).first()

                        if existing:
                            existing.summary_cache = formatted_summary
                            existing.gdrive_link = pdf_url
                            print(f"  Updated: {chapter_title}")
                        else:
                            new_chapter = Chapter(
                                level=level,
                                subject=subject,
                                chapter_name=chapter_title,
                                summary_cache=formatted_summary,
                                gdrive_link=pdf_url
                            )
                            db.session.add(new_chapter)
                            print(f"  Added: {chapter_title}")
                except Exception as e:
                    print(f"Error importing {filename}: {e}")
        
        db.session.commit()
        print("✅ Import complete!")

if __name__ == '__main__':
    import_json_files('data')
