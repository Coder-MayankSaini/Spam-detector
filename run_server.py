#!/usr/bin/env python3
"""
Fixed Windows Flask server
"""

import os
import sys
import socket
import subprocess
from waitress import serve

def main():
    print("🚀 Starting Spam Detector API Server")
    
    # Import Flask app
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app import app
        print("✅ Flask app loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load Flask app: {e}")
        return
    
    # Server configuration
    host = '0.0.0.0'  # Listen on all interfaces
    port = 5001
    
    print(f"📍 Starting server on {host}:{port}")
    print(f"🌐 Access at: http://localhost:{port}")
    print("🛑 Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        # Start Waitress server with fixed configuration
        serve(app, host=host, port=port, threads=6)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"❌ Port {port} is in use!")
            print("🔄 Trying port 5002...")
            try:
                serve(app, host=host, port=5002, threads=6)
            except Exception as e2:
                print(f"❌ Also failed on 5002: {e2}")
        else:
            print(f"❌ Network error: {e}")
    except Exception as e:
        print(f"❌ Server error: {e}")
        print("\n🔧 Try running: python app.py")

if __name__ == '__main__':
    main()
