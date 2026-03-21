import os
import fitz  # PyMuPDF
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Modern Gemini API Initialization (google-genai)
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def extract_text_from_large_pdf(file_path, start_page=0, end_page=15):
    """
    Extracts text from a specific range of a large PDF to stay within AI limits.
    """
    try:
        text = ""
        with fitz.open(file_path) as doc:
            total_pages = len(doc)
            end_page = min(end_page, total_pages)
            
            for page_num in range(start_page, end_page):
                text += doc[page_num].get_text()
        return text, None
    except Exception as e:
        return None, f"Error reading PDF: {str(e)}"

def generate_professional_summary(text, level, subject, chapter_name):
    """Modernized Gemini Pro summary generation."""
    prompt = f"""
    You are an expert educator for {level} students.
    Summarize the chapter '{chapter_name}' in {subject}.
    1. Concise Summary of important concepts.
    2. List Formulas and Definitions.
    3. 5 'Must-Know' points for exams.
    Format with clean HTML (<h3>, <p>, <ul>, <li>).
    
    TEXTBOOK CONTENT:
    {text[:20000]}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", # Faster and modern
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"

def generate_engineering_summary(text, branch, subject, unit_name):
    """Modernized Engineering summary generation."""
    prompt = f"""
    You are a Senior Professor in {branch} Engineering.
    Summarize '{unit_name}' in {subject}.
    1. Technical Summary.
    2. Mathematical Derivations and Formulas.
    3. 5 'Critical' SPPU Exam topics.
    Format with clean HTML.
    
    CONTENT:
    {text[:25000]}
    """
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"
