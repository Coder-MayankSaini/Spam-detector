#!/usr/bin/env python3
"""
Minimal test backend to debug authentication issues
Uses SQLite instead of PostgreSQL for local testing
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple CORS setup for testing
CORS(app, origins=["*"], supports_credentials=True)

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'test-secret-key-for-debugging'

def create_custom_access_token(user_id):
    """Create custom JWT access token"""
    payload = {
        'sub': user_id,
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token

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
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data.get('sub') or data.get('user_id')
            
            if not current_user_id:
                return jsonify({'error': 'Invalid token payload'}), 401
            
            if isinstance(current_user_id, str):
                current_user_id = int(current_user_id)
            
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

# Simple SQLite database setup
def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_by_email(email):
    """Get user by email"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'email': user[1], 
            'password_hash': user[2],
            'created_at': user[3]
        }
    return None

def create_user(email, password_hash):
    """Create a new user"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

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
def register():
    """User registration endpoint"""
    logger.info("=== REGISTER REQUEST ===")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Method: {request.method}")
    
    try:
        # Get raw data for debugging
        raw_data = request.get_data(as_text=True)
        logger.info(f"Raw request data: {raw_data}")
        
        # Try to get JSON data
        data = request.get_json()
        logger.info(f"Parsed JSON data: {data}")
        
        # Check if data is None or empty
        if not data:
            logger.error("No JSON data received or JSON parsing failed")
            return jsonify({'error': 'No data received. Make sure you\'re sending valid JSON.'}), 400
        
        # Check for required fields
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Email received: {repr(email)}")
        logger.info(f"Password received: {repr(password)}")
        
        if not email or not password:
            logger.error(f"Missing required fields - email: {bool(email)}, password: {bool(password)}")
            return jsonify({
                'error': 'Email and password are required',
                'received_data': {
                    'email': email,
                    'password': '***' if password else None
                }
            }), 400
        
        # Clean and validate
        email = str(email).lower().strip()
        password = str(password)
        
        if not email or not password:
            logger.error("Empty fields after cleaning")
            return jsonify({'error': 'Email and password cannot be empty'}), 400
        
        # Check if user already exists
        existing_user = get_user_by_email(email)
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user_id = create_user(email, password_hash)
        
        # Generate JWT token
        access_token = create_custom_access_token(user_id)
        
        logger.info("Registration successful")
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {'id': user_id, 'email': email}
        }), 201
        
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    logger.info("=== LOGIN REQUEST ===")
    logger.info(f"Headers: {dict(request.headers)}")
    logger.info(f"Content-Type: {request.content_type}")
    logger.info(f"Method: {request.method}")
    
    try:
        # Get raw data for debugging
        raw_data = request.get_data(as_text=True)
        logger.info(f"Raw request data: {raw_data}")
        
        # Try to get JSON data
        data = request.get_json()
        logger.info(f"Parsed JSON data: {data}")
        
        # Check if data is None or empty
        if not data:
            logger.error("No JSON data received or JSON parsing failed")
            return jsonify({'error': 'No data received. Make sure you\'re sending valid JSON.'}), 400
        
        # Check for required fields
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Email received: {repr(email)}")
        logger.info(f"Password received: {repr(password)}")
        
        if not email or not password:
            logger.error(f"Missing required fields - email: {bool(email)}, password: {bool(password)}")
            return jsonify({
                'error': 'Email and password are required',
                'received_data': {
                    'email': email,
                    'password': '***' if password else None
                }
            }), 400
        
        # Clean and validate
        email = str(email).lower().strip()
        password = str(password)
        
        if not email or not password:
            logger.error("Empty fields after cleaning")
            return jsonify({'error': 'Email and password cannot be empty'}), 400
        
        # Get user from database
        user = get_user_by_email(email)
        
        if not user:
            logger.warning(f"User not found for email: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            logger.warning(f"Invalid password for email: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate JWT token
        access_token = create_custom_access_token(user['id'])
        
        logger.info("Login successful")
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {'id': user['id'], 'email': user['email']}
        })
        
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/verify-token', methods=['GET'])
@custom_jwt_required
def verify_token():
    """Verify JWT token"""
    try:
        current_user_id = request.current_user_id
        # In a real app, you'd fetch user from database
        return jsonify({
            'valid': True,
            'user': {
                'id': current_user_id,
                'email': f'user{current_user_id}@test.com'
            }
        })
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        return jsonify({'error': 'Token verification failed'}), 500

# OPTIONS handler for CORS preflight
@app.before_request
def handle_options():
    if request.method == 'OPTIONS':
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

if __name__ == '__main__':
    init_db()
    print("🚀 Starting debug server on http://localhost:5001")
    print("📊 Debug logging enabled")
    app.run(host='0.0.0.0', port=5001, debug=True)
