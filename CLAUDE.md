# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests
pytest -v

# Run a single test
pytest tests/test_routes.py::test_login_with_valid_credentials -v

# Run the app
flask run

# Database migrations
flask db migrate -m "Description"
flask db upgrade

# Create a user (prompts for password)
flask create-user <username>
```

## Architecture

Flask application using the app factory pattern with blueprints.

**App Factory** (`app/__init__.py`): Creates the Flask app, initializes extensions (SQLAlchemy, Flask-Login, Flask-Migrate), and registers blueprints. The `create_app(config_name)` function accepts "development", "testing", or "production".

**Blueprints** (`app/routes.py`):
- `main` - Protected routes (homepage requires login)
- `auth` - Authentication routes (`/auth/login`, `/auth/logout`)

**Models** (`app/models.py`):
- `User` - Authentication with password hashing via werkzeug
- `DiscountCode` - Discount code storage

**Authentication**: Flask-Login handles sessions. All routes under `main` blueprint use `@login_required`. Users are created via CLI command, not web registration.

**Frontend**: Jinja2 templates with Tailwind CSS (CDN) and htmx for interactivity. Base template includes nav with logout when authenticated.
The app must be mobile-first.

**Testing**: pytest with fixtures in `tests/conftest.py`. Uses in-memory SQLite. Key fixtures: `db`, `test_user`, `authenticated_client`.

## Style
- Use type hints
- Follow PEP 8
- Include docstrings for functions
- Keep it minimal and clean

## Workflow
- Be sure to typecheck when you’re done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
