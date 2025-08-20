#!/usr/bin/env python3
"""
Windows-optimized Flask server using Waitress WSGI server
Fixes common Windows networking issues with Flask development server
"""
import os
import sys
import socket
import subprocess
from waitress import serve
from app import app, config, log_structured

def check_port_available(host, port):
    """Check if a port is available for binding"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            return result != 0
    except Exception:
        return False

def find_available_port(host, start_port, end_port=None):
    """Find an available port starting from start_port"""
    if end_port is None:
        end_port = start_port + 100
    
    for port in range(start_port, end_port + 1):
        if check_port_available(host, port):
            return port
    return None

def add_firewall_exception(port):
    """Add Windows Firewall exception for the Flask app"""
    try:
        rule_name = f"Python Flask App Port {port}"
        
        # Check if rule already exists
        check_cmd = f'netsh advfirewall firewall show rule name="{rule_name}"'
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        
        if "No rules match" in result.stdout:
            # Add inbound rule
            add_cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport={port}'
            subprocess.run(add_cmd, shell=True, check=True)
            print(f"✅ Added Windows Firewall exception for port {port}")
            return True
        else:
            print(f"ℹ️  Firewall rule already exists for port {port}")
            return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Could not add firewall exception: {e}")
        print("💡 Try running as Administrator or manually add firewall exception")
        return False
    except Exception as e:
        print(f"⚠️  Firewall exception error: {e}")
        return False

def kill_processes_on_port(port):
    """Kill any processes using the specified port"""
    try:
        # Find processes using the port
        find_cmd = f'netstat -ano | findstr :{port}'
        result = subprocess.run(find_cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            pids = set()
            
            for line in lines:
                parts = line.strip().split()
                if len(parts) >= 5 and f':{port}' in parts[1]:
                    pid = parts[-1]
                    if pid.isdigit():
                        pids.add(pid)
            
            for pid in pids:
                try:
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True, capture_output=True)
                    print(f"✅ Killed process {pid} using port {port}")
                except:
                    pass
        
        return True
    except Exception as e:
        print(f"⚠️  Could not kill processes on port {port}: {e}")
        return False

def diagnose_network():
    """Run network diagnostics"""
    print("🔍 Running network diagnostics...")
    
    try:
        # Check if localhost resolves correctly
        import socket
        localhost_ip = socket.gethostbyname('localhost')
        print(f"✅ localhost resolves to: {localhost_ip}")
        
        # Check available network interfaces
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"ℹ️  Machine hostname: {hostname}")
        print(f"ℹ️  Machine IP: {local_ip}")
        
        return True
    except Exception as e:
        print(f"❌ Network diagnostic error: {e}")
        return False

def start_server_with_waitress(host='127.0.0.1', port=5001):
    """Start Flask app using Waitress WSGI server"""
    print("🚀 Starting Spam Detector API Server with Waitress...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print("🔧 WSGI Server: Waitress (Windows optimized)")
    print("-" * 50)
    
    # Run diagnostics
    diagnose_network()
    
    # Check if port is available
    if not check_port_available(host, port):
        print(f"⚠️  Port {port} is in use, attempting to free it...")
        kill_processes_on_port(port)
        
        # Try to find alternative port if still not available
        if not check_port_available(host, port):
            alternative_port = find_available_port(host, port + 1)
            if alternative_port:
                print(f"🔄 Using alternative port: {alternative_port}")
                port = alternative_port
            else:
                print(f"❌ Could not find available port. Please check port {port}")
                return False
    
    # Add firewall exception
    add_firewall_exception(port)
    
    # Log server startup
    log_structured('INFO', 'waitress_server_starting', 
                 host=host, 
                 port=port, 
                 server='waitress')
    
    try:
        # Start Waitress server
        print(f"✅ Server starting on http://{host}:{port}")
        print(f"🌐 Local access: http://localhost:{port}")
        print("📡 Server is ready to accept requests!")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        serve(app, host=host, port=port, threads=6, connection_limit=1000)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        log_structured('INFO', 'waitress_server_stopped', reason='user_interrupt')
    except OSError as e:
        if "address already in use" in str(e).lower():
            print(f"\n❌ Port {port} is still in use!")
            print("🔄 Attempting recovery...")
            kill_processes_on_port(port)
            
            # Try alternative ports
            for alt_port in range(port + 1, port + 6):
                if check_port_available(host, alt_port):
                    print(f"🔄 Retrying on port {alt_port}...")
                    try:
                        serve(app, host=host, port=alt_port, threads=6, connection_limit=1000)
                        return True
                    except:
                        continue
            
            print("❌ Could not start server on any available port")
            print("\n🔧 Troubleshooting suggestions:")
            print("1. Run PowerShell as Administrator")
            print("2. Configure network: .\\configure_network.ps1")
            print("3. Run diagnostics: python diagnose_network.py")
            print("4. Restart computer to clear all port locks")
            return False
        else:
            print(f"\n❌ Network error: {e}")
            print("\n🔧 Troubleshooting suggestions:")
            print("1. Run as Administrator")
            print("2. Configure firewall: .\\configure_network.ps1")
            print("3. Check network settings: python diagnose_network.py")
            print("4. Try different host: python start_server.py --host 0.0.0.0")
            log_structured('ERROR', 'waitress_server_network_error', error=str(e))
            return False
    except Exception as e:
        print(f"❌ Unexpected server error: {e}")
        print("\n🔧 Troubleshooting suggestions:")
        print("1. Check Python installation: python --version")
        print("2. Reinstall dependencies: pip install -r requirements.txt")
        print("3. Run diagnostics: python diagnose_network.py")
        print("4. Try safe mode: python app.py")
        log_structured('ERROR', 'waitress_server_error', error=str(e))
        return False
    
    return True

if __name__ == '__main__':
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Start Spam Detector API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=config.PORT, help=f'Port to bind to (default: {config.PORT})')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    args = parser.parse_args()
    
    # Override config if debug is requested
    if args.debug:
        print("🐛 Debug mode enabled")
    
    # Start server
    success = start_server_with_waitress(args.host, args.port)
    if not success:
        sys.exit(1)
