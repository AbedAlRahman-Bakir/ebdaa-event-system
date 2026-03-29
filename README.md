# Ebdaa Event Attendance & Registration System

Multi-role event attendance and registration system with QR-based check-in, visitor slot booking, and real-time dashboard.

## Features

- **Participant & Judge Management** — CRUD, bulk import (CSV/Excel), badge generation (PDF with QR)
- **QR-Based Attendance** — Camera scanner, duplicate prevention, daily tracking (Day 1–6)
- **Visitor Registration** — Public form with time slot booking and capacity control
- **Real-Time Dashboard** — Stats, attendance charts, slot utilization, auto-refresh
- **Role-Based Access** — Admin (full access), Operator (scan only), Visitor (public registration)
- **JWT Authentication** — Token-based auth with blacklist support

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, SQLAlchemy, Flask-JWT-Extended, Marshmallow |
| Frontend | Jinja2, Bootstrap 5, Chart.js |
| Database | PostgreSQL (prod), SQLite (dev/test) |
| QR System | UUID-based signed encoding |
| Testing | Pytest (47 tests) |
| CI | GitHub Actions (Ruff, Black, Pytest) |

## Project Structure

```
ebdaa-event-system/
├── app/
│   ├── __init__.py          # App factory
│   ├── extensions.py        # Flask extensions
│   ├── commands.py          # CLI commands (seed-admin, seed-slots)
│   ├── decorators.py        # Role-based access decorators
│   ├── errors.py            # Global error handlers
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Marshmallow schemas
│   ├── routes/              # API + page blueprints
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, JS
├── tests/                   # Pytest test suite
├── migrations/              # Alembic migrations
├── config.py                # Environment configs
├── run.py                   # App entry point
├── Dockerfile               # Container build
├── pyproject.toml           # Ruff, Black, Pytest config
└── requirements.txt         # Python dependencies
```

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (for production)

### Installation

```bash
git clone https://github.com/<your-username>/ebdaa-event-system.git
cd ebdaa-event-system
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration

Create a `.env` file:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ACCESS_TOKEN_EXPIRES=3600
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
QR_SECRET=your-qr-secret
DATABASE_TEST_URI=sqlite:///:memory:
DATABASE_PROD_URI=postgresql://user:password@host:5432/dbname
```

### Database Setup

```bash
flask db upgrade
flask seed-admin
flask seed-slots
```

### Run

```bash
python run.py
```

App runs at `http://localhost:5000`

## Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Operator | operator | operator123 |

## API Endpoints

### Auth
- `POST /auth/login` — Login
- `POST /auth/logout` — Logout
- `GET /auth/me` — Current user

### Users (Admin)
- `GET /users` — List users (filters: role, search, pagination)
- `GET /users/<id>` — Get user
- `POST /users` — Create user
- `PUT /users/<id>` — Update user
- `DELETE /users/<id>` — Delete user
- `POST /users/import?role=student|judge` — Bulk import
- `GET /users/<id>/badge` — Download badge PDF
- `GET /users/badges?role=student|judge` — Download all badges
- `GET /users/export?role=student|judge` — Export contacts CSV

### Attendance
- `POST /attendance/checkin` — QR scan check-in
- `GET /attendance` — List logs (filters: day, role, user_id)

### Visitors (Public)
- `GET /visitors/slots` — Available time slots
- `POST /visitors/register` — Register visitor
- `GET /visitors` — List visitors (Admin)

### Dashboard (Admin)
- `GET /dashboard/stats` — Overview stats
- `GET /dashboard/attendance` — Attendance rates + heatmap
- `GET /dashboard/slots` — Slot utilization
- `GET /dashboard/checkins?day=N` — Real-time counter

## Testing

```bash
pytest tests/ -v
```

## Quality Gates

```bash
ruff check app/ tests/
black --check app/ tests/
```

## Docker

```bash
docker build -t ebdaa .
docker run -p 5000:5000 --env-file .env ebdaa
```
