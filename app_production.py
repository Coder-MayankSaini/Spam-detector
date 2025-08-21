"""
Production-ready Spam Detector with OCR and ML Model
Optimized for Railway deployment
"""
import os
import sys
import logging
import time
import base64
import io
import re
import json
import secrets
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path

# Web Framework
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Authentication
import jwt
import bcrypt

# ML and Text Processing
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
import nltk
from bs4 import BeautifulSoup

# OCR and Image Processing
# Logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from PIL import Image, ImageEnhance, ImageFilter
import pytesseract

# Optional OCR dependencies
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    logger.warning("OpenCV not available - using basic image processing")
    CV2_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    logger.warning("EasyOCR not available - OCR will use Tesseract only")
    EASYOCR_AVAILABLE = False

# Email Processing
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Database
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Configuration
class Config:
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-super-secret-key-change-in-production')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # OCR Configuration
    TESSERACT_PATH = os.getenv('TESSERACT_PATH', '/usr/bin/tesseract')
    TESSERACT_CONFIG = '--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,!?@#$%^&*()_+-=[]{}|;":,.<>?/`~'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = '/tmp/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
    
    # Email Configuration
    EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
    
    # Frontend URL
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'https://spamwall.vercel.app')

config = Config()

# Configure Flask
app.config.update(
    SECRET_KEY=config.JWT_SECRET_KEY,
    MAX_CONTENT_LENGTH=config.MAX_CONTENT_LENGTH
)

