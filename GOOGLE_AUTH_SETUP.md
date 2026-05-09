# Google OAuth Setup Guide for GROOVY Tic Tac Toe

This guide walks you through setting up Google OAuth2 authentication for the GROOVY Tic Tac Toe application.

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click on "Select a Project" → "NEW PROJECT"
3. Enter project name: `GROOVY Tic Tac Toe`
4. Click "CREATE"
5. Wait for the project to be created and select it

## Step 2: Enable Google+ API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Google+ API"
3. Click on it and press **ENABLE**
4. This enables user data access through OAuth

## Step 3: Create OAuth 2.0 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If prompted to create an OAuth consent screen first:
   - Click **Configure consent screen**
   - Choose **External** user type
   - Fill in:
     - App name: `GROOVY Tic Tac Toe`
     - User support email: Your email
     - Developer contact info: Your email
   - Click **Save and Continue**
   - On "Scopes" page, click **Add or Remove Scopes**
   - Add: `openid`, `email`, `profile`
   - Click **Update** and continue to finish
4. Back to credentials, click **Create Credentials** → **OAuth client ID**
5. Select application type: **Web application**
6. Name it: `GROOVY Web App`
7. Add authorized redirect URIs:
   - For development: `http://localhost:3000/auth/callback`
   - For production: `https://yourapp.onrender.com/auth/callback`
   - Backend API: `http://localhost:8000/api/auth/google/callback/`
   - Production backend: `https://yourapp.onrender.com/api/auth/google/callback/`
8. Click **Create**
9. Copy the Client ID and Client Secret

## Step 4: Add Credentials to Your Application

### Local Development

1. Open `.env` file in your project root
2. Add:
   ```
   GOOGLE_CLIENT_ID=your-copied-client-id
   GOOGLE_CLIENT_SECRET=your-copied-client-secret
   ```
3. Save the file

### Production (Render)

1. Go to your Render Dashboard
2. Select your application
3. Go to **Environment** → **Environment Variables**
4. Add two variables:
   - Key: `GOOGLE_CLIENT_ID`, Value: Your Client ID
   - Key: `GOOGLE_CLIENT_SECRET`, Value: Your Client Secret
5. Redeploy your application

## Step 5: Backend API Endpoints

The following endpoints are now available:

### Get Google Auth Configuration
```
GET /api/auth/google/config/
```
Returns the Google Client ID and OAuth configuration needed for frontend.

**Response:**
```json
{
  "client_id": "your-client-id.apps.googleusercontent.com",
  "auth_uri": "https://accounts.google.com/o/oauth2/v2/auth",
  "scopes": ["openid", "email", "profile"]
}
```

### Google Login Callback (for existing registered users)
```
POST /api/auth/google/callback/
```

**Request body:**
```json
{
  "auth_code": "authorization-code-from-google",
  "redirect_uri": "http://localhost:3000/auth/callback",
  "email_to_link": "user@example.com"  // Optional: for linking to existing account
}
```

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

### Link Google Account to Existing User
```
POST /api/auth/google/link/
```
Requires authentication (JWT token)

**Request body:**
```json
{
  "auth_code": "authorization-code-from-google",
  "redirect_uri": "http://localhost:3000/auth/callback"
}
```

**Response:**
```json
{
  "message": "Google account linked successfully",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com"
  }
}
```

## Step 6: Frontend Implementation

### 1. Install Google OAuth Library

```bash
npm install @react-oauth/google
```

### 2. Add Google OAuth Button to Login Page

```jsx
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';

function LoginPage() {
  const handleGoogleSuccess = async (credentialResponse) => {
    try {
      // Send authorization code to backend
      const response = await fetch('/api/auth/google/callback/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          auth_code: credentialResponse.credential,
          redirect_uri: window.location.origin + '/auth/callback',
          email_to_link: null // Leave empty for new login
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        // Store tokens
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Login failed');
    }
  };

  return (
    <GoogleOAuthProvider clientId="your-client-id">
      <div className="login-container">
        <h2>Login</h2>
        <GoogleLogin
          onSuccess={handleGoogleSuccess}
          onError={() => alert('Login failed')}
        />
      </div>
    </GoogleOAuthProvider>
  );
}
```

### 3. Link Google Account for Existing Users

```jsx
function AccountSettings() {
  const handleLinkGoogle = async (credentialResponse) => {
    try {
      const response = await fetch('/api/auth/google/link/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        },
        body: JSON.stringify({
          auth_code: credentialResponse.credential,
          redirect_uri: window.location.origin + '/settings'
        })
      });

      const data = await response.json();
      
      if (response.ok) {
        alert('Google account linked successfully!');
        // Refresh user data or redirect
      } else {
        alert('Error: ' + data.error);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="settings">
      <h2>Account Settings</h2>
      <GoogleOAuthProvider clientId="your-client-id">
        <GoogleLogin
          onSuccess={handleLinkGoogle}
          onError={() => alert('Failed to link Google account')}
          text="Link Google Account"
        />
      </GoogleOAuthProvider>
    </div>
  );
}
```

## Troubleshooting

### "Google OAuth not configured"
- Check that `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` are set in your environment variables
- Verify they match your Google Cloud credentials

### Redirect URI mismatch error
- Make sure the redirect URI in your frontend matches exactly with the one in Google Cloud Console
- Include the protocol (http/https) and port number

### CORS errors
- The backend is configured with `CORS_ALLOW_ALL_ORIGINS = True` in development
- For production, restrict CORS_ALLOWED_ORIGINS to your frontend domain

### User not found error
- Ensure the email address is registered in the system before linking
- Use the `email_to_link` parameter when logging in for the first time with Google

## Security Considerations

1. **Never commit credentials**: Always use environment variables
2. **Use HTTPS in production**: Google OAuth requires HTTPS for production apps
3. **Validate tokens**: Always verify tokens on the backend before creating sessions
4. **Refresh tokens**: Use refresh tokens to maintain long-lived sessions
5. **User isolation**: Ensure users can only access their own game rooms and data

## Testing Locally

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Your frontend should be running on http://localhost:3000

3. Test the Google OAuth flow:
   - Click "Login with Google"
   - Authenticate with your Google account
   - You should be redirected with JWT tokens

## Production Deployment

1. Set environment variables in Render dashboard
2. Update ALLOWED_HOSTS in `.env` to include your Render domain
3. Ensure `DEBUG=False` in production
4. Update Google Cloud Console authorized redirect URIs to your production domain
5. Deploy and test the OAuth flow

---

For more information, see:
- [Google OAuth 2.0 Documentation](https://developers.google.com/identity/protocols/oauth2)
- [Google Sign-In for Web](https://developers.google.com/identity/sign-in/web)
