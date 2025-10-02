# MLOps Platform - Hướng dẫn cài đặt toàn bộ hệ thống

## 🎯 Tổng quan

Hệ thống MLOps platform bao gồm các thành phần chính:

- **ClearML**: Platform quản lý ML experiments và model tracking
- **ClearML Agent**: Worker nodes để chạy training jobs
- **MinIO**: Object storage cho artifacts và datasets
- **Keycloak**: Identity và access management
- **Ingress Controller**: Load balancer và SSL termination
- **Cloudflare Tunnel**: Secure external access

## 🏗️ Kiến trúc hệ thống

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Cloudflare      │────│ Ingress          │────│ Applications    │
│ Tunnel          │    │ Controller       │    │ - ClearML       │
│                 │    │ (Traefik/Nginx)  │    │ - MinIO         │
└─────────────────┘    └──────────────────┘    │ - Keycloak      │
                                               └─────────────────┘
                                                        │
                                               ┌─────────────────┐
                                               │ Storage         │
                                               │ - PostgreSQL    │
                                               │ - MongoDB       │
                                               │ - Redis         │
                                               │ - Elasticsearch │
                                               └─────────────────┘
```

## 📋 Prerequisites

### Hệ thống yêu cầu

- **Kubernetes cluster** (v1.20+)
- **kubectl** đã cấu hình
- **Kustomize** (tích hợp trong kubectl v1.14+)
- **Make** (Windows/Linux/macOS)
- **Domain** được quản lý bởi Cloudflare

### Tài nguyên tối thiểu

| Environment | CPU | RAM | Storage |
|-------------|-----|-----|---------|
| Development | 4 cores | 8GB | 50GB |
| Production | 8 cores | 16GB | 200GB |

## 🔧 Cấu hình cần thay đổi

### 1. Domain Configuration

**Hiện tại sử dụng**: `itdevops.id.vn`

**Cần thay đổi tại các file**:

```bash
# Cloudflare Tunnel
cloudflare-tunnel/overlays/development/configmap-patch.yaml
cloudflare-tunnel/overlays/production/configmap-patch.yaml

# Ingress Controller
ingress-controller/overlays/development/clearml-ingress.yaml
ingress-controller/overlays/development/minio-ingress.yaml
ingress-controller/overlays/development/keycloak-ingress.yaml

# Keycloak
keycloak/overlays/development/configmap-patch.yaml
keycloak/overlays/production/configmap-patch.yaml

# MinIO
minio-tenant/overlays/development/minio-config.yaml
minio-tenant/overlays/production/minio-config.yaml

# Test files
test/clearml_minio_test.py
```

**Domains được sử dụng**:
- `clearml.YOUR-DOMAIN.com` - ClearML Web UI
- `api-clearml.YOUR-DOMAIN.com` - ClearML API
- `minio-console.YOUR-DOMAIN.com` - MinIO Console
- `minio.YOUR-DOMAIN.com` - MinIO API
- `keycloak.YOUR-DOMAIN.com` - Keycloak Authentication

### 2. Credentials & Secrets

#### MinIO Credentials
```bash
# Development
minio-tenant/overlays/development/minio-config.yaml
accessKey: "dev-minioadmin"
secretKey: "dev-minioadmin"

# Production  
minio-tenant/overlays/production/minio-config.yaml
accessKey: "prod-minioadmin"
secretKey: "prod-minioadmin"
```

#### ClearML Credentials
```bash
# Development
clearml/overlays/development/apiserver-config.yaml
username: "admin"
password: "admin"
```

#### Keycloak Credentials
```bash
# Được cấu hình trong ConfigMap, cần thay đổi:
# - Database passwords
# - Admin passwords
# - Client secrets
```

### 3. Namespaces

| Service | Development | Production |
|---------|-------------|------------|
| ClearML | `dev-clearml` | `prod-clearml` |
| ClearML Agent | `dev-clearml-agent` | `prod-clearml-agent` |
| MinIO Operator | `dev-minio-operator` | `prod-minio-operator` |
| MinIO Tenant | `dev-minio-tenant` | `prod-minio-tenant` |
| Keycloak | `dev-keycloak` | `prod-keycloak` |
| Ingress | `dev-ingress-controller` | `prod-ingress-controller` |
| Cloudflare | `dev-cloudflare-tunnel` | `prod-cloudflare-tunnel` |

## 🚀 Hướng dẫn cài đặt

### Bước 1: Chuẩn bị Cloudflare Tunnel

#### 1.1 Cài đặt cloudflared

**Linux/macOS:**
```bash
# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# macOS
brew install cloudflared
```

**Windows:**
```powershell
# PowerShell
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"
Move-Item "cloudflared.exe" "C:\Windows\System32\cloudflared.exe"
```

#### 1.2 Tạo Tunnel

```bash
# Đăng nhập Cloudflare
cloudflared tunnel login

