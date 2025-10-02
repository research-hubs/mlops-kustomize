# Traefik Ingress Controller (Kustomize)

This module deploys the Traefik ingress controller using Kustomize with environment-specific overlays.

## Structure

```
. ingress-controller/
├─ base/
│  ├─ kustomization.yaml          # sets namespace and includes all.yaml + ingress-dynamic.yaml
│  ├─ namespace.yaml              # Namespace manifest (ingress-controller)
│  ├─ all.yaml                    # Rendered from official Traefik Helm chart (with CRDs)
│  └─ ingress-dynamic.yaml        # Traefik IngressRoute rules (hosts)
├─ overlays/
│  ├─ development/
│  │  ├─ kustomization.yaml       # namespace: dev-ingress-controller
│  │  └─ ingress-dynamic.yaml     # dev-specific hosts (e.g., traefik.itdevops.id.vn)
│  └─ production/
│     ├─ kustomization.yaml       # namespace: prod-ingress-controller
│     └─ ingress-dynamic.yaml     # prod-specific hosts
└─ Makefile                       # helper targets
```

## Requirements
- kubectl
- A Kubernetes cluster
- Traefik CRDs (included in `base/all.yaml`)

## Quick start

Render manifests:
```bash
make -C ingress-controller build ENV=development
```

Deploy:
```bash
# Development
make -C ingress-controller deploy ENV=development

# Production
make -C ingress-controller deploy ENV=production
```

Check status:
```bash
make -C ingress-controller status ENV=development
```

Delete:
```bash
make -C ingress-controller delete ENV=development
```

## Customizing hosts
- Edit `base/ingress-dynamic.yaml` for defaults.
- Override per environment in `overlays/<env>/ingress-dynamic.yaml`.

Example route (from dev overlay):
```yaml
apiVersion: traefik.io/v1alpha1
kind: IngressRoute
metadata:
  name: traefik-dashboard
spec:
  entryPoints:
    - web
    - websecure
  routes:
    - match: Host(`traefik.itdevops.id.vn`) && PathPrefix(`/`)
      kind: Rule
      services:
        - name: traefik
          port: 9000
  tls: {}
```

## Notes
- The `all.yaml` file was generated from the official Traefik Helm chart with CRDs included.
- Adjust service types, entrypoints, middlewares, and TLS settings as needed.


