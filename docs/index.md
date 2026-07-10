# pico-otel

Part of an ecosystem [built for the AI era](https://dperezcabrera.github.io/pico-ioc/ai-ready/):
machine-readable conventions in every repo, installable
[AI coding skills](https://github.com/dperezcabrera/pico-skills), and
[scaffolds](https://dperezcabrera.github.io/pico-initializer/) that generate
AI-maintainable projects.

OpenTelemetry auto-instrumentation for pico-boot apps: tracing, Prometheus
metrics and log correlation, wired by entry points — zero integration code.

```bash
pip install pico-otel[all]
```

With [pico-actuator](https://github.com/dperezcabrera/pico-actuator) installed
too, `/actuator/metrics` serves the OTel metrics automatically: probes +
metrics + tracing from two `pip install`s.

Continue with [Getting Started](getting-started.md).

**See it in context**: the [flagship use case](https://dperezcabrera.github.io/pico-boot/flagship/) wires this module into a full order platform together with the rest of the ecosystem.
