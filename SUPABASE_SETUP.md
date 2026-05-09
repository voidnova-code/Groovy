# 🚀 Supabase + Vercel Setup Guide

## What is Supabase?

Supabase is an open-source Firebase alternative that provides:
- ✅ **PostgreSQL Database** - Fully managed, production-ready
- ✅ **Free Tier** - 500MB storage, plenty for most projects
- ✅ **Auth System** - User management (we use JWT instead)
- ✅ **Real-time Features** - Websockets support
- ✅ **Automatic Backups** - Daily backups included
- ✅ **REST API** - Auto-generated (not needed, we use Django)

Perfect for: **Vercel + Django** combination

---

## Step 1: Create Supabase Account

### 1. Sign Up
1. Go to [Supabase.com](https://supabase.com)
2. Click **"Sign Up"**
3. Choose **GitHub** as sign-up method (fastest)
4. Authorize Supabase access

### 2. Create First Project
1. Click **"New Project"**
2. Choose organization (create one if needed)
3. Enter project name: **`groovy-tictactoe`**
4. Enter database password (save this!)
5. Select region closest to you (or us-east-1 for US)
6. Click **"Create new project"**

> ⏳ **Wait**: Project creation takes 1-2 minutes

---

## Step 2: Get Database Connection String

### 1. Navigate to Settings
1. In Supabase dashboard, click **Settings** (gear icon)
2. Go to **Database** section
3. Look for **Connection String**

### 2. Copy Connection String
You'll see:
```
postgresql://postgres:[YOUR-PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
```

**Important**: 
- ✅ This is your full connection string
- ✅ Includes password
- ✅ **KEEP SECURE** - Don't share publicly
- ✅ Copy the entire string

### 3. Alternative: URI Format
If needed in URI format:
```
postgres://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
```

---

## Step 3: Configure Vercel Environment Variables

### 1. Go to Vercel Dashboard
1. Visit https://vercel.com/dashboard
2. Select your project: **groovy-tictactoe**
3. Go to **Settings** → **Environment Variables**

### 2. Add DATABASE_URL
1. Click **"Add New"**
2. Name: **`DATABASE_URL`**
3. Value: Paste your Supabase connection string
4. Check **Production, Preview, Development**
5. Click **Save**

### 3. Add Other Variables
Add these too:

| Name | Value |
|------|-------|
| `SECRET_KEY` | `<generate: python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `yourapp.vercel.app,localhost` |
| `GOOGLE_CLIENT_ID` | Your Google OAuth ID |
| `GOOGLE_CLIENT_SECRET` | Your Google OAuth secret |

### 4. Redeploy
1. Go to **Deployments**
2. Click the latest deployment
3. Click **"Redeploy"** button
4. Wait for build to complete

---

## Step 4: Run Database Migrations

After Vercel deployment succeeds, initialize your database:

### Option A: Using Supabase CLI (Easiest)
```bash
# Install Supabase CLI
npm install -g @supabase/cli

# Link to your project
supabase link --project-ref YOUR_PROJECT_ID

# Run migrations
supabase db push
```

### Option B: Using Django Locally
```bash
# Set your local environment variable
export DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres"

# Or on Windows (PowerShell):
$env:DATABASE_URL="postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres"

# Run migrations
python manage.py migrate --noinput

# Create superuser
python manage.py createsuperuser --username admin --email admin@example.com
```

### Option C: Via Supabase SQL Editor (Manual)
1. In Supabase dashboard, go to **SQL Editor**
2. Copy the output of: `python manage.py sqlmigrate game 0001`
3. Paste in SQL editor and run
4. Repeat for other migrations

---

## Step 5: Verify Connection

### Test from Command Line
```bash
# Install psql if not already
# macOS: brew install postgresql
# Windows: Use Docker or PostgreSQL installer

# Test connection
psql postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres -c "SELECT version();"

# Should show PostgreSQL version
```

### Test from Django
```bash
# Verify Vercel deployment can reach database
# Check Vercel deployment logs:
# 1. Vercel Dashboard → Deployments → Latest → Logs
# 2. Look for "System check" and migration messages
```

### Test API Endpoint
```bash
# After deployment
curl https://yourapp.vercel.app/api/auth/google/config/

# Should return:
# {"client_id": "...", "auth_uri": "...", "scopes": [...]}
```

---

## Step 6: Supabase Dashboard Overview

### Key Sections
| Section | Use For |
|---------|---------|
| **SQL Editor** | Write direct SQL queries |
| **Table Editor** | Browse/edit database tables |
| **Auth** | User management (we don't use) |
| **Storage** | File uploads (optional) |
| **Realtime** | Live updates (optional) |
| **Database** | Connection strings, backups |

### Monitor Your Database
1. Click **Database** → **Connection Pool**
2. See active connections
3. Monitor usage in **Statistics** tab

---

## Connection String Formats

### Standard PostgreSQL (Most Compatible)
```
postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
```

### Without Password in String (Safer)
```
# In .env, set separately:
DB_HOST=db.PROJECT_ID.supabase.co
DB_USER=postgres
DB_PASSWORD=YOUR_PASSWORD
DB_PORT=5432
DB_NAME=postgres

# Then in settings.py:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

### Connection String with SSL (Production)
```
postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:6543/postgres?sslmode=require
```

---

## Supabase Features You Get Free

### Storage & Backups
- ✅ 500MB database storage
- ✅ Unlimited API calls
- ✅ Daily backups
- ✅ Point-in-time recovery
- ✅ 7-day backup history

### Performance
- ✅ Connection pooling
- ✅ Auto-scaling (within free tier)
- ✅ 99.9% uptime SLA
- ✅ Global edge functions (Pro feature)

### Security
- ✅ Automatic SSL/TLS
- ✅ Regular security updates
- ✅ DDoS protection
- ✅ Encryption at rest

---

## Troubleshooting

### Issue: "Connection refused"
```
Cause: Firewall blocking connection
Solution: 
1. Check Supabase project status (green = active)
2. Verify password is correct
3. Try from different network
4. Check IP whitelist (if enabled)
```

### Issue: "Database does not exist"
```
Cause: Wrong database name
Solution:
1. Default database name is "postgres"
2. Check connection string last part
3. Should be: ...5432/postgres
```

### Issue: "Password authentication failed"
```
Cause: Wrong password in connection string
Solution:
1. Go to Supabase Settings → Database
2. Look for "Connection String"
3. Copy full string again
4. Verify no typos
```

### Issue: "Timeout connecting to database"
```
Cause: Vercel serverless can't reach Supabase
Solution:
1. Verify DATABASE_URL is set in Vercel
2. Check Supabase project is active
3. Ensure correct region selected
4. Add ?sslmode=require to connection string
```

---

## Performance Tips

### 1. Connection Pooling
Supabase automatically pools connections. Set in Django:
```python
# settings.py
DATABASES['default']['CONN_MAX_AGE'] = 0  # For serverless
```

### 2. Query Optimization
```python
# Good: Single query
users = User.objects.filter(is_active=True).select_related('profile')

# Bad: Multiple queries (N+1 problem)
for user in User.objects.all():
    print(user.profile.name)  # Extra query per user!
```

### 3. Indexes
Supabase shows slow queries in dashboard. Create indexes:
```sql
CREATE INDEX idx_user_email ON auth_user(email);
```

### 4. Connection Pool Size
Default: 10 connections (perfect for most uses)
Adjust in Supabase → Settings → Database if needed

---

## Backups & Recovery

### Automatic Backups
- ✅ Daily automatic backups
- ✅ Keep for 7 days
- ✅ Point-in-time recovery available

### Manual Backup (Recommended)
```bash
# Export database
pg_dump postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres > backup.sql

# Restore (if needed)
psql postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres < backup.sql
```

### In Supabase Dashboard
1. Click **Settings** → **Backups**
2. See all available backups
3. Click **"Restore"** to restore any backup

---

## Scaling from Free to Paid (When Needed)

### When to Upgrade
- Database > 500MB
- More than 5 concurrent connections
- Need for production SLA
- Want edge functions

### Upgrade Process
1. Click **Settings** → **Billing**
2. Choose plan
3. Add payment method
4. Instant upgrade (no downtime)

### Cost Examples
```
Free Tier:        $0/month (500MB, 2 concurrent connections)
Pro:              $25/month (8GB, 10 concurrent connections)
Enterprise:       Custom pricing (unlimited)
```

For most projects, free tier is sufficient!

---

## Security Best Practices

### 1. Secure Connection String
- ✅ Never commit DATABASE_URL to GitHub
- ✅ Use Vercel environment variables (private)
- ✅ Rotate passwords periodically

### 2. Database Users
- ✅ Default user: `postgres`
- ✅ Change password in Supabase dashboard
- ✅ Consider creating app-specific user (advanced)

### 3. Network Security
- ✅ Supabase handles SSL/TLS automatically
- ✅ Use `?sslmode=require` in connection string
- ✅ Firewall rules available (Pro feature)

### 4. Monitor Access
```sql
-- See recent connections
SELECT datname, usename, client_addr, state, query 
FROM pg_stat_activity;
```

---

## Supabase vs Other Options

| Feature | Supabase | Neon | Railway | AWS RDS |
|---------|----------|------|---------|---------|
| **Free Tier** | 500MB | 3GB | $5 credit | Trial |
| **Setup Time** | 2 min | 2 min | 3 min | 10 min |
| **Ease** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ |
| **Features** | Auth, Storage, Realtime | Simple | Simple | Full control |
| **Recommended For** | This project | Light projects | Hobby | Enterprise |

**For GROOVY Tic Tac Toe: Supabase is perfect!**

---

## Checklist: Supabase Setup Complete

- [ ] Supabase account created
- [ ] Project created: "groovy-tictactoe"
- [ ] Database password saved securely
- [ ] Connection string copied
- [ ] DATABASE_URL set in Vercel
- [ ] Other env vars configured
- [ ] Vercel redeployed
- [ ] Migrations run successfully
- [ ] API endpoints tested
- [ ] Data appears in Supabase dashboard

---

## Next Steps

### Immediate
1. ✅ Create Supabase account
2. ✅ Create project
3. ✅ Copy connection string
4. ✅ Add to Vercel
5. ✅ Redeploy

### After Deployment
1. Run migrations
2. Create superuser
3. Test API endpoints
4. Verify data in Supabase dashboard

### Optional
1. Set up database backups
2. Monitor performance
3. Create custom indexes
4. Add more users and test

---

## Support & Resources

- **Supabase Docs**: https://supabase.com/docs
- **Getting Started**: https://supabase.com/docs/guides/getting-started
- **Django Integration**: https://supabase.com/docs/guides/using-supabase-with-python
- **Connection Issues**: https://supabase.com/docs/guides/database/troubleshooting

---

## Quick Reference

```bash
# Get Supabase CLI
npm install -g @supabase/cli

# Link project
supabase link --project-ref PROJECT_ID

# Run migrations
supabase db push

# Access database
psql postgresql://postgres:PASSWORD@db.PROJECT_ID.supabase.co:5432/postgres
```

---

**Status**: ✅ Supabase is the perfect choice for Vercel + Django
**Setup Time**: ~5-10 minutes
**Difficulty**: ⭐ Very Easy

**Ready to go!** 🚀
