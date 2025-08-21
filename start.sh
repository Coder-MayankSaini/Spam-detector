#!/bin/bash
# Railway start script for spam detector

# Ensure we have the latest pip and setuptools
python -m pip install --upgrade pip setuptools wheel || echo "Failed to upgrade pip"

# Download NLTK data if not present
python -c "
import nltk
import os
try:
    nltk.data.path.append('/tmp/nltk_data')
    os.makedirs('/tmp/nltk_data', exist_ok=True)
    nltk.download('punkt', download_dir='/tmp/nltk_data', quiet=True)
    nltk.download('stopwords', download_dir='/tmp/nltk_data', quiet=True)
    nltk.download('wordnet', download_dir='/tmp/nltk_data', quiet=True)
    print('NLTK data downloaded successfully')
except Exception as e:
    print(f'NLTK download warning: {e}')
" || echo "NLTK download failed, continuing anyway"

# Start the application with gunicorn
exec gunicorn app_production:app --bind 0.0.0.0:$PORT --workers 2 --timeout 60 --preload
