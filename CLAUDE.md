# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run tests
pytest -v

# Run a single test
pytest tests/auth/test_routes.py::test_login_with_valid_credentials -v

# Run domain tests
pytest tests/auth/ -v
pytest tests/codes/ -v

# Run the app
flask run

# Database migrations
flask db migrate -m "Description"
flask db upgrade

# Create a user (prompts for password)
flask create-user <username>
```

## Architecture

Flask application using the app factory pattern with domain-based organization.

**Extensions** (`app/extensions.py`): Shared Flask extensions (SQLAlchemy, Flask-Login, Flask-Migrate) initialized here to avoid circular imports.

**App Factory** (`app/__init__.py`): Creates the Flask app, initializes extensions, and registers domain blueprints. The `create_app(config_name)` function accepts "development", "testing", or "production".

**Domains**: Each domain has its own models, routes, and templates:

- `app/auth/` - Authentication domain
  - `models.py` - User model with password hashing
  - `routes.py` - Login/logout routes (`/auth/login`, `/auth/logout`)

- `app/codes/` - Discount codes domain
  - `models.py` - DiscountCode model
  - `routes.py` - CRUD routes (`/`, `/codes/add`)

**Templates**: Organized by domain in `app/templates/`:
- `base.html` - Shared layout
- `auth/` - Auth templates
- `codes/` - Codes templates with `partials/` for HTMX responses

**Testing**: Tests mirror the domain structure in `tests/auth/` and `tests/codes/`. Shared fixtures in `tests/conftest.py`.

## Style
- Use type hints
- Follow PEP 8
- Include docstrings for functions
- Keep it minimal and clean
- Mobile-first frontend design

## Workflow
- Be sure to typecheck when you're done making a series of code changes
- Prefer running single tests, and not the whole test suite, for performance
- Always run tests at the end of the flow: they must pass
- Update the README.md file for any relevant changes.
