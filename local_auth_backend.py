#!/usr/bin/env python3
"""
WORKING Local Test Backend for Immediate Authentication Testing
This will help you test your frontend while fixing Railway issues
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
import logging
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS setup - allow your Vercel frontend
CORS(app, 
     origins=["https://spamwall.vercel.app", "http://localhost:3000", "http://localhost:3001"],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

app.config['JWT_SECRET_KEY'] = 'local-test-secret-key-123'

def create_token(user_id):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'sub': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect('local_auth_test.db')
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
    logger.info("✅ Database initialized")

def get_user_by_email(email):
    """Get user by email"""
    conn = sqlite3.connect('local_auth_test.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, password_hash FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {
            'id': user[0],
            'email': user[1],
            'password_hash': user[2]
        }
    return None

def create_user(email, password_hash):
    """Create new user"""
    conn = sqlite3.connect('local_auth_test.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        'status': 'healthy',
        'message': 'Local authentication test backend is running',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/register', methods=['POST'])
def register():
    """User registration"""
    logger.info("📝 Registration request received")
    
    try:
        # Log request details
        logger.info(f"📨 Headers: {dict(request.headers)}")
        logger.info(f"📨 Content-Type: {request.content_type}")
        
        data = request.get_json()
        logger.info(f"📨 Request data: {data}")
        
        # Validate input
        if not data:
            logger.error("❌ No JSON data received")
            return jsonify({'error': 'No data received'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            logger.error(f"❌ Missing fields - email: {bool(email)}, password: {bool(password)}")
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Clean input
        email = str(email).lower().strip()
        password = str(password)
        
        if len(email) < 3 or len(password) < 6:
            return jsonify({'error': 'Email must be at least 3 chars, password at least 6 chars'}), 400
        
        # Check if user exists
        existing_user = get_user_by_email(email)
        if existing_user:
            logger.warning(f"⚠️ User already exists: {email}")
            return jsonify({'error': 'User with this email already exists'}), 400
        
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Create user
        user_id = create_user(email, password_hash)
        
        # Generate token
        access_token = create_token(user_id)
        
        logger.info(f"✅ User registered successfully: {email}")
        
        return jsonify({
            'message': 'User registered successfully',
            'access_token': access_token,
            'user': {
                'id': user_id,
                'email': email
            }
        }), 201
        
    except Exception as e:
        logger.error(f"🚨 Registration error: {e}", exc_info=True)
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login"""
    logger.info("🔑 Login request received")
    
    try:
        # Log request details
        logger.info(f"📨 Headers: {dict(request.headers)}")
        logger.info(f"📨 Content-Type: {request.content_type}")
        
        data = request.get_json()
        logger.info(f"📨 Request data: {data}")
        
        # Validate input
        if not data:
            logger.error("❌ No JSON data received")
            return jsonify({'error': 'No data received'}), 400
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            logger.error(f"❌ Missing fields - email: {bool(email)}, password: {bool(password)}")
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Clean input
        email = str(email).lower().strip()
        password = str(password)
        
        # Get user
        user = get_user_by_email(email)
        if not user:
            logger.warning(f"⚠️ User not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            logger.warning(f"⚠️ Invalid password for: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        access_token = create_token(user['id'])
        
        logger.info(f"✅ User logged in successfully: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'email': user['email']
            }
        })
        
    except Exception as e:
        logger.error(f"🚨 Login error: {e}", exc_info=True)
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

@app.route('/verify-token', methods=['GET'])
def verify_token():
    """Verify JWT token"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Token missing'}), 401
        
        token = auth_header.split(' ')[1]
        data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        
        return jsonify({
            'valid': True,
            'user_id': data.get('user_id') or data.get('sub')
        })
        
    except jwt.ExpiredSignatureError:
        return jsonify({'error': 'Token expired'}), 401
    except jwt.InvalidTokenError:
        return jsonify({'error': 'Invalid token'}), 401
    except Exception as e:
        return jsonify({'error': f'Token verification failed: {str(e)}'}), 401

# Handle CORS preflight requests
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = jsonify({'status': 'OK'})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', "Content-Type,Authorization,Accept")
        response.headers.add('Access-Control-Allow-Methods', "GET,PUT,POST,DELETE,OPTIONS")
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    print("🚀 LOCAL AUTHENTICATION TEST BACKEND")
    print("=" * 50)
    print("✅ Starting on: http://localhost:5001")
    print("🌐 CORS enabled for:")
    print("   → https://spamwall.vercel.app")
    print("   → http://localhost:3000")
    print("   → http://localhost:3001")
    print("")
    print("📝 TO USE WITH YOUR FRONTEND:")
    print("   1. Update authService.ts baseUrl to: http://localhost:5001")
    print("   2. Test your login/register forms")
    print("   3. Check browser console for detailed logs")
    print("")
    print("🔍 Debug logs will show all requests...")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5001, debug=True)
