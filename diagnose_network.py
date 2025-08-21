#!/usr/bin/env python3
"""
Network Diagnostics Tool for Spam Detector
Helps identify and resolve Windows networking issues
"""
import os
import sys
import socket
import subprocess
import requests
import time
import threading
from flask import Flask

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Python Version Check")
    print(f"   Version: {sys.version}")
    print(f"   Executable: {sys.executable}")
    
    if sys.version_info < (3, 8):
        print("⚠️  Warning: Python 3.8+ recommended")
    else:
        print("✅ Python version is compatible")
    print()

def check_port_status(host, port):
    """Check if a port is available and what's using it"""
    print(f"🔍 Port {port} Status Check")
    
    # Check if port is bound
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            if result == 0:
                print(f"❌ Port {port} is already in use")
                
                # Try to find what's using it
                try:
                    cmd = f'netstat -ano | findstr :{port}'
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.stdout:
                        print(f"   Processes using port {port}:")
                        for line in result.stdout.strip().split('\n'):
                            if f':{port}' in line:
                                print(f"   {line.strip()}")
                except:
                    pass
            else:
                print(f"✅ Port {port} is available")
    except Exception as e:
        print(f"❌ Error checking port {port}: {e}")
    
    print()

def check_firewall():
    """Check Windows Firewall status"""
    print("🔥 Windows Firewall Check")
    
    try:
        # Check firewall status
        cmd = 'netsh advfirewall show allprofiles state'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            if "State                                 ON" in result.stdout:
                print("⚠️  Windows Firewall is enabled")
                print("   This might block Flask server connections")
                
                # Check for existing rules
                rule_name = "Python Flask App Port"
                check_cmd = f'netsh advfirewall firewall show rule name="{rule_name}*"'
                rule_result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                
                if "No rules match" in rule_result.stdout:
                    print("❌ No Flask firewall rules found")
                    print("   Consider running start_server.py as Administrator")
                else:
                    print("✅ Found Flask firewall rules")
            else:
                print("ℹ️  Windows Firewall is disabled")
        else:
            print("❌ Could not check firewall status")
    except Exception as e:
        print(f"❌ Firewall check error: {e}")
    
    print()

def check_network_connectivity():
    """Check basic network connectivity"""
    print("🌐 Network Connectivity Check")
    
    # Check localhost resolution
    try:
        localhost_ip = socket.gethostbyname('localhost')
        print(f"✅ localhost resolves to: {localhost_ip}")
    except Exception as e:
        print(f"❌ localhost resolution failed: {e}")
    
    # Check 127.0.0.1 binding
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(('127.0.0.1', 0))  # Bind to any available port
            host, port = sock.getsockname()
            print(f"✅ Can bind to 127.0.0.1 (test port: {port})")
    except Exception as e:
        print(f"❌ Cannot bind to 127.0.0.1: {e}")
    
    print()

def test_flask_minimal():
    """Test a minimal Flask server"""
    print("🧪 Minimal Flask Server Test")
    
    # Create minimal Flask app
    test_app = Flask(__name__)
    
    @test_app.route('/test')
    def test_endpoint():
        return {'status': 'ok', 'message': 'Test successful'}
    
    # Find available port
    test_port = None
    for port in range(5010, 5020):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                if sock.connect_ex(('127.0.0.1', port)) != 0:
                    test_port = port
                    break
        except:
            continue
    
    if not test_port:
        print("❌ Could not find available port for testing")
        return False
    
    print(f"   Starting test server on port {test_port}...")
    
    # Start server in background thread
    server_error = None
    
    def run_server():
        nonlocal server_error
        try:
            test_app.run(host='127.0.0.1', port=test_port, debug=False, use_reloader=False, threaded=True)
        except Exception as e:
            server_error = e
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    # Test the server
    try:
        response = requests.get(f'http://127.0.0.1:{test_port}/test', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Flask test successful: {data['message']}")
            return True
        else:
            print(f"❌ Flask test failed: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Flask test failed: Connection refused")
        if server_error:
            print(f"   Server error: {server_error}")
        return False
    except Exception as e:
        print(f"❌ Flask test failed: {e}")
        return False
    finally:
        print()

def check_dependencies():
    """Check required Python packages"""
    print("📦 Dependency Check")
    
    required_packages = [
        'flask', 'flask_cors', 'flask_jwt_extended', 
        'bcrypt', 'requests', 'waitress', 'sqlite3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'sqlite3':
                import sqlite3
            else:
                __import__(package.replace('_', '-').replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - MISSING")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install " + ' '.join(missing_packages))
    else:
        print("\n✅ All required packages are installed")
    
    print()

def provide_solutions():
    """Provide troubleshooting solutions"""
    print("💡 Troubleshooting Solutions")
    print("-" * 40)
    
    solutions = [
        "1. Use the Windows-optimized server:",
        "   python start_server.py",
        "   or double-click start_server.bat",
        "",
        "2. Run as Administrator:",
        "   Right-click start_server.bat → 'Run as administrator'",
        "",
        "3. Add manual firewall exception:",
        "   Windows Security → Firewall → Allow an app",
        "   Add Python.exe and allow both private and public networks",
        "",
        "4. Try alternative ports:",
        "   python start_server.py --port 8000",
        "   python start_server.py --port 8080",
        "",
        "5. Check antivirus software:",
        "   Add Python installation folder to antivirus exceptions",
        "",
        "6. Disable Windows Firewall temporarily:",
        "   Windows Security → Firewall → Turn off (for testing only)",
        "",
        "7. Use different network interface:",
        "   python start_server.py --host 0.0.0.0 --port 5001",
    ]
    
    for solution in solutions:
        print(solution)
    
    print()

def main():
    """Run complete network diagnostics"""
    print("=" * 60)
    print("🔧 Spam Detector Network Diagnostics Tool")
    print("=" * 60)
    print()
    
    check_python_version()
    check_dependencies()
    check_network_connectivity()
    check_port_status('127.0.0.1', 5001)
    check_port_status('127.0.0.1', 5000)
    check_firewall()
    
    # Test Flask server
    flask_success = test_flask_minimal()
    
    print("=" * 60)
    print("📊 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    if flask_success:
        print("✅ Flask networking is working!")
        print("   The issue might be with the main application.")
        print("   Try using the Windows-optimized server: python start_server.py")
    else:
        print("❌ Flask networking issues detected")
        print("   This is likely a Windows networking/firewall issue")
    
    print()
    provide_solutions()

if __name__ == '__main__':
    main()
