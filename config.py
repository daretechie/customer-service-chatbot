import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ADMIN_USER = os.getenv('ADMIN_USER', 'admin')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'securepassword')
    SECRET_KEY = os.getenv('SECRET_KEY', 'supersecretkey')
    UPLOAD_FOLDER = 'data'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'csv'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB