from flask import Flask
from flask_cors import CORS
import os
from datetime import timedelta

def create_app():
    app = Flask(__name__)
    
    app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production-12345678')
    
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    app.config['SESSION_COOKIE_NAME'] = 'loan_session'
    app.config['SESSION_COOKIE_HTTPONLY'] = False  
    app.config['SESSION_COOKIE_SAMESITE'] = None  
    app.config['SESSION_COOKIE_SECURE'] = False  
    app.config['SESSION_COOKIE_PATH'] = '/'
    app.config['SESSION_COOKIE_DOMAIN'] = None  
    
    CORS(app, 
         resources={
             r"/api/*": {
                 "origins": [
                     "http://localhost:5500", 
                     "http://127.0.0.1:5500", 
                     "http://[::1]:5500",
                     "http://localhost:*",
                     "http://127.0.0.1:*"
                 ],
                 "supports_credentials": True,
                 "allow_headers": ["Content-Type", "Accept"],
                 "expose_headers": ["Set-Cookie"],
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
             }
         })

    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "..", "uploads")
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

    with app.app_context():
        from app import auth, upload, loan, loans_api 
    
    return app