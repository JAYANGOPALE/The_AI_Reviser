import os
import jwt
import datetime
from functools import wraps
from flask import Blueprint, jsonify, request
from .models import db, Chapter, User
from .ai_engine import extract_text_from_large_pdf, generate_professional_summary, generate_engineering_summary

main_bp = Blueprint('main', __name__)

SECRET_KEY = os.getenv("SECRET_KEY", "default-secret-key")

# --- AUTH DECORATOR ---

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            if not current_user:
                return jsonify({'error': 'User not found!'}), 401
        except Exception as e:
            return jsonify({'error': 'Token is invalid!', 'message': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

# --- AUTH ROUTES ---

@main_bp.route('/api/v1/auth/register', methods=['POST'])
def register():
    data = request.json
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing email or password"}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({"error": "User already exists"}), 409
    
    new_user = User(
        full_name=data.get('full_name', 'User'),
        email=data['email'],
        level=data.get('level', '')
    )
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({"message": "User registered successfully!"}), 201

@main_bp.route('/api/v1/auth/login', methods=['POST'])
def login():
    auth = request.json
    if not auth or not auth.get('email') or not auth.get('password'):
        return jsonify({"error": "Missing credentials"}), 400
    
    user = User.query.filter_by(email=auth['email']).first()
    if not user or not user.check_password(auth['password']):
        return jsonify({"error": "Invalid email or password"}), 401
    
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, SECRET_KEY, algorithm="HS256")
    
    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "level": user.level,
            "profile_pic": user.profile_pic
        }
    })

# --- USER PROFILE ROUTES ---

@main_bp.route('/api/v1/user/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "level": current_user.level,
        "profile_pic": current_user.profile_pic,
        "created_at": current_user.created_at.strftime("%Y-%m-%d")
    })

@main_bp.route('/api/v1/user/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    current_user.full_name = data.get('full_name', current_user.full_name)
    current_user.level = data.get('level', current_user.level)
    current_user.profile_pic = data.get('profile_pic', current_user.profile_pic)
    
    if 'password' in data and data['password']:
        current_user.set_password(data['password'])
    
    db.session.commit()
    return jsonify({"message": "Profile updated successfully!"})

# --- DATA ROUTES ---

@main_bp.route('/api/v1/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Online", "message": "Revise-AI Backend is live!"})

@main_bp.route('/api/v1/levels', methods=['GET'])
def get_levels():
    levels = db.session.query(Chapter.level).distinct().all()
    return jsonify([lvl[0] for lvl in levels])

@main_bp.route('/api/v1/subjects', methods=['GET'])
def get_subjects():
    level = request.args.get('level')
    if not level:
        return jsonify({"error": "level parameter is required"}), 400
    subjects = db.session.query(Chapter.subject).filter_by(level=level).distinct().all()
    return jsonify([sub[0] for sub in subjects])

@main_bp.route('/api/v1/chapters', methods=['GET'])
def get_chapters():
    level = request.args.get('level')
    subject = request.args.get('subject')
    if not level or not subject:
        return jsonify({"error": "level and subject parameters are required"}), 400
    
    chapters = Chapter.query.filter_by(level=level, subject=subject).all()
    return jsonify([{
        "id": ch.id,
        "title": ch.chapter_name,
        "subject": ch.subject,
        "level": ch.level
    } for ch in chapters])

@main_bp.route('/api/v1/chapters/<int:id>', methods=['GET'])
def get_chapter(id):
    chapter = Chapter.query.get(id)
    if not chapter:
        return jsonify({"error": "Chapter not found"}), 404
    
    return jsonify({
        "id": chapter.id,
        "title": chapter.chapter_name,
        "subject": chapter.subject,
        "level": chapter.level,
        "summary": chapter.summary_cache,
        "pdf_url": chapter.gdrive_link
    })
