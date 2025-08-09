# GitHub Actions CI/CD & Docker Compose Configuration

This directory contains GitHub Actions workflows and Docker Compose configuration for the Movie Recommendation Backend project.

## 🚀 GitHub Actions Workflows

### 1. CI/CD Pipeline (`.github/workflows/ci-cd.yml`)

**Triggers:**

- Push to `main` branch only
- Pull requests to `main`
- Manual trigger via workflow_dispatch

**Pipeline Jobs:**

#### Code Quality & Security

- **Code Formatting**: Black, isort
- **Linting**: Flake8
- **Security Scanning**: Bandit, Safety
- **Type Checking**: MyPy

#### Testing

- **Unit Tests**: pytest with coverage
- **Integration Tests**: Database and Redis
- **Coverage Reporting**: Codecov integration

#### Build & Security

- **Docker Build**: Multi-arch (amd64, arm64) with Python 3.12
- **Container Registry**: GitHub Container Registry
- **Vulnerability Scanning**: Trivy with fail-on-critical
- **Security Hardening**: Non-root containers, minimal attack surface

#### Deployment (Docker Compose)

- **Production**: Auto-deploy from `main` branch only
- **Post-deployment Tests**: Health checks with proper error handling
- **Deployment Summary**: Comprehensive status reporting

### 2. Dependency Updates (`.github/workflows/dependency-update.yml`)

**Schedule:** Weekly on Mondays at 2 AM UTC

**Features:**

- Automated dependency updates using pip-tools
- Security vulnerability checks
- Automated pull request creation

### 3. Release Management (`.github/workflows/release.yml`)

**Trigger:** Git tags matching `v*` pattern

**Features:**

- Automated changelog generation
- GitHub release creation
- Production deployment with release tags

### 4. Docker Compose Validation (`.github/workflows/gitops.yml`)

**Features:**

- Docker Compose file validation
- Container security scanning
- Deployment configuration testing

## � Docker Compose Configuration

### Directory Structure

```
docker/
├── docker-compose.yml           # Development environment
├── docker-compose.prod.yml      # Production environment
├── docker-compose.vps.yml       # VPS deployment
└── nginx/
    └── nexus.conf               # Nginx configuration
```

### Deployment Strategy

#### Development Environment

- **Services**: Django, PostgreSQL, Redis
- **Volumes**: Local code mounting for development
- **Networks**: Internal Docker networks
- **Configuration**: Debug mode enabled

#### Production Environment (VPS)

- **Services**: Django, PostgreSQL, Redis, Nginx
- **Scaling**: Horizontal scaling ready
- **Networks**: External nginx-proxy network
- **Security**: Production hardening
- **Domain**: Custom domain with SSL
- **Image**: Pre-built from GitHub Container Registry

### Security Features

- **Secret Management**: Environment-based secrets
- **TLS Termination**: Let's Encrypt certificates
- **Rate Limiting**: Nginx reverse proxy protection
- **Health Checks**: Container-level health monitoring
- **Non-root Containers**: Security best practices
- **Vulnerability Scanning**: Automated Docker image scanning
- **Network Isolation**: Secure container networking

## 🔐 Required Secrets

Configure these secrets in your GitHub repository settings:

### GitHub Secrets

```bash
# Container Registry
GH_TOKEN                     # GitHub token for repository and container registry access

# Docker Deployment (Optional for automated VPS deployment)
VPS_HOST                     # VPS hostname/IP for deployment
VPS_USERNAME                 # VPS username (e.g., deploy)
VPS_SSH_KEY                  # SSH private key for VPS access

# Notifications (Optional)
# SLACK_WEBHOOK              # Removed - no longer used
```

### Environment Variables (VPS Deployment)

```bash
# Database
DB_USER                      # PostgreSQL username
DB_PASSWORD                  # Database password

# External APIs
TMDB_API_KEY                # The Movie Database API key

# Application
SECRET_KEY                  # Django secret key
ALLOWED_HOSTS              # Comma-separated allowed hosts
CSRF_TRUSTED_ORIGINS       # Trusted origins for CSRF
```

## 🚀 Setup Instructions

### 1. GitHub Repository Setup

1. **Enable GitHub Actions**:

   ```bash
   # Actions are enabled by default for new repositories
   # Ensure Actions are enabled in Settings > Actions
   ```

2. **Configure Secrets**:

   ```bash
   # Go to Settings > Secrets and variables > Actions
   # Add all required secrets listed above
   ```

3. **Enable Container Registry**:
   ```bash
   # Go to Settings > Actions > General
   # Enable "Read and write permissions" for GH_TOKEN
   ```

### 2. VPS Server Setup

