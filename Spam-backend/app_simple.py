from flask import Flask, request, jsonify
from flask_cors import CORS
from simple_database import db_manager  # Use simple database instead
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import pandas as pd
import numpy as np
import os
import json
import logging
import time
from datetime import datetime, timedelta
import jwt
from functools import wraps
from dotenv import load_dotenv
import base64
import io
from PIL import Image
import pytesseract
import cv2
import re
import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import hashlib

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Enhanced CORS Configuration for production
cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
CORS(app, 
     origins=cors_origins,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# Custom JWT functions
def create_custom_access_token(user_id):
    """Create custom JWT access token"""
    payload = {
        'sub': user_id,  # Use 'sub' instead of 'user_id' for consistency
        'user_id': user_id,  # Keep both for compatibility
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

# Configuration
class Config:
    DEBUG = os.getenv('DEBUG', 'true').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Email configuration
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM', os.getenv('EMAIL_USER'))
    
    # Frontend URL for password reset emails
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://spamwall.vercel.app')

config = Config()

# Configure logging
logging.basicConfig(level=logging.INFO if not config.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

# Load the spam detection model
MODEL_PATH = 'spam_model.joblib'
model = None

def load_model():
    """Load the trained spam detection model"""
    global model
    try:
        # Try to load from current directory first
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info(f"Spam detection model loaded successfully from {MODEL_PATH}")
            return
        
        # Try to load from backend directory
        backend_model_path = os.path.join('backend', MODEL_PATH)
        if os.path.exists(backend_model_path):
            model = joblib.load(backend_model_path)
            logger.info(f"Spam detection model loaded successfully from {backend_model_path}")
            return
        
        # If no model found, create default
        logger.warning(f"Model file not found. Creating default model...")
        create_default_model()
        
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        logger.info("Attempting to create default model...")
        create_default_model()

def create_default_model():
    """Create a default model if the trained model doesn't exist"""
    global model
    try:
        logger.info("Creating default spam detection model...")
        
        # Enhanced sample training data
        training_data = [
            ("Congratulations! You've won $1000! Click here now!", 1),
            ("Get rich quick! Make money fast!", 1),
            ("Free trial! Limited time offer!", 1),
            ("URGENT: Your account will be suspended!", 1),
            ("You have won a lottery! Claim your prize now!", 1),
            ("Click here for exclusive deals! Act now!", 1),
            ("Meeting scheduled for tomorrow at 2 PM", 0),
            ("Please review the attached document", 0),
            ("How was your weekend?", 0),
            ("Thank you for your email. I will respond shortly.", 0),
            ("The project deadline has been extended to next week.", 0),
            ("Please find the requested information below.", 0),
            ("Can we schedule a call for this afternoon?", 0),
            ("The meeting has been moved to conference room B.", 0)
        ]
        
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        # Create pipeline with more robust settings
        vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        
        model = make_pipeline(vectorizer, MultinomialNB(alpha=1.0))
        model.fit(texts, labels)
        
        # Save the default model
        try:
            joblib.dump(model, MODEL_PATH)
            logger.info(f"Default spam detection model created and saved to {MODEL_PATH}")
        except Exception as save_error:
            logger.warning(f"Could not save model to {MODEL_PATH}: {save_error}")
            logger.info("Model created in memory only")
        
        # Test the model
        test_prediction = model.predict(["Test email content"])[0]
        logger.info(f"Model test successful, prediction: {test_prediction}")
        
    except Exception as e:
        logger.error(f"Error creating default model: {e}", exc_info=True)
        # Create a very basic fallback
        try:
            model = make_pipeline(TfidfVectorizer(), MultinomialNB())
            model.fit(["spam message", "normal message"], [1, 0])
            logger.info("Created minimal fallback model")
        except Exception as fallback_error:
            logger.error(f"Failed to create even fallback model: {fallback_error}")
            model = None

# Initialize database and load model
try:
    db_manager.init_database()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")

load_model()

# Utility functions
def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def custom_jwt_required(f):
    """Custom JWT authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            # Decode JWT token
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            
            # Handle both 'sub' and 'user_id' fields for compatibility
            current_user_id = data.get('sub') or data.get('user_id')
            
            if not current_user_id:
                return jsonify({'error': 'Invalid token payload'}), 401
            
            # Convert to integer if it's a string
            if isinstance(current_user_id, str):
                current_user_id = int(current_user_id)
            
            # Store user ID for the route function
            request.current_user_id = current_user_id
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token is invalid'}), 401
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return jsonify({'error': 'Token validation failed'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def rate_limit(max_requests=60, window=60):
    """Simple rate limiting decorator"""
    requests_data = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            current_time = time.time()
            
            # Clean old entries
            requests_data[client_ip] = [
                req_time for req_time in requests_data.get(client_ip, [])
                if current_time - req_time < window
            ]
            
            # Check rate limit
            if len(requests_data.get(client_ip, [])) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429
            
            # Add current request
            requests_data.setdefault(client_ip, []).append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'model_loaded': model is not None
    })

@app.route('/register', methods=['POST'])
@rate_limit(max_requests=5, window=60)
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Validate email format
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password strength
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = db_manager.get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user_id = db_manager.create_user(email, password_hash)
        
        # Generate JWT token
        access_token = create_custom_access_token(user_id)
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {'id': user_id, 'email': email}
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
@rate_limit(max_requests=10, window=60)
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get user from database
        user = db_manager.get_user_by_email(email)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        access_token = create_custom_access_token(user['id'])
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {'id': user['id'], 'email': user['email']}
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/analyze', methods=['POST'])
@custom_jwt_required
@rate_limit(max_requests=100, window=60)
def analyze_email():
    """Analyze email for spam detection"""
    try:
        logger.info("Starting email analysis")
        
        if not model:
            logger.error("Model not available")
            return jsonify({'error': 'Spam detection model not available. Please try again later.'}), 500
        
        data = request.get_json()
        if not data or not data.get('text'):
            logger.warning("Missing email text in request")
            return jsonify({'error': 'Email text is required'}), 400
        
        email_text = data['text'].strip()
        logger.info(f"Analyzing email with {len(email_text)} characters")
        
        if len(email_text) < 10:
            logger.warning(f"Email text too short: {len(email_text)} characters")
            return jsonify({'error': 'Email text too short for analysis (minimum 10 characters)'}), 400
        
        # Predict spam probability
        logger.debug("Making prediction with model")
        prediction = model.predict([email_text])[0]
        probabilities = model.predict_proba([email_text])[0]
        
        is_spam = bool(prediction)
        confidence = float(max(probabilities))
        
        logger.info(f"Prediction complete: is_spam={is_spam}, confidence={confidence}")
        
        # Get user ID from custom JWT decorator
        user_id = request.current_user_id
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        # Save analysis to database
        try:
            db_manager.save_analysis(user_id, email_text, is_spam, confidence, 'text', client_ip)
            logger.info("Analysis saved to database successfully")
        except Exception as db_error:
            logger.error(f"Failed to save analysis to database: {db_error}")
            # Don't fail the request if database save fails
        
        response_data = {
            'is_spam': is_spam,
            'confidence': confidence,
            'analysis': {
                'spam_probability': float(probabilities[1]) if len(probabilities) > 1 else confidence,
                'ham_probability': float(probabilities[0]) if len(probabilities) > 1 else 1 - confidence
            }
        }
        
        logger.info("Analysis completed successfully")
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@app.route('/history', methods=['GET'])
@custom_jwt_required
def get_history():
    """Get user's analysis history"""
    try:
        user_id = request.current_user_id
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100 records
        
        history = db_manager.get_user_history(user_id, limit)
        
        # Convert datetime objects to strings for JSON serialization
        formatted_history = []
        for item in history:
            formatted_history.append({
                'email_text': item['email_text'][:200] + '...' if len(item['email_text']) > 200 else item['email_text'],
                'is_spam': item['is_spam'],
                'confidence': float(item['confidence']),
                'analysis_type': item['analysis_type'],
                'timestamp': item['timestamp'].isoformat() if item['timestamp'] else None
            })
        
        return jsonify(formatted_history)
        
    except Exception as e:
        logger.error(f"History retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve history'}), 500

@app.route('/stats', methods=['GET'])
@custom_jwt_required
def get_stats():
    """Get user statistics"""
    try:
        user_id = request.current_user_id
        stats = db_manager.get_user_stats(user_id)
        
        return jsonify({
            'total_analyzed': int(stats['total_analyzed']) if stats['total_analyzed'] else 0,
            'spam_detected': int(stats['spam_detected']) if stats['spam_detected'] else 0,
            'ham_detected': int(stats['ham_detected']) if stats['ham_detected'] else 0,
            'avg_confidence': float(stats['avg_confidence']) if stats['avg_confidence'] else 0.0
        })
        
    except Exception as e:
        logger.error(f"Stats retrieval error: {e}")
        return jsonify({'error': 'Failed to retrieve statistics'}), 500

@app.route('/contact', methods=['POST'])
@rate_limit(max_requests=5, window=300)  # 5 messages per 5 minutes
def contact():
    """Handle contact form submissions"""
    try:
        data = request.get_json()
        
        if not data or not all(key in data for key in ['name', 'email', 'message']):
            return jsonify({'error': 'Name, email, and message are required'}), 400
        
        name = data['name'].strip()
        email = data['email'].lower().strip()
        message = data['message'].strip()
        
        # Validate inputs
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(name) < 2 or len(message) < 10:
            return jsonify({'error': 'Name must be at least 2 characters and message at least 10 characters'}), 400
        
        # Save contact message
        db_manager.save_contact_message(name, email, message)
        
        return jsonify({'message': 'Thank you for your message! We will get back to you soon.'})
        
    except Exception as e:
        logger.error(f"Contact form error: {e}")
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/verify-token', methods=['GET'])
@custom_jwt_required
def verify_token():
    """Verify JWT token and return user information"""
    try:
        # Get current user ID from custom JWT decorator
        current_user_id = request.current_user_id
        
        # Get user information
        user = db_manager.get_user_by_id(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
            
        return jsonify({
            'valid': True,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'created_at': user['created_at'].isoformat() if isinstance(user['created_at'], datetime) else str(user['created_at'])
            }
        })
        
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Token verification failed'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(429)
def rate_limit_exceeded(error):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

if __name__ == '__main__':
    app.run(
        host=config.HOST,
        port=config.PORT,
        debug=config.DEBUG
    )
