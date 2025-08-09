# GitHub Secrets & ArgoCD Setup Guide

## GitHub Repository Secrets

Navigate to your repository → Settings → Secrets and variables → Actions

### Required Secrets

# GitHub Secrets & Docker Compose Setup Guide

## GitHub Repository Secrets

Navigate to your repository → Settings → Secrets and variables → Actions

### Required Secrets

```
GH_TOKEN                 # GitHub token for repository and package access
```

**Note**: The CI/CD pipeline uses GitHub Container Registry (ghcr.io) and GitHub's built-in features for notifications. The GH_TOKEN is required for container registry access and Docker deployment operations.

### Setting Up Secrets

**GitHub Token**: Set up GH_TOKEN in repository secrets with appropriate permissions.

The pipeline uses:

- GitHub Container Registry (ghcr.io) for Docker images
- GitHub Security tab for vulnerability reports
- GitHub job summaries for deployment status
- Docker Compose deployment pattern for VPS hosting

## Docker Compose Production Deployment

### 1. Server Prerequisites

```bash
# Install Docker and Docker Compose
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose nginx certbot python3-certbot-nginx git curl
sudo usermod -aG docker $USER
```

### 2. Deploy Application

```bash
# Clone repository to your VPS
git clone https://github.com/your-username/alx_project_nexus.git
cd alx_project_nexus

# Copy environment template
cp .env.vps.example .env

# Edit environment variables
nano .env

# Deploy with Docker Compose
docker-compose -f docker-compose.vps.yml up -d
```

### 3. Environment Configuration

```bash
# Required environment variables in .env file:
DB_USER=movie_api_user
DB_PASSWORD=your_secure_password_here
SECRET_KEY=your_django_secret_key_here
TMDB_API_KEY=your_tmdb_api_key_here
ALLOWED_HOSTS=your_domain.com,your_ip_address
```

## Quick Setup Commands

```bash
# 1. Configure GH_TOKEN in repository secrets with required permissions

# 2. On your VPS, deploy the application
git clone https://github.com/your-username/alx_project_nexus.git
cd alx_project_nexus
cp .env.vps.example .env
# Edit .env with your values
docker-compose -f docker-compose.vps.yml up -d
```

## Verification

1. **Check GitHub Actions**: Push to repository and verify workflow runs
2. **Check Docker Services**: Verify containers are running
3. **Check Application**: Test the deployed application

```bash
# Check running containers
docker-compose -f docker-compose.vps.yml ps

# Check application health
curl -f http://localhost:8000/api/health/
```

**Note**: The CI/CD pipeline uses GitHub Container Registry (ghcr.io) and GitHub's built-in features for notifications. The GH_TOKEN is required for container registry access and GitOps operations.

### Setting Up Secrets

**GitHub Token**: Set up GH_TOKEN in repository secrets with appropriate permissions.

The pipeline uses:

- GitHub Container Registry (ghcr.io) for Docker images
- GitHub Security tab for vulnerability reports
- GitHub job summaries for deployment status
- GitOps pattern with direct git commits for deployment

## ArgoCD Application Setup

### 1. Install ArgoCD

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. Access ArgoCD UI

```bash
# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 3. Create Application

```yaml
# argocd-app.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: movie-recommendation-staging
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-username/alx_project_nexus
    targetRevision: HEAD
    path: gitops/staging
  destination:
    server: https://kubernetes.default.svc
    namespace: movie-recommendation-staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Apply the application:

```bash
kubectl apply -f argocd-app.yaml
```

### 4. Production Application

```yaml
# argocd-app-prod.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: movie-recommendation-production
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/your-username/alx_project_nexus
    targetRevision: HEAD
    path: gitops/production
  destination:
    server: https://kubernetes.default.svc
    namespace: movie-recommendation-production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

## Quick Setup Commands

```bash
# 1. Configure GH_TOKEN in repository secrets with required permissions

# 2. Create namespaces
kubectl create namespace movie-recommendation-staging
kubectl create namespace movie-recommendation-production

# 3. Apply ArgoCD applications
kubectl apply -f argocd-app.yaml
kubectl apply -f argocd-app-prod.yaml
```

## Verification

1. **Check GitHub Actions**: Push to repository and verify workflow runs
2. **Check ArgoCD**: Verify applications are synced and healthy
3. **Check Deployments**: Verify pods are running in both namespaces

```bash
kubectl get pods -n movie-recommendation-staging
kubectl get pods -n movie-recommendation-production
```
