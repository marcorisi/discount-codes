# Discount Code Manager

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
├── models.py            # SQLAlchemy models
├── routes.py            # Blueprint with routes
├── config.py            # Configuration
├── static/
│   └── css/
│       └── style.css    # Custom CSS
└── templates/
    ├── base.html        # Base template
    └── index.html       # Homepage

tests/
├── __init__.py
├── conftest.py          # Pytest fixtures
├── test_models.py       # Model tests
└── test_routes.py       # Route tests
```
