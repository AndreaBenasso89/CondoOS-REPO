# `@condominioos/events` — shared event contracts

Source-of-truth JSON Schemas for the domain events in [docs/14](../../docs/14-event-catalog.md). Both
the Python services (`condominioos.events`) and the TypeScript SDK validate against these. Schema
evolution is **additive-only**; breaking changes require a new `version`.

```
events/
├── envelope.schema.json      # the shared event envelope
└── schemas/
    ├── comms.message.received.v1.json
    ├── firewall.verdict.issued.v1.json
    └── ...                    # one file per event type/version
```
