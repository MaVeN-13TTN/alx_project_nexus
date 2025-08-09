# API Documentation - Movie Recommendation Backend

## 🌐 API Overview

The Movie Recommendation Backend provides a comprehensive RESTful API for managing movie data, user authentication, favorites, and personalized recommendations. All endpoints return JSON responses and follow consistent patterns for error handling and data formatting.

## 🔗 Base URL

- **Development**: `http://localhost:8000/api/v1/`
- **Production**: `https://your-domain.com/api/v1/`

## 📋 API Standards

### Response Format

All API responses follow a consistent structure:

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Success message",
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "pages": 5,
    "has_next": true,
    "has_previous": false
  }
}
```

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["This field is required."]
    }
  }
}
```

### HTTP Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

## 🔐 Authentication

### JWT Token Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Token Lifecycle

- **Access Token**: Valid for 24 hours
- **Refresh Token**: Valid for 7 days
- **Automatic Refresh**: Use refresh endpoint before access token expires

## 📚 API Endpoints

### Authentication Endpoints

#### 1. User Registration

```http
POST /api/v1/auth/register/
```

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "securePassword123",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "date_joined": "2025-08-04T10:30:00Z"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  },
  "message": "User registered successfully"
}
```

#### 2. User Login

```http
POST /api/v1/auth/login/
```

**Request Body:**

```json
{
  "username": "john_doe",
  "password": "securePassword123"
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "john_doe",
      "email": "john@example.com",
      "first_name": "John",
      "last_name": "Doe"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  },
  "message": "Login successful"
}
```

#### 3. Token Refresh

```http
POST /api/v1/auth/refresh/
```

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  },
  "message": "Token refreshed successfully"
}
```

#### 4. User Logout

```http
POST /api/v1/auth/logout/
```

**Headers:** `Authorization: Bearer <access-token>`

**Request Body:**

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

#### 5. User Profile

```http
GET /api/v1/auth/profile/
```

**Headers:** `Authorization: Bearer <access-token>`

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-08-04T10:30:00Z",
    "favorite_count": 15,
    "preferences": {
      "genres": ["Action", "Sci-Fi", "Thriller"]
    }
  }
}
```

### Movie Endpoints

#### 1. Trending Movies

```http
GET /api/v1/movies/trending/?page=1&per_page=20
```

**Query Parameters:**

- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20, max: 100)

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "movies": [
      {
        "id": 1,
        "tmdb_id": 550,
        "title": "Fight Club",
        "overview": "A ticking-time-bomb insomniac...",
        "release_date": "1999-10-15",
        "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
        "backdrop_path": "/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg",
        "vote_average": 8.4,
        "vote_count": 26280,
        "runtime": 139,
        "genres": [
          {
            "id": 1,
            "name": "Drama",
            "tmdb_id": 18
          },
          {
            "id": 2,
            "name": "Thriller",
            "tmdb_id": 53
          }
        ]
      }
    ]
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 500,
    "pages": 25,
    "has_next": true,
    "has_previous": false
  }
}
```

#### 2. Popular Movies

```http
GET /api/v1/movies/popular/?page=1&per_page=20
```

**Response:** Same format as trending movies

#### 3. Movie Search

```http
GET /api/v1/movies/search/?q=fight+club&page=1&per_page=20
```

**Query Parameters:**

- `q` (required): Search query
- `page` (optional): Page number
- `per_page` (optional): Items per page

**Response:** Same format as trending movies

#### 4. Movie Details

```http
GET /api/v1/movies/550/
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "tmdb_id": 550,
    "title": "Fight Club",
    "overview": "A ticking-time-bomb insomniac and a slippery soap salesman channel primal male aggression into a shocking new form of therapy.",
    "release_date": "1999-10-15",
    "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
    "backdrop_path": "/fCayJrkfRaCRCTh8GqN30f8oyQF.jpg",
    "vote_average": 8.4,
    "vote_count": 26280,
    "runtime": 139,
    "status": "Released",
    "genres": [
      {
        "id": 1,
        "name": "Drama",
        "tmdb_id": 18
      }
    ],
    "is_favorite": false,
    "similar_movies": [
      {
        "id": 2,
        "title": "The Matrix",
        "poster_path": "/f89U3ADr1oiB1s9GkdPOEpXUk5H.jpg"
      }
    ]
  }
}
```

#### 5. Personalized Recommendations

```http
GET /api/v1/movies/recommendations/?page=1&per_page=20
```

**Headers:** `Authorization: Bearer <access-token>`

**Response:** Same format as trending movies

#### 6. All Genres

```http
GET /api/v1/genres/
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "genres": [
      {
        "id": 1,
        "name": "Action",
        "tmdb_id": 28
      },
      {
        "id": 2,
        "name": "Adventure",
        "tmdb_id": 12
      }
    ]
  }
}
```

