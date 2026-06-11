# Infrastructure as Code (Terraform)

EU-only, multi-AZ cloud infrastructure for CondominioOS. Skeleton layout; modules are filled in
during the hardening sprints (docs/08 Sprint 10/14).

```
terraform/
├── envs/
│   ├── staging/        # EU region, single-AZ
│   └── prod/           # EU region, multi-AZ
└── modules/
    ├── network/        # VPC, subnets, egress allowlist, service mesh
    ├── database/       # PostgreSQL (operational + separate audit DB), backups, PITR
    ├── object_store/   # S3-compatible bucket, per-tenant key prefixes, crypto-shred keys
    ├── vector/         # Qdrant (managed or self-hosted), per-tenant collections
    ├── messaging/      # NATS JetStream
    ├── kubernetes/     # cluster, node pools, autoscaling
    ├── secrets/        # Vault/KMS, workload identities (no static secrets)
    └── observability/  # Prometheus, Grafana, Loki, OTel collector
```

## Principles
- **EU data residency:** every data-bearing resource is pinned to an EU region. CI policy
  (`infra/ci`) fails a plan that creates data resources outside the allowed regions.
- **Least privilege:** workload identities per service; no long-lived secrets.
- **Immutable + reproducible:** all infra in code; no console changes; `terraform plan` reviewed.
- **State:** remote backend (encrypted, locked) per environment.

## Conventions
- `terraform/envs/<env>/main.tf` composes modules and passes `region`, `tenancy`, `tags`.
- Secrets are referenced from Vault/KMS, never written to state in plaintext.
- `tfsec` / `checkov` run in CI on every PR (docs/06 §8).
