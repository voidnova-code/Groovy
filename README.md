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

## Deployment (Render)

### 1. Setup PostgreSQL on Render
- Create a PostgreSQL database on Render
- Copy the Internal Database URL

### 2. Deploy

```bash
# Push to GitHub (make sure to include these files)
git add .
git commit -m "Ready for deployment"
git push origin main
```

### 3. Configure Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Add Environment Variables:
   - `SECRET_KEY` = (generate a secure random key)
   - `DEBUG` = False
   - `ALLOWED_HOSTS` = your-app.onrender.com
   - `DATABASE_URL` = (paste PostgreSQL URL)

4. Build Command:
   ```
   pip install -r requirements.txt && python manage.py migrate --noinput
   ```

5. Start Command:
   ```
   gunicorn tictactoe.wsgi:application --worker-class=gthread --workers=2 --bind=0.0.0.0:$PORT
   ```

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