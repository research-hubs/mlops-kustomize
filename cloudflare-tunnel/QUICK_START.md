# Cloudflare Tunnel Quick Start Guide

## 🚀 Tổng quan

Hướng dẫn nhanh để setup Cloudflare Tunnel cho Kubernetes cluster hoàn toàn bằng command line:

- Cài đặt cloudflared
- Tạo tunnel và lấy credentials + certificate
- Cấu hình DNS
- Deploy lên Kubernetes

## 📋 Prerequisites

- Kubernetes cluster đang chạy
- kubectl đã cấu hình
- Tài khoản Cloudflare
- Domain đã được quản lý bởi Cloudflare

## 🔧 Bước 1: Cài đặt cloudflared

### Windows (PowerShell)

```powershell
# Tải cloudflared
Invoke-WebRequest -Uri "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe" -OutFile "cloudflared.exe"

# Di chuyển vào PATH
Move-Item "cloudflared.exe" "C:\Windows\System32\cloudflared.exe"

# Kiểm tra cài đặt
cloudflared version
```

### Linux/macOS

```bash
# Linux
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# macOS
brew install cloudflared

# Kiểm tra cài đặt
cloudflared version
```

## 🔐 Bước 2: Tạo Tunnel và lấy thông tin

### 2.1 Đăng nhập Cloudflare

```bash
cloudflared tunnel login
```

- Mở browser và đăng nhập Cloudflare
- Chọn domain `itdevops.id.vn`

### 2.2 Tạo tunnel

```bash
# Tạo tunnel cho development
cloudflared tunnel create mlops-tunnel

# Tạo tunnel cho production (nếu cần)
cloudflared tunnel create mlops-prod-tunnel
```

**Lưu ý:** Ghi lại **Tunnel ID** được tạo (ví dụ: `f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20`)

### 2.3 Lấy thông tin tunnel

```bash
# Xem danh sách tunnel
cloudflared tunnel list

# Xem thông tin chi tiết tunnel
cloudflared tunnel info mlops-tunnel
```

### 2.4 Lấy credentials và certificate

```bash
# Windows - Xem file credentials
type %USERPROFILE%\.cloudflared\f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20.json

# Linux/macOS - Xem file credentials
cat ~/.cloudflared/f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20.json

# Lấy origin certificate
cloudflared tunnel --cred-file ~/.cloudflared/f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20.json --origincert ~/.cloudflared/cert.pem run mlops-tunnel
```

**Kết quả credentials sẽ có dạng:**

```json
{
  "AccountTag": "fd22145188a5cea5847e7540201e8a0f",
  "TunnelID": "f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20",
  "TunnelSecret": "ho2+CzeTI6tjxT1cWDeQnCmYav9uklEkXEYMljnXink="
}
```

**Origin certificate sẽ được tạo tại:** `~/.cloudflared/cert.pem`

## 🌐 Bước 3: Cấu hình DNS

### 3.1 Tạo DNS Records bằng command line

```bash
# Cấu hình routes cho tunnel (tự động tạo DNS records)
cloudflared tunnel route dns mlops-tunnel traefik.itdevops.id.vn
cloudflared tunnel route dns mlops-tunnel minio-console.itdevops.id.vn
cloudflared tunnel route dns mlops-tunnel minio.itdevops.id.vn
```

### 3.2 Kiểm tra DNS records

```bash
# Xem routes đã tạo
cloudflared tunnel route list mlops-tunnel

# Test DNS resolution
nslookup traefik.itdevops.id.vn
nslookup minio-console.itdevops.id.vn
```

## ⚙️ Bước 4: Cập nhật Kubernetes Config

### 4.1 Cập nhật Secret

Copy nội dung từ file credentials và paste vào `overlays/development/secret-patch.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: dev-cloudflare-tunnel
type: Opaque
stringData:
  credentials.json: |
    {
      "AccountTag": "fd22145188a5cea5847e7540201e8a0f",
      "TunnelID": "f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20",
      "TunnelSecret": "ho2+CzeTI6tjxT1cWDeQnCmYav9uklEkXEYMljnXink="
    }
```

