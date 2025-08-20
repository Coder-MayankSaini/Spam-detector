# Architecture Documentation

## System Overview

The Spam Detector is a full-stack application designed for real-time email spam classification using machine learning. The system follows a modern architecture with a React TypeScript frontend and Flask backend.

## High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│   React Client  │◄──►│  Flask Backend  │◄──►│   SQLite DB     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
│                 │    │                 │    │                 │
│ • Theme Toggle  │    │ • ML Pipeline  │    │ • Email History │
│ • Real-time UI  │    │ • REST APIs     │    │ • Timestamps    │
│ • Caching       │    │ • Logging       │    │ • Statistics    │
│ • Search/Filter │    │ • Model Mgmt    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Component Details

### Backend Architecture (Flask)

#### Core Components
1. **Flask Application** (`app.py`)
   - RESTful API server
   - CORS enabled for cross-origin requests
   - Environment-based configuration
   - Structured JSON logging

2. **Machine Learning Pipeline**
   - TF-IDF Vectorizer for text feature extraction
   - Multinomial Naive Bayes classifier
   - Pipeline composition using scikit-learn
   - Model persistence with joblib

3. **Database Layer**
   - SQLite3 for lightweight data persistence
   - Automatic email history storage
   - Timestamp tracking
   - Query optimization for history retrieval

4. **Configuration Management**
   - Environment variable based configuration
   - `.env` file support via python-dotenv
   - Development/Production environment separation
   - Configurable thresholds and paths

#### Request Flow
```
Client Request → CORS Middleware → Logging Middleware → Route Handler → ML Pipeline → Database → Response
```

### Frontend Architecture (React)

#### Component Hierarchy
```
App
├── ThemeProvider (Context)
├── Header
│   ├── ThemeToggle
│   └── Navigation
├── Main
│   ├── Analyzer
│   │   ├── TextInput
│   │   ├── AnalyzeButton
│   │   ├── LoadingSpinner
│   │   └── ResultDisplay
│   └── History
│       ├── SearchFilter
│       ├── Pagination
│       ├── HistoryList
│       └── HistoryItem
└── Footer
```

#### State Management
- **Theme State**: React Context API for global theme management
- **Component State**: React hooks (useState, useEffect) for local state
- **Caching**: Client-side caching for API responses
- **Persistence**: localStorage for theme preferences

#### Data Flow
```
User Action → Component State Update → API Call → Cache Update → UI Re-render
```

### Data Models

#### Email Analysis Model
```typescript
interface EmailAnalysis {
  is_spam: boolean;
  confidence: number;
  threshold: number;
  keywords: string[];
  text: string;
  timestamp?: string;
}
```

#### Training Data Model
```typescript
interface TrainingData {
  text: string;
  label: number; // 0 = ham, 1 = spam
}
```

#### API Response Models
```typescript
interface AnalyzeResponse extends EmailAnalysis {}

interface HistoryResponse {
  emails: EmailAnalysis[];
  total: number;
  page: number;
  per_page: number;
}

interface StatsResponse {
  total_analyzed: number;
  spam_count: number;
  ham_count: number;
  spam_ratio: number;
  model_threshold: number;
}

interface RetrainResponse {
  message: string;
  new_samples: number;
  total_samples: number;
  accuracy: number;
  classification_report: object;
}
```

## Security Architecture

### Input Validation
- Request payload validation
- SQL injection prevention through parameterized queries
- Text sanitization for database storage

### CORS Configuration
- Configurable allowed origins
- Secure headers implementation
- Preflight request handling

### Error Handling
- Structured error responses
- Sensitive information filtering
- Graceful degradation

## Scalability Considerations

### Current Limitations
- Single-threaded Flask development server
- SQLite database (single-writer limitation)
- In-memory model loading
- No horizontal scaling support

### Recommended Production Enhancements
1. **Application Server**: Migrate to Gunicorn/uWSGI with multiple workers
2. **Database**: Upgrade to PostgreSQL for concurrent access
3. **Caching**: Implement Redis for model predictions and API responses
4. **Load Balancing**: Add nginx reverse proxy for multiple backend instances
5. **Containerization**: Docker deployment with health checks
6. **Monitoring**: Prometheus metrics and structured logging

## Performance Characteristics

### Backend Performance
- **Cold Start**: ~500ms (model loading)
- **Prediction Latency**: ~50-100ms per email
- **Memory Usage**: ~50MB base + model size
- **Throughput**: ~100 requests/second (single worker)

### Frontend Performance
- **Initial Load**: ~2-3 seconds (React bundle)
- **Time to Interactive**: ~1-2 seconds
- **Bundle Size**: ~500KB gzipped
- **Client-side Caching**: 5-minute TTL for API responses

## Deployment Architecture

### Development Environment
```
localhost:3000 (React Dev Server) → localhost:5000 (Flask Dev Server) → SQLite File
```

### Production Recommendations
```
CDN → nginx → Load Balancer → Flask Apps → PostgreSQL
                                      ↓
                                   Redis Cache
```

## Monitoring and Observability

### Logging Strategy
- **Structured JSON Logs**: All requests and errors
- **Request Timing**: Performance monitoring
- **Error Tracking**: Detailed error context
- **Classification Metrics**: Spam/ham ratios

### Recommended Metrics
- Request rate and latency percentiles
- Model prediction accuracy over time
- Error rates by endpoint
- Database query performance
- Client-side performance metrics

## Configuration Management

### Environment Variables
```bash
# Application Settings
FLASK_ENV=development
DEBUG=true
HOST=127.0.0.1
PORT=5000

# Database Configuration
DATABASE_URL=emails.db

# Model Configuration
MODEL_PATH=spam_model.joblib
DEFAULT_THRESHOLD=0.6
TRAINING_DATA_CSV=training_data.csv

# Logging Configuration
LOG_LEVEL=INFO
```

### Configuration Hierarchy
1. Environment variables (highest priority)
2. .env file
3. Default values in code (lowest priority)

## Future Architecture Evolution

### Microservices Migration
1. **API Gateway**: Centralized routing and authentication
2. **ML Service**: Dedicated prediction service
3. **Data Service**: Database abstraction layer
4. **Analytics Service**: Real-time metrics and monitoring

### Event-Driven Architecture
1. **Message Queue**: Async processing with Redis/RabbitMQ
2. **Event Streaming**: Real-time updates via WebSocket
3. **Batch Processing**: Scheduled model retraining
4. **Notification Service**: Real-time alerts and updates

This architecture provides a solid foundation for the current requirements while maintaining extensibility for future enhancements.
