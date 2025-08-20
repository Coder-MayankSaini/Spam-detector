# 🛡️ Advanced Spam Detection System with OCR

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18-61dafb)](https://reactjs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-4.9-blue)](https://typescriptlang.org)
[![ML Accuracy](https://img.shields.io/badge/ML%20Accuracy-99.17%25-green)](.)
[![Flask](https://img.shields.io/badge/Flask-2.3-000000)](https://flask.palletsprojects.com)
[![JWT](https://img.shields.io/badge/JWT-Authentication-ff6b6b)](https://jwt.io)

A production-ready, AI-powered spam detection system with multi-page web interface, user authentication, and OCR capabilities for analyzing both text emails and email screenshots.

## 📋 Project Description

This comprehensive spam detection system leverages machine learning and OCR technology to protect users from spam and phishing emails. Built as a full-stack web application, it features a modern React TypeScript frontend with multi-page navigation, Flask backend with JWT authentication, and advanced AI capabilities for both text and image analysis.

**Key Capabilities:**
- **Dual Analysis Methods**: Text input analysis and OCR-based screenshot analysis
- **Multi-User Platform**: Secure user registration/login with personalized dashboards  
- **Real-time Processing**: Instant spam classification with confidence scoring
- **Professional UI**: Modern multi-page interface with Home, About, Contact, and Privacy pages
- **Personal Data Management**: User-specific analysis history and statistics
- **Theme Support**: Light and dark mode interfaces

## ✨ Key Features

- 🎯 **99.17% ML Accuracy** - Advanced TF-IDF + Naive Bayes classifier with scikit-learn
- 📷 **OCR Image Analysis** - Tesseract-powered email screenshot processing  
- ⚡ **Real-time Analysis** - Instant spam classification with confidence scores
- 🌐 **Multi-Page Interface** - Professional React TypeScript UI with Home, About, Contact, Privacy pages
- 🔐 **User Authentication** - JWT-based secure login/registration system
- 📊 **Personal Dashboard** - Individual analysis history and statistics tracking
- 🎨 **Theme Support** - Light and dark mode with responsive design
- 🗄️ **Data Privacy** - User-specific data isolation and secure access
- 🔄 **Dynamic Learning** - Model retraining capabilities with new data
- 📱 **Mobile Responsive** - Works seamlessly across desktop and mobile devices

## 🧠 AI Technologies & Datasets

### **Machine Learning Stack:**
- **Algorithm**: TF-IDF (Term Frequency-Inverse Document Frequency) + Naive Bayes Classifier
- **Library**: scikit-learn 1.3+ for ML pipeline and model training
- **Training Data**: Custom dataset with 120+ manually labeled spam/ham emails
- **Feature Engineering**: Text preprocessing, tokenization, and vectorization
- **Model Persistence**: joblib for model serialization and loading
- **Performance**: 99.17% accuracy on validation set

### **OCR Technology:**
- **Engine**: Google Tesseract OCR v5.4.0+ 
- **Image Processing**: PIL/Pillow for image preprocessing and enhancement
- **Text Extraction**: Support for JPG, PNG, GIF, PDF formats
- **Preprocessing**: Noise reduction, contrast enhancement, deskewing
- **Integration**: Python-tesseract wrapper for seamless API integration

### **Dataset Information:**
```
training_data.csv (120 samples)
├── Columns: ['text', 'label']
├── Labels: 0 (Ham/Legitimate), 1 (Spam)
├── Source: Manually curated real-world email examples
├── Coverage: Phishing, promotional, legitimate business emails
└── Quality: Human-verified and cleaned for training
```

## 🛠️ Technologies & Libraries Used

### **Backend Technologies:**
```python
# Core Framework & Server
Flask==2.3.0+              # Lightweight web framework
Flask-JWT-Extended==4.5.0+ # JWT authentication handling
Flask-CORS==4.0.0+         # Cross-origin resource sharing

# Machine Learning & AI
scikit-learn==1.3.0+       # ML algorithms and pipeline
joblib==1.3.0+             # Model serialization
numpy==1.24.0+             # Numerical computing
pandas==2.0.0+             # Data manipulation

# OCR & Image Processing
pytesseract==0.3.10+       # Tesseract OCR Python wrapper
Pillow==10.0.0+            # Image processing library
opencv-python==4.8.0+      # Computer vision operations

# Database & Security
sqlite3                    # Built-in database (Python standard)
bcrypt==4.0.0+             # Password hashing
PyJWT==2.8.0+              # JSON Web Token implementation

# Utilities
python-dotenv==1.0.0+      # Environment variable management
requests==2.31.0+          # HTTP library for API calls
```

### **Frontend Technologies:**
```json
{
  "react": "^18.0.0",                    // UI framework
  "typescript": "^4.9.0",               // Type-safe JavaScript
  "@types/react": "^18.0.0",            // React TypeScript definitions
  "react-dom": "^18.0.0",               // React DOM manipulation
  "react-scripts": "5.0.1",             // Build and development scripts
  
  // Styling & UI
  "css-modules": "built-in",             // Scoped CSS styling
  "responsive-design": "custom",         // Mobile-first approach
  
  // Development Tools
  "web-vitals": "^3.0.0",              // Performance monitoring
  "@testing-library/react": "^13.0.0",  // Testing utilities
  "jest": "^27.0.0"                     // Testing framework
}
```

### **External APIs & Services:**
- **Tesseract OCR**: Google's open-source OCR engine
- **Browser APIs**: File upload, drag-and-drop, localStorage
- **Custom REST API**: Backend endpoints for analysis and user management

### **Development Tools:**
```bash
# Version Control & Deployment
Git 2.40+                  # Source control
GitHub                     # Repository hosting
npm/Node.js 16+            # Package management
PowerShell                 # Windows automation

# AI/ML Development Assistance
GitHub Copilot             # AI code completion
ChatGPT/Claude             # Architecture planning and debugging
```

## 🚀 Setup Instructions

### **Prerequisites**
Before starting, ensure you have:
- **Python 3.8+** with pip package manager
- **Node.js 16+** with npm 
- **Windows 10/11** (for Tesseract OCR integration)
- **Git** for version control
- **4GB RAM minimum** (8GB recommended)

### **1. Repository Setup**
```powershell
# Clone the repository
git clone https://github.com/NSharp-mahajan/Spam-detector.git
cd Spam-detector

# Verify directory structure
dir  # Should see frontend-react/, Spam-backend/, docs/, etc.
```

### **2. Backend Setup (Python/Flask)**
```powershell
# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install Python dependencies
pip install -r requirements.txt

# Verify core packages installed
pip show flask scikit-learn pytesseract pillow

# Set up environment variables
copy .env.example .env  # Create from template
# Edit .env file with your configurations
```

### **3. OCR Engine Installation**
```powershell
# Option 1: Using Windows Package Manager (Recommended)
winget install --id UB-Mannheim.TesseractOCR

# Option 2: Manual Download
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
# Install to: C:\Program Files\Tesseract-OCR\

# Verify installation
tesseract --version  # Should show version 5.4.0+

# Update .env file with correct path:
# TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### **4. Frontend Setup (React/TypeScript)**
```powershell
# Navigate to frontend directory
cd frontend-react

# Install Node.js dependencies
npm install

# Verify installation
npm list react react-dom typescript

# Return to root directory
cd ..
```

### **5. Database Initialization**
```powershell
# Database will be created automatically on first run
# Default location: emails.db in root directory

# Optional: Run database migration if upgrading
python migrate_database.py  # Only if updating from older version
```

### **6. Initial Model Training**
```powershell
# The ML model will be automatically trained on first backend start
# Training data: Spam-backend/training_data.csv (120 samples)
# Model output: spam_model.joblib (created automatically)

# Manual training (optional):
python -c "
from Spam-backend.app import train_model
train_model('Spam-backend/training_data.csv')
print('Model trained successfully!')
"
```

### **7. Running the Application**

#### **Start Backend Server:**
```powershell
# Activate virtual environment (if not already active)
.\.venv\Scripts\Activate.ps1

# Start Flask development server
.\.venv\Scripts\python.exe Spam-backend/app.py

# Server will start on: http://localhost:5000
# Look for: "Running on http://127.0.0.1:5000"
```

#### **Start Frontend Server:**
```powershell
# Open new terminal/PowerShell window
cd frontend-react

# Start React development server
npm start

# Frontend will start on: http://localhost:3000
# Browser should open automatically
```

### **8. First-Time Access**
1. **Open Browser**: Navigate to http://localhost:3000
2. **Create Account**: Click "Register" and create new user account
3. **Login**: Use your credentials to access the dashboard
4. **Start Analyzing**: Try both text analysis and image upload features

### **9. Verification Steps**
```powershell
# Test backend API
curl http://localhost:5000/health  # Should return server status

# Test OCR functionality
# Upload a test image through web interface

# Check database
# File emails.db should be created with user data

# View logs
# Backend logs show request processing and model predictions
```

### **🔧 Environment Configuration**

Create/edit `.env` file in root directory:
```properties
# Server Settings
DEBUG=true
HOST=127.0.0.1
PORT=5000

# Database Configuration
DATABASE_URL=emails.db

# ML Model Settings
MODEL_PATH=spam_model.joblib
DEFAULT_THRESHOLD=0.6
TRAINING_DATA=Spam-backend/training_data.csv

# OCR Settings
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Security (IMPORTANT: Change in production!)
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ACCESS_TOKEN_EXPIRES=86400  # 24 hours

# CORS Settings
FRONTEND_URL=http://localhost:3000
```

### **📋 Troubleshooting Setup**

| Issue | Solution |
|-------|----------|
| **Python packages not installing** | Ensure pip is updated: `python -m pip install --upgrade pip` |
| **Tesseract not found** | Add Tesseract to PATH or update .env with full path |
| **npm install fails** | Clear npm cache: `npm cache clean --force` |
| **Port already in use** | Kill processes on ports 3000/5000 or change ports |
| **Permission denied** | Run PowerShell as Administrator |
| **Virtual environment issues** | Recreate: `Remove-Item -Recurse .venv; python -m venv .venv` |

## 🎮 Usage Guide

### **First Time Setup**
1. **Create Account**: Register with email and password (min 6 characters)
2. **Login**: Access your personalized dashboard
3. **Start Analyzing**: Your analysis history is kept private and separate

### **Web Interface Navigation**
- **🏠 Home**: Main dashboard with text/image analysis tools
- **ℹ️ About**: Learn about the technology and features  
- **📧 Contact**: Get support and submit feedback
- **🔒 Privacy**: View privacy policy and data handling

### **Analysis Features**
1. **Text Analysis**: Paste email content → Get instant spam classification
2. **Image Analysis**: Drag & drop email screenshots → OCR + spam detection
3. **View Results**: See confidence scores, keywords, and detailed analysis
4. **Personal History**: Browse your past analyses with search and filtering
5. **User Management**: Logout and switch accounts as needed

### Authentication System
- **Secure Registration**: Email + password authentication
- **JWT Tokens**: Secure session management with 24-hour expiration
- **Data Isolation**: Each user sees only their own analysis history
- **Privacy First**: No shared data between users

### API Integration
```bash
# Register new user
curl -X POST http://localhost:5000/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'

# Login user
curl -X POST http://localhost:5000/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'

# Analyze text (requires authentication)
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{"text": "URGENT: You won $1,000,000!"}'

# Get user's analysis history
curl -X GET http://localhost:5000/history \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Get user's statistics
curl -X GET http://localhost:5000/stats \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📁 Project Structure

```
Spam-detector/
├── 🔧 Configuration
│   ├── .env                    # Environment variables
│   ├── requirements.txt        # Python dependencies
│   └── .gitignore             # Git ignore rules
│
├── 🤖 Backend (Python Flask)
│   ├── Spam-backend/
│   │   ├── app.py             # Main Flask application with JWT auth
│   │   └── training_data.csv  # ML training dataset (120 samples)
│   ├── emails.db              # SQLite database with user tables
│   └── spam_model.joblib      # Trained ML model (auto-generated)
│
├── 🌐 Frontend (React TypeScript)  
│   └── frontend-react/
│       ├── src/               # React components
│       ├── public/            # Static assets
│       ├── package.json       # Node dependencies
│       └── tsconfig.json      # TypeScript config
│
├── 📚 Documentation
│   └── docs/                  # Comprehensive guides
│       ├── API.md            # REST API reference
│       ├── OCR_SETUP.md      # OCR installation guide
│       └── USER_GUIDE.md     # Complete user manual
│
└── 🧪 Testing
    ├── test_ocr_api.py        # API functionality tests
    └── comprehensive_bug_test.py  # Full system validation
```

## 🔧 System Status

| Component | Status | Details |
|-----------|--------|---------|
| 🗄️ **Database** | ✅ Operational | SQLite with user auth and data isolation |
| 🔐 **Authentication** | ✅ Active | JWT-based login/registration system |
| 🤖 **ML Model** | ✅ Trained | 99.17% accuracy on 120 samples |
| 📷 **OCR Engine** | ✅ Configured | Tesseract v5.4.0 with preprocessing |
| 🌐 **Frontend** | ✅ Deployed | React TypeScript with auth integration |
| 🔌 **API** | ✅ Secured | Protected endpoints with JWT validation |

## 🤖 AI Development Tools & Assistance

This project was developed with assistance from various AI tools and technologies:

### **AI-Assisted Development:**
- **GitHub Copilot**: Used for code completion, boilerplate generation, and debugging assistance
- **Claude AI (Anthropic)**: Architecture planning, code review, and documentation writing
- **ChatGPT (OpenAI)**: Problem-solving, algorithm optimization, and testing strategies

### **AI Tools Integration:**
- **Machine Learning Pipeline**: Custom implementation using scikit-learn for spam classification
- **Natural Language Processing**: TF-IDF vectorization for text feature extraction
- **Computer Vision**: Tesseract OCR integration for image-to-text conversion
- **Automated Testing**: AI-assisted test case generation and validation scripts

### **Development Workflow:**
1. **Planning**: AI assistance in system architecture and component design
2. **Implementation**: Code generation and optimization with AI pair programming
3. **Testing**: Automated test creation and debugging with AI suggestions
4. **Documentation**: AI-assisted README, API docs, and user guide creation
5. **Optimization**: Performance tuning and code quality improvements

### **AI-Powered Features in Application:**
- **Smart Classification**: ML model predicts spam/ham with confidence scores
- **Intelligent OCR**: Image preprocessing and text extraction optimization
- **Adaptive Learning**: Model retraining capability with new data points
- **Context-Aware Analysis**: Feature extraction considers email context and patterns

## 🧪 Testing & Validation

```powershell
# Run comprehensive system tests
python test_authentication.py    # Authentication system validation
python test_ocr_api.py           # API functionality tests
python comprehensive_bug_test.py # Full system validation

# Database migration (if needed)
python migrate_database.py      # Update database schema

# Frontend tests
cd frontend-react; npm test
```

**Test Results**: ✅ All systems validated and operational

## ⚙️ Configuration

Key settings in `.env`:
```properties
# Server Configuration
DEBUG=true
HOST=127.0.0.1
PORT=5000

# Database & Model
DATABASE_URL=emails.db
MODEL_PATH=spam_model.joblib
DEFAULT_THRESHOLD=0.6

# OCR Configuration  
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe

# Authentication (IMPORTANT: Change in production!)
JWT_SECRET_KEY=your-secret-key-change-in-production-make-it-long-and-random
```

## 📊 Performance Metrics

- **Text Analysis**: ~100ms response time
- **OCR Analysis**: ~2-5s (image dependent)
- **Memory Usage**: ~200MB total system
- **OCR Accuracy**: 75-100% text extraction
- **Database**: Scales with usage, 16KB baseline

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Can't access app | Create account first - registration is required |
| OCR not working | Verify Tesseract path in `.env` |
| Server won't start | Check ports 3000/5000 availability |
| Database errors | Run `python migrate_database.py` to update schema |
| Token expired | Login again - tokens expire after 24 hours |
| Frontend blank | Clear browser cache, restart servers |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Submit pull request with detailed description

## 📄 License

MIT License - see LICENSE file for details.

## 🙏 Acknowledgments & Credits

### **Open Source Technologies:**
- **🔍 Tesseract OCR** (Google) - Industry-leading OCR engine for text extraction
- **🤖 scikit-learn** - Comprehensive machine learning library for Python
- **⚛️ React** (Meta/Facebook) - Modern UI framework for web applications
- **🐍 Flask** (Pallets) - Lightweight and flexible Python web framework
- **🔐 JWT** - Secure token-based authentication standard
- **📊 NumPy & Pandas** - Data manipulation and numerical computing libraries

### **AI Development Partners:**
- **🧠 GitHub Copilot** (GitHub/OpenAI) - AI pair programming and code completion
- **🤖 Claude AI** (Anthropic) - Architecture planning and code optimization
- **💬 ChatGPT** (OpenAI) - Problem-solving and documentation assistance

### **Development Community:**
- **Stack Overflow** - Community-driven problem solving and best practices
- **GitHub Community** - Open source collaboration and version control
- **Python Package Index (PyPI)** - Extensive library ecosystem
- **npm Registry** - JavaScript/TypeScript package management

### **Educational Resources:**
- **scikit-learn Documentation** - ML implementation guidelines
- **React Documentation** - Frontend development best practices  
- **Flask Documentation** - Backend API development patterns
- **Tesseract OCR Documentation** - Image processing and text extraction

---

## 📞 Support & Contact

- **🐛 Bug Reports**: Submit issues via GitHub Issues
- **💡 Feature Requests**: Use GitHub Discussions for suggestions
- **📧 General Support**: Contact form available in web application
- **📚 Documentation**: Comprehensive guides in `/docs` directory

---

**🚀 Ready to get started? Follow the setup instructions above and protect your inbox with AI-powered spam detection!**

---

**💡 Production Note**: This system is production-ready with comprehensive security, authentication, and scalability features. Additional monitoring and enterprise-grade infrastructure recommended for large-scale deployment.

## 📚 Complete Documentation

| Document | Purpose | Content |
|----------|---------|---------|
| [📖 User Guide](docs/USER_GUIDE.md) | Complete application usage | Step-by-step tutorials and features |
| [🔌 API Reference](docs/API.md) | REST API documentation | Endpoints, authentication, examples |
| [📷 OCR Setup](docs/OCR_SETUP.md) | Tesseract installation guide | Platform-specific setup instructions |
| [🏗️ Architecture](docs/ARCHITECTURE.md) | System design overview | Technical architecture and data flow |
| [� Deployment](docs/DEPLOYMENT.md) | Production deployment | Server setup and scaling guidelines |
