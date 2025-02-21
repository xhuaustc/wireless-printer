from flask import Flask
import os
from app.config import Config
from app.routes import bp

def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)
    
    if not os.path.exists(Config.UPLOAD_FOLDER):
        os.makedirs(Config.UPLOAD_FOLDER)
        
    app.register_blueprint(bp)
    
    return app 