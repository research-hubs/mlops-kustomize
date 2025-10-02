## ClearML Stack - Kustomize

Base/overlays structure for ClearML services with meaningful PVC names and dynamic provisioning.

### Structure

- `base/`
  - `apiserver/` (no PVC)
  - `async-delete/` (no PVC)
  - `elasticsearch/`
    - `deployment.yaml`, `service.yaml`, `pvc-data.yaml`, `pvc-logs.yaml`
  - `fileserver/` (no PVC if using S3/MinIO)
  - `mongo/`
    - `deployment.yaml`, `service.yaml`, `pvc-data.yaml`, `pvc-config.yaml`
  - `redis/`
    - `deployment.yaml`, `service.yaml`, `pvc-data.yaml`
  - `kustomization.yaml` (aggregates all components)
- `overlays/`
  - `development/` → namespace `dev-clearml`
  - `production/` → namespace `prod-clearml`

### PVC Policy

- Dynamic provisioning (no storageClassName specified)
- Names reflect purpose: `*-data`, `*-logs`, `*-config`
- Default size: 1Gi (override per environment with patches if needed)

### Usage

Build:

```bash
kubectl kustomize base
kubectl kustomize overlays/development
```

Deploy:

```bash
make deploy ENV=base
make deploy ENV=development
make deploy ENV=production
```

Status / Diff / Delete:

```bash
make status ENV=development
make diff ENV=production
make delete ENV=production
```

### Notes

- If you keep Fileserver local storage, add a `pvc-data.yaml` under `base/fileserver` and mount it in the deployment.
- For production, consider increasing `mongo-data` and `elasticsearch-data` sizes via overlay patches.
