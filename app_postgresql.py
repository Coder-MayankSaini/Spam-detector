from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
from database import db_manager
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
import numpy as np
import os
import json
import logging
import time
from datetime import datetime, timedelta
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
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
jwt = JWTManager(app)

# Configuration
class Config:
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    PORT = int(os.getenv('PORT', 5001))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Email configuration
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    EMAIL_FROM = os.getenv('EMAIL_FROM', os.getenv('EMAIL_USER'))
    
    # OCR configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')

config = Config()

# Configure logging
logging.basicConfig(level=logging.INFO if not config.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)

# Configure Tesseract path
if config.TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH

# Load the spam detection model
MODEL_PATH = 'spam_model.joblib'
model = None

def load_model():
    """Load the trained spam detection model"""
    global model
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
            logger.info("Spam detection model loaded successfully")
        else:
            logger.warning(f"Model file {MODEL_PATH} not found. Creating default model...")
            create_default_model()
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        create_default_model()

def create_default_model():
    """Create a default model if the trained model doesn't exist"""
    global model
    try:
        # Sample training data
        training_data = [
            ("Congratulations! You've won $1000! Click here now!", 1),
            ("Get rich quick! Make money fast!", 1),
            ("Free trial! Limited time offer!", 1),
            ("Meeting scheduled for tomorrow at 2 PM", 0),
            ("Please review the attached document", 0),
            ("How was your weekend?", 0)
        ]
        
        texts = [item[0] for item in training_data]
        labels = [item[1] for item in training_data]
        
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        model.fit(texts, labels)
        
        # Save the default model
        joblib.dump(model, MODEL_PATH)
        logger.info("Default spam detection model created and saved")
        
    except Exception as e:
        logger.error(f"Error creating default model: {e}")
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

