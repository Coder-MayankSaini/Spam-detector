# Production Testing Checklist

## 🧪 Complete System Test

### Backend Testing (Railway)
1. **Health Check:** `https://your-app.up.railway.app/health`
   - Should return: `{"status": "healthy", "database": "connected"}`

2. **API Endpoints:**
   ```bash
   # Test registration
   curl -X POST https://your-app.up.railway.app/api/register \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "testpass123"}'

   # Test login
   curl -X POST https://your-app.up.railway.app/api/login \
     -H "Content-Type: application/json" \
     -d '{"email": "test@example.com", "password": "testpass123"}'

   # Test spam detection (with token from login)
   curl -X POST https://your-app.up.railway.app/api/analyze \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{"text": "Congratulations! You won $1000! Click here now!"}'
   ```

### Frontend Testing (Vercel)
1. **Access your Vercel URL:** `https://your-project.vercel.app`
2. **Test Features:**
   - ✅ Homepage loads
   - ✅ Registration works
   - ✅ Login works
   - ✅ Spam analysis works
   - ✅ History displays
   - ✅ Image upload works (if OCR enabled)

### Database Testing
1. **Check Railway PostgreSQL:**
   - Go to Railway Dashboard → PostgreSQL service
   - Check "Data" tab to see tables created
   - Verify users and analysis_history tables exist

2. **Test Data Persistence:**
   - Register a user
   - Analyze some text
   - Check if history persists after page reload

## 🐛 Troubleshooting Common Issues

### Backend Issues:
- **Database connection failed:** Check DATABASE_URL in Railway variables
- **JWT errors:** Ensure JWT_SECRET_KEY is set in Railway
- **CORS errors:** Check if frontend URL is properly configured

### Frontend Issues:
- **API calls failing:** Verify REACT_APP_API_URL matches Railway backend URL
- **Build failures:** Check if all dependencies are in package.json
- **Routing issues:** Ensure vercel.json has correct rewrites

### Deployment Issues:
- **Railway build fails:** Check Procfile and requirements.txt
- **Vercel build fails:** Verify build command and output directory
- **Environment variables:** Double-check all required vars are set
