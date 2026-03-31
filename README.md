# 💰 Expense Tracking PWA

A progressive web application for tracking personal expenses — installable on any device, with offline support via a service worker.

## Features

- **PWA** — Installable on mobile and desktop, works offline
- **User Authentication** — Register and log in with JWT-based auth
- **Expense Tracking** — Add and categorize expenses quickly
- **Dashboard & Analytics** — View spending summaries across multiple time periods (this month, last month, year-to-date, year-over-year)
- **Offline Mode** — Service worker caches assets for offline use

## Tech Stack

| Layer     | Technology       |
|-----------|-----------------|
| Backend   | Python / Flask   |
| Frontend  | HTML, CSS, JavaScript |
| Database  | SQLite           |
| Auth      | JWT (PyJWT)      |
| PWA       | Service Worker, Web App Manifest |

## Getting Started

### Prerequisites

- Python 3.8+

### Installation

```bash
# Clone the repo
git clone https://github.com/caroo21/expense-tracking-pwa.git
cd expense-tracking-pwa

# Create a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

The app will be available at `http://localhost:5000`.

### Environment Variables (recommended)

Create a `.env` file in the root directory:

```
SECRET_KEY=your-secret-key-here
```

## Project Structure

```
expense-tracking-pwa/
├── app.py                 # Flask application & API routes
├── auth.py                # JWT authentication helpers
├── database.py            # Database connection setup
├── db__init__.py          # Database initialization
├── models/                # Data models
│   ├── expense_model.py   # Expense CRUD operations
│   ├── analytics_model.py # Dashboard analytics queries
│   └── user_model.py      # User registration & login
├── static/                # Frontend assets (HTML, CSS, JS)
│   ├── index.html
│   ├── manifest.json
│   ├── service-worker.js
│   └── ...
├── requirements.txt
└── .gitignore
```

## API Endpoints

| Method | Endpoint              | Auth | Description                    |
|--------|-----------------------|------|--------------------------------|
| POST   | `/api/auth/register`  | ❌   | Register a new user            |
| POST   | `/api/auth/login`     | ❌   | Log in and receive JWT token   |
| GET    | `/api/auth/me`        | ✅   | Get current user info          |
| POST   | `/api`                | ✅   | Add a new expense              |
| GET    | `/api/dashboard`      | ✅   | Get dashboard analytics data   |