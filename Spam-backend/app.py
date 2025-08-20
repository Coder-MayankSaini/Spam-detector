from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import sqlite3
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

# Enhanced CORS Configuration for authentication
CORS(app, 
     origins=["http://localhost:3000", "http://127.0.0.1:3000"],
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
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5001))
    DATABASE_URL = os.getenv('DATABASE_URL', 'emails.db')
    MODEL_PATH = os.getenv('MODEL_PATH', 'spam_model.joblib')
    DEFAULT_THRESHOLD = float(os.getenv('DEFAULT_THRESHOLD', 0.6))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    TRAINING_DATA_CSV = os.getenv('TRAINING_DATA_CSV', 'training_data.csv')
    TESSERACT_CMD = os.getenv('TESSERACT_CMD', None)

config = Config()

# Email configuration
GMAIL_USER = os.getenv('GMAIL_USER')
GMAIL_PASS = os.getenv('GMAIL_PASS')
CONTACT_RECEIVER = 'marketing.nexoradigital@gmail.com'

# Configure Tesseract path if specified
if config.TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_CMD

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(message)s'
)
logger = logging.getLogger(__name__)

def log_structured(level, event, **kwargs):
    """Log structured JSON messages"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'event': event,
        **kwargs
    }
    logger.log(getattr(logging, level), json.dumps(log_entry))

# Request timing middleware
def log_requests(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        try:
            result = f(*args, **kwargs)
            duration = time.time() - start_time
            log_structured('INFO', 'request_completed', 
                         method=request.method, 
                         path=request.path,
                         duration_ms=round(duration * 1000, 2),
                         status_code=getattr(result, 'status_code', 200))
            return result
        except Exception as e:
            duration = time.time() - start_time
            log_structured('ERROR', 'request_failed',
                         method=request.method,
                         path=request.path,
                         duration_ms=round(duration * 1000, 2),
                         error=str(e))
            raise
    return decorated_function  

# Initialize database
def init_db():
    conn = sqlite3.connect(config.DATABASE_URL)
    
    # Create users table
    conn.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 email TEXT UNIQUE NOT NULL,
                 password_hash TEXT NOT NULL,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    
    # Create emails table with user_id foreign key
    conn.execute('''CREATE TABLE IF NOT EXISTS emails
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 content TEXT,
                 is_spam BOOLEAN,
                 confidence REAL,
                 keywords TEXT,
                 timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    # Create password_resets table
    conn.execute('''CREATE TABLE IF NOT EXISTS password_resets
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER NOT NULL,
                 token TEXT UNIQUE NOT NULL,
                 expires_at DATETIME NOT NULL,
                 used BOOLEAN DEFAULT FALSE,
                 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (user_id) REFERENCES users (id))''')
    
    conn.close()
    log_structured('INFO', 'database_initialized', database=config.DATABASE_URL)

# Authentication helper functions
def hash_password(password):
    """Hash a password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def get_user_by_email(email):
    """Get user by email from database"""
    conn = sqlite3.connect(config.DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password_hash FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def create_user(email, password):
    """Create a new user in the database"""
    password_hash = hash_password(password)
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password_hash) VALUES (?, ?)", 
                      (email, password_hash))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
    except sqlite3.IntegrityError:
        return None  # User already exists

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)

