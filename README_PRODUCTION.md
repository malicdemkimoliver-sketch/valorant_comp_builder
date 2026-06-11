# ⚙️ Valorant Comp Builder - Production v3.0

**Professional team composition builder with VCT meta analysis, Google OAuth security, and global user support.**

![Build Composition](https://img.shields.io/badge/Build-Composition-blue?style=flat-square)
![Meta Tracker](https://img.shields.io/badge/Meta-Tracker-green?style=flat-square)
![Agent Stats](https://img.shields.io/badge/Agent-Stats-purple?style=flat-square)
![Google OAuth](https://img.shields.io/badge/Auth-Google%20OAuth-red?style=flat-square)

---

## 🎯 Features

### 🎮 Build Compositions
- Create optimal 5-agent team compositions
- **Balanced scoring system** - rewards synergy, role diversity, map viability
- Role-based recommendations (Duelist, Controller, Initiator, Sentinel)
- Real-time viability feedback

### 📊 Meta Tracker
- Live VCT statistics (9 maps, 29 agents)
- Agent pick rates & win rates by map
- S/A/B/C tier classifications
- Agent-to-map viability matching

### 📈 Your Agent Stats
- Sync with tracker.gg automatically
- Personal win rates by agent
- Compare against VCT meta (🟢/🟡/🔴)
- Best agent recommendations
- CSV export

### 💾 Save Compositions
- Store favorite team builds
- Access from any device
- Personal composition history
- Share composition codes

### 🔐 Secure Google OAuth
- Global authentication
- Users manage their own security
- No passwords stored
- Data isolation per user

---

## 🚀 Quick Start

### Local Development

```bash
# Clone and setup
git clone https://github.com/malicdemkimoliver-sketch/valcompbuilder-prod-final.git
cd valcompbuilder-prod-final

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure secrets
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your Google Client Secret

# Run
streamlit run app.py
```

Visit: **http://localhost:8501**

### Production Deployment

See `DEPLOYMENT.md` for:
- Railway.app deployment
- Heroku deployment
- Environment variable setup
- Troubleshooting

---

## 📋 Navigation

### Main Features (3)
- **🎯 Build Composition** - Create and analyze team comps
- **📊 Meta Tracker** - VCT statistics and agent tiers
- **📈 Your Agent Stats** - Personal tracker.gg integration

### Account Section
- **💾 Saved Comps** - Your saved compositions
- **👤 Account Settings** - User profile & preferences
- **🚪 Logout** - Sign out

---

## 🔐 Security & Authentication

### Google OAuth 2.0
- Industry-standard authentication
- Users manage their own security (2FA, recovery, etc.)
- App never stores passwords
- Data tied to Google account
- Users can revoke access anytime

### Data Protection
- ✅ Email and user name stored (from Google)
- ✅ Compositions stored securely
- ❌ Passwords never stored
- ❌ No sensitive data in logs
- ❌ API tokens are temporary only

---

## 📦 Requirements

```
streamlit==1.28.1
requests==2.31.0
beautifulsoup4==4.12.2
google-auth==2.25.2
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
```

**Python:** 3.8+

---

## 🎯 Scoring System

### Components
1. **Role Diversity** (20 pts)
   - 4 roles: 20 pts | 3 roles: 18 pts | 2 roles: 12 pts

2. **Agent Synergy** (25 pts)
   - Agents that work together get bonuses

3. **Map Viability** (25 pts)
   - S-tier: 5 pts | A-tier: 4 pts | B-tier: 3 pts | C-tier: 1 pt

4. **Utility Coverage** (15 pts)
   - Diverse utility types rewarded

5. **Attack/Defense Balance** (15 pts)
   - Ideal: 1-2 duelists, 2-3 sentinels

### Grades
- **S**: 85+ - Exceptional comp
- **A**: 75+ - Competitive comp
- **B**: 60+ - Good comp
- **C**: 45+ - Playable comp
- **D**: 30+ - Weak comp
- **F**: <30 - Poor comp

---

## 🌍 Global Support

### Supported Regions
- ✅ North America (NA)
- ✅ Europe (EU)
- ✅ Asia-Pacific (AP)
- ✅ Latin America (LATAM)
- ✅ Middle East (MENA)
- ✅ All Google OAuth supported countries

### Localization
- Valorant agent names (global)
- Map names (global)
- English interface
- Future: Multi-language support

---

## 📚 Documentation

- **`DEPLOYMENT.md`** - Production deployment guide
- **`GOOGLE_OAUTH_SETUP.md`** - OAuth configuration
- **`UPDATE_GUIDE_V3.md`** - All changes & improvements
- **`CHANGELOG_LATEST.md`** - Latest updates

---

## 🧪 Testing

### Local Testing
```bash
streamlit run app.py
```

### Test Accounts (Demo)
- kimma@example.com
- user2@example.com
- user3@example.com

### OAuth Testing
1. Click "🔐 Login with Google"
2. Login with your Google account
3. You'll be redirected back
4. Session created

---

## 🐛 Known Issues & Fixes

### Fixed in v3.0
- ✅ Vyse role corrected (Sentinel, not Controller)
- ✅ Google OAuth properly implemented
- ✅ Balanced scoring (no longer too harsh)
- ✅ Agents Used page functional
- ✅ Navigation reorganized
- ✅ Multi-login method support

---

## 🔄 Updates

### Latest Changes (v3.0)
- Google OAuth 2.0 implementation
- Balanced scoring algorithm
- tracker.gg integration
- Navigation restructure
- Security improvements

### How to Update
```bash
git pull origin main
pip install -r requirements.txt
streamlit run app.py
```

---

## 📊 Data Models

### User
```json
{
  "email": "user@example.com",
  "name": "User Name",
  "picture": "https://...",
  "created_at": "2026-06-10T...",
  "last_login": "2026-06-10T..."
}
```

### Composition
```json
{
  "id": "comp_123",
  "user_email": "user@example.com",
  "map": "Haven",
  "agents": ["Jett", "Omen", "Sova", "Killjoy", "Sage"],
  "score": 87,
  "grade": "A",
  "created_at": "2026-06-10T..."
}
```

---

## 🤝 Contributing

Want to contribute? Great!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📞 Support

### Issues?
Check `DEPLOYMENT.md` troubleshooting section for:
- OAuth login issues
- App startup errors
- Database problems
- Performance issues

### FAQ

**Q: How is my data stored?**
A: In `data/db.json` locally. For production, consider migrating to MongoDB.

**Q: Can I revoke Google access?**
A: Yes, anytime at https://myaccount.google.com/permissions

**Q: How often is VCT meta updated?**
A: You can update `data/vct_meta.json` manually as needed.

**Q: Can I export my compositions?**
A: Yes, saved compositions are stored in the database and can be exported.

---

## 📄 License

This project is private/proprietary. Contact owner for licensing information.

---

## 👥 Authors

- **Developer:** GYDRENZIN (Kimma)
- **Version:** 3.0 - Production Ready
- **Last Updated:** June 10, 2026

---

## 🎉 Acknowledgments

- **Riot Games** - Valorant
- **VCT** - Professional esports data
- **Google** - OAuth & Cloud services
- **Streamlit** - Web framework
- **tracker.gg** - Player statistics

---

## 📞 Contact

For questions or support:
- GitHub: [@malicdemkimoliver-sketch](https://github.com/malicdemkimoliver-sketch)
- Repository: [valcompbuilder-prod-final](https://github.com/malicdemkimoliver-sketch/valcompbuilder-prod-final)

---

**Ready to build better comps?** 🎮✨