### 4.2 Cập nhật Origin Certificate

Copy nội dung từ file `~/.cloudflared/cert.pem` và paste vào `overlays/development/origin-cert.yaml`:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cloudflare-origin-cert
  namespace: dev-cloudflare-tunnel
type: Opaque
stringData:
  origin.pem: |
    -----BEGIN CERTIFICATE-----
    MIIE... (copy từ ~/.cloudflared/cert.pem)
    -----END CERTIFICATE-----
```

### 4.3 Cập nhật ConfigMap (nếu cần)

Mở file `overlays/development/configmap-patch.yaml` và cập nhật ingress rules:

```yaml
ingress:
  - hostname: traefik.itdevops.id.vn
    service: http://traefik.ingress-controller.svc.cluster.local:80
  - hostname: minio-console.itdevops.id.vn
    service: http://traefik.ingress-controller.svc.cluster.local:80
  - hostname: minio.itdevops.id.vn
    service: http://traefik.ingress-controller.svc.cluster.local:80
  - service: http_status:404
```

## 🚀 Bước 5: Deploy lên Kubernetes

### 5.1 Deploy Development

```bash
cd cloudflare-tunnel
make deploy ENV=development
```

### 5.2 Kiểm tra trạng thái

```bash
# Xem pods
kubectl get pods -n dev-cloudflare-tunnel

# Xem logs
kubectl logs -n dev-cloudflare-tunnel deployment/cloudflare-tunnel

# Kiểm tra tunnel status
kubectl exec -n dev-cloudflare-tunnel deployment/cloudflare-tunnel -- cloudflared tunnel info f94d7ca3-c21f-4f9a-8a18-8b2fa9bfac20
```

### 5.3 Test kết nối

```bash
# Test DNS resolution
nslookup traefik.itdevops.id.vn
nslookup minio-console.itdevops.id.vn

# Test HTTP access
curl -I https://traefik.itdevops.id.vn
curl -I https://minio-console.itdevops.id.vn
```

## 🔍 Troubleshooting

### Lỗi thường gặp:

1. **"CRYPTO_ERROR 0x178"**

   - Kiểm tra origin certificate có đúng format không
   - Đảm bảo certificate được mount đúng trong pod

2. **"no application protocol"**

   - Kiểm tra tunnel credentials có đúng không
   - Restart tunnel: `kubectl rollout restart deployment/cloudflare-tunnel -n dev-cloudflare-tunnel`

3. **DNS không resolve**

   - Kiểm tra CNAME records trong Cloudflare
   - Đảm bảo proxy status là "Proxied" (mây cam)

4. **Tunnel không kết nối**
   - Kiểm tra logs: `kubectl logs -n dev-cloudflare-tunnel deployment/cloudflare-tunnel`
   - Kiểm tra credentials và certificate

### Debug commands:

```bash
# Xem cấu hình tunnel
kubectl get configmap -n dev-cloudflare-tunnel cloudflare-tunnel -o yaml

# Xem secret
kubectl get secret -n dev-cloudflare-tunnel cloudflare-tunnel -o yaml

# Test tunnel locally
cloudflared tunnel --config /path/to/config.yaml run mlops-tunnel
```

## 📚 Tài liệu tham khảo

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared GitHub](https://github.com/cloudflare/cloudflared)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)

## 🎯 Kết quả mong đợi

Sau khi setup xong, bạn sẽ có thể truy cập:

- ✅ `https://traefik.itdevops.id.vn` - Traefik Dashboard
- ✅ `https://minio-console.itdevops.id.vn` - MinIO Console
- ✅ `https://minio.itdevops.id.vn` - MinIO API

Tất cả đều được bảo mật bởi Cloudflare và có SSL certificate tự động!
