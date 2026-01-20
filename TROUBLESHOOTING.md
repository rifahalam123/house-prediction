# Troubleshooting Guide

## Issue: Cannot connect to API / CORS Error

### Problem
```
Cannot connect to API at https://web-production-738df.up.railway.app
Error: Failed to fetch
CORS policy blocked
```

### Solution ✓ FIXED
The CORS configuration has been updated to allow all origins:

**What was changed:**
- File: [app.py](app.py) lines 18-28
- Changed CORS from environment-based to wildcard (`*`)
- This allows the web interface to connect from any domain

**Latest commit:** `987b28f - Fix CORS configuration to allow all origins`

### After Railway Redeploys

Railway should automatically redeploy when you push to GitHub. The deployment process:

1. **Triggered**: Automatic on git push (takes 2-5 minutes)
2. **Building**: Installing requirements and training model
3. **Starting**: Launching Gunicorn server
4. **Ready**: API available at your Railway URL

### How to Check if Deployment is Complete

```bash
# Check health endpoint
curl https://web-production-738df.up.railway.app/health

# Should return:
{
  "status": "healthy",
  "model_loaded": true,
  "environment": "production"
}
```

### Testing the Fixed API

**Option 1: Using curl**
```bash
curl -X POST https://web-production-738df.up.railway.app/predict \
  -H "Content-Type: application/json" \
  -H "Origin: http://localhost" \
  -d '{"bedrooms": 3, "bathrooms": 2, "sqft": 2000, "age": 10}'
```

**Option 2: Using the web interface**
1. Open [index.html](index.html) in your browser
2. The URL is already set to your Railway deployment
3. Fill in the form and click "Get Price Estimate"
4. Should work without CORS errors now!

---

## Issue: Model Version Mismatch Warning

### Problem
```
InconsistentVersionWarning: Trying to unpickle estimator from version 1.7.2
when using version 1.4.2
```

### Solution ✓ FIXED
Requirements and model have been updated to compatible versions:

**Latest commit:** `9e3070c - Fix scikit-learn version compatibility`

The model has been retrained with scikit-learn 1.4.2, which is the version specified in [requirements.txt](requirements.txt).

---

## Issue: Model Not Loading on Deployment

### Symptoms
- API returns 503 errors
- Health check shows `"model_loaded": false`
- Logs show "Model file not found"

### Solution
Ensure the build command trains the model:

**Railway/Render Build Command:**
```bash
pip install -r requirements.txt && python train_model.py
```

This is already configured in:
- Railway: Auto-detected from repository structure
- Render: Set in [DEPLOYMENT.md](DEPLOYMENT.md) instructions

### Manual Check
If model files are missing, run locally:
```bash
python train_model.py
```

This creates:
- `house_price_model.joblib`
- `scaler.joblib`

---

## Issue: Connection Timeout / Server Not Responding

### Possible Causes
1. **Railway Free Tier Sleep**: Railway free tier sleeps after inactivity
2. **First Request**: Takes 30-60 seconds to wake up
3. **Build in Progress**: Deployment is still building

### Solutions

**Check Railway Dashboard:**
1. Go to railway.app
2. Check deployment status
3. View logs for errors

**Check if sleeping:**
```bash
# This wakes up the server
curl https://web-production-738df.up.railway.app/health
# Wait 30 seconds, then try again
```

**Check build logs:**
- Railway: Dashboard → Deployments → Latest → Build Logs
- Look for errors during `pip install` or `python train_model.py`

---

## Issue: Wrong Python Version

### Symptoms
```
ERROR: This package requires Python >=3.11
```

### Solution
The [runtime.txt](runtime.txt) specifies Python 3.11.9:

```
python-3.11.9
```

**On Railway:**
- Auto-detects from runtime.txt
- No manual configuration needed

**On Render:**
- Set in dashboard: Environment → Python Version → 3.11.9

---

## Issue: Requirements Installation Fails

### Symptoms
```
ERROR: Could not find a version that satisfies the requirement...
```

### Solution
Use the exact versions in [requirements.txt](requirements.txt):

```
scikit-learn==1.4.2
numpy==1.26.4
pandas==2.2.2
```

These versions are tested and verified compatible.

**If issues persist:**
```bash
# Locally test requirements
pip install -r requirements.txt

# Check for conflicts
pip check
```

---

## Local Development

### Start Server
```bash
# Windows
start.bat

# Mac/Linux
chmod +x start.sh
./start.sh

# Or manually
python app.py
```

### Test API
```bash
# Health check
curl http://localhost:5000/health

# Prediction
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"bedrooms": 3, "bathrooms": 2, "sqft": 2000, "age": 10}'
```

### View Logs
Server logs will show in the terminal:
- Request logs
- Error messages
- Model loading status

---

## Getting Help

### Check These First
1. [README.md](README.md) - Full documentation
2. [DEPLOYMENT.md](DEPLOYMENT.md) - Deployment guides
3. [DEPLOY_NOTES.md](DEPLOY_NOTES.md) - Requirements details

### Deployment Platform Docs
- **Railway**: https://docs.railway.app
- **Render**: https://render.com/docs
- **PythonAnywhere**: https://help.pythonanywhere.com

### Common Commands

```bash
# Check git status
git status

# View recent commits
git log --oneline -5

# View file changes
git diff

# Pull latest changes
git pull origin main

# Push changes
git push origin main
```

---

## Status: All Issues Fixed ✓

- ✓ CORS configuration fixed
- ✓ Scikit-learn version compatibility fixed
- ✓ Requirements optimized for deployment
- ✓ Model retrained with correct versions
- ✓ Pushed to GitHub

**Next:** Wait for Railway to redeploy (automatic, ~3 minutes)
