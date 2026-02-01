# Deployment Guide - Adaptive Logistics Platform

## Overview
This guide will help you deploy your logistics platform with:
- **Backend (Python/FastAPI)** → Render.com
- **Frontend (React/Vite)** → Vercel

---

## 🔧 Pre-Deployment Checklist

### 1. Backend Preparation

Create a `render.yaml` file in your project root:

```yaml
services:
  - type: web
    name: adaptive-logistics-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn api:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: PORT
        generateValue: true
```

### 2. Update `requirements.txt`
Make sure your `requirements.txt` includes all dependencies:

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
requests==2.31.0
openai==1.3.0
python-dotenv==1.0.0
```

### 3. Update CORS Configuration in `api.py`
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-vercel-domain.vercel.app"  # Update this after Vercel deployment
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🚀 Deploy Backend to Render

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account

### Step 2: Connect Repository
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select your repository

### Step 3: Configure Service
- **Name**: `adaptive-logistics-api`
- **Region**: Oregon (US West)
- **Branch**: `main`
- **Runtime**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
- **Plan**: Free

### Step 4: Add Environment Variables
Add these in Render dashboard:
```
OPENAI_API_KEY=your_api_key_here
PYTHON_VERSION=3.11.0
```

### Step 5: Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes)
3. Copy your API URL: `https://adaptive-logistics-api.onrender.com`

---

## 🌐 Deploy Frontend to Vercel

### Step 1: Update API Base URL

Edit `frontend/src/services/api.ts`:

```typescript
const BASE_URL = import.meta.env.PROD 
  ? 'https://adaptive-logistics-api.onrender.com/api'  // Your Render URL
  : '/api'
```

Or create `frontend/.env.production`:

```env
VITE_API_URL=https://adaptive-logistics-api.onrender.com/api
```

And update `api.ts`:

```typescript
const BASE_URL = import.meta.env.VITE_API_URL || '/api'
```

### Step 2: Create Vercel Account
1. Go to https://vercel.com
2. Sign up with GitHub

### Step 3: Import Project
1. Click "Add New..." → "Project"
2. Import your GitHub repository
3. Vercel auto-detects Vite configuration

### Step 4: Configure Build Settings
- **Framework Preset**: Vite
- **Root Directory**: `frontend`
- **Build Command**: `npm run build`
- **Output Directory**: `dist`

### Step 5: Add Environment Variables (Optional)
```
VITE_API_URL=https://adaptive-logistics-api.onrender.com/api
```

### Step 6: Deploy
1. Click "Deploy"
2. Wait 2-3 minutes
3. Get your URL: `https://your-project.vercel.app`

---

## 🔄 Update CORS After Frontend Deployment

After deploying frontend, update your backend `api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://your-project.vercel.app",  # Add your actual Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Commit and push this change - Render will auto-redeploy.

---

## 🧪 Testing Deployment

### Test Backend
```bash
curl https://adaptive-logistics-api.onrender.com/api/state
```

### Test Frontend
1. Visit `https://your-project.vercel.app`
2. Click "Launch Fleet Intelligence"
3. Verify trucks appear on map

---

## 🔧 Troubleshooting

### Backend Issues

**Problem**: OSRM timeout errors
```python
# In utils/osrm_client.py, increase timeout:
response = requests.get(url, params=params, timeout=15)  # Changed from 5 to 15
```

**Problem**: Port binding error
- Render automatically sets `PORT` env variable
- Ensure using: `--port $PORT`

**Problem**: Module not found
- Check all imports in `requirements.txt`
- Run locally first: `pip freeze > requirements.txt`

### Frontend Issues

**Problem**: API calls fail (CORS)
- Check Render logs for CORS errors
- Verify Vercel URL is in `allow_origins`

**Problem**: 404 on routes
- Vercel automatically handles SPA routing
- No additional configuration needed

**Problem**: Environment variables not working
- Use `VITE_` prefix for all env vars
- Redeploy after adding env vars

---

## 📊 Monitoring

### Render Dashboard
- View logs: Dashboard → Your Service → Logs
- Monitor metrics: CPU, Memory, Response time
- Check health: Auto-pings every 15 minutes (Free tier sleeps after 15 min inactivity)

### Vercel Dashboard
- View deployments: Dashboard → Your Project
- Check analytics: Analytics tab
- View logs: Functions → Logs

---

## 💡 Pro Tips

### Keep Render Free Tier Active
Free tier sleeps after 15 minutes of inactivity. To keep it active:

1. Use UptimeRobot (free)
2. Ping your API every 14 minutes: `https://adaptive-logistics-api.onrender.com/api/state`

### Optimize Cold Starts
```python
# Add health check endpoint in api.py
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Environment-Specific Configs

```typescript
// frontend/src/config.ts
export const config = {
  apiUrl: import.meta.env.PROD 
    ? 'https://adaptive-logistics-api.onrender.com/api'
    : '/api',
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
}
```

---

## 🔐 Security Checklist

- [ ] Remove any hardcoded API keys
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS only (both platforms do this by default)
- [ ] Set proper CORS origins (not `*`)
- [ ] Add rate limiting if needed
- [ ] Review Render/Vercel security settings

---

## 📚 Next Steps

1. **Custom Domain** (Optional)
   - Vercel: Settings → Domains → Add domain
   - Render: Settings → Custom Domain

2. **CI/CD** (Already configured!)
   - Push to `main` branch
   - Both platforms auto-deploy

3. **Monitoring & Alerts**
   - Set up Render email alerts
   - Use Vercel deployment notifications

4. **Scale Up** (When needed)
   - Render: Upgrade to Starter ($7/month) for always-on
   - Vercel: Pro plan for more bandwidth

---

## 🆘 Support

- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- GitHub Issues: Create issues in your repository

---

**Deployment Completed!** 🎉

Your logistics platform is now live:
- Backend API: `https://adaptive-logistics-api.onrender.com`
- Frontend: `https://your-project.vercel.app`
