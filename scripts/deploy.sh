#!/bin/bash
#
# Deployment script for discount-codes application
#
# Required environment variables:
#   DISCOUNT_CODES_REPO_DIR   - Path to the git repository (e.g., ~/discount-codes)
#   DISCOUNT_CODES_DEPLOY_DIR - Path to the deployment directory served by nginx (e.g., /var/www/discount-codes)
#   DISCOUNT_CODES_PID_FILE   - Path to the gunicorn PID file (e.g., /tmp/discount-code-gunicorn.pid)
#
# Usage: ./scripts/deploy.sh
#

set -e  # Exit immediately on error

# Validate required environment variables
if [[ -z "$DISCOUNT_CODES_REPO_DIR" ]]; then
    echo "Error: DISCOUNT_CODES_REPO_DIR environment variable is not set"
    exit 1
fi

if [[ -z "$DISCOUNT_CODES_DEPLOY_DIR" ]]; then
    echo "Error: DISCOUNT_CODES_DEPLOY_DIR environment variable is not set"
    exit 1
fi

if [[ -z "$DISCOUNT_CODES_PID_FILE" ]]; then
    echo "Error: DISCOUNT_CODES_PID_FILE environment variable is not set"
    exit 1
fi

echo "==> Pulling latest changes..."
cd "$DISCOUNT_CODES_REPO_DIR"
git pull

echo "==> Syncing files to deployment directory..."
rsync -av --delete \
    --exclude='.git' \
    --exclude='.gitignore' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='instance/' \
    "$DISCOUNT_CODES_REPO_DIR/" "$DISCOUNT_CODES_DEPLOY_DIR/"

echo "==> Activating virtual environment..."
cd "$DISCOUNT_CODES_DEPLOY_DIR"

# Create venv if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo "==> Creating virtual environment..."
    python3 -m venv venv    # Alternative, you could also use virtualenv venv if virtualenv is preferred
fi

source venv/bin/activate

echo "==> Installing dependencies..."
pip install -r requirements.txt --quiet

echo "==> Running database migrations..."
flask db upgrade

echo "==> Restarting gunicorn..."
if [[ -f "$DISCOUNT_CODES_PID_FILE" ]]; then
    kill -TERM "$(cat "$DISCOUNT_CODES_PID_FILE")"
    echo "    Sent SIGTERM to gunicorn (systemd will restart it)"
else
    echo "    Warning: PID file not found at $DISCOUNT_CODES_PID_FILE"
fi

echo "==> Deployment complete!"
