# FAQ

## Do I need pico-fastapi installed?

No. The FastAPI configurer matches pico-fastapi's protocol structurally; with
pico-fastapi absent it simply never runs.

## Why do my metrics not appear at /actuator/metrics?

Install the `prometheus` extra and pico-actuator. The contract is
`prometheus_client`'s **default registry**: pico-otel writes there,
pico-actuator reads from there.

## How do I silence the console exporter in dev?

`otel.traces_exporter: none` — spans are still created (instrumentation
active) but nothing is exported.

## Can two containers configure OTel twice?

No: setup is idempotent per process; the first configuration wins and a
second container reuses it.