# Tạo tunnel
cloudflared tunnel create mlops-tunnel

# Ghi lại Tunnel ID (ví dụ: f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20)
cloudflared tunnel list
```

#### 1.3 Cấu hình DNS

```bash
# Tạo DNS records
cloudflared tunnel route dns mlops-tunnel clearml.YOUR-DOMAIN.com
cloudflared tunnel route dns mlops-tunnel api-clearml.YOUR-DOMAIN.com
cloudflared tunnel route dns mlops-tunnel minio-console.YOUR-DOMAIN.com
cloudflared tunnel route dns mlops-tunnel minio.YOUR-DOMAIN.com
cloudflared tunnel route dns mlops-tunnel keycloak.YOUR-DOMAIN.com
```

#### 1.4 Cập nhật Tunnel Credentials

```bash
# Lấy credentials từ file
cat ~/.cloudflared/TUNNEL-ID.json

# Cập nhật vào file
# cloudflare-tunnel/overlays/development/secret-patch.yaml
```

### Bước 2: Thay đổi Domain trong tất cả file

#### 2.1 Script tự động thay đổi domain

```bash
#!/bin/bash
OLD_DOMAIN="itdevops.id.vn"
NEW_DOMAIN="YOUR-DOMAIN.com"

# Tìm và thay thế trong tất cả file
find . -type f \( -name "*.yaml" -o -name "*.yml" -o -name "*.py" \) -exec sed -i "s/$OLD_DOMAIN/$NEW_DOMAIN/g" {} +

echo "Đã thay đổi domain từ $OLD_DOMAIN thành $NEW_DOMAIN"
```

#### 2.2 Kiểm tra các file đã thay đổi

```bash
# Kiểm tra domain mới
grep -r "YOUR-DOMAIN.com" . --include="*.yaml" --include="*.yml"
```

### Bước 3: Cài đặt theo thứ tự

#### 3.1 MinIO Operator (Bước đầu tiên)

```bash
cd minio-operator
make deploy ENV=development
make status ENV=development
```

#### 3.2 MinIO Tenant

```bash
cd ../minio-tenant
make deploy ENV=development
make status ENV=development

# Kiểm tra MinIO console
make pf-console ENV=development
# Truy cập: https://localhost:9001
```

#### 3.3 Keycloak

```bash
cd ../keycloak
make deploy ENV=development
make status ENV=development
make logs ENV=development
```

#### 3.4 ClearML

```bash
cd ../clearml
make deploy ENV=development
make status ENV=development
```

#### 3.5 ClearML Agent

```bash
cd ../clearml-agent
make deploy ENV=development
make status ENV=development
```

#### 3.6 Ingress Controller

```bash
cd ../ingress-controller
make deploy ENV=development
make status ENV=development
```

#### 3.7 Cloudflare Tunnel

```bash
cd ../cloudflare-tunnel
make deploy ENV=development
make status ENV=development
make logs ENV=development
```

### Bước 4: Xác minh cài đặt

#### 4.1 Kiểm tra tất cả pods

```bash
# Kiểm tra tất cả namespaces
kubectl get pods --all-namespaces | grep -E "(dev-|prod-)"

# Kiểm tra services
kubectl get svc --all-namespaces | grep -E "(dev-|prod-)"
```

#### 4.2 Test connectivity

```bash
# Test DNS resolution
nslookup clearml.YOUR-DOMAIN.com
nslookup minio-console.YOUR-DOMAIN.com
nslookup keycloak.YOUR-DOMAIN.com

# Test HTTP access
curl -I https://clearml.YOUR-DOMAIN.com
curl -I https://minio-console.YOUR-DOMAIN.com
curl -I https://keycloak.YOUR-DOMAIN.com
```

#### 4.3 Test ClearML integration

```bash
cd test
python clearml_minio_test.py
```

## 🔒 Cấu hình bảo mật

### 1. Thay đổi passwords mặc định

#### MinIO
```yaml
# minio-tenant/overlays/production/minio-config.yaml
accessKey: "STRONG-ACCESS-KEY"
secretKey: "STRONG-SECRET-KEY-WITH-32-CHARS"
```

#### ClearML
```yaml
# clearml/overlays/production/apiserver-config.yaml
username: "admin"
password: "STRONG-PASSWORD"
```

#### Keycloak
```yaml
# keycloak/overlays/production/configmap-patch.yaml
KC_BOOTSTRAP_ADMIN_USERNAME: "admin"
KC_BOOTSTRAP_ADMIN_PASSWORD: "STRONG-PASSWORD"
```

### 2. SSL Certificates

#### Development (Self-signed)
```bash
# Tự động tạo bởi ingress controller
kubectl get secrets -A | grep tls
```

#### Production (Let's Encrypt)
```bash
# Cài đặt cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Cấu hình ClusterIssuer cho Let's Encrypt
```

## 🔧 Troubleshooting

### 1. Pods không start

```bash
# Kiểm tra events
kubectl get events -n NAMESPACE --sort-by='.lastTimestamp'

