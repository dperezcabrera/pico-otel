# pico-otel

[![PyPI](https://img.shields.io/pypi/v/pico-otel.svg)](https://pypi.org/project/pico-otel/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/dperezcabrera/pico-otel)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
![CI (tox matrix)](https://github.com/dperezcabrera/pico-otel/actions/workflows/ci.yml/badge.svg)
[![codecov](https://codecov.io/gh/dperezcabrera/pico-otel/branch/main/graph/badge.svg)](https://codecov.io/gh/dperezcabrera/pico-otel)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-otel&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-otel)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-otel&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-otel)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=dperezcabrera_pico-otel&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=dperezcabrera_pico-otel)
[![PyPI Downloads](https://img.shields.io/pypi/dm/pico-otel)](https://pypi.org/project/pico-otel/)
[![Docs](https://img.shields.io/badge/Docs-pico--otel-blue?style=flat&logo=readthedocs&logoColor=white)](https://dperezcabrera.github.io/pico-otel/)
[![Interactive Lab](https://img.shields.io/badge/Learn-online-green?style=flat&logo=python&logoColor=white)](https://dperezcabrera.github.io/pico-learn/)

**OpenTelemetry auto-instrumentation** for the [Pico](https://github.com/dperezcabrera/pico-ioc) ecosystem. Install it and your [pico-boot](https://github.com/dperezcabrera/pico-boot) app gets distributed tracing, log correlation and Prometheus metrics — wired by entry points, zero integration code.

## Install

```bash
pip install pico-otel[all]      # or pick: [otlp] [prometheus] [fastapi] [sqlalchemy] [celery] [logging]
```

## What you get

- **Tracing**: FastAPI requests, SQLAlchemy queries and Celery tasks become spans — whichever libraries are present get instrumented, the rest are skipped silently.
- **Metrics**: the OTel meter provider exports to `prometheus_client`'s default registry — the same one [pico-actuator](https://github.com/dperezcabrera/pico-actuator) serves at `/actuator/metrics`. Installing both = probes + metrics + tracing with zero config.
- **Log correlation**: trace/span ids injected into log records.

```yaml
# application.yaml (optional — sensible defaults without it)
otel:
  service_name: my-service
  endpoint: http://otel-collector:4317   # switches export to OTLP
  traces_sample_ratio: 1.0
```

`traces_exporter`: `auto` (OTLP if `endpoint` is set, console otherwise), `otlp`, `console` or `none`. Setup is idempotent per process.

## Documentation

Full docs at **[dperezcabrera.github.io/pico-otel](https://dperezcabrera.github.io/pico-otel/)**.

## License

MIT