### User Favorites Endpoints

#### 1. Get User Favorites

```http
GET /api/v1/favorites/?page=1&per_page=20
```

**Headers:** `Authorization: Bearer <access-token>`

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "favorites": [
      {
        "id": 1,
        "movie": {
          "id": 1,
          "tmdb_id": 550,
          "title": "Fight Club",
          "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
          "vote_average": 8.4,
          "release_date": "1999-10-15"
        },
        "created_at": "2025-08-04T14:30:00Z"
      }
    ]
  },
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 15,
    "pages": 1,
    "has_next": false,
    "has_previous": false
  }
}
```

#### 2. Add Movie to Favorites

```http
POST /api/v1/favorites/550/
```

**Headers:** `Authorization: Bearer <access-token>`

**Response (201 Created):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "movie": {
      "id": 1,
      "tmdb_id": 550,
      "title": "Fight Club"
    },
    "created_at": "2025-08-04T14:30:00Z"
  },
  "message": "Movie added to favorites"
}
```

#### 3. Remove Movie from Favorites

```http
DELETE /api/v1/favorites/550/
```

**Headers:** `Authorization: Bearer <access-token>`

**Response (200 OK):**

```json
{
  "success": true,
  "message": "Movie removed from favorites"
}
```

### User Preferences Endpoints

#### 1. Get User Preferences

```http
GET /api/v1/preferences/
```

**Headers:** `Authorization: Bearer <access-token>`

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "user": 1,
    "genres": [
      {
        "id": 1,
        "name": "Action",
        "tmdb_id": 28
      },
      {
        "id": 2,
        "name": "Sci-Fi",
        "tmdb_id": 878
      }
    ],
    "created_at": "2025-08-04T10:30:00Z",
    "updated_at": "2025-08-04T14:30:00Z"
  }
}
```

#### 2. Update User Preferences

```http
PUT /api/v1/preferences/
```

**Headers:** `Authorization: Bearer <access-token>`

**Request Body:**

```json
{
  "genre_ids": [28, 878, 53, 18]
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "user": 1,
    "genres": [
      {
        "id": 1,
        "name": "Action",
        "tmdb_id": 28
      },
      {
        "id": 2,
        "name": "Sci-Fi",
        "tmdb_id": 878
      },
      {
        "id": 3,
        "name": "Thriller",
        "tmdb_id": 53
      },
      {
        "id": 4,
        "name": "Drama",
        "tmdb_id": 18
      }
    ],
    "updated_at": "2025-08-04T15:45:00Z"
  },
  "message": "Preferences updated successfully"
}
```

### Utility Endpoints

#### 1. Health Check

```http
GET /api/health/
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-08-04T16:00:00Z",
    "version": "v1.0.0",
    "database": "connected",
    "cache": "connected"
  },
  "message": "Service is healthy"
}
```

#### 2. API Information

```http
GET /api/v1/
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "name": "Movie Recommendation API",
    "version": "v1",
    "description": "RESTful API for movie recommendations and user management",
    "endpoints": {
      "authentication": "/api/v1/auth/",
      "movies": "/api/v1/movies/",
      "favorites": "/api/v1/favorites/",
      "preferences": "/api/v1/preferences/",
      "documentation": "/api/docs/"
    }
  }
}
```

## 🔄 API Versioning

### Version Strategy

The API uses URL-based versioning with the `/v1/` prefix:

- **Current Version**: `v1`
- **Base Path**: `/api/v1/`
- **Backward Compatibility**: Maintained for major versions
- **Deprecation Policy**: 6 months notice before version retirement

### Version Headers

Optionally, you can specify the API version using headers:

```http
Accept: application/vnd.movieapi.v1+json
Content-Type: application/json
```

### Future Versions

When new versions are released:

- **v2**: `/api/v2/` (future)
- **v3**: `/api/v3/` (future)

### Version Compatibility

| Version | Status | Support Until | Breaking Changes |
|---------|--------|---------------|------------------|
| v1      | Current| TBD           | None             |
| v2      | Planned| TBD           | TBD              |

## 📊 Rate Limiting

### Rate Limits

- **Authenticated Users**: 1000 requests/hour
- **Anonymous Users**: 100 requests/hour
- **Burst Limit**: 50 requests/minute

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641024000
```

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "details": {
      "limit": 1000,
      "reset_time": "2025-08-04T17:00:00Z"
    }
  }
}
```

## 🔍 Error Handling

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid input data |
| `AUTHENTICATION_REQUIRED` | 401 | Missing or invalid token |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |
| `SERVICE_UNAVAILABLE` | 503 | External service down |

### Error Response Examples

#### Validation Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["Enter a valid email address."],
      "password": ["This field is required."]
    }
  }
}
```

#### Authentication Error

```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Authentication credentials were not provided."
  }
}
```

