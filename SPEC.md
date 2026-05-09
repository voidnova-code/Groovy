# Tic Tac Toe Online - Specification Document

## 1. Project Overview

**Project Name:** Tic Tac Toe Online
**Type:** Multiplayer Web Game with Real-time Updates
**Core Functionality:** A Tic Tac Toe game where users can register, create/join game rooms via room codes, and play against friends online.
**Target Users:** Casual gamers who want quick matches with friends.

---

## 2. Technology Stack

- **Backend:** Django 5.x + Django REST Framework
- **Database:** SQLite (for simplicity)
- **Authentication:** JWT (using djangorestframework-simplejwt)
- **Frontend:** Vanilla HTML/CSS/JS (single page application)
- **Real-time:** Polling-based updates (5-second intervals for simplicity)

---

## 3. Feature List

### Authentication
- User registration with username/email/password
- User login with JWT token authentication
- User logout (token blacklisting optional - simplified)

### Game Rooms
- Create a new game room (generates unique 6-character room code)
- Join an existing room using room code
- View list of active rooms (optional - can be discoverable)
- Room auto-expires after 1 hour of inactivity

### Game Logic
- Standard 3x3 Tic Tac Toe rules
- First player is X, second player is O
- Win detection (rows, columns, diagonals)
- Draw detection (board full, no winner)
- No move after game ends

### Gameplay Flow
- Host creates room → waits for opponent
- Opponent joins with room code → game starts
- Players take turns
- Game result displayed (win/draw)
- Option to play again or return to menu

---

## 4. API Endpoints

### Auth Endpoints
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/logout/` - Logout (discard token)

### Game Endpoints
- `POST /api/games/rooms/` - Create a new room
- `GET /api/games/rooms/` - List available rooms
- `GET /api/games/rooms/{code}/` - Get room details
- `POST /api/games/rooms/{code}/join/` - Join a room
- `POST /api/games/move/` - Make a move
- `GET /api/games/my-games/` - Get user's active games

---

## 5. Data Models

### User (Django default + extended)
- username, email, password
- created_at timestamp

### GameRoom
- code (6-char unique identifier)
- player_x (User) - host
- player_o (User) - joiner (nullable)
- status: waiting | playing | finished
- winner (nullable, User reference)
- is_draw (boolean)
- created_at, updated_at

### GameMove
- room (GameRoom)
- player (User)
- position (0-8, board cell index)
- move_number (1-9)
- created_at

---

## 6. Frontend Pages

1. **Login/Register Page** - Auth forms
2. **Dashboard** - Show active games, create/join options
3. **Game Board** - The actual Tic Tac Toe grid

---

## 7. UI/UX Design

- **Style:** Clean, modern, minimal
- **Color Scheme:**
  - Primary: #2196F3 (Blue)
  - Secondary: #4CAF50 (Green for X)
  - Accent: #F44336 (Red for O)
  - Background: #f5f5f5
  - Board: white with subtle shadows
- **Typography:** System fonts (sans-serif)
- **Layout:** Centered card-based design

---

## 8. Game Board Layout

```
 0 | 1 | 2
-----------
 3 | 4 | 5
-----------
 6 | 7 | 8
```

Position indices: 0-8 mapping to cells

---

## 9. Acceptance Criteria

1. Users can register and login
2. Authenticated users can create game rooms
3. Users can join rooms using room codes
4. Two players can play a complete game
5. Win/draw conditions are correctly detected
6. Game state updates are visible to both players
7. Users can see their game history
8. Room codes are unique and 6 characters
9. Invalid moves are rejected with appropriate error messages