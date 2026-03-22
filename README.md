# Revise-AI Dashboard

Revise-AI is a professional revision tool that uses AI and pre-generated JSON summaries to help students revise their subjects efficiently. Now featuring a complete user authentication system and profile management.

## Features
- **User Authentication**: Secure Login and Registration.
- **Dark Mode**: Toggle between Light and Dark themes with persistence.
- **Dynamic Dashboard**: Personalized content based on your grade level with a "Welcome Hero" section.
- **Modern UI**: Clean, professional design with Font Awesome icons, animations, and glassmorphism effects.
- **User Profile**: Update your name, grade, and profile picture URL.
- **Supabase Powered**: All data (Chapters & Users) is stored securely in Supabase.

## Backend setup

1. Install dependencies:
   ```bash
   pip install flask flask-sqlalchemy flask-cors python-dotenv google-genai pymupdf psycopg2-binary PyJWT
   ```
2. Configure environment variables in `backend/.env`:
   - `GEMINI_API_KEY`: Your Gemini API key.
   - `SUPABASE_DB_URL`: The full PostgreSQL connection string.
   - `SECRET_KEY`: A random string for securing user tokens.

3. Import the data into the database:
   ```bash
   cd backend
   python import_data.py
   ```
4. Run the backend server:
   ```bash
   python run.py
   ```

## Frontend setup

Open `frontend/login.html` in your browser to get started.

## Project Structure
- `backend/app/models.py`: Database models for Chapters and Users.
- `backend/app/routes.py`: API endpoints for data and authentication.
- `frontend/index.html`: Main dashboard.
- `frontend/profile.html`: User profile settings.
- `frontend/login.html` / `register.html`: Auth pages.
