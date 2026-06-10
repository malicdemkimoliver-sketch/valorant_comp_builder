# 🔐 Google OAuth 2.0 Setup Guide

## Overview

This app uses **Google OAuth 2.0** for secure authentication. Users login with their Google account instead of creating passwords.

**Benefits:**
- ✅ Users manage their own security (2FA, recovery, etc.)
- ✅ App never stores passwords
- ✅ Global trust - users recognize Google login
- ✅ Data is tied to Google account

---

## 📋 Setup Steps

### Step 1: Create Google Cloud Project

1. Go to **[Google Cloud Console](https://console.cloud.google.com)**
2. Create a new project
   - Click "Select a Project" at top
   - Click "New Project"
   - Name: "Valorant Comp Builder"
   - Click "Create"

### Step 2: Create OAuth 2.0 Credentials

1. In Google Cloud Console, go to **APIs & Services** → **Credentials**
2. Click **+ Create Credentials** → **OAuth 2.0 Client ID**
3. If prompted, configure OAuth consent screen first:
   - Click "Configure Consent Screen"
   - User type: **External**
   - Fill required fields:
     - App name: "Valorant Comp Builder"
     - User support email: your email
     - Developer contact: your email
   - Click "Save and Continue"
   - Add scopes: `openid`, `email`, `profile`
   - Click "Save and Continue"
   - Click "Back to Dashboard"

4. Now create OAuth Client ID:
   - Application type: **Web application**
   - Name: "Valorant Comp Builder Web"
   - Authorized redirect URIs:
     ```
     http://localhost:8501
     ```
   - Click "Create"

5. **Copy your credentials:**
   - **Client ID:** `479281130427-ntgbl24stb04n08t7d1i7dcoibgvbsuc.apps.googleusercontent.com`
   - **Client Secret:** (You'll need this for environment variable)

### Step 3: Set Environment Variables

**For Local Development:**

Create a `.env` file in your project root:
```bash
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

Then load it before running:
```bash
# Windows PowerShell
$env:GOOGLE_CLIENT_SECRET="your_client_secret_here"
python -m streamlit run app.py

# macOS/Linux
export GOOGLE_CLIENT_SECRET="your_client_secret_here"
python -m streamlit run app.py
```

**For Production (Heroku/Railway/etc):**

Set environment variable in deployment platform:
```
GOOGLE_CLIENT_SECRET = your_client_secret_here
```

### Step 4: Update Redirect URI for Production

When deploying to production, update authorized redirect URIs:

1. Go to **Google Cloud Console** → **Credentials**
2. Click your OAuth Client
3. Add production URL:
   ```
   https://your-app-domain.com
   ```
4. Click "Save"

Then update `REDIRECT_URI` in `app/services/google_oauth_proper.py`:
```python
REDIRECT_URI = "https://your-app-domain.com"  # Production URL
```

---

## 🚀 Running the App

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variable
export GOOGLE_CLIENT_SECRET="your_secret"  # or use .env

# 3. Run the app
python -m streamlit run app.py

# 4. Open http://localhost:8501 in browser
# 5. Click "🔐 Login with Google"
# 6. You'll be redirected to Google login
# 7. After login, you're redirected back to the app
```

### Deployment

**Example: Railway.app**

1. Push code to GitHub
2. Connect Railway to GitHub repo
3. Add environment variable:
   - Key: `GOOGLE_CLIENT_SECRET`
   - Value: your actual secret
4. Deploy

---

## 🧪 Testing

### Test OAuth Flow Locally

1. Run app: `python -m streamlit run app.py`
2. Click **🔐 Login with Google**
3. You should be redirected to Google login
4. Login with your Google account
5. You'll be redirected back to app
6. Should see: ✅ Logged in as [your email]

### Demo Login (For Testing)

If you want to test without Google OAuth:
- Expand "📝 Demo Login (Testing Only)"
- Click any demo account
- You'll be logged in immediately

---

## 🔒 Security Notes

### What We Store
- ✅ Email address
- ✅ User name
- ✅ Profile picture URL
- ✅ User compositions

### What We DON'T Store
- ❌ Password
- ❌ Google credentials
- ❌ Access tokens (temporary only)

### User Privacy
- Users can revoke access anytime: https://myaccount.google.com/permissions
- Data is stored in app database (db.json)
- No data shared with third parties

---

## ⚠️ Common Issues

### Issue: "Client ID not found"
**Solution:** Make sure `GOOGLE_CLIENT_ID` is set in `google_oauth_proper.py`

### Issue: "Redirect URI mismatch"
**Solution:** 
- Make sure redirect URI in Google Cloud matches your app URL
- Local: `http://localhost:8501`
- Production: `https://your-domain.com`

### Issue: "Invalid Client Secret"
**Solution:** 
- Check environment variable is set correctly
- Make sure you're using the actual secret, not Client ID
- Restart app after changing env var

### Issue: "Login redirects but doesn't work"
**Solution:**
- Check Google Cloud OAuth consent screen is configured
- Make sure scopes include `openid`, `email`, `profile`
- Clear browser cache and try again

---

## 📚 Files Modified/Created

**New Files:**
- `app/services/google_oauth_proper.py` - Google OAuth 2.0 implementation
- `app/ui/login_page_google_oauth.py` - Login page with OAuth redirect
- `GOOGLE_OAUTH_SETUP.md` - This file

**Modified Files:**
- `app.py` - Added login requirement check
- `requirements.txt` - Added OAuth libraries

---

## 🎯 Production Deployment Checklist

- [ ] Google Cloud Project created
- [ ] OAuth Client ID created
- [ ] OAuth Client Secret created and saved securely
- [ ] Environment variable `GOOGLE_CLIENT_SECRET` set
- [ ] Production redirect URI added to Google Cloud
- [ ] `REDIRECT_URI` updated in `google_oauth_proper.py`
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] App tested locally with OAuth
- [ ] Code pushed to Git
- [ ] Deployment platform configured
- [ ] Production environment variables set

---

## 📖 References

- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Cloud Console](https://console.cloud.google.com)
- [Streamlit Documentation](https://docs.streamlit.io)

---

**Version:** 3.0 - Google OAuth Implementation  
**Date:** June 10, 2026

