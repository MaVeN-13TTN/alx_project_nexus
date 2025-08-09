# Archived Kubernetes/ArgoCD Configuration

This directory contains the original Kubernetes and ArgoCD configuration files that were initially designed for this project. They have been archived in favor of a Docker Compose deployment approach which is more suitable for single VPS deployments.

## Contents

- `gitops/` - Original GitOps configuration with ArgoCD
  - `argocd-applications.yaml` - ArgoCD application definitions
  - `staging/` - Staging environment Kubernetes manifests
  - `production/` - Production environment Kubernetes manifests

## Why Archived?

The project has been refactored to use **Docker Compose** instead of Kubernetes for the following reasons:

1. **Simpler Setup** - No Kubernetes cluster required
2. **Resource Efficient** - Better for single-server deployments
3. **Easier Management** - Direct Docker commands
4. **Cost Effective** - No additional orchestration overhead
5. **VPS Friendly** - Optimized for single VPS deployment

## If You Want to Use Kubernetes

If you prefer to deploy with Kubernetes and ArgoCD, you can:

1. Restore these files to the project root:

   ```bash
   mv archive/kubernetes/gitops ./
   ```

2. Follow the original Kubernetes setup instructions in the archived documentation

3. Update the CI/CD workflows to deploy to Kubernetes instead of Docker Compose

## Current Deployment Approach

The project now uses:

- **Docker Compose** for container orchestration
- **VPS deployment** with automated scripts
- **GitHub Actions** for CI/CD
- **Direct container management** instead of Kubernetes

See the main [VPS Deployment Guide](../../docs/VPS_DEPLOYMENT_GUIDE.md) for current deployment instructions.

## Kubernetes Benefits (For Reference)

While we chose Docker Compose for simplicity, Kubernetes would provide:

- Auto-scaling capabilities
- Self-healing containers
- Advanced networking features
- Multi-node deployment
- Built-in load balancing
- Rolling updates with zero downtime

Consider Kubernetes if you need to scale beyond a single server or require enterprise-grade orchestration features.
