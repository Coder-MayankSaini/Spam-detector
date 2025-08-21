# ✅ Vercel + Railway Deployment Checklist

Print this out or keep it open while deploying!

## 🛠️ Pre-Deployment (5 min)

- [ ] Create Railway account at [railway.app](https://railway.app)
- [ ] Create Vercel account at [vercel.com](https://vercel.com)  
- [ ] Both connected to GitHub
- [ ] Gmail 2FA enabled + app password generated
- [ ] Code pushed to GitHub

## 🚂 Railway Setup (10 min)

### Create Project
- [ ] Railway → "New Project" → "Deploy from GitHub repo"
- [ ] Select Spam-detector repository
- [ ] Auto-detects Python project

### Add Database  
- [ ] "New Service" → "Database" → "Add PostgreSQL"
- [ ] DATABASE_URL automatically provided

### Environment Variables
- [ ] Click backend service → "Variables" tab
- [ ] Add JWT_SECRET_KEY (make it long and random)
- [ ] Add EMAIL_HOST=smtp.gmail.com
- [ ] Add EMAIL_PORT=587  
- [ ] Add EMAIL_USER=your-email@gmail.com
- [ ] Add EMAIL_PASSWORD=your-16-char-app-password
- [ ] Add EMAIL_FROM=your-email@gmail.com
- [ ] Add CORS_ORIGINS=http://localhost:3000
- [ ] Add DEBUG=false

### Deploy & Test
- [ ] Wait for "Deployed" status
- [ ] Copy Railway URL (e.g., https://your-app.railway.app)
- [ ] Test: https://your-app.railway.app/health
- [ ] Should show: {"status":"healthy"}

## 🌐 Vercel Setup (5 min)

### Deploy Frontend
- [ ] Vercel → "New Project" → Import Spam-detector repo
- [ ] Framework: "Create React App"
- [ ] Root Directory: Select "frontend-react" folder
- [ ] Environment Variables → Add:
  - [ ] REACT_APP_API_BASE_URL = https://your-app.railway.app

### Launch
- [ ] Click "Deploy"
- [ ] Wait for deployment (1-2 minutes)
- [ ] Copy Vercel URL (e.g., https://your-app.vercel.app)
- [ ] Visit and verify homepage loads

## 🔧 Final Steps (3 min)

### Update CORS
- [ ] Railway → Backend service → Variables
- [ ] Update CORS_ORIGINS to: https://your-app.vercel.app,http://localhost:3000

### Test Everything
- [ ] Visit your Vercel URL
- [ ] Register new account (tests backend connection)
- [ ] Login works
- [ ] Email analysis works
- [ ] Try "Forgot Password" (tests email)

## 🎉 Success!

**Your URLs:**
- Frontend: https://your-app.vercel.app
- Backend: https://your-app.railway.app
- Database: Managed by Railway

**Total time:** ~18 minutes
**Total cost:** $0-5/month
**Services to manage:** 2 (simple!)

## 🐛 If Something Goes Wrong

**Backend not working?**
- [ ] Check Railway logs
- [ ] Verify environment variables
- [ ] Test /health endpoint

**Frontend can't connect?**
- [ ] Check REACT_APP_API_BASE_URL in Vercel
- [ ] Update CORS_ORIGINS in Railway
- [ ] Check browser console for errors

**Email not working?**  
- [ ] Use Gmail app password (16 chars)
- [ ] Enable Gmail 2FA first
- [ ] Check Railway logs for email errors

---

**Need the detailed guide?** See `VERCEL_RAILWAY_GUIDE.md`

**🚀 Ready to deploy? Start checking boxes! ✅**
