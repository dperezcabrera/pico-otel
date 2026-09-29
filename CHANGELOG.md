# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Dependency floors raised to what the test suite proves: `pico-ioc >= 2.3.3` (was 2.2.0) and `opentelemetry-sdk >= 1.37` (was 1.25; older releases pull instrumentations that import the removed `pkg_resources`). A new CI job runs the suite with every declared floor pinned, so a floor that installs but does not work can no longer ship.

## [0.1.0] - 2026-07-03

### Added

- `OtelBootstrap`: idempotent SDK setup (tracer + meter providers) at container startup.
- Exporters: `auto`/`otlp`/`console`/`none`; OTLP behind the `otlp` extra.
- Prometheus metrics into `prometheus_client`'s default registry (pico-actuator `/metrics` contract).
- Auto-instrumentation (import-guarded) for FastAPI, SQLAlchemy, Celery and logging.
- `OtelSettings` (prefix `otel`); zero-config defaults.

[Unreleased]: https://github.com/dperezcabrera/pico-otel/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/dperezcabrera/pico-otel/releases/tag/v0.1.0
