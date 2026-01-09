# Discount Code Manager

> **Learning Project**: Built to explore Agentic Development and experiment with [Claude Code](https://claude.ai/code).

A Flask web application for managing discount codes.

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
├── static/
│   └── css/
│       └── style.css    # Custom CSS
└── templates/
    ├── base.html        # Base template
    ├── auth/
    │   └── login.html   # Login page
    └── codes/
        ├── index.html   # Codes list
        ├── add.html     # Add code form
        ├── edit.html    # Edit code form
        └── partials/    # HTMX partials
            ├── add_success.html
            └── edit_success.html

tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── auth/                # Auth domain tests
│   ├── __init__.py
│   ├── test_models.py
│   └── test_routes.py
└── codes/               # Codes domain tests
    ├── __init__.py
    ├── test_models.py
    └── test_routes.py

migrations/              # Flask-Migrate migrations
└── versions/
```
