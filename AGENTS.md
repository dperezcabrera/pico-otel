# pico-otel

OpenTelemetry auto-instrumentation wired at container startup.

## Commands

```bash
pip install -e ".[dev]" opentelemetry-sdk opentelemetry-exporter-prometheus opentelemetry-instrumentation-fastapi
pytest tests/ -v
pytest --cov=pico_otel --cov-report=term-missing tests/
mkdocs serve -f mkdocs.yml
```

## Project Structure

```
src/pico_otel/
  __init__.py    # Public API
  bootstrap.py   # OtelBootstrap (@configure setup) + OtelFastApiConfigurer
  config.py      # OtelSettings (prefix "otel")
```

## Key Concepts

- Idempotent setup: only configures if the current provider is the proxy default.
- Exporter modes: auto (otlp if endpoint set, else console) / otlp / console / none.
- Metrics: PrometheusMetricReader -> prometheus_client default REGISTRY (the pico-actuator /metrics contract).
- Instrumentors are import-guarded; missing extra = silent skip (INFO log).
- `OtelFastApiConfigurer` matches pico-fastapi's `FastApiConfigurer` protocol structurally — never import pico-fastapi.

## Boundaries

- Do not modify `_version.py`
- Setup must remain idempotent per process
- No hard dependency on any instrumentation package (extras only)