# Configure CORS
CORS(app, 
     origins=config.CORS_ORIGINS,
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configure logging
logging.basicConfig(
    level=logging.INFO if not config.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure upload directory exists
os.makedirs(config.UPLOAD_FOLDER, exist_ok=True)

# Configure Tesseract
if config.TESSERACT_PATH and os.path.exists(config.TESSERACT_PATH):
    pytesseract.pytesseract.tesseract_cmd = config.TESSERACT_PATH
    logger.info(f"Tesseract configured at: {config.TESSERACT_PATH}")
else:
    logger.warning("Tesseract path not found, using system default")

# Initialize global variables
spam_model = None
ocr_reader = None

class DatabaseManager:
    """Database manager with fallback to in-memory storage"""
    
    def __init__(self):
        self.db_url = config.DATABASE_URL
        self.use_postgres = DB_AVAILABLE and self.db_url
        
        if not self.use_postgres:
            logger.warning("Using in-memory database - data will be lost on restart")
            self.users = {}
            self.analysis_history = []
            self.contact_messages = []
            self.next_user_id = 1
    
    def init_database(self):
        """Initialize database tables"""
        if self.use_postgres:
            try:
                with psycopg2.connect(self.db_url) as conn:
                    with conn.cursor() as cur:
                        # Create users table
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id SERIAL PRIMARY KEY,
                                email VARCHAR(255) UNIQUE NOT NULL,
                                password_hash VARCHAR(255) NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                reset_token VARCHAR(255),
                                reset_token_expires TIMESTAMP
                            )
                        """)
                        
                        # Create analysis_history table
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS analysis_history (
                                id SERIAL PRIMARY KEY,
                                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                                email_text TEXT NOT NULL,
                                is_spam BOOLEAN NOT NULL,
                                confidence FLOAT NOT NULL,
                                analysis_type VARCHAR(50) DEFAULT 'text',
                                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                ip_address VARCHAR(45),
                                extracted_text TEXT
                            )
                        """)
                        
                        # Create contact_messages table
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS contact_messages (
                                id SERIAL PRIMARY KEY,
                                name VARCHAR(255) NOT NULL,
                                email VARCHAR(255) NOT NULL,
                                message TEXT NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)
                        
                        conn.commit()
                        logger.info("PostgreSQL database initialized successfully")
                        
            except Exception as e:
                logger.error(f"PostgreSQL initialization failed: {e}")
                self.use_postgres = False
        
        logger.info(f"Database initialized: {'PostgreSQL' if self.use_postgres else 'In-memory'}")
        return True
    
    def get_user_by_email(self, email):
        """Get user by email"""
        if self.use_postgres:
            try:
                with psycopg2.connect(self.db_url) as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cur:
                        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                        return cur.fetchone()
            except Exception as e:
                logger.error(f"Database error: {e}")
                return None
        else:
            for user_id, user_data in self.users.items():
                if user_data['email'] == email:
                    return {'id': int(user_id), **user_data}
            return None
    
    def create_user(self, email, password_hash):
        """Create a new user"""
        if self.use_postgres:
            try:
                with psycopg2.connect(self.db_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute(
                            "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                            (email, password_hash)
                        )
                        user_id = cur.fetchone()[0]
                        conn.commit()
                        return user_id
            except Exception as e:
                logger.error(f"Database error: {e}")
                raise
        else:
            user_id = self.next_user_id
            self.next_user_id += 1
            self.users[str(user_id)] = {
                'email': email,
                'password_hash': password_hash,
                'created_at': datetime.now()
            }
            return user_id
    
    def save_analysis(self, user_id, email_text, is_spam, confidence, analysis_type='text', ip_address=None, extracted_text=None):
        """Save analysis to history"""
        if self.use_postgres:
            try:
                with psycopg2.connect(self.db_url) as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO analysis_history (user_id, email_text, is_spam, confidence, analysis_type, ip_address, extracted_text)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """, (user_id, email_text, is_spam, confidence, analysis_type, ip_address, extracted_text))
                        conn.commit()
            except Exception as e:
                logger.error(f"Database error: {e}")
        else:
            self.analysis_history.append({
                'user_id': user_id,
                'email_text': email_text,
                'is_spam': is_spam,
                'confidence': confidence,
                'analysis_type': analysis_type,
                'timestamp': datetime.now(),
                'ip_address': ip_address,
                'extracted_text': extracted_text
            })

# Initialize database manager
db_manager = DatabaseManager()

def download_nltk_data():
    """Download required NLTK data"""
    try:
        import ssl
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context
        
        nltk_data_path = '/tmp/nltk_data'
        os.makedirs(nltk_data_path, exist_ok=True)
        nltk.data.path.append(nltk_data_path)
        
        required_corpora = ['punkt', 'stopwords', 'wordnet', 'vader_lexicon']
        for corpus in required_corpora:
            try:
                nltk.download(corpus, download_dir=nltk_data_path, quiet=True)
                logger.info(f"Downloaded NLTK corpus: {corpus}")
            except Exception as e:
                logger.warning(f"Could not download NLTK corpus {corpus}: {e}")
                
    except Exception as e:
        logger.error(f"NLTK setup failed: {e}")

def load_spam_model():
    """Load or create spam detection model"""
    global spam_model
    
    model_path = 'spam_model.joblib'
    
    try:
        # Try to load existing model
        if os.path.exists(model_path):
            spam_model = joblib.load(model_path)
            logger.info("Spam detection model loaded successfully")
            return
    except Exception as e:
        logger.warning(f"Could not load existing model: {e}")
    
    # Create new model with comprehensive training data
    try:
        logger.info("Creating new spam detection model...")
        
        # Enhanced training data
        spam_samples = [
            "Congratulations! You've won $1,000,000! Click here to claim your prize now!",
            "URGENT: Your account will be suspended! Click here immediately!",
            "Get rich quick! Make money fast with this amazing opportunity!",
            "Free trial! Limited time offer! Act now or miss out forever!",
            "You have been selected for a special offer! Click here now!",
            "Earn $5000 a week working from home! No experience needed!",
            "Your credit card has been charged $500. Click to dispute immediately!",
            "Hot singles in your area want to meet you tonight!",
            "Lose 30 pounds in 30 days with this miracle pill!",
            "Work from home and earn big money! No boss! No commute!",
            "Free iPhone! Just pay shipping and handling!",
            "Nigerian prince needs your help transferring $10 million!",
            "Act now! This offer expires in 24 hours!",
            "100% guaranteed! Risk-free! Money back guarantee!",
            "Click here to unsubscribe (this is usually a spam trick)"
        ]
        
        ham_samples = [
            "Hi, can we schedule a meeting for next Tuesday?",
            "Please review the attached document and send me your feedback.",
            "Thank you for your email. I will respond by tomorrow.",
            "The project deadline has been extended to next Friday.",
            "Please find the requested information in the attachment.",
            "How was your weekend? Hope you had a great time!",
            "The meeting has been moved to conference room B.",
            "Can you please send me the latest version of the report?",
            "Thanks for the quick response. This is very helpful.",
            "Let's discuss this further in our next team meeting.",
            "I've forwarded your request to the appropriate department.",
            "Please let me know if you need any additional information.",
            "The conference call is scheduled for 3 PM today.",
            "I appreciate your patience while we resolve this issue.",
            "Looking forward to hearing from you soon."
        ]
        
        # Prepare training data
        texts = spam_samples + ham_samples
        labels = [1] * len(spam_samples) + [0] * len(ham_samples)
        
        # Create and train model
        spam_model = make_pipeline(
            TfidfVectorizer(
                max_features=5000,
                stop_words='english',
                ngram_range=(1, 3),
                min_df=1,
                max_df=0.95,
                sublinear_tf=True
            ),
            MultinomialNB(alpha=1.0)
        )
        
        spam_model.fit(texts, labels)
        
        # Save model
        joblib.dump(spam_model, model_path)
        logger.info("Spam detection model created and saved successfully")
        
        # Test model
        test_spam = "Congratulations! You won $1000! Click now!"
        test_ham = "Please review the attached document"
        
        spam_pred = spam_model.predict([test_spam])[0]
        ham_pred = spam_model.predict([test_ham])[0]
        
        logger.info(f"Model test - Spam prediction: {spam_pred}, Ham prediction: {ham_pred}")
        
    except Exception as e:
        logger.error(f"Model creation failed: {e}")
        spam_model = None

def initialize_ocr():
    """Initialize OCR engines"""
    global ocr_reader
    
    try:
        # Test Tesseract
        test_img = Image.new('RGB', (100, 50), color='white')
        pytesseract.image_to_string(test_img, config=config.TESSERACT_CONFIG)
        logger.info("Tesseract OCR initialized successfully")
    except Exception as e:
        logger.warning(f"Tesseract initialization failed: {e}")
    
    try:
        # Initialize EasyOCR
        ocr_reader = easyocr.Reader(['en'], gpu=False)
        logger.info("EasyOCR initialized successfully")
    except Exception as e:
        logger.warning(f"EasyOCR initialization failed: {e}")

def preprocess_image(image):
    """Enhanced image preprocessing for better OCR"""
    try:
        # Convert to grayscale
        if image.mode != 'L':
            image = image.convert('L')
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2.0)
        
        # Enhance sharpness
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(1.5)
        
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_GRAY2BGR)
        
        # Apply denoising
        cv_image = cv2.fastNlMeansDenoising(cv_image)
        
        # Apply threshold
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Convert back to PIL
        return Image.fromarray(thresh)
        
    except Exception as e:
        logger.error(f"Image preprocessing failed: {e}")
        return image

def extract_text_from_image(image):
    """Extract text using multiple OCR methods"""
    extracted_texts = []
    
    # Preprocess image
    processed_image = preprocess_image(image)
    
    # Method 1: Tesseract OCR
    try:
        tesseract_text = pytesseract.image_to_string(
            processed_image, 
            config=config.TESSERACT_CONFIG
        ).strip()
        if tesseract_text:
            extracted_texts.append(("Tesseract", tesseract_text))
    except Exception as e:
        logger.error(f"Tesseract OCR failed: {e}")
    
    # Method 2: EasyOCR
    if ocr_reader:
        try:
            results = ocr_reader.readtext(np.array(processed_image))
            easyocr_text = ' '.join([result[1] for result in results if result[2] > 0.5]).strip()
            if easyocr_text:
                extracted_texts.append(("EasyOCR", easyocr_text))
        except Exception as e:
            logger.error(f"EasyOCR failed: {e}")
    
    # Return best result (longest text)
    if extracted_texts:
        best_result = max(extracted_texts, key=lambda x: len(x[1]))
        logger.info(f"Best OCR result from {best_result[0]}: {len(best_result[1])} characters")
        return best_result[1]
    else:
        return None

def clean_text(text):
    """Clean and preprocess text for spam detection"""
    if not text:
        return ""
    
    try:
        # Remove HTML tags if present
        text = BeautifulSoup(text, 'html.parser').get_text()
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{2,}', '!', text)
        text = re.sub(r'[?]{2,}', '?', text)
        
        return text.strip()
        
    except Exception as e:
        logger.error(f"Text cleaning failed: {e}")
        return text

# JWT utilities
def create_access_token(user_id):
    """Create JWT access token"""
    payload = {
        'sub': user_id,
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, config.JWT_SECRET_KEY, algorithm='HS256')

def jwt_required(f):
    """JWT authentication decorator"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            data = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
            current_user_id = data.get('sub') or data.get('user_id')
            
            if not current_user_id:
                return jsonify({'error': 'Invalid token'}), 401
            
            request.current_user_id = int(current_user_id) if isinstance(current_user_id, str) else current_user_id
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'components': {
            'spam_model': spam_model is not None,
            'ocr_tesseract': True,  # Always assume available
            'ocr_easyocr': ocr_reader is not None,
            'database': db_manager.use_postgres
        }
    })

