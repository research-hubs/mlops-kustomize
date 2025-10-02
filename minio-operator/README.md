MinIO Operator - Kustomize

Structure
- base: Operator manifests
- overlays/
  - development: namespace `dev-minio-operator`
  - production: namespace `prod-minio-operator`

Commands
- Deploy
  - make deploy ENV=development
  - make deploy ENV=production
- Status
  - make status ENV=development
- Diff
  - make diff ENV=development
- Delete
  - make delete ENV=development

Notes
- Avoid namePrefix for the operator Deployment. The operator expects the Deployment to be named `minio-operator` internally; changing it can cause crashes. Current overlays do not use namePrefix.
- Makefile is PowerShell-friendly (no inline comments in recipes).

