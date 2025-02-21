import os

class Config:
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif'}
    IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'} 