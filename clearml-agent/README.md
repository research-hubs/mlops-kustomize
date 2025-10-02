## ClearML Agent - Kustomize

This module deploys ClearML Agents with Kustomize. The base provides safe defaults; overlays define namespaces and override queues, replicas, hosts and credentials.

### Structure

- `base/`
  - `deployment.yaml` – base Deployment with defaults (queue, PVC, mounts)
  - `config.yaml` – default `clearml.conf` (no secrets)
  - `pvc.yaml` – persistent cache volume
  - `kustomization.yaml`
- `overlays/`
  - `development/`
    - `agents/default/` – default queue agent (replicas via patch)
    - `agents/train/` – train queue agent
    - `deployment-patch.yaml` – shared env (WEB_HOST/API_HOST/keys)
    - `config-patch.yaml` – overrides `clearml.conf` (e.g., MinIO endpoint/keys)
    - `kustomization.yaml` – namespace `dev-clearml`
  - `production/` – same layout, namespace `prod-clearml`

### Prerequisites

- kubectl on PATH and access to your cluster
- Kustomize (built into kubectl >=1.14 via `-k`)

### Usage

Build manifests (preview):

```bash
kubectl kustomize overlays/development
```

Deploy:

```bash
make -C clearml-agent deploy ENV=development
make -C clearml-agent deploy ENV=production
```

Other targets:

```bash
make -C clearml-agent status ENV=development
make -C clearml-agent diff ENV=production
make -C clearml-agent logs ENV=development
make -C clearml-agent delete ENV=production
```

### Add more agents

Copy one of the folders under `overlays/<env>/agents/*` and change:

- `nameSuffix` in its `kustomization.yaml`
- replicas and `CLEARML_AGENT_QUEUE` in `deployment-patch.yaml`

### Notes

- Credentials in overlays are inline for simplicity, consider switching to Secrets for production.
- To run more workers for a queue, increase `spec.replicas` in that agent's `deployment-patch.yaml`.
