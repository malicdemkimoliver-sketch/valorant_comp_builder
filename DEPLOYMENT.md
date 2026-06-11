# 🚀 Deployment Guide - Valorant Comp Builder

## Production Deployment

This guide covers deploying to Railway.app, Heroku, or similar platforms.

### Prerequisites

- GitHub repository with code pushed
- Google OAuth credentials (already configured)
- Deployment platform account (Railway, Heroku, Vercel, etc.)

---

## 🌐 Railway.app Deployment (Recommended)

### Step 1: Connect Repository

1. Go to [Railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub"
4. Connect your GitHub account
5. Select repository: `valcompbuilder-prod-final`

### Step 2: Set Environment Variables

In Railway dashboard, go to **Variables**:

```
GOOGLE_CLIENT_SECRET = YOUR_CLIENT_SECRET
```

### Step 3: Configure Streamlit

Create `railwayapp.json`:
```json
{
  "buildCommand": "pip install -r requirements.txt",
  "startCommand": "streamlit run app.py"
}
```

Or set environment variables in Railway:
```
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
```

### Step 4: Update Redirect URI

1. Get your Railway app URL from dashboard (e.g., `https://app-xyz.up.railway.app`)
2. Go to Google Cloud Console → Credentials
3. Edit OAuth Client ID
4. Add redirect URI: `https://app-xyz.up.railway.app`
5. Update `REDIRECT_URI` in `app/services/google_oauth_proper.py`:

```python
REDIRECT_URI = "https://app-xyz.up.railway.app"
```

### Step 5: Deploy

```bash
git add .
git commit -m "Deploy to production"
git push origin main
```

Railway will automatically deploy your latest push.

---

## 🔧 Heroku Deployment

### Step 1: Create Heroku App

```bash
heroku login
heroku create your-app-name
```

### Step 2: Set Config Variables

```bash
heroku config:set GOOGLE_CLIENT_SECRET="YOUR_CLIENT_SECRET"
```

### Step 3: Create Procfile

```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Step 4: Deploy

```bash
git push heroku main
```

### Step 5: Update Google Redirect URI

Same as Railway - add your Heroku app URL to Google Cloud credentials and update `REDIRECT_URI`.

---

## 🎯 Local Development

### Setup

```bash
# Clone repository
git clone https://github.com/malicdemkimoliver-sketch/valcompbuilder-prod-final.git
cd valcompbuilder-prod-final

# Create Python environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### Configure Secrets

```bash
# Copy template
cp .streamlit/secrets.toml.example .streamlit/secrets.toml

# Edit and add your Google Client Secret
# .streamlit/secrets.toml:
# GOOGLE_CLIENT_SECRET = "YOUR_CLIENT_SECRET"
```

### Run App

```bash
streamlit run app.py
```

Visit: http://localhost:8501

---

## 🔐 Environment Variables Summary

| Variable | Value | Where |
|----------|-------|-------|
| `GOOGLE_CLIENT_SECRET` | Your secret key | `.streamlit/secrets.toml` or platform env vars |
| `REDIRECT_URI` | Your app URL | Update in `google_oauth_proper.py` |

---

## 📋 Production Checklist

### Before Deploying

- [ ] Repository created and code pushed
- [ ] Google OAuth credentials configured
- [ ] `GOOGLE_CLIENT_SECRET` added to environment
- [ ] `REDIRECT_URI` updated to production URL
- [ ] `.gitignore` prevents secrets from being committed
- [ ] `requirements.txt` has all dependencies
- [ ] Local testing successful

### After Deploying

- [ ] App loads without errors
- [ ] Login with Google works
- [ ] Demo login works
- [ ] Can build compositions
- [ ] Can save compositions
- [ ] Agents Used page works
- [ ] Meta Tracker displays correctly

---

## 🆘 Troubleshooting

### OAuth Login Fails

**Problem:** "Redirect URI mismatch"
- Check Google Cloud console redirect URIs
- Verify `REDIRECT_URI` in `google_oauth_proper.py` matches
- Clear browser cache and try again

**Problem:** "Client Secret invalid"
- Verify environment variable is set correctly
- Make sure you're using secret, not Client ID
- Restart app after changing env var

### App Crashes on Startup

**Problem:** "ModuleNotFoundError"
- Run: `pip install -r requirements.txt`
- Make sure virtual environment is activated

**Problem:** "Database error"
- Check `data/` directory permissions
- Ensure `data/db.json` is readable/writable

### Slow Login/Timeouts

**Problem:** Google redirect takes too long
- Check internet connection
- Verify firewall isn't blocking Google domains
- Try incognito/private browser mode

---

## 📊 Performance Notes

For global deployment:
- App uses Streamlit (works worldwide)
- Database stored locally (consider migrating to MongoDB for scaling)
- Tracker.gg API has rate limits (5-min caching built-in)

---

## 🔄 Updates & Maintenance

### Getting Latest Updates

```bash
git pull origin main
pip install -r requirements.txt  # In case deps changed
streamlit run app.py
```

### Database Management

Database stored in `data/db.json`. To backup:

```bash
cp data/db.json data/db.json.backup
```

---

## 📞 Support

See `GOOGLE_OAUTH_SETUP.md` for OAuth configuration help.

---

**Deployed? Let me know!** 🚀

