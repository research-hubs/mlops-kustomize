MinIO Tenant - Kustomize

Structure
- base: Tenant CR and default config Secret
- overlays/
  - development: namespace `minio-tenant-dev`
  - production: namespace `minio-tenant-prod`

Commands
- Deploy
  - make deploy ENV=development
  - make deploy ENV=production
- Status
  - make status ENV=development
- Diff
  - make diff ENV=development
- Delete (cleans tenant CRs, PVCs, and namespace)
  - make delete ENV=development

Notes
- If using namePrefix, ensure references like `Tenant.spec.configuration.name` are updated via kustomize `nameReference` to avoid broken Secret references. Current overlays include this when namePrefix is enabled.
- Port-forward helpers:
  - API: make pf-api ENV=development → http://localhost:9000
  - Console: make pf-console ENV=development → https://localhost:9001

