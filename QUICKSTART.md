# 🚀 Quick Start - Google OAuth & Bug Fixes

## What's New?
✅ **6 Security Bugs Fixed**
✅ **Google OAuth 2.0 Implemented** 
✅ **Full Documentation Provided**

## Prerequisites
- Python 3.12+
- Django 5.1.7
- Google Cloud Project (for OAuth)

## Local Setup (5 minutes)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python manage.py migrate
```

### 3. Create Test Admin (optional)
```bash
python manage.py createsuperuser
# Or use management command:
python manage.py create_superuser --username=admin --password=admin123
```

### 4. Test API
```bash
# Register
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"SecurePass123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"SecurePass123"}'

# Get Current User
curl http://localhost:8000/api/auth/me/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"

# Get Google Config (no auth needed)
curl http://localhost:8000/api/auth/google/config/
```

### 5. Start Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000/admin/login/

---

## Google OAuth Setup (15 minutes)

### 1. Get Google Credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "GROOVY Tic Tac Toe"
3. Enable Google+ API
4. Create OAuth 2.0 Web Application credentials
5. Add Authorized Redirect URIs:
   - `http://localhost:3000/auth/callback`
   - `http://localhost:8000/api/auth/google/callback/`

### 2. Add to .env
```
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

### 3. Test Google Auth Endpoint
```bash
curl http://localhost:8000/api/auth/google/config/
```

Should return:
```json
{
  "client_id": "your-client-id.apps.googleusercontent.com",
  "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
  "scopes": ["openid", "email", "profile"]
}
```

---

## Frontend Integration (React)

### 1. Install Google OAuth Library
```bash
npm install @react-oauth/google
```

### 2. Add Login Component
```jsx
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

function Login() {
  const handleGoogleSuccess = async (credentialResponse) => {
    const response = await fetch('http://localhost:8000/api/auth/google/callback/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        auth_code: credentialResponse.credential,
        redirect_uri: 'http://localhost:3000/auth/callback'
      })
    });
    
    const data = await response.json();
    localStorage.setItem('access_token', data.tokens.access);
  };

  return (
    <GoogleOAuthProvider clientId="your-client-id">
      <GoogleLogin onSuccess={handleGoogleSuccess} />
    </GoogleOAuthProvider>
  );
}
```

---

## Production Deployment

### 1. Update Environment (Render)
```
DEBUG=False
SECRET_KEY=<strong-random-key>
GOOGLE_CLIENT_ID=<your-prod-client-id>
GOOGLE_CLIENT_SECRET=<your-prod-client-secret>
ALLOWED_HOSTS=yourapp.onrender.com,localhost,127.0.0.1
```

### 2. Update Google Cloud Console
Add Production Redirect URIs:
- `https://yourapp.onrender.com/auth/callback`
- `https://yourapp.onrender.com/api/auth/google/callback/`

### 3. Deploy
```bash
git add .
git commit -m "Add Google OAuth and fix security bugs"
git push
```

---

## API Endpoints Summary

### Auth Endpoints
| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| POST | `/api/auth/register/` | Register new user | ❌ |
| POST | `/api/auth/login/` | Login user | ❌ |
| GET | `/api/auth/me/` | Get current user | ✅ |
| POST | `/api/auth/logout/` | Logout user | ✅ |

### Google OAuth Endpoints
| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/auth/google/config/` | Get OAuth config | ❌ |
| POST | `/api/auth/google/callback/` | OAuth callback | ❌ |
| POST | `/api/auth/google/link/` | Link to existing | ✅ |

### Game Endpoints
| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| GET | `/api/rooms/` | List user's rooms | ✅ |
| POST | `/api/rooms/` | Create room | ✅ |
| POST | `/api/rooms/join_room/` | Join room | ✅ |
| POST | `/api/rooms/move/` | Make move | ✅ |

---

## Bug Fixes Reference

| # | Bug | Status |
|---|-----|--------|
| 1 | DEBUG=True in .env | ✅ Fixed |
| 2 | Invalid SECRET_KEY | ✅ Fixed |
| 3 | No email validation | ✅ Fixed |
| 4 | Unauthenticated /me endpoint | ✅ Fixed |
| 5 | Missing game room permission checks | ✅ Fixed |
| 6 | Missing requests library | ✅ Fixed |

---

## Testing

### Unit Test Example
```bash
python manage.py test game
```

### Security Check
```bash
python manage.py check --deploy
```

### Database Check
```bash
python manage.py migrate --plan
```

---

## Troubleshooting

### Issue: "Google OAuth not configured"
```
✓ Solution: Check GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in .env
```

### Issue: CORS error on Google callback
```
✓ Solution: Verify CORS_ALLOW_ALL_ORIGINS=True or add frontend URL to CORS_ALLOWED_ORIGINS
```

### Issue: Redirect URI mismatch
```
✓ Solution: Ensure URI matches exactly in Google Cloud Console
```

### Issue: Email already registered
```
✓ Solution: Email validation now prevents duplicates - register with different email
```

---

## Files Modified

- ✅ `.env` - Updated configuration
- ✅ `.env.example` - Updated template
- ✅ `game/serializers.py` - Added validation
- ✅ `game/views.py` - Added auth checks + Google endpoints
- ✅ `game/urls.py` - Added OAuth routes
- ✅ `game/auth_google.py` - NEW: Google OAuth handler
- ✅ `tictactoe/settings.py` - Added Google config
- ✅ `requirements.txt` - Added dependencies
- ✅ `GOOGLE_AUTH_SETUP.md` - NEW: Detailed setup guide
- ✅ `BUGFIXES_AND_OAUTH_SUMMARY.md` - NEW: Complete summary

---

## Documentation

📖 **Full Google OAuth Setup**: See [GOOGLE_AUTH_SETUP.md](./GOOGLE_AUTH_SETUP.md)

📖 **All Changes Summary**: See [BUGFIXES_AND_OAUTH_SUMMARY.md](./BUGFIXES_AND_OAUTH_SUMMARY.md)

---

## Next Steps

1. ✅ Install requirements: `pip install -r requirements.txt`
2. ✅ Test locally: `python manage.py runserver`
3. ⏳ Set up Google OAuth credentials (see Google OAuth Setup above)
4. ⏳ Test Google login endpoint
5. ⏳ Integrate with frontend
6. ⏳ Deploy to production

---

**Status**: Ready for testing and integration
**Questions?**: Check GOOGLE_AUTH_SETUP.md or BUGFIXES_AND_OAUTH_SUMMARY.md