def send_password_reset_email(email, reset_token):
    """Send password reset email with beautiful HTML template"""
    try:
        if not config.EMAIL_USER or not config.EMAIL_PASSWORD:
            logger.error("Email configuration missing")
            return False
        
        reset_url = f"http://localhost:3000/reset-password?token={reset_token}"
        
        # Beautiful HTML email template
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Reset Your Password - Spam Detector</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 0;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                }}
                .container {{
                    max-width: 600px;
                    margin: 40px auto;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                    overflow: hidden;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 28px;
                    font-weight: 700;
                }}
                .header .subtitle {{
                    margin: 10px 0 0 0;
                    font-size: 16px;
                    opacity: 0.9;
                }}
                .content {{
                    padding: 40px 30px;
                }}
                .greeting {{
                    font-size: 18px;
                    color: #333;
                    margin-bottom: 20px;
                }}
                .message {{
                    font-size: 16px;
                    color: #555;
                    margin-bottom: 30px;
                    line-height: 1.8;
                }}
                .reset-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 50px;
                    font-weight: 600;
                    font-size: 16px;
                    text-align: center;
                    margin: 20px 0;
                    box-shadow: 0 10px 25px rgba(102, 126, 234, 0.3);
                    transition: all 0.3s ease;
                }}
                .reset-button:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
                }}
                .security-info {{
                    background: #f8f9ff;
                    border-left: 4px solid #667eea;
                    padding: 20px;
                    margin: 30px 0;
                    border-radius: 0 8px 8px 0;
                }}
                .security-info h3 {{
                    margin: 0 0 10px 0;
                    color: #333;
                    font-size: 16px;
                }}
                .security-info p {{
                    margin: 0;
                    color: #666;
                    font-size: 14px;
                    line-height: 1.6;
                }}
                .footer {{
                    background: #f8f9fa;
                    padding: 30px;
                    text-align: center;
                    border-top: 1px solid #e9ecef;
                }}
                .footer p {{
                    margin: 0;
                    color: #666;
                    font-size: 14px;
                }}
                .footer .brand {{
                    font-weight: 600;
                    color: #667eea;
                }}
                .divider {{
                    height: 1px;
                    background: linear-gradient(90deg, transparent 0%, #667eea 50%, transparent 100%);
                    margin: 30px 0;
                }}
                @media (max-width: 600px) {{
                    .container {{
                        margin: 20px;
                        border-radius: 10px;
                    }}
                    .header, .content, .footer {{
                        padding: 25px 20px;
                    }}
                    .header h1 {{
                        font-size: 24px;
                    }}
                    .reset-button {{
                        padding: 12px 30px;
                        font-size: 14px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Spam Detector</h1>
                    <p class="subtitle">Password Reset Request</p>
                </div>
                
                <div class="content">
                    <div class="greeting">Hello there! 👋</div>
                    
                    <div class="message">
                        We received a request to reset your password for your Spam Detector account. 
                        If you made this request, click the button below to reset your password:
                    </div>
                    
                    <div style="text-align: center;">
                        <a href="{reset_url}" class="reset-button">
                            🔐 Reset My Password
                        </a>
                    </div>
                    
                    <div class="security-info">
                        <h3>🔒 Security Information</h3>
                        <p>
                            • This link will expire in 1 hour for security reasons<br>
                            • If you didn't request this reset, please ignore this email<br>
                            • Your password won't change until you create a new one<br>
                            • For security, always verify the sender's email address
                        </p>
                    </div>
                    
                    <div class="divider"></div>
                    
                    <div class="message">
                        <strong>Having trouble with the button?</strong><br>
                        Copy and paste this link into your browser:<br>
                        <a href="{reset_url}" style="color: #667eea; word-break: break-all;">{reset_url}</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>
                        This email was sent by <span class="brand">Spam Detector</span><br>
                        Your trusted email security solution
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "🔐 Reset Your Spam Detector Password"
        msg['From'] = config.EMAIL_FROM
        msg['To'] = email
        
        # Attach HTML content
        html_part = MIMEText(html_template, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(config.EMAIL_HOST, config.EMAIL_PORT) as server:
            server.starttls()
            server.login(config.EMAIL_USER, config.EMAIL_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Password reset email sent to {email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending password reset email: {e}")
        return False

# Routes

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
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
        access_token = create_access_token(identity=user_id)
        
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
        access_token = create_access_token(identity=user['id'])
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {'id': user['id'], 'email': user['email']}
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/analyze', methods=['POST'])
@jwt_required()
@rate_limit(max_requests=100, window=60)
def analyze_email():
    """Analyze email for spam detection"""
    try:
        if not model:
            return jsonify({'error': 'Model not available'}), 500
        
        data = request.get_json()
        if not data or not data.get('text'):
            return jsonify({'error': 'Email text is required'}), 400
        
        email_text = data['text'].strip()
        
        if len(email_text) < 10:
            return jsonify({'error': 'Email text too short for analysis'}), 400
        
        # Predict spam probability
        prediction = model.predict([email_text])[0]
        probabilities = model.predict_proba([email_text])[0]
        
        is_spam = bool(prediction)
        confidence = float(max(probabilities))
        
        # Get user ID from JWT
        user_id = get_jwt_identity()
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        # Save analysis to database
        db_manager.save_analysis(user_id, email_text, is_spam, confidence, 'text', client_ip)
        
        return jsonify({
            'is_spam': is_spam,
            'confidence': confidence,
            'analysis': {
                'spam_probability': float(probabilities[1]) if len(probabilities) > 1 else confidence,
                'ham_probability': float(probabilities[0]) if len(probabilities) > 1 else 1 - confidence
            }
        })
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/analyze-image', methods=['POST'])
@jwt_required()
@rate_limit(max_requests=20, window=60)
def analyze_image():
    """Analyze image for spam detection using OCR"""
    try:
        data = request.get_json()
        if not data or not data.get('image'):
            return jsonify({'error': 'Image data is required'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to OpenCV format for preprocessing
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocess image for better OCR
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Apply threshold to get better text extraction
        _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(threshold)
        
        if not extracted_text.strip():
            return jsonify({'error': 'No text could be extracted from the image'}), 400
        
        if not model:
            return jsonify({'error': 'Model not available'}), 500
        
        # Analyze extracted text
        prediction = model.predict([extracted_text])[0]
        probabilities = model.predict_proba([extracted_text])[0]
        
        is_spam = bool(prediction)
        confidence = float(max(probabilities))
        
        # Get user ID from JWT
        user_id = get_jwt_identity()
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        # Save analysis to database
        db_manager.save_analysis(user_id, extracted_text, is_spam, confidence, 'image', client_ip)
        
        return jsonify({
            'is_spam': is_spam,
            'confidence': confidence,
            'extracted_text': extracted_text,
            'analysis': {
                'spam_probability': float(probabilities[1]) if len(probabilities) > 1 else confidence,
                'ham_probability': float(probabilities[0]) if len(probabilities) > 1 else 1 - confidence
            }
        })
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return jsonify({'error': 'Image analysis failed'}), 500

@app.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    """Get user's analysis history"""
    try:
        user_id = get_jwt_identity()
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
@jwt_required()
def get_stats():
    """Get user statistics"""
    try:
        user_id = get_jwt_identity()
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

@app.route('/forgot-password', methods=['POST'])
@rate_limit(max_requests=3, window=300)  # 3 requests per 5 minutes
def forgot_password():
    """Handle password reset requests"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400
        
        email = data['email'].lower().strip()
        
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if user exists
        user = db_manager.get_user_by_email(email)
        if not user:
            # Don't reveal whether user exists or not
            return jsonify({'message': 'If the email exists, a reset link has been sent'})
        
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Save reset token
        if db_manager.update_reset_token(email, reset_token, expires_at):
            # Send password reset email
            if send_password_reset_email(email, reset_token):
                return jsonify({'message': 'If the email exists, a reset link has been sent'})
            else:
                return jsonify({'error': 'Failed to send reset email'}), 500
        else:
            return jsonify({'error': 'Failed to process reset request'}), 500
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/reset-password', methods=['POST'])
@rate_limit(max_requests=5, window=300)
def reset_password():
    """Handle password reset"""
    try:
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('password'):
            return jsonify({'error': 'Token and new password are required'}), 400
        
        token = data['token']
        new_password = data['password']
        
        # Validate password strength
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Get user by reset token
        user = db_manager.get_user_by_reset_token(token)
        if not user:
            return jsonify({'error': 'Invalid or expired reset token'}), 400
        
        # Hash new password
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update password
        if db_manager.update_password(user['id'], password_hash):
            return jsonify({'message': 'Password reset successfully'})
        else:
            return jsonify({'error': 'Failed to reset password'}), 500
        
    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return jsonify({'error': 'Password reset failed'}), 500

@app.route('/retrain', methods=['POST'])
@jwt_required()
@rate_limit(max_requests=5, window=300)
def retrain_model():
    """Retrain the spam detection model with new data"""
    try:
        data = request.get_json()
        
        if not data or not data.get('training_data'):
            return jsonify({'error': 'Training data is required'}), 400
        
        training_data = data['training_data']
        
        if not isinstance(training_data, list) or len(training_data) == 0:
            return jsonify({'error': 'Training data must be a non-empty list'}), 400
        
        # Validate training data format
        texts = []
        labels = []
        
        for item in training_data:
            if not isinstance(item, dict) or 'text' not in item or 'is_spam' not in item:
                return jsonify({'error': 'Each training item must have "text" and "is_spam" fields'}), 400
            
            texts.append(item['text'])
            labels.append(1 if item['is_spam'] else 0)
        
        # Create and train new model
        global model
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        model.fit(texts, labels)
        
        # Save the retrained model
        joblib.dump(model, MODEL_PATH)
        
        return jsonify({'message': f'Model retrained successfully with {len(training_data)} samples'})
        
    except Exception as e:
        logger.error(f"Model retraining error: {e}")
        return jsonify({'error': 'Model retraining failed'}), 500

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
