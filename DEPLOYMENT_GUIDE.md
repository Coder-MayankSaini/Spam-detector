# 🚀 Production Deployment Guide

This guide offers **two deployment approaches** for your Spam Detector project:

## 🎯 Choose Your Deployment Strategy

### Option A: Simplified (Recommended) 🥇
**Frontend (Vercel) + Backend + Database (Railway)**
- ✅ Only 2 platforms to manage
- ✅ Railway provides both backend hosting AND PostgreSQL
- ✅ Simpler environment variables
- ✅ Lower cost and easier management

### Option B: Separate Services
**Frontend (Vercel) + Backend (Railway) + Database (Neon.tech)**
- More complex but gives you specialized database features
- Use if you specifically need Neon.tech's advanced features

---

## 🚀 Option A: Simplified Deployment (Recommended)

### Prerequisites
- Git repository (GitHub, GitLab, etc.)
- Accounts on:
  - [Vercel](https://vercel.com) (Frontend)
  - [Railway](https://railway.app) (Backend + Database)

### � Step 1: Backend + Database Setup (Railway)

Railway provides both application hosting AND managed PostgreSQL in one platform.

#### 1.1: Create Railway Account
1. Go to [Railway](https://railway.app)
2. Sign up with GitHub account
3. Verify your account

#### 1.2: Deploy Backend
1. **Create New Project**:
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your Spam Detector repository
   - Choose the `Spam-backend` folder (or Railway will auto-detect)

2. **Railway Auto-Detection**:
   - Railway will automatically detect it's a Python Flask app
   - It will use the `requirements.txt` and `Procfile` we created

#### 1.3: Add PostgreSQL Database
1. **In your Railway project dashboard**:
   - Click "New Service" → "Database" → "Add PostgreSQL" 
   - Railway will create a managed PostgreSQL instance
   - DATABASE_URL will be automatically provided to your backend

#### 1.4: Configure Environment Variables
In Railway dashboard, add these environment variables:

```env
JWT_SECRET_KEY=your-super-secret-jwt-key-256-bits-long
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_FROM=your-email@gmail.com
CORS_ORIGINS=https://your-app.vercel.app
DEBUG=false
```

**Note**: `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.

#### 1.5: Deploy
- Railway automatically deploys when you push to GitHub
- Your backend will be available at: `https://your-app.railway.app`

### 🌐 Step 2: Frontend Deployment (Vercel)

#### 2.1: Prepare Frontend
1. **Navigate to frontend directory**:
   ```bash
   cd frontend-react
   ```

2. **Create production environment file** (`.env.production`):
   ```env
   REACT_APP_API_BASE_URL=https://your-app.railway.app
   ```
   Replace `your-app` with your actual Railway deployment URL.

#### 2.2: Deploy to Vercel

**Option A: Vercel Dashboard (Recommended)**
1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click "Add New..." → "Project"
3. Import your Git repository
4. **Configure Project**:
   - Framework Preset: "Create React App"
   - Root Directory: `frontend-react`
5. **Environment Variables**:
   - `REACT_APP_API_BASE_URL`: `https://your-app.railway.app`
6. Click "Deploy"

**Option B: Vercel CLI**
```bash
npm install -g vercel
vercel login
cd frontend-react
vercel --prod
```

#### 2.3: Update CORS
After deployment, update your Railway backend's `CORS_ORIGINS` environment variable:
```env
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
```

---

## 🎉 Your App is Live!

- **Frontend**: `https://your-app.vercel.app`
- **Backend API**: `https://your-app.railway.app`
- **Database**: Managed by Railway (PostgreSQL)

---

## Option B: Separate Services (Advanced)

If you prefer using separate specialized services:

## 🔧 Configuration Details

### Backend Environment Variables

```env
# Database (Neon.tech)
DATABASE_URL=postgresql://username:password@ep-name.region.aws.neon.tech/dbname?sslmode=require

# Security
JWT_SECRET_KEY=your-256-bit-secret-key-here

# Email (Gmail App Password recommended)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-16-character-app-password
EMAIL_FROM=your-email@gmail.com

# CORS (Update with your Vercel URL)
CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

# Production settings
DEBUG=false
PORT=5000
HOST=0.0.0.0
TESSERACT_PATH=/usr/bin/tesseract
```

### Frontend Environment Variables

```env
# API Base URL (your deployed backend)
REACT_APP_API_BASE_URL=https://your-backend-url.railway.app
REACT_APP_NODE_ENV=production
```

## 📧 Email Setup (Gmail)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this 16-character password as `EMAIL_PASSWORD`

## 🔍 Testing Your Deployment

### 1. Test Backend API

```bash
curl https://your-backend-url.railway.app/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-01-XX...",
  "version": "1.0.0"
}
```

### 2. Test Frontend

1. Visit your Vercel URL
2. Try registering a new account
3. Test email analysis functionality
4. Check browser console for errors

### 3. Test Email Functionality

1. Use "Forgot Password" feature
2. Check if you receive the reset email
3. Verify the reset link works

## 🐛 Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure `CORS_ORIGINS` includes your Vercel URL
   - Check if both HTTP and HTTPS are needed

2. **Database Connection**:
   - Verify Neon.tech connection string is correct
   - Check if database is active (Neon has auto-pause)

3. **Email Not Sending**:
   - Verify Gmail app password is correct
   - Check if less secure apps is disabled (use app password instead)

4. **Build Failures**:
   - Check Node.js version compatibility
   - Verify all environment variables are set

### Debugging Commands

```bash
# Check Railway logs
railway logs

# Check Vercel logs
vercel logs your-app-name

# Test local build
npm run build
python app_postgresql.py
```

## 📊 Monitoring

### Set Up Monitoring

1. **Railway**: Built-in metrics dashboard
2. **Vercel**: Built-in analytics and performance monitoring
3. **Neon**: Database usage dashboard

### Health Checks

Both platforms provide:
- Uptime monitoring
- Error tracking
- Performance metrics

## 🔒 Security Checklist

- [ ] JWT secret is 256+ bits and random
- [ ] Database credentials are secure
- [ ] CORS origins are restrictive
- [ ] Email credentials use app passwords
- [ ] Debug mode is disabled in production
- [ ] HTTPS is enforced

## 🚀 Scaling Considerations

### When to Scale

- **Database**: Neon auto-scales, monitor connection limits
- **Backend**: Railway provides automatic scaling
- **Frontend**: Vercel's edge network handles traffic

### Performance Optimization

1. **Database**: Add indexes for frequent queries
2. **Backend**: Implement caching for model predictions
3. **Frontend**: Use code splitting and lazy loading

---

## 🎉 Deployment Checklist

- [ ] Neon.tech database created and configured
- [ ] Backend deployed on Railway/Heroku
- [ ] Environment variables configured
- [ ] Frontend deployed on Vercel
- [ ] CORS configured correctly
- [ ] Email functionality tested
- [ ] SSL certificates active
- [ ] Custom domain configured (optional)

Your Spam Detector is now live! 🎊

**Frontend URL**: https://your-app.vercel.app
**Backend API**: https://your-backend-url.railway.app
**Database**: Neon.tech PostgreSQL

Need help? Check the troubleshooting section or create an issue in your repository.
