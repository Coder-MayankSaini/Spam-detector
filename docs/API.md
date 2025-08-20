# API Documentation

## Base URL
- **Development**: `http://localhost:5000`
- **Production**: `https://your-domain.com`

## Authentication
Currently, the API does not require authentication. All endpoints are publicly accessible.

## Content Types
- **Request Content-Type**: `application/json`
- **Response Content-Type**: `application/json`

## Error Handling

### Error Response Format
```json
{
  "error": "Error description",
  "status": "error",
  "code": 400
}
```

### HTTP Status Codes
- `200` - OK: Request successful
- `400` - Bad Request: Invalid request data
- `404` - Not Found: Resource not found
- `500` - Internal Server Error: Server-side error

## Endpoints

### 1. Analyze Email

Classify an email as spam or ham using the trained machine learning model.

**Endpoint**: `POST /analyze`

**Request Body**:
```json
{
  "emailText": "Win a free iPhone now! Click here to claim your prize!"
}
```

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| emailText | string | Yes | The email content to analyze |

**Success Response**:
```json
{
  "is_spam": true,
  "confidence": 0.8743,
  "threshold": 0.6,
  "keywords": ["win", "free", "iphone", "click", "claim", "prize"],
  "text": "Win a free iPhone now! Click here to claim your prize!",
  "analysis_timestamp": "2025-08-20T14:30:00Z"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| is_spam | boolean | True if classified as spam, false if ham |
| confidence | float | Model confidence score (0.0 to 1.0) |
| threshold | float | Classification threshold used |
| keywords | array | Important keywords contributing to classification |
| text | string | Original email text analyzed |
| analysis_timestamp | string | ISO timestamp of analysis |
```json
{
  "is_spam": true,
  "confidence": 0.87,
  "threshold": 0.6,
  "keywords": ["win", "free", "iphone", "prize"],
  "text": "Win a free iPhone now! Click here to claim your prize!"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| is_spam | boolean | Whether the email is classified as spam |
| confidence | number | Confidence score (0-1) |
| threshold | number | Classification threshold used |
| keywords | array | Key words that influenced the classification |
| text | string | Original email text |

**Example cURL**:
```bash
curl -X POST http://localhost:5000/analyze \
  -H "Content-Type: application/json" \
  -d '{"emailText": "Limited time offer! Buy now and save 90%!"}'
```

---

### 2. Retrain Model

Update the machine learning model with new training data.

**Endpoint**: `POST /retrain`

**Request Body**:
```json
{
  "training_data": [
    {
      "text": "Congratulations! You've won $1000! Claim now!",
      "label": 1
    },
    {
      "text": "Meeting scheduled for tomorrow at 2 PM",
      "label": 0
    }
  ]
}
```

**Request Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| training_data | array | Yes | Array of training samples |
| training_data[].text | string | Yes | Email text content |
| training_data[].label | integer | Yes | Label (0 = ham, 1 = spam) |

**Response**:
```json
{
  "message": "Model retrained successfully",
  "new_samples": 2,
  "total_samples": 14,
  "accuracy": 0.95,
  "classification_report": {
    "0": {
      "precision": 0.94,
      "recall": 0.96,
      "f1-score": 0.95,
      "support": 7
    },
    "1": {
      "precision": 0.96,
      "recall": 0.94,
      "f1-score": 0.95,
      "support": 7
    },
    "accuracy": 0.95,
    "macro avg": {
      "precision": 0.95,
      "recall": 0.95,
      "f1-score": 0.95,
      "support": 14
    },
    "weighted avg": {
      "precision": 0.95,
      "recall": 0.95,
      "f1-score": 0.95,
      "support": 14
    }
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| message | string | Success message |
| new_samples | integer | Number of new samples added |
| total_samples | integer | Total samples in training set |
| accuracy | number | Model accuracy on training data |
| classification_report | object | Detailed performance metrics |

**Example cURL**:
```bash
curl -X POST http://localhost:5000/retrain \
  -H "Content-Type: application/json" \
  -d '{
    "training_data": [
      {"text": "Free lottery winner!", "label": 1},
      {"text": "Project deadline reminder", "label": 0}
    ]
  }'
