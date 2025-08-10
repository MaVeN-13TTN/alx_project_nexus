# Movie Recommendation API - Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Movie Endpoints](#movie-endpoints)
4. [User Features](#user-features)
5. [Recommendations](#recommendations)
6. [Error Handling](#error-handling)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

## Getting Started

### Base URL

- **Development:** `http://localhost:8000`
- **Production:** `https://api.movierecommendations.com`

### API Documentation

- **Swagger UI:** `/api/docs/`
- **ReDoc:** `/api/redoc/`
- **OpenAPI Schema:** `/api/schema/`

### Health Check

```bash
curl -X GET http://localhost:8000/api/health/
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. All protected endpoints require a valid JWT token in the Authorization header.

### 1. User Registration

**Endpoint:** `POST /api/v1/auth/register/`

```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "moviefan",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

**Response:**

```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user": {
      "id": 1,
      "username": "moviefan",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "full_name": "John Doe"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
  }
}
```

### 2. User Login

**Endpoint:** `POST /api/v1/auth/token/`

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### 3. Token Refresh

**Endpoint:** `POST /api/v1/auth/token/refresh/`

```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

### 4. Using Tokens

Include the access token in the Authorization header for protected endpoints:

```bash
curl -X GET http://localhost:8000/api/v1/favorites/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

## Movie Endpoints

### 1. Trending Movies

**Endpoint:** `GET /api/v1/movies/trending/`

```bash
# Get daily trending movies
curl -X GET "http://localhost:8000/api/v1/movies/trending/?time_window=day&page=1"

# Get weekly trending movies
curl -X GET "http://localhost:8000/api/v1/movies/trending/?time_window=week&page=1"
```

### 2. Popular Movies

**Endpoint:** `GET /api/v1/movies/popular/`

```bash
curl -X GET "http://localhost:8000/api/v1/movies/popular/?page=1"
```

### 3. Search Movies

**Endpoint:** `GET /api/v1/movies/search/`

```bash
# Basic search
curl -X GET "http://localhost:8000/api/v1/movies/search/?query=avengers"

# Search with year filter
curl -X GET "http://localhost:8000/api/v1/movies/search/?query=batman&year=2022"
```

### 4. Movie Details

**Endpoint:** `GET /api/v1/movies/movies/{tmdb_id}/`

```bash
curl -X GET "http://localhost:8000/api/v1/movies/movies/550/"
```

### 5. Discover Movies

**Endpoint:** `GET /api/v1/movies/discover/`

```bash
# Discover action movies with high ratings
curl -X GET "http://localhost:8000/api/v1/movies/discover/?genre_ids=28&min_vote_average=7.0&sort_by=vote_average.desc"
```

### 6. Genres

**Endpoint:** `GET /api/v1/movies/genres/`

```bash
curl -X GET "http://localhost:8000/api/v1/movies/genres/"
```

## User Features

### 1. Favorites Management

#### Add to Favorites

```bash
curl -X POST http://localhost:8000/api/v1/favorites/add/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 550}'
```

#### List Favorites

```bash
curl -X GET http://localhost:8000/api/v1/favorites/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Remove from Favorites

```bash
curl -X DELETE http://localhost:8000/api/v1/favorites/remove/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"movie_id": 550}'
```

#### Check Favorite Status

```bash
curl -X GET http://localhost:8000/api/v1/favorites/check/550/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. User Preferences

#### Get Preferences

```bash
curl -X GET http://localhost:8000/api/v1/preferences/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Update Preferences

```bash
curl -X PUT http://localhost:8000/api/v1/preferences/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_genres": [28, 12, 16],
    "avoided_genres": [27, 53],
    "min_vote_average": 7.0,
    "preferred_languages": ["en", "es"]
  }'
```

#### Quick Preference Update

```bash
curl -X POST http://localhost:8000/api/v1/preferences/quick-update/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "add_genre",
    "genre_id": 35
  }'
```

### 3. Viewing History

#### Add Viewing History Entry

```bash
curl -X POST http://localhost:8000/api/v1/preferences/history/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": 550,
    "rating": 9,
    "watched_at": "2025-08-10T15:30:00Z"
  }'
```

#### Get Viewing History

```bash
curl -X GET http://localhost:8000/api/v1/preferences/history/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get User Statistics

```bash
curl -X GET http://localhost:8000/api/v1/preferences/statistics/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Recommendations

### 1. Get Recommendations

**Endpoint:** `GET /api/v1/recommendations/`

```bash
# Basic recommendations
curl -X GET http://localhost:8000/api/v1/recommendations/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Content-based recommendations
curl -X GET "http://localhost:8000/api/v1/recommendations/?type=content&limit=10" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Advanced algorithm recommendations
curl -X GET "http://localhost:8000/api/v1/recommendations/?type=matrix_factorization&algorithm=advanced" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 2. Advanced Recommendations

**Endpoint:** `POST /api/v1/recommendations/`

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recommendation_type": "neural_cf",
    "limit": 15,
    "force_refresh": true,
    "include_metadata": true
  }'
