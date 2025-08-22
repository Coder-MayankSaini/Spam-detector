#!/usr/bin/env python3
"""
COMPREHENSIVE AUTHENTICATION FIX GUIDE
Based on your specific spam detector app setup
"""

def print_section(title, emoji="🔧"):
    print(f"\n{emoji} {title}")
    print("="*60)

def main():
    print_section("AUTHENTICATION PROBLEM DIAGNOSIS", "🔍")
    
    print("✅ Your Railway backend IS running (health check passes)")
    print("❌ Authentication endpoints (/login, /register) are timing out")
    print("🎯 This indicates a specific problem with auth routes")
    
    print_section("ROOT CAUSE ANALYSIS", "🔬")
    
    print("Most likely causes:")
    print("1. 🐛 Database connection issues in auth routes")
    print("2. 🔒 Missing environment variables for auth")
    print("3. 📦 Dependencies missing on Railway") 
    print("4. 🌐 CORS issues blocking auth requests")
    print("5. 🔄 Auth routes hanging due to external service calls")
    
    print_section("IMMEDIATE FIXES", "🚀")
    
    print("FIX 1: Check Railway Environment Variables")
    print("-" * 40)
    print("Go to Railway Dashboard → Your Project → Variables")
    print("Ensure these are set:")
    print("  • DATABASE_URL")
    print("  • JWT_SECRET_KEY") 
    print("  • CORS_ORIGINS=https://spamwall.vercel.app")
    print("  • DB_HOST, DB_NAME, DB_USER, DB_PASSWORD (if using individual vars)")
    
    print("\nFIX 2: Check Railway Deployment Logs")
    print("-" * 40)
    print("Railway Dashboard → Your Project → Deployments → View Logs")
    print("Look for errors related to:")
    print("  • Database connection failures")
    print("  • Import errors (psycopg2, bcrypt, etc.)")
    print("  • Authentication route errors")
    
    print("\nFIX 3: Simplify Backend for Testing")
    print("-" * 40)
    print("Create a minimal auth endpoint to test:")
    
    print("""
# Add this simple test route to your app.py:
@app.route('/test-auth', methods=['POST'])
def test_auth():
    try:
        data = request.get_json()
        return jsonify({
            'status': 'success',
            'received': data,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    """)
    
    print("\nFIX 4: Update Frontend for Better Error Handling")
    print("-" * 40)
    print("Modify your authService.ts:")
    
    print("""
// Add timeout and better error handling
async login(data: LoginRequest): Promise<AuthResponse> {
  console.log('🔑 Attempting login...', { email: data.email });
  
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 30000); // 30s timeout
    
    const response = await fetch(`${this.baseUrl}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    
    console.log('📊 Response status:', response.status);
    
    if (!response.ok) {
      const error = await response.json();
      console.error('❌ Login error:', error);
      throw new Error(error.error || 'Login failed');
    }
    
    const result = await response.json();
    console.log('✅ Login successful!');
    this.setToken(result.access_token);
    return result;
    
  } catch (error) {
    console.error('🚨 Login exception:', error);
    if (error.name === 'AbortError') {
      throw new Error('Request timed out - please try again');
    }
    throw error;
  }
}
    """)
    
    print_section("QUICK LOCAL TESTING SOLUTION", "⚡")
    
    print("While fixing Railway, test locally:")
    print("1. Run your backend locally on port 5001")
    print("2. Update frontend authService.ts temporarily:")
    print("   baseUrl = 'http://localhost:5001'")
    print("3. Test authentication locally")
    print("4. Once working, deploy fixes to Railway")
    
    print_section("ALTERNATIVE BACKEND ENDPOINT", "🔄")
    
    print("Create this working endpoint to test your frontend:")

if __name__ == "__main__":
    main()
    
    # Create a working local backend for immediate testing
    create_test_backend = input("\n🤔 Create a local test backend? (y/n): ").lower().startswith('y')
    
    if create_test_backend:
        print("\n📝 Creating local test backend...")
        
        test_backend_code = '''#!/usr/bin/env python3
"""
WORKING Local Test Backend for Immediate Testing
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
from datetime import datetime, timedelta
from functools import wraps
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True, allow_headers=["Content-Type", "Authorization"])

app.config['JWT_SECRET_KEY'] = 'local-test-secret'

def create_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm='HS256')

def init_db():
    conn = sqlite3.connect('local_test.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'healthy',
        'message': 'Local test backend running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/register', methods=['POST'])
def register():
    logger.info("📝 Registration request received")
    
    try:
        data = request.get_json()
        logger.info(f"📨 Request data: {data}")
        
        if not data or not data.get('email') or not data.get('password'):
            logger.error("❌ Missing email or password")
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Check existing user
        conn = sqlite3.connect('local_test.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE email = ?', (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'User already exists'}), 400
        
        # Create user
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        cursor.execute('INSERT INTO users (email, password_hash) VALUES (?, ?)', (email, password_hash))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        token = create_token(user_id)
        logger.info(f"✅ User registered: {email}")
        
        return jsonify({
            'message': 'Registration successful',
            'access_token': token,
            'user': {'id': user_id, 'email': email}
        }), 201
        
    except Exception as e:
        logger.error(f"🚨 Registration error: {e}")
        return jsonify({'error': f'Registration failed: {str(e)}'}), 500

@app.route('/login', methods=['POST'])
def login():
    logger.info("🔑 Login request received")
    
    try:
        data = request.get_json()
        logger.info(f"📨 Request data: {data}")
        
        if not data or not data.get('email') or not data.get('password'):
            logger.error("❌ Missing email or password")
            return jsonify({'error': 'Email and password are required'}), 400
        
        email = data['email'].lower().strip()
        password = data['password']
        
        # Get user
        conn = sqlite3.connect('local_test.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id, password_hash FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            logger.error(f"❌ User not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user[1].encode('utf-8')):
            logger.error(f"❌ Invalid password for: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        token = create_token(user[0])
        logger.info(f"✅ User logged in: {email}")
        
        return jsonify({
            'message': 'Login successful',
            'access_token': token,
            'user': {'id': user[0], 'email': email}
        })
        
    except Exception as e:
        logger.error(f"🚨 Login error: {e}")
        return jsonify({'error': f'Login failed: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    print("🚀 Local test backend starting on http://localhost:5001")
    print("📝 Update your frontend authService.ts baseUrl to: http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=True)
'''
        
        with open("local_test_backend.py", "w") as f:
            f.write(test_backend_code)
        
        print("✅ Created: local_test_backend.py")
        print("\n🚀 TO USE:")
        print("1. Run: python local_test_backend.py")
        print("2. Update your frontend authService.ts baseUrl to: http://localhost:5001")
        print("3. Test your authentication!")
        print("4. Once working, apply same fixes to Railway")