```

---

### 3. Get Email History

Retrieve previously analyzed emails with pagination support.

**Endpoint**: `GET /history`

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| page | integer | No | 1 | Page number |
| per_page | integer | No | 10 | Items per page |
| search | string | No | - | Search text in email content |
| filter | string | No | all | Filter by type: 'spam', 'ham', 'all' |

**Response**:
```json
{
  "emails": [
    {
      "id": 1,
      "text": "Limited time offer!",
      "is_spam": true,
      "confidence": 0.89,
      "keywords": ["limited", "time", "offer"],
      "timestamp": "2025-08-20T10:30:00"
    },
    {
      "id": 2,
      "text": "Meeting reminder for tomorrow",
      "is_spam": false,
      "confidence": 0.15,
      "keywords": ["meeting", "reminder"],
      "timestamp": "2025-08-20T10:25:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 25,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| emails | array | List of analyzed emails |
| emails[].id | integer | Unique email ID |
| emails[].text | string | Email content |
| emails[].is_spam | boolean | Spam classification result |
| emails[].confidence | number | Classification confidence |
| emails[].keywords | array | Extracted keywords |
| emails[].timestamp | string | Analysis timestamp (ISO 8601) |
| pagination | object | Pagination metadata |
| pagination.page | integer | Current page number |
| pagination.per_page | integer | Items per page |
| pagination.total | integer | Total number of emails |
| pagination.pages | integer | Total number of pages |
| pagination.has_next | boolean | Whether next page exists |
| pagination.has_prev | boolean | Whether previous page exists |

**Example cURL**:
```bash
# Get first page
curl "http://localhost:5000/history"

# Get second page with 5 items per page
curl "http://localhost:5000/history?page=2&per_page=5"

# Search for specific content
curl "http://localhost:5000/history?search=meeting"

# Filter only spam emails
curl "http://localhost:5000/history?filter=spam"
```

---

### 4. Get Statistics

Retrieve overall system and model statistics.

**Endpoint**: `GET /stats`

**Response**:
```json
{
  "total_analyzed": 125,
  "spam_count": 67,
  "ham_count": 58,
  "spam_ratio": 0.536,
  "model_threshold": 0.6,
  "model_info": {
    "algorithm": "MultinomialNB",
    "vectorizer": "TfidfVectorizer",
    "features": 1000,
    "training_samples": 12
  },
  "performance_metrics": {
    "accuracy": 0.95,
    "precision": 0.94,
    "recall": 0.96,
    "f1_score": 0.95
  },
  "recent_activity": {
    "last_analysis": "2025-08-20T15:30:00",
    "analyses_today": 23,
    "analyses_this_week": 89
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| total_analyzed | integer | Total emails analyzed |
| spam_count | integer | Number of spam emails detected |
| ham_count | integer | Number of ham emails detected |
| spam_ratio | number | Ratio of spam to total emails |
| model_threshold | number | Current classification threshold |
| model_info | object | Information about the ML model |
| model_info.algorithm | string | ML algorithm used |
| model_info.vectorizer | string | Text vectorizer used |
| model_info.features | integer | Number of features |
| model_info.training_samples | integer | Training set size |
| performance_metrics | object | Model performance metrics |
| recent_activity | object | Recent usage statistics |

**Example cURL**:
```bash
curl "http://localhost:5000/stats"
```

---

## Rate Limiting
Currently, there are no rate limits implemented. In production, consider implementing:
- 100 requests per minute for `/analyze`
- 10 requests per minute for `/retrain`
- 200 requests per minute for `/history` and `/stats`

## Response Times
Expected response times under normal conditions:
- `/analyze`: 50-200ms
- `/retrain`: 1-5 seconds (depending on dataset size)
- `/history`: 10-50ms
- `/stats`: 5-20ms

## Data Validation

### Email Text Validation
- Minimum length: 1 character
- Maximum length: 10,000 characters
- Allowed characters: All UTF-8 characters
- HTML tags are processed as plain text

### Training Data Validation
- Maximum 1,000 samples per retrain request
- Text length: 1-10,000 characters per sample
- Labels must be 0 (ham) or 1 (spam)
- Duplicate samples are allowed

## CORS Configuration
The API supports Cross-Origin Resource Sharing (CORS) with the following configuration:
- **Allowed Origins**: `*` (all origins in development)
- **Allowed Methods**: GET, POST, OPTIONS
- **Allowed Headers**: Content-Type, Authorization
- **Preflight Max Age**: 86400 seconds (24 hours)

## WebSocket Support (Future)
Real-time updates for email analysis results will be available via WebSocket connections:
- **Endpoint**: `ws://localhost:5000/ws`
- **Events**: `new_analysis`, `model_updated`, `stats_changed`

## API Versioning
Currently using v1 (implicit). Future versions will use URL versioning:
- v1: `/api/v1/analyze`
- v2: `/api/v2/analyze`

## Changelog

### v1.0.0 (Current)
- Initial API implementation
- Basic CRUD operations
- ML model integration
- Pagination support
- Search and filtering

### Planned Features
- Authentication and authorization
- Rate limiting
- WebSocket real-time updates
- Bulk operations
- Email templates and presets
- Advanced analytics endpoints
