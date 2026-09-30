# Troubleshooting

## No spans anywhere

- `otel.enabled: true`? `traces_exporter` not `none`?
- The instrumentation extra must be installed (e.g.
  `pico-otel[fastapi]`) — absence is a silent skip (INFO log at startup).

## Every span exported twice (FastAPI >= 0.142)

FastAPI 0.142 ships its own OpenTelemetry integration, on by default. When
`OTEL_EXPORTER_OTLP_ENDPOINT` is set it appends an OTLP exporter to the global
providers at startup, on top of the one pico-otel configured. Use pico-fastapi
>= 0.4.3, which sets `fastapi.telemetry.auto_configure: false` by default. If you
build the `FastAPI()` app yourself, pass `telemetry={"auto_configure": False}`.
FastAPI's own spans stay off while pico-otel instruments the app, so a request
still produces one server span.

## No metrics at /actuator/metrics

Install `pico-otel[prometheus]` **and** pico-actuator. The meter provider
writes to `prometheus_client`'s default registry; actuator serves it.

## Spans exported to console in production

`traces_exporter: auto` falls back to console when `otel.endpoint` is empty.
Set the collector endpoint (switches to OTLP) or `none`.

## Second container logs nothing / keeps old service_name

By design: setup is idempotent per process, first configuration wins. Run
suites that need different settings in separate processes.

## SQLAlchemy spans missing

The instrumentor hooks engines created **after** instrumentation. pico-boot
runs `@configure` hooks at init — if you build engines before `init()`,
instrument first or let pico-sqlalchemy create them.
