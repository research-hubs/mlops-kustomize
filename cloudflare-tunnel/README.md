# Cloudflare Tunnel Kustomize

This directory contains Kustomize configurations for deploying Cloudflare Tunnel (cloudflared) to Kubernetes.

## Structure

```
cloudflare-tunnel/
├── base/                    # Base configuration
│   ├── namespace.yaml       # Namespace definition
│   ├── configmap.yaml       # Cloudflared configuration
│   ├── secret.yaml          # Tunnel credentials
│   ├── serviceaccount.yaml  # Service account
│   ├── deployment.yaml      # Cloudflared deployment
│   └── kustomization.yaml   # Base kustomization
├── overlays/
│   ├── development/         # Development environment
│   │   ├── kustomization.yaml
│   │   ├── configmap-patch.yaml
│   │   ├── secret-patch.yaml
│   │   └── deployment-patch.yaml
│   └── production/          # Production environment
│       ├── kustomization.yaml
│       ├── configmap-patch.yaml
│       ├── secret-patch.yaml
│       └── deployment-patch.yaml
├── Makefile                 # Deployment commands
└── README.md               # This file
```

## Prerequisites

1. **Cloudflare Account**: You need a Cloudflare account with access to Cloudflare Tunnel
2. **Tunnel Setup**: Create a tunnel in your Cloudflare dashboard and get:
   - Account Tag
   - Tunnel ID
   - Tunnel Secret
3. **Kubernetes Cluster**: A running Kubernetes cluster with kubectl configured

## Configuration

### 1. Update Tunnel Credentials

Edit the secret files in the overlays to include your actual tunnel credentials:

**Development** (`overlays/development/secret-patch.yaml`):

```yaml
stringData:
  credentials.json: |
    {
      "AccountTag": "YOUR_DEV_ACCOUNT_TAG",
      "TunnelID": "YOUR_DEV_TUNNEL_ID",
      "TunnelSecret": "YOUR_DEV_TUNNEL_SECRET"
    }
```

**Production** (`overlays/production/secret-patch.yaml`):

```yaml
stringData:
  credentials.json: |
    {
      "AccountTag": "YOUR_PROD_ACCOUNT_TAG",
      "TunnelID": "YOUR_PROD_TUNNEL_ID",
      "TunnelSecret": "YOUR_PROD_TUNNEL_SECRET"
    }
```

### 2. Configure Ingress Rules

Update the ConfigMap files to define your ingress rules:

**Development** (`overlays/development/configmap-patch.yaml`):

```yaml
data:
  config.yaml: |
    tunnel: "dev-tunnel"
    ingress:
      - hostname: dev.example.com
        service: http://dev-service:80
      - service: http_status:404
```

**Production** (`overlays/production/configmap-patch.yaml`):

```yaml
data:
  config.yaml: |
    tunnel: "prod-tunnel"
    ingress:
      - hostname: example.com
        service: http://prod-service:80
      - hostname: api.example.com
        service: http://api-service:80
      - service: http_status:404
```

## Deployment

### Using Makefile

```bash
# Deploy to development (default)
make deploy ENV=development

# Deploy to production
make deploy ENV=production

# Deploy base configuration
make deploy ENV=base

# Delete from development
make delete ENV=development

# Delete from production
make delete ENV=production

# View resources
make status ENV=development
make status ENV=production

# View logs
make logs ENV=development
make logs ENV=production

# Check tunnel status
make tunnel-status ENV=development
make tunnel-status ENV=production

# Build configuration (dry-run)
make build ENV=development

# Show differences
make diff ENV=development
```

### Using kubectl directly

```bash
# Deploy to development
kubectl apply -k overlays/development

# Deploy to production
kubectl apply -k overlays/production

# Delete from development
kubectl delete -k overlays/development

# Delete from production
kubectl delete -k overlays/production
```

## Verification

After deployment, check the status:

```bash
# Check pods
kubectl get pods -n dev-cloudflare-tunnel
kubectl get pods -n prod-cloudflare-tunnel

# Check logs
kubectl logs -n dev-cloudflare-tunnel deployment/dev-cloudflare-tunnel
kubectl logs -n prod-cloudflare-tunnel deployment/prod-cloudflare-tunnel

# Check tunnel status
kubectl exec -n dev-cloudflare-tunnel deployment/dev-cloudflare-tunnel -- cloudflared tunnel info

# Or use Makefile commands
make status ENV=development
make logs ENV=development
make tunnel-status ENV=development
```

## Customization

### Resource Limits

Adjust resource limits in the deployment patch files:

```yaml
# overlays/development/deployment-patch.yaml
spec:
  template:
    spec:
      containers:
        - name: cloudflare-tunnel
          resources:
            limits:
              cpu: 50m
              memory: 64Mi
            requests:
              cpu: 25m
              memory: 32Mi
```

### Replica Count

Change replica count in the kustomization files:

```yaml
# overlays/production/kustomization.yaml
replicas:
  - name: cloudflare-tunnel
    count: 3
```

### Additional Configuration

You can add more configuration options to the ConfigMap:

- `warp-routing.enabled`: Enable/disable WARP routing
- `metrics`: Configure metrics endpoint
- `ingress`: Define routing rules

## Troubleshooting

1. **Tunnel not connecting**: Check credentials in the secret
2. **Ingress not working**: Verify ingress rules in ConfigMap
3. **Pod not starting**: Check logs and resource limits
4. **DNS issues**: Ensure DNS is properly configured in Cloudflare

## Security Notes

- Store tunnel credentials securely (consider using external secret management)
- Use least privilege principle for service accounts
- Regularly rotate tunnel secrets
- Monitor tunnel logs for suspicious activity
