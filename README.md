# GROOVY - [Tic Tac Toe Online](https://github.com/voidnova-code/)

A retro 70s-styled multiplayer Tic Tac Toe game built with Django REST Framework.

![GROOVY Tic Tac Toe](https://via.placeholder.com/600x400/FF6B6B/2C1810?text=GROOVY+Tic+Tac+Toe)

## Features

- 🔐 **User Authentication** - Register, login, JWT-based auth
- 🎮 **Multiplayer** - Create game rooms, share codes with friends
- 🎯 **Real-time Updates** - Polling-based game state sync
- 🏆 **Score Tracking** - Win/draw statistics
- 💕 **Donations** - Razorpay integration
- 📊 **Admin Panel** - Full dashboard with analytics
- 📱 **Responsive Design** - Works on mobile and desktop

## Tech Stack

- **Backend:** Django 5.x + Django REST Framework
- **Database:** PostgreSQL (production) / SQLite (development)
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Deployment:** Render, Gunicorn

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (optional, for production)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/groovy-tictactoe.git
cd groovy-tictactoe

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations
python manage.py migrate

# Create superuser (for admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Visit http://127.0.0.1:8000

### Admin Panel
- Access at http://127.0.0.1:8000/admin/dashboard/
- Login with your superuser credentials

## Deployment (Render + Supabase)

This project is configured to deploy on Render with a Supabase (PostgreSQL) database.

1. Create a new Web Service on Render and connect your GitHub repository.

2. Add the following Environment Variables in the Render dashboard:
   - `SECRET_KEY` = (generate a secure random key)
   - `DEBUG` = False
   - `ALLOWED_HOSTS` = your-app.onrender.com
   - `DATABASE_URL` = (Supabase Postgres connection URL)
   - `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` if you want Google OAuth

3. Build Command (Render):

```
pip install -r requirements.txt
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

4. Start Command (Render / Procfile):

```
gunicorn tictactoe.wsgi:application --worker-class=gthread --workers=2 --bind=0.0.0.0:$PORT
```

Notes:
- The `DATABASE_URL` from Supabase usually looks like `postgres://user:pass@db.host:5432/dbname`.
- For Supabase, ensure your connection allows connections from Render IP ranges or use the Supabase connection string and credentials in the Render env var.
- Do not create a default superuser in your build pipeline — create one manually via the Render shell or use an admin-only management command.
- If you previously experimented with Vercel files, they can be left in the repo; Render will ignore them.

If you'd like, I can add step-by-step Render and Supabase setup instructions and a small management command to safely create an admin user.

## Project Structure

```
groovy-tictactoe/
├── templates/          # HTML templates
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── game.html
│   ├── donate.html
│   └── about.html
│   └── admin/        # Admin templates
├── game/             # Game app
│   ├── models.py     # GameRoom, GameMove
│   ├── views.py     # API views
│   ├── serializers.py
│   ├── urls.py
│   └── admin.py
├── tictactoe/        # Django project
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── pages/            # Page views
├── templates/
├── manage.py
├── requirements.txt
├── Procfile
├── render.yaml
└── .env.example
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | Login |
| `/api/auth/logout/` | POST | Logout |
| `/api/rooms/` | POST | Create room |
| `/api/rooms/` | GET | List rooms |
| `/api/rooms/join/` | POST | Join room |
| `/api/rooms/move/` | POST | Make move |
| `/api/rooms/delete/` | DELETE | Delete room |

## Screenshots

- Login/Register with retro 70s theme
- Game room creation with shareable codes
- Real-time multiplayer gameplay
- Score tracking
- Admin dashboard with analytics
- Donation page with Razorpay

## License

MIT License

## Credits

- Designed and built by [Voidnova](https://github.com/yourusername)
- Inspired by 70s retro aesthetics