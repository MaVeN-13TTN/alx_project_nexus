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

- Docker & Docker Compose
- Git
- TMDb API Key

### Quick Start (Development)

1. **Clone the repository**

   ```bash
   git clone https://github.com/MaVeN-13TTN/alx_project_nexus.git
   cd alx_project_nexus
   ```

2. **Setup development environment**

   ```bash
   # Make scripts executable
   chmod +x scripts/manage-environments.sh
   
   # Setup and start development environment
   ./scripts/manage-environments.sh dev setup
   ```

3. **Access the application**
   - **API**: http://localhost:8000
   - **Admin**: http://localhost:8000/admin/
   - **API Docs**: http://localhost:8000/api/docs/

### Environment Management

```bash
# Development environment
./scripts/manage-environments.sh dev start    # Start services
./scripts/manage-environments.sh dev logs     # View logs
./scripts/manage-environments.sh dev shell web # Access Django shell

# Staging environment
./scripts/manage-environments.sh staging start
./scripts/manage-environments.sh staging migrate

# Production environment
./scripts/manage-environments.sh prod start
./scripts/manage-environments.sh prod backup
./scripts/manage-environments.sh prod health
```

### Environment Configuration

The project supports three environments with separate configuration:

- **Development**: `.env.dev` (from `.env.example`)
- **Staging**: `.env.staging` (from `.env.staging.example`)
- **Production**: `.env.production` (from `.env.production.example`)

**Development Example**:
```env
# Environment
DJANGO_SETTINGS_MODULE=config.settings.development
ENVIRONMENT=development

# Django Settings
SECRET_KEY=your-dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Cache (Local memory for development)
REDIS_URL=redis://redis:6379/0

# TMDb API
TMDB_API_KEY=your-tmdb-api-key
```

**Production Example**:
```env
# Environment
DJANGO_SETTINGS_MODULE=config.settings.production
ENVIRONMENT=production

# Django Settings
SECRET_KEY=your-very-secure-production-key
DEBUG=False
ALLOWED_HOSTS=nexus.k1nyanjui.com

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://user:pass@db:5432/movie_recommendation_prod

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## 🐳 Multi-Environment Docker Setup

### Development Environment

```bash
# Start development environment
./scripts/manage-environments.sh dev start

# View logs
./scripts/manage-environments.sh dev logs

# Access Django shell
./scripts/manage-environments.sh dev shell web
```

### Staging Environment

```bash
# Start staging environment
./scripts/manage-environments.sh staging start

# Run migrations
./scripts/manage-environments.sh staging migrate

# View status
./scripts/manage-environments.sh staging status
```

### Production Environment

```bash
# Start production environment
./scripts/manage-environments.sh prod start

# Create database backup
./scripts/manage-environments.sh prod backup

# Run health checks
./scripts/manage-environments.sh prod health
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

## 🚀 Multi-Environment Deployment

### Environment Overview

| Environment | Purpose | URL | Branch |
|-------------|---------|-----|--------|
| Development | Local development | http://localhost:8000 | develop |
| Staging | Pre-production testing | https://staging-nexus.k1nyanjui.com | staging |
| Production | Live application | https://nexus.k1nyanjui.com | main |

### Deployment Workflow

1. **Develop locally**:
   ```bash
   ./scripts/manage-environments.sh dev start
   # Make changes and test
   ```

2. **Deploy to staging**:
   ```bash
   git checkout staging
   git merge develop
   git push origin staging  # Auto-deploys via GitHub Actions
   ```

3. **Deploy to production**:
   ```bash
   git checkout main
   git merge staging
   git push origin main  # Auto-deploys via GitHub Actions
   ```

### Manual Deployment

- Go to GitHub Actions → CI/CD Pipeline → Run workflow
- Select target environment (development/staging/production)
- Click "Run workflow"

### VPS Deployment

For detailed VPS deployment instructions, see:
- [Multi-Environment Guide](docs/MULTI_ENVIRONMENT_GUIDE.md)
- [VPS Deployment Guide](docs/VPS_DEPLOYMENT_GUIDE.md)

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

## 🚀 CI/CD & Deployment

### GitHub Actions Workflows

- **CI/CD Pipeline**: Automated testing, building, and multi-environment deployment
- **Configuration Validation**: Docker Compose and environment file validation

### Deployment Options

#### Development Environment
```bash
./scripts/manage-environments.sh dev setup
./scripts/manage-environments.sh dev start
```

#### VPS Deployment (Production + Staging)
```bash
# Clone and deploy
git clone https://github.com/MaVeN-13TTN/alx_project_nexus.git
cd alx_project_nexus
cp .env.vps.example .env
# Edit .env with your values
./scripts/deploy-vps.sh
```

### Pipeline Features

- ✅ Multi-environment deployment (dev/staging/production)
- ✅ Code quality checks and security scanning
- ✅ Automated testing with coverage reports
- ✅ Docker image building and validation
- ✅ Post-deployment health checks

### Documentation

- [VPS Deployment Guide](docs/VPS_DEPLOYMENT_GUIDE.md) - Complete deployment instructions
- [API Documentation](docs/API_DOCUMENTATION.md) - Complete API reference

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
