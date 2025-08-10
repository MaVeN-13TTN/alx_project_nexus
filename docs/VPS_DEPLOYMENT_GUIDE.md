# VPS Deployment Guide for Nexus Movie Recommendation Backend

## 🏗️ Multi-Environment VPS Setup

This guide covers deploying **both staging and production** environments on a single VPS using domain-based routing.

### 1. Server Specifications (Contabo VPS)

- **OS**: Ubuntu 20.04/22.04 LTS
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 50GB+ SSD
- **CPU**: 2+ cores
- **IP**: 161.97.116.5

### 2. DNS Configuration ✅ COMPLETED

```bash
nexus.k1nyanjui.com → 161.97.116.5 (Production)
staging-nexus.k1nyanjui.com → 161.97.116.5 (Staging)
ndungu.k1nyanjui.com → 161.97.116.5
k1nyanjui.com → 161.97.116.5
```

## 🔧 Installation Steps

### Step 1: Initial Server Setup

```bash
# Connect to your VPS
ssh deploy@161.97.116.5

# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y \
    docker.io \
    docker-compose \
    nginx \
    certbot \
    python3-certbot-nginx \
    git \
    curl \
    htop \
    ufw

# Add deploy user to docker group
sudo usermod -aG docker deploy

# Logout and login again for group changes to take effect
exit
ssh deploy@161.97.116.5
```

### Step 2: Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Step 3: Deploy Multi-Environment Application

```bash
# Navigate to projects directory
cd /home/deploy/projects

# Clone the repository (if not already done)
git clone https://github.com/MaVeN-13TTN/alx_project_nexus.git nexus
cd nexus

# Make deployment script executable
chmod +x scripts/deploy-vps.sh
chmod +x scripts/manage-environments.sh

# Run the deployment script
./scripts/deploy-vps.sh
```

### Step 4: Configure Environment Variables

```bash
# Edit the environment file
nano /home/deploy/projects/nexus/.env

# Fill in these required values:
DJANGO_SETTINGS_MODULE=config.settings.multi_environment
SECRET_KEY=your_very_long_secret_key_minimum_50_characters
DB_USER=prod_user
DB_PASSWORD=your_secure_password_here
TMDB_API_KEY=your_tmdb_api_key_here
ALLOWED_HOSTS=nexus.k1nyanjui.com,staging-nexus.k1nyanjui.com,161.97.116.5,localhost
```

### Step 5: SSL Certificate Setup

```bash
# Option 1: Let's Encrypt (Recommended for production)
sudo certbot --nginx -d nexus.k1nyanjui.com

# Option 2: Self-signed certificates (for testing)
# This is handled automatically by the deployment script
```

### Step 6: Start Services

```bash
cd /home/deploy/projects/nexus

# Start all services (serves both environments)
docker-compose -f docker-compose.vps.yml up -d

# Check status
docker-compose -f docker-compose.vps.yml ps

# View logs
docker-compose -f docker-compose.vps.yml logs -f
```

## 📁 Directory Structure After Deployment

```
/home/deploy/projects/
├── nexus/                              # Main application
│   ├── .env                           # Environment variables
│   ├── docker-compose.vps.yml         # Production compose file
│   ├── nginx/nexus.conf               # Nginx configuration
│   ├── scripts/
│   │   ├── deploy-vps.sh              # Deployment script
│   │   └── manage-nexus.sh            # Management script
│   ├── data/postgres/                 # Database data
│   ├── logs/                          # Application logs
│   └── backups/                       # Database backups
├── nginx-proxy/                       # Nginx configuration
│   ├── conf.d/nexus.conf              # Site configuration
│   └── ssl/                           # SSL certificates
└── ndungu/                            # Other projects
```

## 🔄 Management Operations

### Daily Operations

```bash
# Check application status
docker-compose -f docker-compose.vps.yml ps

# View logs
docker-compose -f docker-compose.vps.yml logs -f

# Restart services
docker-compose -f docker-compose.vps.yml restart

# Health check
curl -f https://nexus.k1nyanjui.com/api/health/
curl -f https://staging-nexus.k1nyanjui.com/api/health/
```

### Updates and Maintenance

