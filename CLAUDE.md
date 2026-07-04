Read and follow ./AGENTS.md for project conventions.

## Pico Ecosystem Context

pico-otel wires the OpenTelemetry SDK at container startup (`OtelBootstrap` with `@configure`) and instruments installed libraries (FastAPI via a structural `FastApiConfigurer`, SQLAlchemy/Celery/logging via import-guarded instrumentors). Prometheus metrics go to prometheus_client's default registry — the contract with pico-actuator's `/actuator/metrics`. Config prefix `otel` (zero-config).

## Key Reminders

- pico-ioc dependency: `>= 2.2.0`
- **NEVER change `version_scheme`** in pyproject.toml. It MUST remain `"post-release"`.
- requires-python >= 3.11
- Commit messages: one line only
- Setup MUST stay idempotent (second container in the same process must not reconfigure providers)
- Never import pico-fastapi: the configurer matches `FastApiConfigurer` structurally
- Every instrumentor import stays guarded; extras map 1:1 to instrumentations
