# Auth Gateway

FastAPI-based authentication gateway that sits between oauth2-proxy and ClearML webserver to provide seamless authentication flow.

## Architecture

```
Client → oauth2-proxy → auth-gateway (FastAPI) → clearml-webserver
```

## Features

- **OAuth2 Integration**: Handles OAuth2 callback from oauth2-proxy
- **Authentication Check**: Validates user authentication before proxying to ClearML
- **Request Proxying**: Forwards authenticated requests to ClearML webserver
- **Health Checks**: Provides health and readiness endpoints
- **Logout Handling**: Manages user logout flow

## Configuration

### Environment Variables

- `CLEARML_WEBSERVER_URL`: URL of the ClearML webserver (default: `http://webserver:8080`)
- `OAUTH2_PROXY_URL`: URL of the oauth2-proxy service (default: `http://oauth2-proxy:4180`)
- `LOG_LEVEL`: Logging level (default: `INFO`)

### Endpoints

- `GET /` - Redirects to oauth2-proxy for authentication
- `GET /oauth2/callback` - Handles OAuth2 callback
- `GET /auth` - Checks authentication status
- `GET /logout` - Handles logout
- `GET /health` - Health check endpoint
- `GET /ready` - Readiness check endpoint
- `* /{path:path}` - Proxies authenticated requests to ClearML

## Usage

### Deploy

```bash
# Development
make deploy ENV=development

# Production
make deploy ENV=production
```

### Restart

```bash
make restart ENV=development
```

### Status

```bash
make status ENV=development
```

### Delete

```bash
make delete ENV=development
```

## Integration with oauth2-proxy

The auth gateway expects oauth2-proxy to be configured with:

- `--upstream=http://clearml-auth-gateway:8000` (pointing to this service)
- `--redirect-url=http://clearml-auth-gateway:8000/oauth2/callback`
- `--whitelist-domain=clearml-auth-gateway`

## Development

The FastAPI application is stored in a ConfigMap and mounted into the container. For development, you can modify the `main.py` content in the ConfigMap.
