#!/bin/bash
#
# Deployment script for discount-codes application
#
# Required environment variables:
#   REPO_DIR   - Path to the git repository (e.g., ~/discount-codes)
#   DEPLOY_DIR - Path to the deployment directory served by nginx (e.g., /var/www/discount-codes)
#   PID_FILE   - Path to the gunicorn PID file (e.g., /tmp/discount-code-gunicorn.pid)
#
# Usage: ./scripts/deploy.sh
#

set -e  # Exit immediately on error

# Validate required environment variables
if [[ -z "$REPO_DIR" ]]; then
    echo "Error: REPO_DIR environment variable is not set"
    exit 1
fi

if [[ -z "$DEPLOY_DIR" ]]; then
    echo "Error: DEPLOY_DIR environment variable is not set"
    exit 1
fi

if [[ -z "$PID_FILE" ]]; then
    echo "Error: PID_FILE environment variable is not set"
    exit 1
fi

echo "==> Pulling latest changes..."
cd "$REPO_DIR"
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
    "$REPO_DIR/" "$DEPLOY_DIR/"

echo "==> Activating virtual environment..."
cd "$DEPLOY_DIR"

# Create venv if it doesn't exist
if [[ ! -d "venv" ]]; then
    echo "==> Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

echo "==> Installing dependencies..."
pip install -r requirements.txt --quiet

echo "==> Running database migrations..."
flask db upgrade

echo "==> Restarting gunicorn..."
if [[ -f "$PID_FILE" ]]; then
    kill -TERM "$(cat "$PID_FILE")"
    echo "    Sent SIGTERM to gunicorn (systemd will restart it)"
else
    echo "    Warning: PID file not found at $PID_FILE"
fi

echo "==> Deployment complete!"