def create_reset_token(user_id):
    """Create a password reset token for a user"""
    token = generate_reset_token()
    # Token expires in 1 hour
    expires_at = datetime.now() + timedelta(hours=1)
    
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO password_resets (user_id, token, expires_at) 
            VALUES (?, ?, ?)
        """, (user_id, token, expires_at))
        conn.commit()
        conn.close()
        return token
    except Exception as e:
        log_structured('ERROR', 'reset_token_creation_failed', error=str(e))
        return None

def verify_reset_token(token):
    """Verify a password reset token and return user_id if valid"""
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id FROM password_resets 
            WHERE token = ? AND expires_at > datetime('now') AND used = FALSE
        """, (token,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except Exception as e:
        log_structured('ERROR', 'reset_token_verification_failed', error=str(e))
        return None

def mark_reset_token_used(token):
    """Mark a reset token as used"""
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("UPDATE password_resets SET used = TRUE WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_structured('ERROR', 'reset_token_marking_failed', error=str(e))
        return False

def update_user_password(user_id, new_password):
    """Update a user's password"""
    password_hash = hash_password(new_password)
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", 
                      (password_hash, user_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        log_structured('ERROR', 'password_update_failed', error=str(e))
        return False

def send_password_reset_email(email, reset_token):
    """Send password reset email to user with beautiful HTML template"""
    if not GMAIL_USER or not GMAIL_PASS:
        log_structured('ERROR', 'gmail_credentials_missing_for_reset')
        return False

    # Create reset link - you can customize this URL
    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"
    
    subject = "🔐 Password Reset Request - Spam Detector"
    
    # Create beautiful HTML email template
    html_body = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Password Reset - Spam Detector</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', 'Helvetica', sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh;">
    <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 20px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); overflow: hidden; margin-top: 40px; margin-bottom: 40px;">
        
        <!-- Header -->
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center;">
            <div style="background: white; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; box-shadow: 0 10px 20px rgba(0,0,0,0.2);">
                <span style="font-size: 36px; color: #667eea;">🛡️</span>
            </div>
            <h1 style="margin: 0; color: white; font-size: 28px; font-weight: 700;">Spam Detector</h1>
            <p style="margin: 10px 0 0; color: rgba(255,255,255,0.9); font-size: 16px;">Secure Email Protection</p>
        </div>
        
        <!-- Main Content -->
        <div style="padding: 50px 40px;">
            <div style="text-align: center; margin-bottom: 40px;">
                <h2 style="color: #2c3e50; font-size: 24px; margin: 0 0 15px; font-weight: 600;">Password Reset Request</h2>
                <div style="width: 60px; height: 4px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0 auto; border-radius: 2px;"></div>
            </div>
            
            <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 25px;">Hello there,</p>
            <p style="color: #555; font-size: 16px; line-height: 1.6; margin: 0 0 30px;">
                We received a request to reset your password for your <strong>Spam Detector</strong> account. 
                If you made this request, click the button below to set a new password.
            </p>
            
            <!-- Reset Button -->
            <div style="text-align: center; margin: 40px 0;">
                <a href="{reset_link}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 16px 40px; text-decoration: none; border-radius: 50px; font-weight: 600; font-size: 16px; box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3); transition: all 0.3s ease;">
                    🔐 Reset My Password
                </a>
            </div>
            
            <!-- Security Info -->
            <div style="background: #f8f9fa; border-left: 4px solid #667eea; padding: 20px; border-radius: 0 10px 10px 0; margin: 30px 0;">
                <h3 style="color: #2c3e50; font-size: 16px; margin: 0 0 10px; font-weight: 600;">
                    🔒 Security Information
                </h3>
                <ul style="color: #666; font-size: 14px; margin: 0; padding-left: 20px; line-height: 1.5;">
                    <li>This link will expire in <strong>1 hour</strong></li>
                    <li>This link can only be used once</li>
                    <li>If you didn't request this, you can safely ignore this email</li>
                </ul>
            </div>
            
            <!-- Alternative Link -->
            <div style="border: 2px dashed #e0e6ed; border-radius: 10px; padding: 20px; margin: 30px 0; background: #fafbfc;">
                <p style="color: #666; font-size: 14px; margin: 0 0 10px; font-weight: 600;">
                    Button not working? Copy and paste this link:
                </p>
                <p style="word-break: break-all; color: #667eea; font-size: 13px; margin: 0; font-family: monospace;">
                    {reset_link}
                </p>
            </div>
            
            <p style="color: #666; font-size: 14px; line-height: 1.5; margin: 30px 0 0;">
                If you have any questions or need help, please don't hesitate to contact our support team.
            </p>
        </div>
        
        <!-- Footer -->
        <div style="background: #2c3e50; padding: 30px 40px; text-align: center;">
            <p style="color: #95a5a6; font-size: 14px; margin: 0 0 15px;">
                This email was sent by <strong style="color: #ecf0f1;">Spam Detector</strong>
            </p>
            <p style="color: #7f8c8d; font-size: 12px; margin: 0;">
                🛡️ Protecting your inbox with advanced AI detection
            </p>
            <div style="margin: 20px 0 0; padding: 15px 0; border-top: 1px solid #34495e;">
                <span style="color: #7f8c8d; font-size: 11px;">
                    © 2025 Spam Detector. All rights reserved.
                </span>
            </div>
        </div>
    </div>
</body>
</html>
"""

    # Fallback plain text version
    text_body = f"""
Hello,

You have requested to reset your password for your Spam Detector account.

Click the link below to reset your password:
{reset_link}

This link will expire in 1 hour for security reasons.

If you did not request this password reset, please ignore this email.

Best regards,
Spam Detector Team
"""
    
    msg = MIMEMultipart('alternative')
    msg['From'] = GMAIL_USER
    msg['To'] = email
    msg['Subject'] = subject
    
    # Add both plain text and HTML versions
    text_part = MIMEText(text_body, 'plain')
    html_part = MIMEText(html_body, 'html')
    
    msg.attach(text_part)
    msg.attach(html_part)

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, email, msg.as_string())
        
        log_structured('INFO', 'password_reset_email_sent', email=email)
        return True
    except Exception as e:
        log_structured('ERROR', 'password_reset_email_failed', error=str(e))
        return False

def load_training_data():
    """Load training data from CSV with validation"""
    csv_path = config.TRAINING_DATA_CSV
    if not os.path.exists(csv_path):
        log_structured('WARNING', 'training_csv_not_found', path=csv_path)
        # Fallback to hardcoded data
        return pd.DataFrame({
            'text': [
                "Win a free iPhone now!", 
                "Meeting at 3pm tomorrow",
                "Limited time offer!", 
                "Your account statement"
            ],
            'label': [1, 0, 1, 0] 
        })
    
    try:
        df = pd.read_csv(csv_path)
        if 'text' not in df.columns or 'label' not in df.columns:
            raise ValueError("CSV must have 'text' and 'label' columns")
        
        # Validation
        df = df.dropna()
        valid_labels = df['label'].isin([0, 1])
        if not valid_labels.all():
            log_structured('WARNING', 'invalid_labels_found', 
                         invalid_count=len(df) - valid_labels.sum())
            df = df[valid_labels]
        
        log_structured('INFO', 'training_data_loaded', 
                     total_samples=len(df),
                     spam_samples=len(df[df['label'] == 1]),
                     ham_samples=len(df[df['label'] == 0]))
        return df
    except Exception as e:
        log_structured('ERROR', 'training_data_load_failed', error=str(e))
        raise

# Train or load ML model
def get_model():
    model_path = config.MODEL_PATH
    try:
        model = joblib.load(model_path)
        log_structured('INFO', 'model_loaded', path=model_path)
        return model
    except:
        log_structured('INFO', 'training_new_model')
        df = load_training_data()
        
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        model.fit(df['text'], df['label'])
        joblib.dump(model, model_path)
        
        log_structured('INFO', 'model_trained_and_saved', path=model_path)
        return model

def get_feature_importance(model, text, top_k=5):
    """Extract keyword importance using log probabilities"""
    try:
        # Get the vectorizer and classifier from pipeline
        vectorizer = model.named_steps['tfidfvectorizer']
        classifier = model.named_steps['multinomialnb']
        
        # Transform text and get feature names
        text_vector = vectorizer.transform([text])
        feature_names = vectorizer.get_feature_names_out()
        
        # Get log probabilities for each class
        log_proba = classifier.predict_log_proba(text_vector)[0]
        spam_log_proba = log_proba[1]
        
        # Get feature log probabilities (for spam class)
        feature_log_proba = classifier.feature_log_prob_[1]
        
        # Get active features (non-zero in TF-IDF)
        active_features = text_vector.toarray()[0]
        active_indices = np.where(active_features > 0)[0]
        
        # Calculate importance scores
        importance_scores = []
        for idx in active_indices:
            word = feature_names[idx]
            tfidf_score = active_features[idx]
            log_prob = feature_log_proba[idx]
            importance = tfidf_score * log_prob
            importance_scores.append((word, importance))
        
        # Sort by importance and return top_k
        importance_scores.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in importance_scores[:top_k]]
    
    except Exception as e:
        log_structured('WARNING', 'feature_importance_failed', error=str(e))
        return []

def process_image_ocr(image_data):
    """Extract text from image using OCR"""
    try:
        # Check if Tesseract is available
        try:
            pytesseract.get_tesseract_version()
        except pytesseract.TesseractNotFoundError:
            raise ValueError("Tesseract OCR is not installed. Please install Tesseract OCR engine. See docs/OCR_SETUP.md for instructions.")
        
        # Decode base64 image
        if image_data.startswith('data:image'):
            # Remove data URL prefix
            image_data = image_data.split(',', 1)[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Convert PIL image to OpenCV format for preprocessing
        opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocessing for better OCR results
        # Convert to grayscale
        gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
        
        # Resize image if too small (helps with OCR accuracy)
        height, width = gray.shape
        if height < 100 or width < 100:
            scale_factor = max(200/height, 200/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            gray = cv2.resize(gray, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        
        # Apply threshold to get better contrast
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.medianBlur(thresh, 3)
        
        # Extract text using pytesseract with optimized config
        # Try multiple PSM modes for better results
        ocr_configs = [
            '--psm 6',  # Assume uniform block of text
            '--psm 8',  # Treat image as single word
            '--psm 7',  # Treat image as single text line
            '--psm 3'   # Fully automatic page segmentation
        ]
        
        extracted_text = ""
        for config in ocr_configs:
            try:
                text = pytesseract.image_to_string(denoised, config=config).strip()
                if len(text) > len(extracted_text):
                    extracted_text = text
            except:
                continue
        
        # If no text found, try with original image
        if not extracted_text:
            extracted_text = pytesseract.image_to_string(image).strip()
        
        # Clean up extracted text
        cleaned_text = re.sub(r'\s+', ' ', extracted_text).strip()
        
        log_structured('INFO', 'ocr_processing_completed', 
                     text_length=len(cleaned_text),
                     original_image_size=image.size)
        
        return cleaned_text
    
    except pytesseract.TesseractNotFoundError:
        raise ValueError("Tesseract OCR engine is not installed. Please follow the setup instructions in docs/OCR_SETUP.md")
    except Exception as e:
        log_structured('ERROR', 'ocr_processing_failed', error=str(e))
        raise ValueError(f"Failed to process image: {str(e)}")

def clean_extracted_text(text):
    """Clean and improve OCR extracted text"""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Fix common OCR character mistakes
    char_fixes = {
        '0': 'o',  # Zero to o in words
        '1': 'l',  # One to l in words  
        '5': 's',  # Five to s in words
        '8': 'B',  # Eight to B
        '6': 'G',  # Six to G
        'rn': 'm', # rn to m
        'vv': 'w', # vv to w
    }
    
    # Fix common OCR word mistakes for spam detection
    word_fixes = {
        'FR33': 'FREE',
        'FR3E': 'FREE', 
        'FREB': 'FREE',
        'W1N': 'WIN',
        'W!N': 'WIN',
        '0FFER': 'OFFER',
        'CFFER': 'OFFER',
        '0FF3R': 'OFFER',
        'CL1CK': 'CLICK',
        'CL!CK': 'CLICK',
        'URG3NT': 'URGENT',
        'URG!NT': 'URGENT',
        'LIMI7ED': 'LIMITED',
        '-IMITED': 'LIMITED',
        'L1MITED': 'LIMITED',
        'M0NEY': 'MONEY',
        'MON3Y': 'MONEY',
        'PRIZB': 'PRIZE',
        'PR1ZE': 'PRIZE',
        'WINNBR': 'WINNER',
        'W1NNER': 'WINNER',
    }
    
    # Split into words and fix each word
    words = text.split()
    cleaned_words = []
    
    for word in words:
        original_word = word
        word_upper = word.upper()
        
        # Check for direct word replacements
        if word_upper in word_fixes:
            word = word_fixes[word_upper]
        else:
            # Apply character-level fixes for words that might have OCR errors
            for wrong, right in char_fixes.items():
                # Only fix if it makes sense in context
                if wrong in word and len(word) > 2:
                    # Be careful about number vs letter context
                    if wrong == '0' and ('$' in word or any(c.isdigit() for c in word.replace('0', ''))):
                        continue  # Keep 0 in monetary amounts
                    if wrong in ['0', '1', '5'] and word.isdigit():
                        continue  # Keep numbers as numbers
                    word = word.replace(wrong, right)
        
        # Special fixes for monetary amounts and phone numbers
        if '$' in word:
            # Fix $10.000 to $10,000 and other monetary issues
            word = re.sub(r'\$l(\d)', r'$1\1', word)  # $l0 -> $10
            word = re.sub(r'\$(\d+)\.(\d{3})', r'$\1,\2', word)  # $10.000 -> $10,000
        
        # Fix phone numbers
        if re.match(r'[l1]-[B8]00', word):
            word = re.sub(r'^[l1]-([B8])00', r'1-800', word)
        
        # Fix common word patterns
        if re.match(r'^[0o] claim$', word.lower()):
            word = 'to claim'
        
        cleaned_words.append(word)
    
    result = ' '.join(cleaned_words).strip()
    
    # Final cleanup
    result = re.sub(r'\s+', ' ', result)  # Remove extra spaces
    result = re.sub(r'[^\w\s.,!?@$%()-]', '', result)  # Remove artifacts
    
    return result

model = get_model()
init_db()

# Authentication endpoints
@app.route('/register', methods=['POST'])
@log_requests
def register():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Check if user already exists
    if get_user_by_email(email):
        return jsonify({"error": "User already exists"}), 409
    
    # Create user
    user_id = create_user(email, password)
    if user_id is None:
        return jsonify({"error": "Failed to create user"}), 500
    
    # Create access token
    access_token = create_access_token(identity=str(user_id))
    
    log_structured('INFO', 'user_registered', user_id=user_id, email=email)
    return jsonify({
        "message": "User registered successfully",
        "access_token": access_token,
        "user": {"id": user_id, "email": email}
    }), 201

@app.route('/login', methods=['POST'])
@log_requests
def login():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Get user from database
    user = get_user_by_email(email)
    if not user or not verify_password(password, user[2]):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Create access token
    access_token = create_access_token(identity=str(user[0]))
    
    log_structured('INFO', 'user_logged_in', user_id=user[0], email=email)
    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "user": {"id": user[0], "email": user[1]}
    }), 200

@app.route('/verify-token', methods=['GET'])
@jwt_required()
@log_requests
def verify_token():
    user_id = int(get_jwt_identity())
    conn = sqlite3.connect(config.DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
        "valid": True,
        "user": {"id": user_id, "email": user[0]}
    }), 200

@app.route('/forgot-password', methods=['POST'])
@log_requests
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    # Validate email format
    import re
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        return jsonify({"error": "Please enter a valid email address"}), 400
    
    # Get user by email
    user = get_user_by_email(email)
    if not user:
        # Don't reveal if email exists or not for security
        return jsonify({
            "message": "If an account with that email exists, a password reset link has been sent."
        }), 200
    
    user_id = user[0]
    
    # Create reset token
    reset_token = create_reset_token(user_id)
    if not reset_token:
        return jsonify({"error": "Failed to create reset token"}), 500
    
    # Send reset email
    if send_password_reset_email(email, reset_token):
        log_structured('INFO', 'password_reset_requested', user_id=user_id, email=email)
        return jsonify({
            "message": "If an account with that email exists, a password reset link has been sent."
        }), 200
    else:
        return jsonify({"error": "Failed to send reset email"}), 500

@app.route('/reset-password', methods=['POST'])
@log_requests
def reset_password():
    data = request.get_json(silent=True) or {}
    token = data.get('token', '').strip()
    new_password = data.get('password', '').strip()
    
    if not token or not new_password:
        return jsonify({"error": "Token and new password are required"}), 400
    
    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Verify reset token
    user_id = verify_reset_token(token)
    if not user_id:
        return jsonify({"error": "Invalid or expired reset token"}), 400
    
    # Update password
    if not update_user_password(user_id, new_password):
        return jsonify({"error": "Failed to update password"}), 500
    
    # Mark token as used
    mark_reset_token_used(token)
    
    log_structured('INFO', 'password_reset_completed', user_id=user_id)
    return jsonify({"message": "Password has been reset successfully"}), 200

# Health check endpoint
@app.route('/', methods=['GET'])
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "message": "Spam Detector API is running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/analyze', methods=['POST'])
@jwt_required()
@log_requests
def analyze():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    # Support both 'emailText' (original) and 'text' (new) for backward compatibility
    email_text = (data.get('emailText') or data.get('text') or '').strip()
    if not email_text:
        return jsonify({"error": "emailText or text is required"}), 400

    try:
        proba = model.predict_proba([email_text])[0]
        spam_prob = float(proba[1])
    except Exception as e:
        log_structured('ERROR', 'model_inference_failed', error=str(e))
        return jsonify({"error": "Model inference failed", "details": str(e)}), 500

    threshold = config.DEFAULT_THRESHOLD
    is_spam = bool(spam_prob > threshold)

    # Get keyword importance
    keywords = get_feature_importance(model, email_text)

    # Persist to DB with user_id
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        conn.execute("INSERT INTO emails (user_id, content, is_spam, confidence, keywords) VALUES (?, ?, ?, ?, ?)", 
                    (user_id, email_text, int(is_spam), spam_prob, json.dumps(keywords)))
        conn.commit()
        conn.close()
        log_structured('INFO', 'email_analyzed_and_stored', is_spam=is_spam, confidence=spam_prob)
    except Exception as e:
        log_structured('WARNING', 'db_insert_failed', error=str(e))

    return jsonify({
        "is_spam": is_spam,
        "confidence": spam_prob,
        "threshold": threshold,
        "keywords": keywords,
        "text": email_text,
        "prediction": "spam" if is_spam else "ham"
    })

@app.route('/analyze-image', methods=['POST'])
@jwt_required()
@log_requests
def analyze_image():
    """Analyze email screenshot using OCR and spam classification"""
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}
    image_data = data.get('image')
    
    if not image_data:
        return jsonify({"error": "image data is required"}), 400
    
    try:
        # Extract text from image using OCR
        log_structured('INFO', 'starting_ocr_processing')
        extracted_text = process_image_ocr(image_data)
        
        if not extracted_text.strip():
            return jsonify({
                "error": "No text could be extracted from the image",
                "extracted_text": "",
                "suggestions": [
                    "Ensure the image is clear and high resolution",
                    "Make sure the text is clearly visible",
                    "Try adjusting the image contrast or brightness"
                ]
            }), 400
        
        # Clean the extracted text
        cleaned_text = clean_extracted_text(extracted_text)
        
        # Analyze the extracted text for spam
        try:
            proba = model.predict_proba([cleaned_text])[0]
            spam_prob = float(proba[1])
        except Exception as e:
            log_structured('ERROR', 'model_inference_failed', error=str(e))
            return jsonify({
                "error": "Model inference failed", 
                "details": str(e),
                "extracted_text": extracted_text
            }), 500

        threshold = config.DEFAULT_THRESHOLD
        is_spam = bool(spam_prob > threshold)

        # Get keyword importance
        keywords = get_feature_importance(model, cleaned_text)

        # Persist to DB with OCR source indicator and user_id
        try:
            conn = sqlite3.connect(config.DATABASE_URL)
            conn.execute("INSERT INTO emails (user_id, content, is_spam, confidence, keywords) VALUES (?, ?, ?, ?, ?)", 
                        (user_id, f"[OCR] {cleaned_text}", int(is_spam), spam_prob, json.dumps(keywords)))
            conn.commit()
            conn.close()
            log_structured('INFO', 'image_email_analyzed_and_stored', 
                         user_id=user_id, is_spam=is_spam, confidence=spam_prob, 
                         text_length=len(cleaned_text))
        except Exception as e:
            log_structured('WARNING', 'db_insert_failed', error=str(e))

        return jsonify({
            "is_spam": is_spam,
            "confidence": spam_prob,
            "threshold": threshold,
            "keywords": keywords,
            "text": cleaned_text,
            "extracted_text": extracted_text,
            "source": "ocr",
            "processing_notes": "Text extracted from image using OCR",
            "prediction": "spam" if is_spam else "ham"
        })
    
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        log_structured('ERROR', 'image_analysis_failed', error=str(e))
        return jsonify({
            "error": "Image analysis failed", 
            "details": str(e)
        }), 500

@app.route('/retrain', methods=['POST'])
@log_requests 
def retrain():
    """Retrain model with new labeled data"""
    data = request.get_json(silent=True) or {}
    training_data = data.get('training_data', [])
    
    if not training_data:
        return jsonify({"error": "training_data is required"}), 400
    
    if not all('text' in item and 'label' in item for item in training_data):
        return jsonify({"error": "Each training item must have 'text' and 'label'"}), 400
    
    try:
        # Load existing data and combine with new data
        existing_df = load_training_data()
        new_df = pd.DataFrame(training_data)
        
        # Validate labels
        if not new_df['label'].isin([0, 1]).all():
            return jsonify({"error": "Labels must be 0 or 1"}), 400
        
        # Combine datasets
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Retrain model
        global model
        model = make_pipeline(TfidfVectorizer(), MultinomialNB())
        model.fit(combined_df['text'], combined_df['label'])
        
        # Save updated model
        joblib.dump(model, config.MODEL_PATH)
        
        # Generate training report
        y_pred = model.predict(combined_df['text'])
        report = classification_report(combined_df['label'], y_pred, output_dict=True)
        
        log_structured('INFO', 'model_retrained', 
                     total_samples=len(combined_df),
                     new_samples=len(new_df),
                     accuracy=report['accuracy'])
        
        return jsonify({
            "message": "Model retrained successfully",
            "total_samples": len(combined_df),
            "new_samples": len(new_df),
            "accuracy": report['accuracy'],
            "classification_report": report
        })
        
    except Exception as e:
        log_structured('ERROR', 'retrain_failed', error=str(e))
        return jsonify({"error": "Retraining failed", "details": str(e)}), 500

@app.route('/history', methods=['GET'])
@jwt_required()
@log_requests
def get_history():
    user_id = int(get_jwt_identity())
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        cursor = conn.execute("""
            SELECT content, is_spam, confidence, keywords, timestamp 
            FROM emails 
            WHERE user_id = ? 
            ORDER BY timestamp DESC
        """, (user_id,))
        emails = []
        for row in cursor:
            keywords = json.loads(row[3]) if row[3] else []
            emails.append({
                "text": row[0], 
                "is_spam": bool(row[1]), 
                "confidence": row[2],
                "keywords": keywords,
                "timestamp": row[4]
            })
        conn.close()
        return jsonify(emails)
    except Exception as e:
        log_structured('ERROR', 'history_fetch_failed', error=str(e), user_id=user_id)
        return jsonify({"error": "Failed to fetch history"}), 500

@app.route('/stats', methods=['GET'])
@jwt_required()
@log_requests
def get_stats():
    """Get model and data statistics for the current user"""
    user_id = int(get_jwt_identity())
    try:
        conn = sqlite3.connect(config.DATABASE_URL)
        cursor = conn.execute("""
            SELECT COUNT(*) as total, SUM(is_spam) as spam_count 
            FROM emails 
            WHERE user_id = ?
        """, (user_id,))
        result = cursor.fetchone()
        total_emails = result[0]
        spam_count = result[1] or 0
        ham_count = total_emails - spam_count
        conn.close()
        
        return jsonify({
            "total_analyzed": total_emails,
            "spam_count": spam_count,
            "ham_count": ham_count,
            "spam_ratio": round(spam_count / max(total_emails, 1), 3),
            "model_threshold": config.DEFAULT_THRESHOLD
        })
    except Exception as e:
        log_structured('ERROR', 'stats_fetch_failed', error=str(e))
        return jsonify({"error": "Failed to fetch statistics"}), 500

@app.route('/contact', methods=['POST'])
@log_requests
def contact():
    data = request.get_json(silent=True) or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    message = data.get('message', '').strip()
    
    if not name or not email or not message:
        return jsonify({'error': 'Name, email, and message are required.'}), 400

    # Validate email format
    import re
    email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_regex, email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    # Check if Gmail credentials are configured
    if not GMAIL_USER or not GMAIL_PASS:
        log_structured('ERROR', 'gmail_credentials_missing')
        return jsonify({'error': 'Email service is not configured.'}), 500

    # Compose email
    subject = f"Contact Form Submission from {name}"
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
    
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = CONTACT_RECEIVER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, CONTACT_RECEIVER, msg.as_string())
        
        log_structured('INFO', 'contact_email_sent', 
                     sender_name=name, sender_email=email)
        return jsonify({'message': 'Contact form submitted successfully. We will get back to you soon!'}), 200
    except Exception as e:
        log_structured('ERROR', 'contact_email_failed', error=str(e))
        return jsonify({'error': 'Failed to send email. Please try again later.'}), 500

if __name__ == '__main__':
    import platform
    is_windows = platform.system().lower() == 'windows'
    
    log_structured('INFO', 'application_starting', 
                 host=config.HOST, 
                 port=config.PORT, 
                 debug=config.DEBUG,
                 platform=platform.system())
    
    if is_windows:
        # Windows-specific recommendations
        print("🪟 Windows detected - For better stability, consider using:")
        print("   python start_server.py")
        print("   or")
        print("   start_server.bat")
        print("")
    
    # Use Windows-optimized settings
    app.run(
        debug=config.DEBUG, 
        host=config.HOST, 
        port=config.PORT,
        threaded=True,  # Enable threading for better Windows compatibility
        use_reloader=False if is_windows else True  # Disable reloader on Windows to prevent crashes
    )