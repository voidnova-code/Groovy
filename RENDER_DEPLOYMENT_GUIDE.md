# Render Deployment Guide - GROOVY Tic Tac Toe

This guide covers deploying the GROOVY Tic Tac Toe game to Render with PostgreSQL (Supabase) database.

## Prerequisites

- GitHub account with this repository pushed
- Render account (https://render.com)
- Supabase account for PostgreSQL (optional - Render offers PostgreSQL too)
- Google OAuth credentials (optional but recommended)

## Step 1: Set Up PostgreSQL Database

### Option A: Supabase (Recommended for free tier)

1. Go to https://supabase.com and create an account
2. Create a new project
3. Copy the PostgreSQL connection string:
   - Go to Project Settings → Database
   - Look for "Connection string" (PostgreSQL)
   - Copy the full URL (should look like: `postgresql://user:password@host:5432/dbname`)
4. Keep this safe - you'll need it in Render environment variables

### Option B: Render PostgreSQL

1. In your Render dashboard, create a new PostgreSQL database
2. Note the internal database URL
3. You'll get the connection string after creation

## Step 2: Deploy on Render

1. **Connect GitHub Repository:**
   - Go to https://dashboard.render.com
   - Click "New +" and select "Web Service"
   - Select "Build and deploy from a Git repository"
   - Connect your GitHub account and select the `groovy-tictactoe` repository

2. **Configure Build Settings:**
   - **Name:** groovy-tictactoe (or your preferred name)
   - **Environment:** Python 3
   - **Build Command:** (Leave as default - render.yaml specifies it)
   - **Start Command:** (Leave as default - render.yaml specifies it)
   - **Instance Type:** Free (or Starter for production)

3. **Set Environment Variables:**
   Click "Environment" and add these variables:

   ```
   DEBUG=False
   SECRET_KEY=<generate-a-random-secure-key>
   ALLOWED_HOSTS=<your-app-name>.onrender.com
   DATABASE_URL=<your-postgres-connection-string-from-above>
   GOOGLE_CLIENT_ID=<your-google-oauth-client-id>
   GOOGLE_CLIENT_SECRET=<your-google-oauth-client-secret>
   ```

   **To generate SECRET_KEY:**
   - Python: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
   - Or use: https://miniwebtool.com/django-secret-key-generator/

4. **Deploy:**
   - Click "Create Web Service"
   - Render will automatically deploy when you push to GitHub

## Step 3: Post-Deployment Setup

After deployment succeeds:

1. **Create Superuser:**
   - Go to your Render service dashboard
   - Click "Shell" tab
   - Run:
     ```bash
     python manage.py migrate --noinput
     python manage.py createsuperuser
     ```
   - Follow prompts to create admin account

2. **Verify Deployment:**
   - Visit `https://<your-app-name>.onrender.com`
   - Login page should load
   - Try registering a new account
   - Visit `/admin/dashboard/` with your superuser account

3. **Google OAuth Setup (if configured):**
   - Go to https://console.cloud.google.com
   - Add authorized redirect URIs:
     - `https://<your-app-name>.onrender.com/auth/google/callback/`

## Step 4: Enable Auto-Deploy on GitHub Push

- Render automatically deploys when you push to your main branch
- You can change this in your service's "Settings" → "Auto Deploy"

## Troubleshooting

### Database Connection Errors
- Verify DATABASE_URL is correct (from Supabase or Render)
- Check that firewall allows connections (Supabase: check IP allowlist)
- Ensure `?sslmode=require` is in the connection string

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput` in Render Shell
- Check that STATIC_ROOT and STATIC_URL are correct

### Build Failures
- Check build logs in Render dashboard
- Common issues:
  - Missing dependencies: Update `requirements.txt`
  - Python version: Ensure Python 3.10+ is used
  - Environment variables: Verify all required vars are set

### App Crashes
- Check logs in Render: Service dashboard → "Logs" tab
- Common issues:
  - `DEBUG=False` without proper ALLOWED_HOSTS
  - Database not initialized (run migrations in Shell)
  - Missing environment variables

## Production Checklist

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` is random and secure
- [ ] `ALLOWED_HOSTS` includes your Render domain
- [ ] `DATABASE_URL` points to production PostgreSQL
- [ ] Superuser account created
- [ ] Google OAuth configured (if enabled)
- [ ] HTTPS enabled (Render provides free SSL)
- [ ] Backups configured (if using Supabase, enable backups)

## Monitoring

- **Logs:** Check "Logs" tab in Render service dashboard
- **Metrics:** View CPU, memory usage in service dashboard
- **Errors:** Set up error tracking (optional, integrates with Sentry)

## Helpful Links

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Supabase: https://supabase.com/docs
- PostgreSQL: https://www.postgresql.org/docs/

---

**Last Updated:** May 14, 2026
**For Issues:** Check Render logs and Django error pages for details
