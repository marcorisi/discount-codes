```
This is a Learning Project 🧪👨‍🔬🎢

Built to explore Agentic Development 
and experiment with Claude Code.
```

# Discount Code Manager

A Flask web application for managing and sharing discount codes.  
Keep track of your promotional codes, coupons, and discounts in one place.  
Features include:
- **User authentication** - Secure login with password hashing
- **Discount code management** - Store codes with details like store name, discount value, expiry date, and notes
- **Expiration tracking** - Visual indicators for expired and used codes
- **Shareable links** - Generate temporary links to share codes with others (auto-expire after 24 hours)
- **Multi-user support** - Each user manages their own codes with filtering options

## Tech Stack

- Python 3.11+
- Flask with blueprints
- SQLite with SQLAlchemy ORM
- htmx for frontend interactivity
- Tailwind CSS via CDN

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

### 4. Initialize Database

```python
from app import create_app, init_db
app = create_app()
init_db(app)
```

## Database Migrations

This project uses Flask-Migrate (Alembic) for database migrations. Migrations are **not** run automatically on app startup - you must apply them manually.

### Apply pending migrations

```bash
flask db upgrade
```

### Create a new migration after model changes

```bash
flask db migrate -m "Description of changes"
flask db upgrade
```

> **Note:** `migrate.init_app()` in the app factory only registers the `flask db` CLI commands - it does not auto-run migrations. This is intentional to prevent data loss and race conditions in production.

## Running the Application

```bash
flask run
```

Or:

```bash
python run.py
```

Visit http://localhost:5000

## Running Tests

```bash
pytest
```

With verbose output:

```bash
pytest -v
```

## Project Structure

```
app/
├── __init__.py          # Flask app factory
├── config.py            # Configuration
├── extensions.py        # Shared Flask extensions
├── auth/                # Authentication domain
│   ├── __init__.py
│   ├── models.py        # User model
│   └── routes.py        # Login/logout routes
├── codes/               # Discount codes domain
│   ├── __init__.py
│   ├── models.py        # DiscountCode model
│   └── routes.py        # CRUD routes
├── shares/              # Code sharing domain
│   ├── __init__.py
│   ├── models.py        # Share model
│   └── routes.py        # Share routes
├── static/
│   └── css/
│       └── style.css    # Custom CSS
└── templates/
    ├── base.html        # Base template
    ├── auth/
    │   └── login.html   # Login page
    ├── codes/
    │   ├── index.html   # Codes list
    │   ├── add.html     # Add code form
    │   ├── edit.html    # Edit code form
    │   └── partials/    # HTMX partials
    │       ├── add_success.html
    │       └── edit_success.html
    └── shares/
        ├── view.html    # Shared code view
        └── expired.html # Expired share page

tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── auth/                # Auth domain tests
│   ├── __init__.py
│   ├── test_models.py
│   └── test_routes.py
├── codes/               # Codes domain tests
│   ├── __init__.py
│   ├── test_models.py
│   └── test_routes.py
└── shares/              # Shares domain tests
    ├── __init__.py
    ├── test_models.py
    └── test_routes.py

migrations/              # Flask-Migrate migrations
└── versions/
```
