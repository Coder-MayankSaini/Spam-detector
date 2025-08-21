#!/usr/bin/env python
"""
Railway start script - ensures Railway can properly start the application
"""
from app import app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting Spam Detector API on {host}:{port}")
    print(f"🗄️ Database URL configured: {'DATABASE_URL' in os.environ}")
    print(f"📧 Email configured: {'EMAIL_USER' in os.environ}")
    
    app.run(host=host, port=port, debug=False)
