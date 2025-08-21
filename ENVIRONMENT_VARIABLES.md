# Environment Variables Configuration

## 🔐 Railway Backend Variables

### Required Variables:
```bash
DATABASE_URL=postgresql://username:password@host:port/database
# ↑ Auto-generated when you add PostgreSQL service

JWT_SECRET_KEY=your_secure_secret_key_minimum_32_characters_long
FLASK_ENV=production
PORT=5000
# ↑ Port is auto-configured by Railway
```

### Optional Variables (for full features):
```bash
# Email functionality
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_gmail_app_password

# OCR functionality (if using image analysis)
TESSERACT_PATH=/usr/bin/tesseract
TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata
```

## 🌐 Vercel Frontend Variables

### Required Variables:
```bash
# Backend API URL (replace with your actual Railway URL)
REACT_APP_API_URL=https://your-railway-app.up.railway.app

# Production build optimization
NODE_ENV=production
```

### Optional Variables:
```bash
# Analytics (if using)
REACT_APP_GA_TRACKING_ID=G-XXXXXXXXXX

# Feature flags
REACT_APP_ENABLE_OCR=true
REACT_APP_ENABLE_HISTORY=true
```

## 📝 How to Set Variables:

### Railway:
1. Go to Railway Dashboard
2. Select your project
3. Click on backend service
4. Go to "Variables" tab
5. Add each variable with "New Variable" button

### Vercel:
1. Go to Vercel Dashboard
2. Select your project
3. Go to "Settings" → "Environment Variables"
4. Add each variable
5. Set Environment: "Production" (and "Preview" if needed)

## 🔍 Finding Your Railway Backend URL:
1. Railway Dashboard → Your Project → Backend Service
2. Settings tab → "Domains" section
3. Copy the "Public Domain" URL
4. Use this as your `REACT_APP_API_URL` in Vercel