```bash
# Update application
./scripts/deploy-vps.sh

# Create database backup
docker-compose -f docker-compose.vps.yml exec db pg_dump -U prod_user movie_recommendation_prod > backup_$(date +%Y%m%d).sql

# Clean up Docker resources
docker system prune -f
```

### Troubleshooting

```bash
# Access application shell
./scripts/manage-nexus.sh shell web

# Access database shell
./scripts/manage-nexus.sh shell db

# View specific service logs
./scripts/manage-nexus.sh logs web
./scripts/manage-nexus.sh logs db
```

## 🌐 URLs and Access

- **Production URL**: https://nexus.k1nyanjui.com
- **Staging URL**: https://staging-nexus.k1nyanjui.com
- **Health Check**: 
  - Production: https://nexus.k1nyanjui.com/api/health/
  - Staging: https://staging-nexus.k1nyanjui.com/api/health/
- **Admin Panel**: 
  - Production: https://nexus.k1nyanjui.com/admin/
  - Staging: https://staging-nexus.k1nyanjui.com/admin/

## 🔒 Security Considerations

### 1. Environment Variables

- Never commit `.env` files to git
- Use strong, unique passwords
- Rotate secrets regularly

### 2. SSL/TLS

- Use Let's Encrypt for production SSL certificates
- Enable HSTS headers (configured in Nginx)
- Force HTTPS redirects

### 3. Database Security

- Database is only accessible within Docker network
- Regular backups are created
- Use strong database passwords

### 4. Firewall

- Only necessary ports are open (22, 80, 443)
- SSH access should use key-based authentication
- Consider changing SSH port from default 22

## 📊 Monitoring and Logs

### Application Logs

```bash
# Real-time logs
docker-compose -f docker-compose.vps.yml logs -f

# Service-specific logs
docker-compose -f docker-compose.vps.yml logs web
docker-compose -f docker-compose.vps.yml logs db
```

### Environment Detection

The application automatically detects the environment based on the domain:
- `nexus.k1nyanjui.com` → Production database
- `staging-nexus.k1nyanjui.com` → Staging database

Both use the same codebase but separate data stores.

### System Monitoring

```bash
# Resource usage
htop

# Disk usage
df -h

# Docker container stats
docker stats
```

## 🚨 Backup Strategy

### Automated Backups

```bash
# Add to crontab for daily backups
crontab -e

# Add this line for daily backup at 2 AM
0 2 * * * cd /home/deploy/projects/nexus && ./scripts/manage-nexus.sh backup
```

### Manual Backup

```bash
# Create immediate backup
./scripts/manage-nexus.sh backup

# List existing backups
ls -la /home/deploy/projects/nexus/backups/
```

## 🔄 CI/CD Integration (Optional)

Your GitHub Actions workflows can deploy to this VPS by:

1. Adding VPS SSH credentials to GitHub Secrets
2. Using SSH deployment actions
3. Pulling latest images and restarting services

Example GitHub Actions deployment step:

```yaml
- name: Deploy to VPS
  uses: appleboy/ssh-action@v0.1.5
  with:
    host: 161.97.116.5
    username: deploy
    key: ${{ secrets.VPS_SSH_KEY }}
    script: |
      cd /home/deploy/projects/nexus
      ./scripts/manage-nexus.sh update
```

## 📞 Support and Troubleshooting

### Common Issues

1. **Port 8000 already in use**

   ```bash
   sudo lsof -i :8000
   ./scripts/manage-nexus.sh stop
   ./scripts/manage-nexus.sh start
   ```

2. **Database connection errors**

   ```bash
   ./scripts/manage-nexus.sh logs db
   ./scripts/manage-nexus.sh restart db
   ```

3. **SSL certificate issues**
   ```bash
   sudo certbot renew
   sudo nginx -t
   sudo systemctl reload nginx
   ```

### Health Checks

```bash
# Test application directly
curl -f http://localhost:8000/api/health/

# Test through Nginx
curl -f -k https://nexus.k1nyanjui.com/api/health/

# Check all containers
docker ps
```

This setup provides a production-ready multi-environment deployment serving both staging and production from a single VPS with proper security, monitoring, and management capabilities.
