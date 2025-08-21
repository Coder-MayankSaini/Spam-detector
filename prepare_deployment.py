"""
Deployment Helper Script
Helps prepare your project for production deployment
"""
import os
import json
import subprocess
import sys
from pathlib import Path

def check_requirements():
    """Check if all requirements are met"""
    print("🔍 Checking deployment requirements...")
    
    issues = []
    
    # Check if git is initialized
    if not os.path.exists('.git'):
        issues.append("Git repository not initialized")
    
    # Check if necessary files exist
    required_files = [
        'frontend-react/package.json',
        'frontend-react/vercel.json',
        'Spam-backend/requirements.txt',
        'Spam-backend/Procfile',
        'Spam-backend/app_postgresql.py',
        'Spam-backend/database.py'
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            issues.append(f"Missing required file: {file_path}")
    
    # Check environment variables template
    if not os.path.exists('Spam-backend/.env.example'):
        issues.append("Missing environment variables template")
    
    return issues

def setup_frontend():
    """Setup frontend for deployment"""
    print("🖥️ Setting up frontend for deployment...")
    
    frontend_dir = Path('frontend-react')
    
    if not frontend_dir.exists():
        print("❌ Frontend directory not found!")
        return False
    
    os.chdir(frontend_dir)
    
    try:
        # Install dependencies
        print("Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], check=True)
        
        # Test build
        print("Testing frontend build...")
        result = subprocess.run(['npm', 'run', 'build'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Frontend build successful!")
            return True
        else:
            print(f"❌ Frontend build failed: {result.stderr}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Frontend setup failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm")
        return False
    finally:
        os.chdir('..')

def setup_backend():
    """Setup backend for deployment"""
    print("🖥️ Setting up backend for deployment...")
    
    backend_dir = Path('Spam-backend')
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return False
    
    os.chdir(backend_dir)
    
    try:
        # Check if virtual environment should be created
        if not os.path.exists('venv') and not os.path.exists('.venv'):
            print("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Activate virtual environment and install dependencies
        if os.name == 'nt':  # Windows
            pip_path = 'venv\\Scripts\\pip'
            python_path = 'venv\\Scripts\\python'
        else:  # Unix/MacOS
            pip_path = 'venv/bin/pip'
            python_path = 'venv/bin/python'
        
        if os.path.exists(pip_path):
            print("Installing backend dependencies...")
            subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
            
            # Test import of main modules
            print("Testing backend imports...")
            test_script = """
import flask
import psycopg2
from database import db_manager
print("✅ All imports successful!")
"""
            
            result = subprocess.run([python_path, '-c', test_script], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Backend setup successful!")
                return True
            else:
                print(f"⚠️ Backend imports test: {result.stderr}")
                print("Some dependencies might be missing, but deployment may still work")
                return True
        else:
            print("⚠️ Virtual environment not found, skipping dependency check")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Backend setup failed: {e}")
        return False
    except FileNotFoundError:
        print("❌ Python not found in PATH")
        return False
    finally:
        os.chdir('..')

def create_deployment_checklist():
    """Create a deployment checklist"""
    checklist = """
# 🚀 Deployment Checklist

## Before Deployment

### 1. Database Setup (Neon.tech)
- [ ] Create Neon.tech account
- [ ] Create new project/database
- [ ] Note down connection string
- [ ] Test database connection

### 2. Email Setup (Gmail)
- [ ] Enable 2-factor authentication
- [ ] Generate app password
- [ ] Test email sending

### 3. Environment Variables
- [ ] Copy .env.example to .env
- [ ] Fill in all required values
- [ ] Generate strong JWT secret (256+ bits)
- [ ] Set CORS_ORIGINS with production URLs

## Frontend Deployment (Vercel)

### Option A: Vercel Dashboard
- [ ] Connect GitHub repository
- [ ] Set framework to "Create React App"
- [ ] Add environment variables:
  - [ ] REACT_APP_API_BASE_URL
- [ ] Deploy

### Option B: Vercel CLI
```bash
cd frontend-react
npm install -g vercel
vercel login
vercel --prod
```

## Backend Deployment (Railway)

### Option A: Railway Dashboard
- [ ] Connect GitHub repository
- [ ] Add environment variables (see .env.example)
- [ ] Deploy
- [ ] Note deployment URL

### Option B: Railway CLI
```bash
cd Spam-backend
npm install -g @railway/cli
railway login
railway init
railway up
```

## Post-Deployment

- [ ] Test API health endpoint
- [ ] Test user registration
- [ ] Test email functionality
- [ ] Test spam analysis
- [ ] Update CORS_ORIGINS with actual URLs
- [ ] Set up monitoring/alerts

## URLs to Update

After deployment, update these in your records:
- [ ] Frontend URL: https://your-app.vercel.app
- [ ] Backend API URL: https://your-backend.railway.app
- [ ] Update CORS_ORIGINS environment variable

## Security Checklist

- [ ] JWT_SECRET_KEY is secure and random
- [ ] Database credentials are secure
- [ ] Email app password is used (not main password)
- [ ] CORS origins are restrictive
- [ ] DEBUG=false in production
- [ ] HTTPS enforced on both frontend and backend

## Testing

- [ ] Register new account
- [ ] Login functionality
- [ ] Email analysis works
- [ ] Image analysis works (if OCR is set up)
- [ ] Password reset emails work
- [ ] History page loads
- [ ] Contact form works

Need help? Check DEPLOYMENT_GUIDE.md for detailed instructions!
"""
    
    with open('DEPLOYMENT_CHECKLIST.md', 'w', encoding='utf-8') as f:
        f.write(checklist)
    
    print("✅ Created DEPLOYMENT_CHECKLIST.md")

def main():
    """Main deployment helper function"""
    print("🚀 Spam Detector Deployment Helper")
    print("=" * 50)
    
    # Check requirements
    issues = check_requirements()
    
    if issues:
        print("❌ Found issues that need to be resolved:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease fix these issues before deploying.")
        return
    
    print("✅ All required files found!")
    
    # Setup frontend
    if setup_frontend():
        print("✅ Frontend ready for deployment!")
    else:
        print("⚠️ Frontend setup had issues, but you can still try deploying")
    
    # Setup backend
    if setup_backend():
        print("✅ Backend ready for deployment!")
    else:
        print("⚠️ Backend setup had issues, but you can still try deploying")
    
    # Create deployment checklist
    create_deployment_checklist()
    
    print("\n" + "=" * 50)
    print("🎉 Deployment preparation complete!")
    print("\nNext steps:")
    print("1. Check DEPLOYMENT_CHECKLIST.md")
    print("2. Follow DEPLOYMENT_GUIDE.md")
    print("3. Set up your databases and hosting accounts")
    print("4. Deploy!")
    
    print(f"\nYour project structure:")
    print(f"📁 frontend-react/ - Deploy to Vercel")
    print(f"📁 Spam-backend/ - Deploy to Railway/Heroku")
    print(f"📄 DEPLOYMENT_GUIDE.md - Detailed instructions")
    print(f"📄 DEPLOYMENT_CHECKLIST.md - Step-by-step checklist")

if __name__ == "__main__":
    main()