```

### 3. Similar Movies

**Endpoint:** `GET /api/v1/recommendations/similar/{movie_id}/`

```bash
curl -X GET http://localhost:8000/api/v1/recommendations/similar/550/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 4. Recommendation Feedback

**Endpoint:** `POST /api/v1/recommendations/feedback/`

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/feedback/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": 550,
    "recommendation_type": "hybrid",
    "feedback": "like"
  }'
```

### 5. Recommendation Settings

#### Get Settings

```bash
curl -X GET http://localhost:8000/api/v1/recommendations/settings/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### Update Settings

```bash
curl -X PATCH http://localhost:8000/api/v1/recommendations/settings/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "prefer_content_based": true,
    "prefer_collaborative": true,
    "genre_diversity": 0.7,
    "min_vote_average": 6.5,
    "max_recommendations": 25
  }'
```

## Error Handling

The API uses standard HTTP status codes and returns consistent error responses:

### Error Response Format

```json
{
  "error": "Error type",
  "message": "Human-readable error message",
  "details": {
    "field": ["Specific field error"]
  }
}
```

### Common HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Permission denied
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Example Error Responses

#### Validation Error (400)

```json
{
  "error": "Validation failed",
  "message": "One or more fields are invalid",
  "details": {
    "email": ["This field is required."],
    "password": ["Password must be at least 8 characters long."]
  }
}
```

#### Authentication Error (401)

```json
{
  "error": "Authentication failed",
  "message": "Invalid or expired token"
}
```

#### Rate Limit Error (429)

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after": 60
}
```

## Rate Limiting

### Limits

- **Anonymous users:** 100 requests per hour
- **Authenticated users:** 1000 requests per hour
- **TMDb API calls:** 40 requests per 10 seconds

### Headers

Response headers include rate limit information:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1692547200
```

## Examples

### Complete User Workflow

#### 1. Register and Login

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "johndoe",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe"
  }'

# Extract token from response and set variable
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

#### 2. Set Up Preferences

```bash
curl -X PUT http://localhost:8000/api/v1/preferences/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "preferred_genres": [28, 12, 878],
    "min_vote_average": 7.0,
    "preferred_languages": ["en"]
  }'
```

#### 3. Add Some Favorites

```bash
# Add multiple favorites
for movie_id in 550 680 155 13; do
  curl -X POST http://localhost:8000/api/v1/favorites/add/ \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"movie_id\": $movie_id}"
done
```

#### 4. Add Viewing History

```bash
curl -X POST http://localhost:8000/api/v1/preferences/history/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": 550,
    "rating": 9,
    "watched_at": "2025-08-10T20:00:00Z"
  }'
```

#### 5. Get Recommendations

```bash
# Get hybrid recommendations
curl -X GET "http://localhost:8000/api/v1/recommendations/?type=hybrid&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# Get advanced neural collaborative filtering recommendations
curl -X GET "http://localhost:8000/api/v1/recommendations/?type=neural_cf&algorithm=advanced" \
  -H "Authorization: Bearer $TOKEN"
```

#### 6. Provide Feedback

```bash
curl -X POST http://localhost:8000/api/v1/recommendations/feedback/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "movie_id": 680,
    "recommendation_type": "hybrid",
    "feedback": "like"
  }'
```

### Advanced Search and Discovery

#### 1. Complex Movie Discovery

```bash
# Find high-rated sci-fi movies from 2020-2025
curl -X GET "http://localhost:8000/api/v1/movies/discover/?genre_ids=878&min_vote_average=7.5&year=2023&sort_by=vote_average.desc" \
  -H "Content-Type: application/json"
```

#### 2. Search with Multiple Filters

```bash
# Search for Batman movies from specific year
curl -X GET "http://localhost:8000/api/v1/movies/search/?query=batman&year=2022&include_adult=false" \
  -H "Content-Type: application/json"
```

### Recommendation Analytics

#### 1. Get User Statistics

```bash
curl -X GET http://localhost:8000/api/v1/preferences/statistics/ \
  -H "Authorization: Bearer $TOKEN"
```

#### 2. Get Recommendation Analytics

```bash
curl -X GET http://localhost:8000/api/v1/recommendations/analytics/ \
  -H "Authorization: Bearer $TOKEN"
```

## Best Practices

### 1. Authentication

- Store JWT tokens securely
- Implement token refresh logic
- Handle token expiration gracefully

### 2. Error Handling

- Always check response status codes
- Parse error messages for user feedback
- Implement retry logic for temporary failures

### 3. Performance

- Use pagination for large datasets
- Cache frequently accessed data
- Implement proper loading states

### 4. User Experience

- Provide meaningful error messages
- Show loading indicators
- Implement optimistic updates where appropriate

## Support

For additional help and support:

- **Documentation:** [GitHub Repository](https://github.com/MaVeN-13TTN/alx_project_nexus)
- **Issues:** [GitHub Issues](https://github.com/MaVeN-13TTN/alx_project_nexus/issues)
- **API Documentation:** `/api/docs/` (Interactive Swagger UI)
