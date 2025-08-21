#!/bin/bash
# Ultra-minimal Railway start script

echo "Starting Ultra-Minimal Spam Detector..."
echo "Working directory: $(pwd)"

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export FLASK_APP=app_minimal.py
export FLASK_ENV=production

# Start the application with gunicorn
echo "Starting gunicorn server..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 30 app_minimal:app
