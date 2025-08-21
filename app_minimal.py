"""
Ultra-minimal Spam Detector for Railway deployment
Only core authentication and basic spam detection
"""
import os
import logging
import traceback
from datetime import datetime, timedelta
from functools import wraps
import sqlite3
import re
import hashlib

from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="*", allow_headers=["Content-Type", "Authorization"])

# Configuration
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
DATABASE_URL = os.environ.get('DATABASE_URL')

# Database setup
def init_db():
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create emails table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                is_spam INTEGER NOT NULL,
                confidence REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")

def hash_password(password):
    """Hash password using hashlib (fallback when bcrypt unavailable)"""
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest()

def check_password(password, password_hash):
    """Check password using hashlib"""
    return hashlib.sha256((password + SECRET_KEY).encode()).hexdigest() == password_hash

def create_jwt_token(user_id, username):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def jwt_required(f):
    """JWT required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header required'}), 401
            
        try:
            token = auth_header.split(' ')[1]
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify({'error': 'Invalid or expired token'}), 401
                
            request.user = payload
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': 'Token verification failed'}), 401
    
    return decorated_function

def rule_based_spam_detection(text):
    """Simple rule-based spam detection"""
    if not text:
        return False, 0.0
    
    text_lower = text.lower()
    
    # Spam indicators
    spam_keywords = [
        'urgent', 'winner', 'congratulations', 'free money', 'click here',
        'limited time', 'act now', 'guaranteed', 'no risk', 'call now',
        'make money fast', 'work from home', 'lose weight', 'viagra',
        'casino', 'lottery', 'inheritance', 'prince', 'millions'
    ]
    
    spam_score = 0
    for keyword in spam_keywords:
        if keyword in text_lower:
            spam_score += 1
    
    # Check for excessive caps
    caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
    if caps_ratio > 0.3:
        spam_score += 2
    
    # Check for excessive exclamation marks
    exclamation_count = text.count('!')
    if exclamation_count > 3:
        spam_score += 1
    
    # Check for suspicious patterns
    if re.search(r'\$\d+', text):  # Dollar amounts
        spam_score += 1
    
    confidence = min(spam_score / 10.0, 1.0)
    is_spam = spam_score >= 3
    
    return is_spam, confidence

# Routes
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'message': 'Spam Detector API is running'
    }), 200

@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Username, email, and password required'}), 400
        
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Hash password
        password_hash = hash_password(password)
        
        # Store user
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            user_id = cursor.lastrowid
            conn.commit()
            
            # Create JWT token
            token = create_jwt_token(user_id, username)
            
            return jsonify({
                'message': 'User registered successfully',
                'token': token,
                'user': {'id': user_id, 'username': username, 'email': email}
            }), 201
            
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Username or email already exists'}), 409
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['username', 'password']):
            return jsonify({'error': 'Username and password required'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, username, email, password_hash FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if not user or not check_password(password, user[3]):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create JWT token
        token = create_jwt_token(user[0], user[1])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {'id': user[0], 'username': user[1], 'email': user[2]}
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/analyze', methods=['POST'])
@jwt_required
def analyze_email():
    """Analyze email for spam"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Email text required'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Email text cannot be empty'}), 400
        
        # Perform spam detection
        is_spam, confidence = rule_based_spam_detection(text)
        
        # Store analysis result
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO emails (user_id, content, is_spam, confidence) VALUES (?, ?, ?, ?)",
            (request.user['user_id'], text, int(is_spam), confidence)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'is_spam': is_spam,
            'confidence': confidence,
            'classification': 'Spam' if is_spam else 'Not Spam',
            'message': 'Email analyzed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/history', methods=['GET'])
@jwt_required
def get_history():
    """Get user's analysis history"""
    try:
        conn = sqlite3.connect('emails.db')
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, content, is_spam, confidence, created_at 
               FROM emails 
               WHERE user_id = ? 
               ORDER BY created_at DESC 
               LIMIT 50""",
            (request.user['user_id'],)
        )
        
        emails = cursor.fetchall()
        conn.close()
        
        history = []
        for email in emails:
            history.append({
                'id': email[0],
                'content': email[1][:200] + '...' if len(email[1]) > 200 else email[1],
                'is_spam': bool(email[2]),
                'confidence': email[3],
                'classification': 'Spam' if email[2] else 'Not Spam',
                'created_at': email[4]
            })
        
        return jsonify({
            'history': history,
            'total': len(history)
        }), 200
        
    except Exception as e:
        logger.error(f"History error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Get port from environment
    port = int(os.environ.get('PORT', 5000))
    
    # Run the app
    app.run(host='0.0.0.0', port=port, debug=False)
