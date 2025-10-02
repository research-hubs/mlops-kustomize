# Keycloak Kustomize Configuration

This directory contains Kustomize configurations for deploying Keycloak with PostgreSQL database across multiple environments.

## Structure

```
keycloak/
├── base/                           # Base configuration
│   ├── kustomization.yaml         # Base kustomization
│   ├── namespace.yaml             # Namespace definition
│   ├── configmap.yaml             # Configuration values
│   ├── deployment.yaml            # Keycloak deployment
│   ├── service.yaml               # Keycloak service
│   ├── db-deployment.yaml         # PostgreSQL deployment
│   ├── db-service.yaml            # PostgreSQL service
│   ├── pvc-db.yaml                # Database PVC
│   └── pvc-data.yaml              # Keycloak data PVC
├── overlays/
│   ├── development/               # Development environment
│   │   ├── kustomization.yaml
│   │   ├── configmap-patch.yaml
│   │   └── deployment-patch.yaml
│   └── production/                # Production environment
│       ├── kustomization.yaml
│       ├── configmap-patch.yaml
│       └── deployment-patch.yaml
├── Makefile                       # Build and deployment commands
└── README.md                      # This file
```

## Features

- **Environment Isolation**: Separate namespaces for each environment
- **No Secrets**: All configuration stored in ConfigMaps
- **Resource Management**: Proper resource requests and limits
- **Health Checks**: Liveness and readiness probes
- **Persistent Storage**: PVCs for database and Keycloak data
- **Clean Labels**: Proper Kubernetes labels for organization

## Quick Start

### Environment-based Deployment

The Makefile supports three environments with separate namespaces:

- **base**: `keycloak` namespace
- **development**: `dev-keycloak` namespace
- **production**: `prod-keycloak` namespace

### Usage

```bash
# Show help and current environment
make help

# Deploy to development (default)
make deploy ENV=development

# Deploy to production
make deploy ENV=production

# Deploy base configuration
make deploy ENV=base

# Check status
make status ENV=development

# View logs
make logs ENV=production

# Build manifests without deploying
make build ENV=development

# Show diff against live cluster
make diff ENV=production

# Delete deployment
make delete ENV=development
```

## Configuration

### Base Configuration

- Keycloak 26.0.7
- PostgreSQL 16.8
- ConfigMap with all environment variables
- Persistent storage for database and Keycloak data

### Environment Differences

| Environment     | Namespace       | Replicas | Resources | Hostname                  |
| --------------- | --------------- | -------- | --------- | ------------------------- |
| **base**        | `keycloak`      | 1        | Standard  | `keycloak.itdevops.id.vn` |
| **development** | `dev-keycloak`  | 1        | Lower     | `keycloak.itdevops.id.vn` |
| **production**  | `prod-keycloak` | 2        | Higher    | `keycloak.itdevops.id.vn` |

## Customization

### Modify Configuration

1. **Base changes**: Edit files in `base/` directory
2. **Environment-specific**: Edit patch files in `overlays/{environment}/`
3. **New environment**: Create new directory in `overlays/` with kustomization.yaml

### Environment Variables

All configuration is stored in ConfigMaps. Key variables:

- `KC_DB_*`: Database connection settings
- `KC_BOOTSTRAP_ADMIN_*`: Admin user credentials
- `KC_HOSTNAME_*`: Keycloak hostname settings
- `POSTGRES_*`: PostgreSQL settings

## Security Note

This configuration stores sensitive data (passwords) in ConfigMaps for simplicity. In production, consider using:

- Kubernetes Secrets
- External secret management (e.g., HashiCorp Vault)
- Operator-based secret management

## Troubleshooting

```bash
# Check status for specific environment
make status ENV=development

# Check all resources in namespace
kubectl get all -n dev-keycloak
kubectl get all -n prod-keycloak

# Check PVCs
kubectl get pvc -n dev-keycloak
kubectl get pvc -n prod-keycloak

# Check events
kubectl get events -n dev-keycloak --sort-by='.lastTimestamp'
kubectl get events -n prod-keycloak --sort-by='.lastTimestamp'

# Describe problematic resources
kubectl describe <resource-type> <resource-name> -n dev-keycloak
kubectl describe <resource-type> <resource-name> -n prod-keycloak

# Show diff before applying changes
make diff ENV=development
```

## Examples

### Deploy Development Environment

```bash
# Deploy to development
make deploy ENV=development

# Check if everything is running
make status ENV=development

# View logs
make logs ENV=development
```

### Deploy Production Environment

```bash
# Deploy to production
make deploy ENV=production

# Check status
make status ENV=production

# View logs
make logs ENV=production
```

### Clean Up

```bash
# Delete development environment
make delete ENV=development

# Delete production environment
make delete ENV=production
```
