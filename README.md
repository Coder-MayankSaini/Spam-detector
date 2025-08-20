# 🛡️ Spam Detector - Advanced Email Security Platform

> **Modern AI-powered spam detection with beautiful user experience**

A comprehensive email spam detection system featuring machine learning classification, OCR image analysis, JWT authentication, and professional HTML email templates.

![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Version](https://img.shields.io/badge/Version-2.0.0-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%20Optimized-lightblue)

## ✨ **Latest Updates**

### 🎨 **Enhanced Email Templates** (New!)
- **Beautiful HTML password reset emails** with gradient backgrounds
- **Professional branding** with shield logo and brand colors
- **Mobile-responsive design** that works on all devices
- **Security information** boxes with clear instructions
- **Both HTML and plain text** versions for maximum compatibility

## 🚀 **Key Features**

### 🤖 **AI-Powered Detection**
- Advanced **Naive Bayes** spam classification
- **TF-IDF vectorization** for feature extraction
- **Real-time analysis** with confidence scoring
- **Keyword importance** highlighting

### 🖼️ **OCR Image Analysis**
- **Tesseract OCR** for screenshot analysis
- **Image preprocessing** for better accuracy
- **Text extraction** from email screenshots
- **Automated spam detection** on images

### 🔐 **Security & Authentication**
- **JWT-based authentication** system
- **Bcrypt password hashing** for security
- **Beautiful HTML email templates** for password reset
- **Secure token generation** and validation
- **User data isolation** per account

### 🎨 **Modern Frontend**
- **React TypeScript** application
- **Multi-page navigation** with routing
- **Responsive design** for all devices
- **Dark/Light theme** support
- **Real-time analysis** results

### 🛠️ **Windows Optimization**
- **Waitress WSGI** server for production
- **PowerShell automation** scripts
- **Network diagnostics** tools
- **Firewall configuration** helpers

## 📧 **Enhanced Email Experience**

### 🎨 **New Password Reset Email Features:**
```html
✨ Gradient background design
🛡️ Professional shield logo
🔐 Prominent call-to-action button
ℹ️ Security information box
🔗 Fallback text link
📱 Mobile-responsive layout
🏢 Branded footer
```

The password reset emails now feature:
- **Subject line**: "🔐 Password Reset Request - Spam Detector"
- **Professional HTML template** with brand colors
- **Security tips** and expiration information
- **Accessible design** with proper contrast
- **Fallback plain text** version

## 🏃‍♂️ **Quick Start**

### **Backend Setup**
```bash
cd Spam-backend
python run_server.py
```

### **Frontend Setup**
```bash
cd frontend-react
npm install
npm start
```

### **Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/health

## 🔧 **Configuration**

### **Email Configuration**
The system now sends beautiful HTML emails for password reset:

```python
# In Spam-backend/.env
GMAIL_USER=your-email@gmail.com
GMAIL_PASS=your-app-password
```

### **Features Enabled**
- ✅ HTML email templates with gradients
- ✅ Professional branding
- ✅ Mobile-responsive design
- ✅ Security information boxes
- ✅ Fallback plain text versions

## 🧪 **Testing the Enhanced Emails**

### **Preview Email Template**
```bash
cd Spam-backend
python test_email_template.py
# Opens email_preview.html in browser
```

### **Test Password Reset**
```bash
cd Spam-backend
python test_enhanced_password_reset.py
```

## 📊 **API Endpoints**

### **Authentication**
- `POST /register` - Create new account
- `POST /login` - User login
- `POST /forgot-password` - **Enhanced HTML email**
- `POST /reset-password` - Reset with token

### **Analysis**
- `POST /analyze` - Text spam detection
- `POST /analyze-image` - OCR + spam detection
- `GET /history` - Analysis history
- `GET /stats` - User statistics

## 🎯 **Email Template Highlights**

The new password reset email includes:

1. **🎨 Visual Design**
   - Gradient background (#667eea to #764ba2)
   - Professional white card layout
   - Rounded corners and shadows

2. **🛡️ Branding Elements**
   - Shield emoji logo in circular badge
   - "Spam Detector" title
   - "Secure Email Protection" subtitle

3. **📱 User Experience**
   - Large, prominent reset button
   - Clear security information
   - Alternative text link
   - Mobile-responsive design

4. **🔒 Security Features**
   - 1-hour expiration notice
   - One-time use information
   - Contact support section

## 🌟 **Technical Improvements**

### **Email Implementation**
```python
# Now using MIMEMultipart('alternative') for both HTML and text
msg = MIMEMultipart('alternative')
msg.attach(MIMEText(text_body, 'plain'))
msg.attach(MIMEText(html_body, 'html'))
```

### **Enhanced Subject Line**
```python
subject = "🔐 Password Reset Request - Spam Detector"
```

### **Professional Footer**
- Copyright notice
- Service description
- Brand consistency

## 📋 **Project Structure**

```
Spam-detector/
├── 📁 Spam-backend/          # Flask API server
│   ├── app.py               # Main application (Enhanced emails!)
│   ├── run_server.py        # Windows-optimized server
│   ├── test_email_template.py  # Email preview generator
│   └── test_enhanced_password_reset.py  # Email testing
├── 📁 frontend-react/       # React TypeScript frontend
├── 📁 docs/                 # Documentation
└── 📄 README.md            # This file
```

## 🔍 **Development & Testing**

### **Email Development**
- Test templates with `test_email_template.py`
- Preview in browser before sending
- Test actual sending with `test_enhanced_password_reset.py`

### **Cross-Platform Support**
- Windows optimized with Waitress
- CORS enabled for frontend integration
- Environment variable configuration

## 🛡️ **Security Features**

- **JWT tokens** for session management
- **Bcrypt hashing** for passwords
- **Secure token generation** for resets
- **HTTPS ready** configuration
- **Input validation** and sanitization

## 💡 **Usage Tips**

1. **Email Preview**: Always run `test_email_template.py` to preview
2. **Mobile Testing**: Check emails on different screen sizes
3. **Fallback Support**: Plain text version included automatically
4. **Brand Consistency**: Uses project colors throughout

## 🎉 **What's New**

✅ **Beautiful HTML password reset emails**  
✅ **Professional gradient design**  
✅ **Mobile-responsive templates**  
✅ **Enhanced user experience**  
✅ **Security information boxes**  
✅ **Brand-consistent styling**  
✅ **Comprehensive testing tools**  

---

## 📞 **Support**

Need help? The enhanced email system now provides:
- Clear instructions in every email
- Professional support contact information
- Comprehensive error handling
- User-friendly messaging

**Built with ❤️ for secure email communication**

---
*© 2025 Spam Detector. Professional email security with beautiful design.*
