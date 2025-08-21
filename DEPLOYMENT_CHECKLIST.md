
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
