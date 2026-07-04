# Getting Started

## Install

```bash
pip install pico-otel[all]
# or select: [otlp] [prometheus] [fastapi] [sqlalchemy] [celery] [logging]
```

Each extra maps to one instrumentation; anything not installed is skipped
silently. No code changes: `OtelBootstrap` runs at container startup.

## Configure

```yaml
otel:
  service_name: my-service
  endpoint: http://otel-collector:4317   # enables OTLP export
  traces_sample_ratio: 1.0
  traces_exporter: auto    # auto | otlp | console | none
  prometheus_metrics: true
  instrument_fastapi: true
  instrument_sqlalchemy: true
  instrument_celery: true
  instrument_logging: true
```

`auto` exports via OTLP when `endpoint` is set, console otherwise.

## What gets instrumented

- **FastAPI**: one span per request (via a `FastApiConfigurer` collected by
  pico-fastapi — no imports, structural typing).
- **SQLAlchemy / Celery**: spans for queries and tasks when installed.
- **Logging**: trace/span ids injected into log records.
- **Metrics**: exported to `prometheus_client`'s default registry, which
  pico-actuator serves at `/actuator/metrics`.

## Idempotency

Setup runs once per process: a second container reuses the existing
providers (first configuration wins).