# Kiểm tra logs
kubectl logs -n NAMESPACE POD-NAME

# Kiểm tra resources
kubectl describe pod -n NAMESPACE POD-NAME
```

### 2. Ingress không hoạt động

```bash
# Kiểm tra ingress controller
kubectl get pods -n dev-ingress-controller

# Kiểm tra ingress rules
kubectl get ingress -A

# Test internal connectivity
kubectl exec -it POD-NAME -- curl http://SERVICE-NAME:PORT
```

### 3. Cloudflare Tunnel issues

```bash
# Kiểm tra tunnel logs
kubectl logs -n dev-cloudflare-tunnel deployment/cloudflare-tunnel

# Kiểm tra credentials
kubectl get secret -n dev-cloudflare-tunnel cloudflare-tunnel -o yaml

# Test tunnel status
kubectl exec -n dev-cloudflare-tunnel deployment/cloudflare-tunnel -- cloudflared tunnel info TUNNEL-ID
```

### 4. Storage issues

```bash
# Kiểm tra PVCs
kubectl get pvc -A

# Kiểm tra storage class
kubectl get storageclass

# Kiểm tra persistent volumes
kubectl get pv
```

## 📊 Monitoring và Maintenance

### 1. Health Checks

```bash
# Script kiểm tra health tất cả services
#!/bin/bash
NAMESPACES=("dev-clearml" "dev-minio-tenant" "dev-keycloak" "dev-ingress-controller" "dev-cloudflare-tunnel")

for ns in "${NAMESPACES[@]}"; do
    echo "=== Checking $ns ==="
    kubectl get pods -n $ns
    echo ""
done
```

### 2. Backup Strategy

#### Database Backups
```bash
# MongoDB (ClearML)
kubectl exec -n dev-clearml deployment/mongo -- mongodump --out /backup

# PostgreSQL (Keycloak)
kubectl exec -n dev-keycloak deployment/postgres -- pg_dump -U keycloak keycloak > backup.sql
```

#### MinIO Backups
```bash
# Sử dụng mc (MinIO Client)
mc mirror minio/clearml backup/clearml
```

### 3. Updates và Upgrades

```bash
# Update images
kubectl set image deployment/DEPLOYMENT-NAME CONTAINER-NAME=NEW-IMAGE:TAG -n NAMESPACE

# Rolling restart
kubectl rollout restart deployment/DEPLOYMENT-NAME -n NAMESPACE

# Rollback
kubectl rollout undo deployment/DEPLOYMENT-NAME -n NAMESPACE
```

## 🎯 Production Deployment

### 1. Thay đổi cho Production

```bash
# Deploy tất cả services với ENV=production
cd minio-operator && make deploy ENV=production
cd ../minio-tenant && make deploy ENV=production
cd ../keycloak && make deploy ENV=production
cd ../clearml && make deploy ENV=production
cd ../clearml-agent && make deploy ENV=production
cd ../ingress-controller && make deploy ENV=production
cd ../cloudflare-tunnel && make deploy ENV=production
```

### 2. Production Checklist

- [ ] Thay đổi tất cả passwords mặc định
- [ ] Cấu hình SSL certificates (Let's Encrypt)
- [ ] Setup monitoring và alerting
- [ ] Cấu hình backup tự động
- [ ] Test disaster recovery
- [ ] Setup log aggregation
- [ ] Cấu hình resource limits và requests
- [ ] Setup network policies
- [ ] Cấu hình RBAC

## 📚 Tài liệu tham khảo

- [ClearML Documentation](https://clear.ml/docs)
- [MinIO Documentation](https://docs.min.io/)
- [Keycloak Documentation](https://www.keycloak.org/documentation)
- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

## 🆘 Support

Nếu gặp vấn đề trong quá trình cài đặt:

1. Kiểm tra logs của từng service
2. Xem troubleshooting section
3. Kiểm tra GitHub issues của từng project
4. Tạo issue mới với đầy đủ thông tin lỗi

---

**Lưu ý**: Hướng dẫn này được viết cho môi trường development. Đối với production, cần thêm các bước bảo mật và monitoring bổ sung.
