# 🎬 Movie Recommendation Backend - ALX Project Nexus

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Django](https://img.shields.io/badge/django-v4.2+-green.svg)
![PostgreSQL](https://img.shields.io/badge/postgresql-v15+-blue.svg)
![Redis](https://img.shields.io/badge/redis-v7+-red.svg)
![Docker](https://img.shields.io/badge/docker-compose-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎬 Overview

A production-ready Django REST API backend for movie recommendations featuring comprehensive CI/CD pipeline, Docker containerization, and VPS deployment capabilities. This project emphasizes modern development practices, security, and scalable deployment strategies.

## 🚀 Project Goals

The primary objectives of this movie recommendation backend are:

- **Production-Ready API**: Develop robust endpoints for movie recommendations and user management
- **Modern DevOps**: Implement CI/CD pipeline with automated testing and deployment
- **Container Deployment**: Provide Docker-based deployment for development and production
- **Security First**: Implement comprehensive security scanning and best practices
- **Performance Optimization**: Optimize API performance with caching and database optimization
- **Comprehensive Documentation**: Provide detailed documentation and API specs

## 🛠 Technologies Used

- **Django 4.2+**: Modern Python web framework
- **PostgreSQL 15**: Advanced relational database
- **Redis 7**: High-performance caching and session storage
- **Docker**: Containerization for consistent deployments
- **Docker Compose**: Multi-container orchestration
- **GitHub Actions**: CI/CD automation
- **TMDb API**: External movie data source
- **Nginx**: Reverse proxy and load balancer
- **Let's Encrypt**: Automated SSL certificate management

## ✨ Key Features

### 🎭 Movie API Integration

- Integration with TMDb (The Movie Database) API
- Trending movies endpoint
- Movie recommendations based on user preferences
- Detailed movie information retrieval
- Robust error handling for API calls

### 🔐 User Authentication & Preferences

- JWT-based user authentication
- User registration and login
- Save and retrieve favorite movies
- User preference management
- Secure API endpoints

### ⚡ Performance Optimization

- Redis caching for movie data
- Optimized database queries
- API response time improvements
- Reduced third-party API call frequency

### 📚 Comprehensive Documentation

- Swagger UI for interactive API documentation
- Detailed endpoint descriptions
- Request/response examples
- Authentication requirements

## 🏗 System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │───▶│   Django API    │───▶│   PostgreSQL    │
│   Application   │    │   Backend       │    │   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │   TMDb API      │
                       │                 │    │   (External)    │
                       └─────────────────┘    └─────────────────┘
```

## 📊 Database Schema

### Core Models

#### User Model (Extended)

- `id`: Primary key
- `username`: Unique username
- `email`: User email
- `password`: Hashed password
- `created_at`: Account creation timestamp
- `updated_at`: Last update timestamp

#### Movie Model

- `id`: Primary key
- `tmdb_id`: TMDb movie ID
- `title`: Movie title
- `overview`: Movie description
- `release_date`: Release date
- `poster_path`: Poster image URL
- `backdrop_path`: Backdrop image URL
- `vote_average`: Average rating
- `vote_count`: Number of votes
- `genres`: Many-to-many relationship with Genre
- `created_at`: Record creation timestamp
- `updated_at`: Last update timestamp

#### Genre Model

- `id`: Primary key
- `tmdb_id`: TMDb genre ID
- `name`: Genre name

#### UserFavorite Model

- `id`: Primary key
- `user`: Foreign key to User
- `movie`: Foreign key to Movie
- `created_at`: Favorite creation timestamp

#### UserPreference Model

- `id`: Primary key
- `user`: One-to-one relationship with User
- `preferred_genres`: Many-to-many relationship with Genre
- `created_at`: Preference creation timestamp
- `updated_at`: Last update timestamp

## 🔗 API Endpoints

### Authentication Endpoints

```
POST   /api/auth/register/     - User registration
POST   /api/auth/login/        - User login
POST   /api/auth/logout/       - User logout
POST   /api/auth/refresh/      - Refresh JWT token
GET    /api/auth/profile/      - Get user profile
PUT    /api/auth/profile/      - Update user profile
```

### Movie Endpoints

```
GET    /api/movies/trending/            - Get trending movies
GET    /api/movies/popular/             - Get popular movies
GET    /api/movies/recommendations/     - Get personalized recommendations
GET    /api/movies/{id}/                - Get movie details
GET    /api/movies/search/?q={query}    - Search movies
GET    /api/genres/                     - Get all genres
```

### User Favorites Endpoints

```
GET    /api/favorites/                  - Get user's favorite movies
POST   /api/favorites/{movie_id}/       - Add movie to favorites
DELETE /api/favorites/{movie_id}/       - Remove movie from favorites
```

### User Preferences Endpoints

```
GET    /api/preferences/                - Get user preferences
PUT    /api/preferences/                - Update user preferences
```

### Utility Endpoints

```
GET    /api/health/                     - Health check
GET    /api/docs/                       - Swagger documentation
```

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL 13+
- Redis 6+
- TMDb API Key

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/MaVeN-13TTN/alx_project_nexus.git
   cd alx_project_nexus
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Environment setup**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**

   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the server**
   ```bash
   python manage.py runserver
   ```

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=movie_recommendation_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# TMDb API
TMDB_API_KEY=your-tmdb-api-key
TMDB_BASE_URL=https://api.themoviedb.org/3

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DELTA=86400
```

## 🐳 Docker Setup

### Using Docker Compose

1. **Build and run containers**

   ```bash
   docker-compose up --build
   ```

2. **Run migrations**

   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create superuser**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

## 🧪 Testing

Run the test suite:

```bash
python manage.py test
```

Run with coverage:

```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

## 📈 Performance Monitoring

### Caching Strategy

- **Movie Data**: Cached for 1 hour
- **Trending Movies**: Cached for 30 minutes
- **User Recommendations**: Cached for 2 hours per user
- **Genre Data**: Cached for 24 hours

### Optimization Techniques

- Database query optimization using `select_related` and `prefetch_related`
- API response pagination
- Efficient Redis key management
- Background task processing for data updates

## 📖 API Documentation

Interactive API documentation is available at:

- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up Redis in production
- [ ] Configure static files serving
- [ ] Set up SSL certificates
- [ ] Configure logging
- [ ] Set up monitoring

### Deployment Platforms

- **Heroku**: Ready with `Procfile` and `runtime.txt`
- **AWS**: ECS/Fargate deployment ready
- **DigitalOcean**: App Platform compatible
- **Railway**: One-click deployment

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**MaVeN-13TTN**

- GitHub: [@MaVeN-13TTN](https://github.com/MaVeN-13TTN)
- Project Link: [Movie Recommendation Backend](https://github.com/MaVeN-13TTN/alx_project_nexus)

## 🙏 Acknowledgments

- [The Movie Database (TMDb)](https://www.themoviedb.org/) for providing the movie data API
- [Django Documentation](https://docs.djangoproject.com/) for excellent framework documentation
- [ALX Africa](https://www.alxafrica.com/) for the ProDev Backend Program

## 🚀 CI/CD & Docker Deployment

This project uses GitHub Actions for continuous integration and Docker Compose for deployment automation.

### GitHub Actions Workflows

- **CI/CD Pipeline**: Automated testing, building, and deployment
- **Dependency Updates**: Weekly automated dependency updates
- **Release Management**: Automated releases and changelog generation
- **Security Scanning**: Vulnerability scanning and code quality checks
- **Docker Validation**: Docker Compose configuration validation

### Docker Deployment Options

#### Option 1: Development Environment

```bash
# Start development environment
docker-compose up --build

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

#### Option 2: Production VPS Deployment

```bash
# Clone repository on VPS
git clone https://github.com/MaVeN-13TTN/alx_project_nexus.git
cd alx_project_nexus

# Configure environment
cp .env.vps.example .env
nano .env  # Edit with your values

# Deploy with production compose
docker-compose -f docker-compose.vps.yml up -d

# Run automated deployment script
./scripts/deploy-vps.sh
```

### Pipeline Features

- ✅ Code quality checks (Black, Flake8, MyPy)
- ✅ Security scanning (Bandit, Safety, Trivy)
- ✅ Automated testing with coverage reports
- ✅ Multi-arch Docker builds (amd64, arm64)
- ✅ Docker Compose validation
- ✅ Post-deployment health checks
- ✅ Automated container updates

### Deployment Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │───▶│   Django API    │───▶│   PostgreSQL    │
│   (SSL/TLS)     │    │   (Gunicorn)    │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   Redis Cache   │    │   TMDb API      │
                       │   (Sessions)    │    │   (External)    │
                       └─────────────────┘    └─────────────────┘
```

See [VPS Deployment Guide](docs/VPS_DEPLOYMENT_GUIDE.md) for detailed deployment instructions.

## �📊 Project Status

- [x] Project Setup
- [x] Database Design
- [x] CI/CD Pipeline Setup
- [x] GitOps Configuration
- [x] Docker Configuration
- [ ] TMDb API Integration
- [ ] User Authentication
- [ ] Movie Endpoints
- [ ] Caching Implementation
- [ ] API Documentation
- [ ] Testing Suite
- [ ] Deployment
- [ ] Final Review

---

**Built with ❤️ for the ALX ProDev Backend Program**
