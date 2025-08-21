#!/bin/bash
# Railway start script for spam detector

# Download NLTK data if not present
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"

# Start the application
python -m gunicorn app_production:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --preload
