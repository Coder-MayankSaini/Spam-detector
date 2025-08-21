# 🚂 Railway + Vercel Deployment Checklist

## ✅ Pre-Deployment Setup

### 1. Accounts Setup
- [ ] Create Railway account at [railway.app](https://railway.app)
- [ ] Create Vercel account at [vercel.com](https://vercel.com)
- [ ] Connect both accounts to your GitHub

### 2. Email Setup (Gmail)
- [ ] Enable 2-factor authentication on Gmail
- [ ] Generate app password for email
- [ ] Test email sending locally

### 3. Repository Setup
- [ ] Push all code to GitHub repository
- [ ] Ensure main branch has latest changes

## 🚂 Backend + Database (Railway)

### Step 1: Create Railway Project
- [ ] Go to [railway.app](https://railway.app)
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select your Spam Detector repository
- [ ] Railway auto-detects Python Flask app

### Step 2: Add PostgreSQL Database
- [ ] In Railway project dashboard
- [ ] Click "New Service" → "Database" → "Add PostgreSQL"
- [ ] Railway automatically connects database to your app

### Step 3: Configure Environment Variables
Copy from RAILWAY_ENV_VARS.txt to Railway dashboard:
- [ ] JWT_SECRET_KEY
- [ ] EMAIL_HOST
- [ ] EMAIL_PORT  
- [ ] EMAIL_USER
- [ ] EMAIL_PASSWORD
- [ ] EMAIL_FROM
- [ ] CORS_ORIGINS (update with your Vercel URL)
- [ ] DEBUG=false

### Step 4: Deploy Backend
- [ ] Railway automatically deploys on git push
- [ ] Note your Railway app URL: https://your-app.railway.app
- [ ] Test health endpoint: https://your-app.railway.app/health

## 🌐 Frontend (Vercel)

### Step 1: Deploy Frontend
- [ ] Go to [vercel.com](https://vercel.com)
- [ ] Click "New Project" → Import from GitHub
- [ ] Select your repository
- [ ] Set root directory to `frontend-react`
- [ ] Framework preset: "Create React App"

### Step 2: Environment Variables
- [ ] Add REACT_APP_API_BASE_URL = https://your-app.railway.app

### Step 3: Deploy
- [ ] Click Deploy
- [ ] Note your Vercel URL: https://your-app.vercel.app

## 🔧 Final Configuration

### Update CORS Origins
- [ ] Go back to Railway dashboard
- [ ] Update CORS_ORIGINS with your actual Vercel URL
- [ ] CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000

## 🧪 Testing

### Backend Tests
- [ ] https://your-app.railway.app/health → Should return {"status": "healthy"}
- [ ] Test user registration via frontend
- [ ] Test email functionality

### Frontend Tests  
- [ ] https://your-app.vercel.app → Should load homepage
- [ ] Register new account
- [ ] Login functionality
- [ ] Spam analysis works
- [ ] History page loads
- [ ] Password reset emails work

## 🎉 Success!

Your app is now live:
- **Frontend**: https://your-app.vercel.app
- **Backend**: https://your-app.railway.app  
- **Database**: Managed by Railway (PostgreSQL)

## 💰 Cost Estimate

### Free Tier (Good for testing/demos)
- Railway: $0/month (with usage limits)
- Vercel: $0/month (hobby use)
- **Total**: $0/month

### Production Tier
- Railway: ~$5-20/month (backend + database)
- Vercel: $0/month (still free for most apps)
- **Total**: ~$5-20/month

## 🆘 Troubleshooting

### Common Issues
1. **Build fails on Railway**:
   - Check requirements.txt has all dependencies
   - Verify Python version in runtime.txt

2. **Database connection errors**:
   - Railway automatically provides DATABASE_URL
   - Don't manually set database connection

3. **CORS errors**:
   - Ensure CORS_ORIGINS includes your Vercel URL
   - Update after frontend deployment

4. **Email not working**:
   - Verify Gmail app password
   - Check email environment variables

### Get Help
- Railway docs: [docs.railway.app](https://docs.railway.app)
- Vercel docs: [vercel.com/docs](https://vercel.com/docs)
- Check Railway project logs for errors