@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Validate email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        if db_manager.get_user_by_email(email):
            return jsonify({'error': 'User already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user_id = db_manager.create_user(email, password_hash)
        
        # Generate token
        access_token = create_access_token(user_id)
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': {'id': user_id, 'email': email}
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get user
        user = db_manager.get_user_by_email(email)
        if not user:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        access_token = create_access_token(user['id'])
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {'id': user['id'], 'email': user['email']}
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Login failed'}), 500

@app.route('/analyze', methods=['POST'])
@jwt_required
def analyze_text():
    """Analyze text for spam detection"""
    try:
        if not spam_model:
            return jsonify({'error': 'Spam detection model not available'}), 503
        
        data = request.get_json()
        if not data or not data.get('text'):
            return jsonify({'error': 'Text content required'}), 400
        
        email_text = data['text'].strip()
        
        if len(email_text) < 10:
            return jsonify({'error': 'Text too short for analysis'}), 400
        
        # Clean text
        clean_email_text = clean_text(email_text)
        
        # Predict
        prediction = spam_model.predict([clean_email_text])[0]
        probabilities = spam_model.predict_proba([clean_email_text])[0]
        
        is_spam = bool(prediction)
        confidence = float(max(probabilities))
        
        # Save to database
        user_id = request.current_user_id
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        try:
            db_manager.save_analysis(
                user_id=user_id,
                email_text=email_text[:1000],  # Truncate for storage
                is_spam=is_spam,
                confidence=confidence,
                analysis_type='text',
                ip_address=client_ip
            )
        except Exception as db_error:
            logger.error(f"Database save failed: {db_error}")
        
        return jsonify({
            'is_spam': is_spam,
            'confidence': confidence,
            'analysis': {
                'spam_probability': float(probabilities[1]) if len(probabilities) > 1 else confidence,
                'ham_probability': float(probabilities[0]) if len(probabilities) > 1 else (1 - confidence),
                'processed_text_length': len(clean_email_text)
            }
        })
        
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        return jsonify({'error': 'Analysis failed'}), 500

@app.route('/analyze-image', methods=['POST'])
@jwt_required
def analyze_image():
    """Analyze image with OCR and spam detection"""
    try:
        if not spam_model:
            return jsonify({'error': 'Spam detection model not available'}), 503
        
        data = request.get_json()
        if not data or not data.get('image'):
            return jsonify({'error': 'Image data required'}), 400
        
        # Decode base64 image
        image_data = data['image']
        if ',' in image_data:
            image_data = image_data.split(',')[1]
        
        try:
            image_bytes = base64.b64decode(image_data)
            image = Image.open(io.BytesIO(image_bytes))
        except Exception as e:
            return jsonify({'error': 'Invalid image data'}), 400
        
        # Extract text using OCR
        extracted_text = extract_text_from_image(image)
        
        if not extracted_text or len(extracted_text.strip()) < 5:
            return jsonify({'error': 'No readable text found in image'}), 400
        
        # Clean extracted text
        clean_extracted_text = clean_text(extracted_text)
        
        # Analyze with spam model
        prediction = spam_model.predict([clean_extracted_text])[0]
        probabilities = spam_model.predict_proba([clean_extracted_text])[0]
        
        is_spam = bool(prediction)
        confidence = float(max(probabilities))
        
        # Save to database
        user_id = request.current_user_id
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        
        try:
            db_manager.save_analysis(
                user_id=user_id,
                email_text=clean_extracted_text[:1000],
                is_spam=is_spam,
                confidence=confidence,
                analysis_type='image',
                ip_address=client_ip,
                extracted_text=extracted_text[:2000]
            )
        except Exception as db_error:
            logger.error(f"Database save failed: {db_error}")
        
        return jsonify({
            'is_spam': is_spam,
            'confidence': confidence,
            'extracted_text': extracted_text,
            'analysis': {
                'spam_probability': float(probabilities[1]) if len(probabilities) > 1 else confidence,
                'ham_probability': float(probabilities[0]) if len(probabilities) > 1 else (1 - confidence),
                'extracted_text_length': len(extracted_text),
                'processed_text_length': len(clean_extracted_text)
            }
        })
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        return jsonify({'error': 'Image analysis failed'}), 500

@app.route('/upload-analyze', methods=['POST'])
@jwt_required
def upload_and_analyze():
    """Upload file and analyze with OCR"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        # Save uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        try:
            # Open and process image
            image = Image.open(filepath)
            
            # Extract text
            extracted_text = extract_text_from_image(image)
            
            if not extracted_text or len(extracted_text.strip()) < 5:
                return jsonify({'error': 'No readable text found in uploaded image'}), 400
            
            # Analyze with spam model
            if spam_model:
                clean_extracted_text = clean_text(extracted_text)
                prediction = spam_model.predict([clean_extracted_text])[0]
                probabilities = spam_model.predict_proba([clean_extracted_text])[0]
                
                is_spam = bool(prediction)
                confidence = float(max(probabilities))
                
                # Save to database
                user_id = request.current_user_id
                client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
                
                try:
                    db_manager.save_analysis(
                        user_id=user_id,
                        email_text=clean_extracted_text[:1000],
                        is_spam=is_spam,
                        confidence=confidence,
                        analysis_type='upload',
                        ip_address=client_ip,
                        extracted_text=extracted_text[:2000]
                    )
                except Exception as db_error:
                    logger.error(f"Database save failed: {db_error}")
                
                result = {
                    'is_spam': is_spam,
                    'confidence': confidence,
                    'extracted_text': extracted_text,
                    'analysis': {
                        'spam_probability': float(probabilities[1]) if len(probabilities) > 1 else confidence,
                        'ham_probability': float(probabilities[0]) if len(probabilities) > 1 else (1 - confidence),
                        'extracted_text_length': len(extracted_text),
                        'processed_text_length': len(clean_extracted_text)
                    }
                }
            else:
                result = {
                    'extracted_text': extracted_text,
                    'message': 'Text extracted successfully, but spam analysis unavailable'
                }
            
            return jsonify(result)
            
        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                
    except Exception as e:
        logger.error(f"Upload analysis error: {e}")
        return jsonify({'error': 'Upload analysis failed'}), 500

@app.errorhandler(413)
def file_too_large(error):
    return jsonify({'error': 'File too large (max 16MB)'}), 413

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# Initialize components
def initialize_app():
    """Initialize all app components"""
    logger.info("Initializing Spam Detector application...")
    
    # Initialize database
    try:
        db_manager.init_database()
        logger.info("Database initialization completed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    
    # Download NLTK data
    try:
        download_nltk_data()
        logger.info("NLTK data download completed")
    except Exception as e:
        logger.error(f"NLTK setup failed: {e}")
    
    # Load spam model
    try:
        load_spam_model()
        logger.info("Spam model initialization completed")
    except Exception as e:
        logger.error(f"Spam model initialization failed: {e}")
    
    # Initialize OCR
    try:
        initialize_ocr()
        logger.info("OCR initialization completed")
    except Exception as e:
        logger.error(f"OCR initialization failed: {e}")
    
    logger.info("Application initialization completed")

if __name__ == '__main__':
    initialize_app()
    
    if os.getenv('RAILWAY_ENVIRONMENT') == 'production':
        # Production mode
        import gunicorn
        logger.info("Starting in production mode with Gunicorn")
    else:
        # Development mode
        logger.info(f"Starting development server on {config.HOST}:{config.PORT}")
        app.run(
            host=config.HOST,
            port=config.PORT,
            debug=config.DEBUG
        )
else:
    # When imported by WSGI server
    initialize_app()
