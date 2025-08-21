# Vercel Deployment Guide

## Deploy React Frontend to Vercel

### Option 1: Vercel CLI (Recommended)
```bash
# Install Vercel CLI
npm i -g vercel

# Navigate to frontend directory
cd frontend-react

# Deploy to Vercel
vercel

# Follow prompts:
# - Set up and deploy? Yes
# - Which scope? (your account)
# - Link to existing project? No
# - Project name: spam-detector-frontend
# - Directory: ./
# - Override settings? Yes
# - Build command: npm run build
# - Output directory: build
# - Install command: npm install
```

### Option 2: Vercel Dashboard
1. Go to https://vercel.com/dashboard
2. Click "Add New..." → "Project"
3. Import from GitHub: your spam-detector repo
4. Configure:
   - **Root Directory:** `frontend-react`
   - **Framework Preset:** Create React App
   - **Build Command:** `npm run build`
   - **Output Directory:** `build`

### Required Environment Variables for Vercel:

Add these in Vercel Dashboard → Project → Settings → Environment Variables:

```bash
# Your Railway backend URL (replace with your actual Railway URL)
REACT_APP_API_URL=https://your-app-name.up.railway.app

# Optional: Google Analytics, etc.
REACT_APP_GA_TRACKING_ID=your_ga_id_here
```

### Finding Your Railway Backend URL:
1. Go to Railway dashboard
2. Click on your backend service
3. Go to "Settings" tab
4. Copy the "Public Domain" URL
5. Use this as your `REACT_APP_API_URL`
