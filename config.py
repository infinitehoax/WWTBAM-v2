import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'wwtbam-school-secret-change-me')

    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///wwtbam.db')
    # Render provides postgres:// but SQLAlchemy 1.4+ requires postgresql://
    if _db_url and _db_url.startswith("postgres://"):
        _db_url = _db_url.replace("postgres://", "postgresql://", 1)

    # Log the scheme for verification without exposing the full URL
    scheme = _db_url.split('://')[0] if '://' in _db_url else 'None'
    print(f"[Config] Database scheme detected: {scheme}")

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')
    DEBUG = os.environ.get('DEBUG', 'True') == 'True'