1. **Install Dependencies**:

   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx
   sudo usermod -aG docker $USER
   ```

2. **Clone Repository**:

   ```bash
   git clone https://github.com/your-username/alx_project_nexus.git
   cd alx_project_nexus
   ```

3. **Configure Environment**:

   ```bash
   cp .env.vps.example .env
   nano .env  # Edit with your values
   ```

### 3. Domain & SSL Setup

1. **Configure DNS**:

   ```bash
   # Point your domain to the VPS IP
   your-domain.com     -> <VPS_IP>
   ```

2. **Install SSL Certificate**:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

### 4. Deploy Application

1. **Start Services**:
   ```bash
   docker-compose -f docker-compose.vps.yml up -d
   ```

### 4. Monitoring Setup (Optional)

1. **Install Prometheus & Grafana**:
   ```bash
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm install monitoring prometheus-community/kube-prometheus-stack
   ```

## 📊 Pipeline Monitoring

### GitHub Actions Dashboard

- Monitor workflow runs in the Actions tab
- Review deployment status and logs
- Track code quality metrics

### ArgoCD Dashboard

- Visual deployment status
- Sync status and history
- Application health monitoring

### Kubernetes Monitoring

- Pod status and logs: `kubectl get pods -n production`
- Service status: `kubectl get svc -n production`
- Ingress status: `kubectl get ingress -n production`

## 🔄 Deployment Workflow

### Development Flow

1. **Feature Development**:

   ```bash
   git checkout -b feature/new-feature
   # Develop and test locally
   git push origin feature/new-feature
   # Create pull request to main
   ```

2. **Production Deployment**:

   ```bash
   # Merge to main branch
   git checkout main
   git merge feature/new-feature
   git push origin main
   # Automatic deployment to production
   ```

3. **Release Tagging**:
   ```bash
   # Create release tag
   git tag v1.0.0
   git push origin main --tags
   # Triggers release workflow
   ```

### Rollback Procedures

1. **Quick Rollback**:

   ```bash
   # Revert to previous image
   kubectl set image deployment/movie-recommendation-api api=ghcr.io/maven-13ttn/alx_project_nexus:previous-tag -n production
   ```

2. **GitOps Rollback**:
   ```bash
   # Revert GitOps repository changes
   git revert <commit-hash>
   git push origin main
   ```

## 🧪 Testing the Pipeline

### Local Testing

1. **Test Docker Build**:

   ```bash
   docker build -t test-image .
   docker run --rm test-image python manage.py test
   ```

2. **Test Docker Compose**:
   ```bash
   docker-compose up --build
   curl http://localhost:8000/api/health/
   ```

### Pipeline Testing

1. **Create Test PR**:

   ```bash
   git checkout -b test/pipeline-validation
   echo "# Test change" >> README.md
   git add README.md
   git commit -m "test: validate pipeline"
   git push origin test/pipeline-validation
   # Create PR to main and observe pipeline execution
   ```

2. **Monitor Deployment**:

   ```bash
   # Check production deployment (after merge to main)
   curl https://movierecommendation.app/api/health/

   # Check deployment status
   kubectl get pods -n production
   kubectl get ingress -n production
   ```

## 📈 Optimization Tips

### Performance

- **Parallel Jobs**: Most jobs run in parallel to reduce pipeline time
- **Caching**: Docker layer caching and pip dependency caching
- **Conditional Deployment**: Deploy only when necessary

### Security

- **Least Privilege**: Minimal required permissions
- **Secret Scanning**: Automated vulnerability detection
- **Image Scanning**: Container security scanning

### Reliability

- **Health Checks**: Comprehensive application health monitoring
- **Retry Logic**: Automated retry for transient failures
- **Rollback**: Quick rollback capabilities

## 🔧 Recent Improvements Applied

### Security & Reliability Fixes

1. **Docker Security**: Updated to Python 3.12, enhanced vulnerability scanning
2. **Removed Slack Webhook**: Eliminated external notification dependency
3. **Main Branch Only**: Simplified deployment to single branch strategy
4. **Specific Image Tags**: Replaced `latest` with commit-specific tags (`main-<sha>`)
5. **Enhanced Error Handling**: Added proper error handling throughout workflows
6. **External Health Check Script**: Moved inline Python to `scripts/health_check.py`
7. **Probe Improvements**: Added `failureThreshold`, `successThreshold`, and `timeoutSeconds`
8. **Git Configuration**: Using actor-based git configuration
9. **SSRF Protection**: URL validation in health check script
10. **Build Security**: Added `.dockerignore` to reduce attack surface

### Docker Security Enhancements

- **Base Image**: Updated from Python 3.11 to 3.12 for latest security patches
- **System Packages**: Replaced `netcat-traditional` with `netcat-openbsd`
- **CA Certificates**: Added for secure TLS connections
- **Dependency Validation**: Added `pip check` for integrity verification
- **Vulnerability Scanning**: Enhanced Trivy to fail on CRITICAL/HIGH vulnerabilities
- **Attack Surface**: Minimized Docker context with comprehensive `.dockerignore`

### Workflow Optimizations

- **Reduced Complexity**: Single branch deployment reduces merge conflicts
- **Better Error Messages**: Clear error reporting for failed operations
- **Maintainable Scripts**: External scripts for better code organization
- **Consistent Tagging**: Predictable image tagging strategy
- **Security First**: Pipeline fails on critical vulnerabilities

### Kubernetes Improvements

- **Probe Timeouts**: Added `timeoutSeconds` to prevent hanging health checks
- **Failure Thresholds**: Proper `failureThreshold` and `successThreshold` settings
- **Resource Management**: Optimized CPU and memory limits
- **High Availability**: Pod anti-affinity rules for production

This GitOps setup now provides a production-ready CI/CD pipeline with enhanced security, monitoring, and reliability best practices for your Movie Recommendation Backend project.th Check Script**: Moved inline Python to `scripts/health_check.py` 6. **Probe Improvements**: Added `failureThreshold` and `successThreshold` to Kubernetes probes 7. **Git Configuration**: Using actor-based git configuration instead of hardcoded values 8. **Dependency Security\*\*: Improved security check handling in dependency updates

### Workflow Optimizations

- **Reduced Complexity**: Single branch deployment reduces merge conflicts
- **Better Error Messages**: Clear error reporting for failed operations
- **Maintainable Scripts**: External scripts for better code organization
- **Consistent Tagging**: Predictable image tagging strategy

### Security Enhancements

- **No Hardcoded Credentials**: Removed placeholder credentials from templates
- **Proper Secret Management**: Templates require external secret injection
- **Vulnerability Handling**: Dependency updates properly report security issues

This GitOps setup now provides a production-ready CI/CD pipeline with enhanced security, monitoring, and reliability best practices for your Movie Recommendation Backend project.
