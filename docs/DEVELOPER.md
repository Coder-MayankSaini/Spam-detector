# Developer Guide

This guide is for developers who want to contribute to or extend the Spam Detector project.

## Table of Contents
1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Backend Development](#backend-development)
5. [Frontend Development](#frontend-development)
6. [Testing](#testing)
7. [Code Style and Standards](#code-style-and-standards)
8. [Contributing Guidelines](#contributing-guidelines)
9. [Debugging](#debugging)
10. [Performance Optimization](#performance-optimization)

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git
- Code editor (VS Code recommended)

### Initial Setup
```bash
# Clone the repository
git clone https://github.com/your-username/Spam-detector.git
cd Spam-detector

# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Copy environment configuration
cp .env.example .env
```

### Development Tools Setup
```bash
# Install recommended VS Code extensions
code --install-extension ms-python.python
code --install-extension ms-python.flake8
code --install-extension ms-python.black-formatter
code --install-extension bradlc.vscode-tailwindcss
code --install-extension ms-vscode.vscode-typescript-next

# Install React development tools
cd frontend-react
npm install
cd ..
```

## Project Structure

```
Spam-detector/
├── .env                          # Environment configuration
├── .gitignore                    # Git ignore rules
├── README.md                     # Main project documentation
├── requirements.txt              # Python dependencies
├── requirements-dev.txt          # Development dependencies
├── .pre-commit-config.yaml      # Pre-commit hooks configuration
│
├── docs/                         # Documentation
│   ├── API.md                   # API documentation
│   ├── ARCHITECTURE.md          # Architecture overview
│   ├── DEPLOYMENT.md            # Deployment guide
│   └── DEVELOPER.md             # This file
│
├── Spam-backend/                 # Flask backend
│   ├── app.py                   # Main Flask application
│   ├── models.py                # Data models
│   ├── utils.py                 # Utility functions
│   ├── config.py                # Configuration management
│   ├── training_data.csv        # Training dataset
│   └── tests/                   # Backend tests
│       ├── __init__.py
│       ├── test_app.py
│       ├── test_models.py
│       └── test_utils.py
│
├── frontend/                     # Static frontend (legacy)
│   ├── index.html
│   ├── styles.css
│   └── script.js
│
├── frontend-react/               # React TypeScript frontend
│   ├── public/                  # Static assets
│   ├── src/                     # Source code
│   │   ├── components/          # React components
│   │   ├── contexts/            # React contexts
│   │   ├── hooks/               # Custom hooks
│   │   ├── types/               # TypeScript type definitions
│   │   ├── utils/               # Utility functions
│   │   └── __tests__/           # Frontend tests
│   ├── package.json
│   └── tsconfig.json
│
├── scripts/                      # Development and deployment scripts
│   ├── setup.py                 # Setup script
│   ├── test.py                  # Test runner
│   ├── lint.py                  # Linting script
│   └── deploy.py                # Deployment script
│
└── .github/                      # GitHub Actions workflows
    └── workflows/
        ├── ci.yml               # Continuous Integration
        ├── cd.yml               # Continuous Deployment
        └── codeql.yml           # Code security analysis
```

## Architecture Overview

### Backend Architecture
- **Flask Application**: RESTful API server with CORS support
- **Machine Learning Pipeline**: TF-IDF + Multinomial Naive Bayes
- **Database Layer**: SQLite3 for development, PostgreSQL for production
- **Configuration Management**: Environment-based configuration with python-dotenv
- **Logging**: Structured JSON logging with request timing

### Frontend Architecture
- **React Application**: Modern React 18 with TypeScript
- **Component Architecture**: Functional components with hooks
- **State Management**: React Context API for global state
- **Styling**: CSS modules with custom properties for theming
- **Build System**: Create React App with TypeScript template

## Backend Development

### Flask Application Structure

#### Main Application (`app.py`)
```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

app = Flask(__name__)
CORS(app)

# Configuration loading
class Config:
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    HOST = os.getenv('HOST', '127.0.0.1')
    PORT = int(os.getenv('PORT', 5000))
    # ... more configuration
```

#### Key Components

1. **Configuration Management**
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key')
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///dev.db')

class ProductionConfig(Config):
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///prod.db')

class TestingConfig(Config):
    TESTING = True
    DATABASE_URL = 'sqlite:///:memory:'
```

2. **Machine Learning Pipeline**
```python
# models.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib
import pandas as pd

class SpamClassifier:
    def __init__(self, model_path=None):
        self.pipeline = None
        self.model_path = model_path
        
    def train(self, training_data):
        """Train the spam classifier"""
        texts = [item['text'] for item in training_data]
        labels = [item['label'] for item in training_data]
        
        self.pipeline = make_pipeline(
            TfidfVectorizer(max_features=1000, stop_words='english'),
            MultinomialNB()
        )
        
        self.pipeline.fit(texts, labels)
        
    def predict(self, text):
        """Predict if text is spam"""
        if not self.pipeline:
            raise ValueError("Model not trained")
            
        probabilities = self.pipeline.predict_proba([text])[0]
        return {
            'is_spam': probabilities[1] > 0.6,
            'confidence': probabilities[1],
            'probabilities': probabilities.tolist()
        }
        
    def save_model(self):
        """Save trained model to disk"""
        if self.model_path:
            joblib.dump(self.pipeline, self.model_path)
            
    def load_model(self):
        """Load trained model from disk"""
        if self.model_path and os.path.exists(self.model_path):
            self.pipeline = joblib.load(self.model_path)
```

3. **Database Operations**
```python
# database.py
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    is_spam BOOLEAN NOT NULL,
                    confidence REAL NOT NULL,
                    keywords TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
    def insert_email(self, email_data: Dict):
        """Insert analyzed email into database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO emails (text, is_spam, confidence, keywords)
                VALUES (?, ?, ?, ?)
            ''', (
                email_data['text'],
                email_data['is_spam'],
                email_data['confidence'],
                ','.join(email_data.get('keywords', []))
            ))
            
    def get_emails(self, page: int = 1, per_page: int = 10, 
                   search: str = None, filter_type: str = 'all') -> Dict:
        """Get paginated email history"""
        offset = (page - 1) * per_page
        
        # Build query conditions
        conditions = []
        params = []
        
        if search:
            conditions.append("text LIKE ?")
            params.append(f"%{search}%")
            
        if filter_type == 'spam':
            conditions.append("is_spam = 1")
        elif filter_type == 'ham':
            conditions.append("is_spam = 0")
            
        where_clause = " AND ".join(conditions) if conditions else ""
        if where_clause:
            where_clause = f"WHERE {where_clause}"
            
        with sqlite3.connect(self.db_path) as conn:
            # Get total count
            count_query = f"SELECT COUNT(*) FROM emails {where_clause}"
            total = conn.execute(count_query, params).fetchone()[0]
            
            # Get paginated results
            query = f'''
                SELECT id, text, is_spam, confidence, keywords, timestamp
                FROM emails {where_clause}
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            '''
            params.extend([per_page, offset])
            
            results = conn.execute(query, params).fetchall()
            
        return {
            'emails': [
                {
                    'id': row[0],
                    'text': row[1],
                    'is_spam': bool(row[2]),
                    'confidence': row[3],
                    'keywords': row[4].split(',') if row[4] else [],
                    'timestamp': row[5]
                }
                for row in results
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }
```

### Adding New API Endpoints

1. **Define the route**:
```python
@app.route('/api/new-endpoint', methods=['POST'])
def new_endpoint():
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'required_field' not in data:
            return jsonify({'error': 'Missing required field'}), 400
            
        # Process request
        result = process_data(data)
        
        # Log the request
        log_structured('INFO', 'new_endpoint_success', 
                      user_data=data, result=result)
        
        return jsonify(result)
        
    except Exception as e:
        log_structured('ERROR', 'new_endpoint_error', error=str(e))
        return jsonify({'error': 'Internal server error'}), 500
```

2. **Add tests**:
```python
# tests/test_new_endpoint.py
import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_new_endpoint_success(client):
    response = client.post('/api/new-endpoint', 
                          json={'required_field': 'test_value'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'result' in data

def test_new_endpoint_missing_field(client):
    response = client.post('/api/new-endpoint', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
```

## Frontend Development

### React Component Development

#### Component Structure
```typescript
// components/ExampleComponent.tsx
import React, { useState, useEffect } from 'react';
import './ExampleComponent.css';

interface ExampleComponentProps {
  title: string;
  onAction: (data: string) => void;
  optional?: boolean;
}

const ExampleComponent: React.FC<ExampleComponentProps> = ({
  title,
  onAction,
  optional = false
}) => {
  const [state, setState] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    // Component initialization logic
  }, []);

  const handleAction = async () => {
    setLoading(true);
    try {
      await onAction(state);
    } catch (error) {
      console.error('Action failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="example-component">
      <h2>{title}</h2>
      {optional && <span>Optional content</span>}
      <button onClick={handleAction} disabled={loading}>
        {loading ? 'Processing...' : 'Action'}
      </button>
    </div>
  );
};

export default ExampleComponent;
```

#### Custom Hooks
```typescript
// hooks/useApi.ts
import { useState, useCallback } from 'react';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T>() {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null
  });

  const execute = useCallback(async (apiCall: () => Promise<T>) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await apiCall();
      setState({ data, loading: false, error: null });
      return data;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState({ data: null, loading: false, error: errorMessage });
      throw error;
    }
  }, []);

  return { ...state, execute };
}
```

#### Context for Global State
```typescript
// contexts/ThemeContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem('theme');
    return (saved as Theme) || 'light';
  });

  useEffect(() => {
    localStorage.setItem('theme', theme);
    document.body.className = theme;
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};
```

### API Integration
```typescript
// utils/api.ts
const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:5000';

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Request failed');
    }

    return response.json();
  }

  async analyzeEmail(emailText: string) {
    return this.request<AnalyzeResponse>('/analyze', {
      method: 'POST',
      body: JSON.stringify({ emailText }),
    });
  }

  async getHistory(params: HistoryParams = {}) {
    const searchParams = new URLSearchParams(params as any);
    return this.request<HistoryResponse>(`/history?${searchParams}`);
  }
}

export const apiClient = new ApiClient();
```

## Testing

### Backend Testing

#### Unit Tests with pytest
```python
# tests/test_models.py
import pytest
from Spam-backend.models import SpamClassifier

class TestSpamClassifier:
    @pytest.fixture
    def classifier(self):
        return SpamClassifier()
    
    @pytest.fixture
    def training_data(self):
        return [
            {'text': 'Free money now!', 'label': 1},
            {'text': 'Meeting tomorrow at 2pm', 'label': 0}
        ]
    
    def test_train_classifier(self, classifier, training_data):
        classifier.train(training_data)
        assert classifier.pipeline is not None
    
    def test_predict_spam(self, classifier, training_data):
        classifier.train(training_data)
        result = classifier.predict('Free lottery winner!')
        assert isinstance(result['is_spam'], bool)
        assert 0 <= result['confidence'] <= 1
    
    def test_predict_without_training(self, classifier):
        with pytest.raises(ValueError):
            classifier.predict('test email')
```

#### Integration Tests
```python
# tests/test_app.py
import pytest
import json
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE_URL'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client

def test_analyze_endpoint(client):
    response = client.post('/analyze', 
                          data=json.dumps({'emailText': 'Test email'}),
                          content_type='application/json')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'is_spam' in data
    assert 'confidence' in data

def test_analyze_empty_text(client):
    response = client.post('/analyze', 
                          data=json.dumps({'emailText': ''}),
                          content_type='application/json')
    assert response.status_code == 400
```

### Frontend Testing

#### Component Tests with Jest and React Testing Library
```typescript
// components/__tests__/ExampleComponent.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ExampleComponent from '../ExampleComponent';

describe('ExampleComponent', () => {
  const mockOnAction = jest.fn();

  beforeEach(() => {
    mockOnAction.mockClear();
  });

  it('renders with title', () => {
    render(<ExampleComponent title="Test Title" onAction={mockOnAction} />);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('calls onAction when button is clicked', async () => {
    render(<ExampleComponent title="Test" onAction={mockOnAction} />);
    
    const button = screen.getByRole('button', { name: /action/i });
    await userEvent.click(button);
    
    await waitFor(() => {
      expect(mockOnAction).toHaveBeenCalledTimes(1);
    });
  });

  it('shows loading state', async () => {
    mockOnAction.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
    
    render(<ExampleComponent title="Test" onAction={mockOnAction} />);
    
    const button = screen.getByRole('button');
    await userEvent.click(button);
    
    expect(screen.getByText('Processing...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.queryByText('Processing...')).not.toBeInTheDocument();
    });
  });
});
```

#### API Mocking
```typescript
// __mocks__/api.ts
export const apiClient = {
  analyzeEmail: jest.fn(),
  getHistory: jest.fn(),
  getStats: jest.fn(),
};

// Test setup
import { apiClient } from '../utils/api';

jest.mock('../utils/api');
const mockedApiClient = apiClient as jest.Mocked<typeof apiClient>;

beforeEach(() => {
  mockedApiClient.analyzeEmail.mockResolvedValue({
    is_spam: false,
    confidence: 0.3,
    threshold: 0.6,
    keywords: ['meeting'],
    text: 'Test email'
  });
});
```

### Running Tests
```bash
# Backend tests
cd Spam-backend
python -m pytest tests/ -v --cov=. --cov-report=html

# Frontend tests
cd frontend-react
npm test -- --coverage --watchAll=false

# E2E tests
npm run test:e2e
```

## Code Style and Standards

### Python Code Style
We follow PEP 8 with some modifications:

```python
# .flake8
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude = .venv, .git, __pycache__

# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  \.venv
  | \.git
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

### TypeScript/React Code Style
```json
// .eslintrc.json
{
  "extends": [
    "react-app",
    "react-app/jest",
    "@typescript-eslint/recommended"
  ],
  "rules": {
    "prefer-const": "error",
    "no-var": "error",
    "@typescript-eslint/no-unused-vars": "error",
    "react/jsx-uses-react": "error",
    "react/jsx-uses-vars": "error"
  }
}

// prettier.config.js
module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 80,
  tabWidth: 2,
};
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/psf/black
    rev: 22.10.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 5.0.4
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.0.0-alpha.4
    hooks:
      - id: prettier
        files: \.(js|jsx|ts|tsx|css|md|json)$
```

## Contributing Guidelines

### Workflow
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make changes and commit**: Follow conventional commit format
4. **Write tests**: Ensure new features are tested
5. **Run tests**: Make sure all tests pass
6. **Update documentation**: Add/update relevant docs
7. **Submit a Pull Request**

### Commit Message Format
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```bash
git commit -m "feat(api): add email classification endpoint"
git commit -m "fix(frontend): resolve theme toggle issue"
git commit -m "docs: update API documentation"
```

### Pull Request Guidelines
- **Title**: Clear, descriptive title
- **Description**: Explain what and why
- **Tests**: Include test results
- **Screenshots**: For UI changes
- **Breaking Changes**: Highlight any breaking changes

## Debugging

### Backend Debugging
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use pdb for debugging
import pdb; pdb.set_trace()

# Flask debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1

# Profiling with cProfile
python -m cProfile -s cumulative app.py
```

### Frontend Debugging
```typescript
// React Developer Tools
console.log('Debug info:', data);

// Performance profiling
console.time('render');
// ... component rendering
console.timeEnd('render');

// Network debugging
fetch('/api/analyze', { ... })
  .then(response => {
    console.log('Response:', response);
    return response.json();
  });
```

### Common Issues and Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| CORS errors | Frontend and backend on different ports | Configure CORS properly |
| Model not found | Missing model file | Train and save model first |
| Database locked | Concurrent SQLite access | Use connection pooling or PostgreSQL |
| TypeScript errors | Type mismatches | Update type definitions |
| Import errors | Missing dependencies | Install required packages |

## Performance Optimization

### Backend Performance
```python
# Caching with Flask-Caching
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/stats')
@cache.cached(timeout=300)  # 5 minutes
def get_stats():
    # Expensive operation
    return jsonify(stats)

# Database optimization
# Use indexes
CREATE INDEX idx_emails_timestamp ON emails(timestamp);
CREATE INDEX idx_emails_is_spam ON emails(is_spam);

# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### Frontend Performance
```typescript
// Code splitting
import { lazy, Suspense } from 'react';

const History = lazy(() => import('./components/History'));

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <History />
    </Suspense>
  );
}

// Memoization
import { memo, useMemo, useCallback } from 'react';

const ExpensiveComponent = memo(({ data }) => {
  const processedData = useMemo(() => {
    return expensiveProcessing(data);
  }, [data]);

  return <div>{processedData}</div>;
});

// Debouncing for search
import { useMemo } from 'react';
import { debounce } from 'lodash';

const debouncedSearch = useMemo(
  () => debounce((query) => {
    // Perform search
  }, 300),
  []
);
```

This developer guide provides comprehensive information for contributing to and extending the Spam Detector project. For additional help, consult the other documentation files or open an issue on GitHub.
