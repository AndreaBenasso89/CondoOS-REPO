# Helm charts

One chart per microservice (docs/09 §2), plus an umbrella chart `condominioos` that composes them.

```
helm/
├── condominioos/        # umbrella chart (values per env)
└── charts/
    ├── gateway/
    ├── channels/
    ├── agent-runtime/
    ├── firewall/
    ├── notification/
    ├── knowledge/
    ├── registry/  accounting/  maintenance/  vendors/  assemblies/  compliance/  documents/
    ├── audit/
    ├── review/
    ├── identity/
    └── workflows/
```

Each chart ships: Deployment (non-root, read-only FS), Service, HPA, NetworkPolicy (default-deny +
explicit egress), ServiceMonitor (Prometheus), and a PodDisruptionBudget. Images are signed and
scanned (docs/06 §5/§8). Per-tenant autonomy flags and the kill-switch are runtime config, not chart
values.
