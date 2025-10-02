## clearml-session – Hướng dẫn nhanh cho đội dự án

Tài liệu này giúp bạn tạo và quản lý phiên làm việc tương tác (JupyterLab, VSCode Server, SSH) trên máy/GPU từ xa thông qua ClearML. Công cụ sử dụng là `clearml-session` (CLI client), chạy trên máy DEV của bạn.

Tham khảo gốc: [clearml/clearml-session](https://github.com/clearml/clearml-session)

### 1) Yêu cầu tối thiểu

- **ClearML Server** hoạt động (self-host hoặc Cloud) và truy cập được.
- Ít nhất một **clearml-agent** (bare-metal/VM/Kubernetes) đang online và nghe một queue (ví dụ `default`, `gpu`, `k8s-gpu`).
- Máy DEV có Python/pip và kết nối ra ClearML Server.

### 2) Cài đặt trên máy DEV

- Windows PowerShell:

```powershell
python --version
pip --version
pip install --upgrade pip
pip install clearml clearml-session
```

- macOS/Linux:

```bash
python3 --version
pip3 --version
pip3 install --upgrade pip
pip3 install clearml clearml-session
```

### 3) Khởi tạo kết nối tới ClearML Server (lưu credentials)

Chạy một lần để lưu cấu hình vào `~/.clearml.conf`:

```bash
clearml-init
```

Điền: Server API URL, Web App URL, Access Key, Secret Key (lấy trong Web UI ClearML: User → Settings → Profile → API Credentials).

Kiểm tra nhanh:

```bash
python - << 'PY'
from clearml import Task
Task.init(project_name="test", task_name="connectivity_check")
print("OK")
PY
```

### 4) Tạo một phiên tương tác cơ bản

Chọn queue phù hợp với agent của bạn (ví dụ `gpu`, `default`, `k8s-gpu`):

```bash
clearml-session --queue gpu
```

Sau khi agent cấp máy/khởi tạo container, CLI sẽ hiển thị URL JupyterLab, URL VSCode Server và thông tin SSH tạm thời (được bảo vệ bằng mật khẩu ngẫu nhiên).

### 5) Tùy chọn phổ biến khi tạo phiên

- Chọn Docker image:

```bash
clearml-session --queue gpu --docker nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04
```

- Cài thêm gói Python nhanh:

```bash
clearml-session --queue gpu --packages "torch==2.4.0 torchvision==0.19.0 tqdm"
```

- Dùng requirements.txt:

```bash
clearml-session --queue gpu --requirements /path/to/requirements.txt
```

- Script khởi tạo khi boot phiên:

```bash
clearml-session --queue gpu --init-script /path/to/init.sh
```

- Bật/tắt dịch vụ:

```bash
clearml-session --queue gpu --jupyter-lab true --vscode-server true
```

- Gửi git-credentials vào phiên:

```bash
clearml-session --queue gpu --git-credentials true
```

- Upload thư mục local vào phiên:

```bash
clearml-session --queue gpu --upload-files "/path/to/project"
```

### 6) Lưu/khôi phục workspace giữa các phiên (Workspace Syncing)

- Lưu thư mục làm việc trong container khi tắt phiên và dùng lại sau:

```bash
clearml-session --queue gpu --store-workspace "~/workspace"
```

- Tiếp tục một phiên trước (khôi phục snapshot):

```bash
clearml-session --queue gpu --continue-session <SESSION_ID>
```

- Liệt kê các phiên để lấy `SESSION_ID`:

```bash
clearml-session list
```

### 7) Debug một Task/Experiment đã chạy

Tạo phiên tương tác từ một Task cũ (sao chép môi trường/liên quan):

```bash
clearml-session --queue gpu --debugging-session <TASK_ID>
```

### 8) Quản lý vòng đời phiên

- Gắn lại vào phiên đang chạy:

```bash
clearml-session --attach <SESSION_ID>
```

- Xem thông tin chi tiết:

```bash
clearml-session info --attach <SESSION_ID>
```

- Tắt phiên:

```bash
clearml-session --shutdown <SESSION_ID>
# hoặc phiên gần nhất:
clearml-session --shutdown
```

### 9) Lưu ý khi agent chạy trong Kubernetes

- Bỏ `--network host` khi dùng k8s ingestion:

```bash
clearml-session --queue k8s-gpu --skip-docker-network true
```

- Dùng ánh xạ port thay vì host network (yêu cầu clearml-agent v2+):

```bash
clearml-session --queue k8s-gpu --docker-network port
```

- Bật router nếu có ClearML Router:

```bash
clearml-session --queue k8s-gpu --router-enabled true
```

- Cấu hình gateway qua LB/Ingress:

```bash
clearml-session --queue k8s-gpu --remote-gateway "my-gateway.domain:443"
```

### 10) SSH trực tiếp và các tham số nâng cao

- Mở shell SSH ngay (thoát SSH không tắt phiên):

```bash
clearml-session --queue gpu --shell
```

- Đặt username/password SSH (chỉ khi thực sự cần):

```bash
clearml-session --queue gpu --username dev --password "StrongPassword123!"
```

- Ngẫu nhiên mật khẩu mỗi phiên:

```bash
clearml-session --queue gpu --randomize always
```

- Bỏ kiểm tra SSH fingerprint (chỉ dùng khi hiểu rủi ro):

```bash
clearml-session --disable-fingerprint-check
```

### 11) Troubleshooting nhanh

- Agent không nhận job: kiểm tra agent online, đúng queue; xem log agent (k8s: `kubectl logs -f <agent-pod>`).
- Không mở được URL: thử `--attach` lại để tái tạo tunnel; kiểm tra mạng/proxy.
- Thiếu GPU/driver: chọn image phù hợp; với k8s cần `nvidia-device-plugin` và `resources.limits.nvidia.com/gpu`.
- Lỗi package: dùng `--packages`, `--requirements`, hoặc `--init-script` để cài đủ phụ thuộc.

### 12) Công thức nhanh (copy–paste)

```bash
# Tạo phiên chuẩn trên queue k8s-gpu với PyTorch và workspace syncing
clearml-session --queue k8s-gpu \
  --docker pytorch/pytorch:2.4.0-cuda12.1-cudnn8-runtime \
  --packages "numpy pandas scikit-learn" \
  --jupyter-lab true --vscode-server true \
  --store-workspace "~/workspace"

# Tắt phiên gần nhất
clearml-session --shutdown
```

### Tham khảo

- clearml-session – README và CLI options: [clearml/clearml-session](https://github.com/clearml/clearml-session)