## 📖 Usage Examples

### Complete User Journey

```javascript
// 1. Register user
const registerResponse = await fetch('/api/v1/auth/register/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'moviefan',
    email: 'fan@movies.com',
    password: 'SecurePass123'
  })
});

// 2. Get trending movies
const moviesResponse = await fetch('/api/v1/movies/trending/');

// 3. Add movie to favorites
const favoriteResponse = await fetch('/api/v1/favorites/550/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  }
});

// 4. Get personalized recommendations
const recommendationsResponse = await fetch('/api/v1/movies/recommendations/', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});
```

### Python SDK Example

```python
import requests

class MovieAPIClient:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def get_trending_movies(self, page=1):
        response = self.session.get(
            f'{self.base_url}/api/v1/movies/trending/',
            params={'page': page}
        )
        return response.json()
    
    def add_to_favorites(self, movie_id):
        response = self.session.post(
            f'{self.base_url}/api/v1/favorites/{movie_id}/'
        )
        return response.json()

# Usage
client = MovieAPIClient('https://movierecommendation.app', token='your-jwt-token')
movies = client.get_trending_movies()
```

## 🚀 Getting Started

### Quick Start

1. **Register an account**: `POST /api/v1/auth/register/`
2. **Get your JWT token**: Use login response tokens
3. **Explore movies**: `GET /api/v1/movies/trending/`
4. **Add favorites**: `POST /api/v1/favorites/{movie_id}/`
5. **Get recommendations**: `GET /api/v1/movies/recommendations/`

### Interactive Documentation

- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

This comprehensive API documentation provides all the information needed to integrate with the Movie Recommendation Backend effectively.Body:**

```json
{
  "genre_ids": [28, 878, 53, 18]
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "id": 1,
    "user": 1,
    "genres": [
      {
        "id": 1,
        "name": "Action",
        "tmdb_id": 28
      },
      {
        "id": 2,
        "name": "Sci-Fi",
        "tmdb_id": 878
      },
      {
        "id": 3,
        "name": "Thriller",
        "tmdb_id": 53
      },
      {
        "id": 4,
        "name": "Drama",
        "tmdb_id": 18
      }
    ],
    "updated_at": "2025-08-04T15:30:00Z"
  },
  "message": "Preferences updated successfully"
}
```

### Utility Endpoints

#### 1. Health Check

```http
GET /api/health/
```

**Response (200 OK):**

```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "timestamp": "2025-08-04T15:30:00Z",
    "version": "1.0.0",
    "database": "connected",
    "cache": "connected",
    "tmdb_api": "connected"
  }
}
```

## 🔒 Rate Limiting

### Rate Limits

- **Anonymous users**: 100 requests per hour
- **Authenticated users**: 1000 requests per hour
- **TMDb API calls**: Cached to reduce external API usage

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1691158800
```

## 📊 Pagination

### Query Parameters

- `page`: Page number (starts from 1)
- `per_page`: Items per page (1-100, default: 20)

### Pagination Response

```json
{
  "pagination": {
    "page": 2,
    "per_page": 20,
    "total": 500,
    "pages": 25,
    "has_next": true,
    "has_previous": true,
    "next_page": 3,
    "previous_page": 1
  }
}
```

## 🚫 Error Handling

### Common Error Codes

#### Authentication Errors

```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Authentication credentials were not provided"
  }
}
```

#### Validation Errors

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "username": ["This field is required."],
      "email": ["Enter a valid email address."]
    }
  }
}
```

#### Not Found Errors

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Movie not found"
  }
}
```

#### Rate Limit Errors

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again in 3600 seconds."
  }
}
```

## 🧪 Testing

### API Testing Tools

- **Postman Collection**: Available at `/api/postman/`
- **OpenAPI Spec**: Available at `/api/schema/`
- **Interactive Docs**: Available at `/api/docs/`

### Example cURL Commands

#### Get trending movies

```bash
curl -X GET "http://localhost:8000/api/movies/trending/" \
  -H "Accept: application/json"
```

#### Login user

```bash
curl -X POST "http://localhost:8000/api/auth/login/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securePassword123"
  }'
```

#### Add movie to favorites

```bash
curl -X POST "http://localhost:8000/api/favorites/550/" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -H "Content-Type: application/json"
```

## 📈 Performance

### Caching Strategy

- **Trending movies**: Cached for 30 minutes
- **Popular movies**: Cached for 1 hour
- **Movie details**: Cached for 24 hours
- **User recommendations**: Cached for 2 hours per user

### Response Times (Target)

- **Cached responses**: < 100ms
- **Database queries**: < 200ms
- **External API calls**: < 500ms
- **Complex recommendations**: < 1000ms

This comprehensive API documentation provides all the information needed for frontend developers and API consumers to effectively integrate with the Movie Recommendation Backend.
