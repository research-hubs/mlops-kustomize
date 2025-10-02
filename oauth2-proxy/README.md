oauth2-proxy (Kustomize)

Protect ClearML Web UI behind Keycloak OIDC using oauth2-proxy.

Layout

```
oauth2-proxy/
  base/
    deployment.yaml
    service.yaml
    kustomization.yaml
  overlays/
    development/
      deployment-patch.yaml
      kustomization.yaml
```

Prerequisites

- Ingress Controller (Traefik) routing `clearml.itdevops.id.vn` to Service `oauth2-proxy` in namespace `dev-oauth2-proxy`.
- Cloudflare Tunnel (optional) forwarding your domain to Traefik.
- Keycloak realm `mlops`, client `clearml` (confidential), redirect URI:
  - `https://clearml.itdevops.id.vn/oauth2/callback`

Configure

- Edit `overlays/development/deployment-patch.yaml`:
  - `--oidc-issuer-url=https://keycloak.itdevops.id.vn/realms/mlops`
  - `--client-id=clearml`
  - `--client-secret=<your_secret>`
  - `--redirect-url=https://clearml.itdevops.id.vn/oauth2/callback`

Deploy

```bash
make -C oauth2-proxy deploy ENV=development
```

Verify

- Open `https://clearml.itdevops.id.vn` → redirected to Keycloak → back to ClearML.
- Logs:

```bash
make -C oauth2-proxy logs ENV=development
```

Notes

- oauth2-proxy adds an external auth layer; ClearML Community still requires its own login (fixed_users / credentials.json).
- Tune cookies:
  - `--cookie-domain=.itdevops.id.vn`
  - `--whitelist-domain=.itdevops.id.vn`
