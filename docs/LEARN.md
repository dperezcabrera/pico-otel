# Learning Roadmap

1. **Install** — `pip install pico-otel[all]`
   ([Getting Started](getting-started.md)).
2. **See spans locally** — default console exporter; hit an endpoint, read
   the span dump.
3. **Name your service** — `otel.service_name`; find it in the span
   resource.
4. **Ship to a collector** — set `otel.endpoint`; `auto` switches to OTLP.
5. **Metrics with actuator** — install pico-actuator; curl
   `/actuator/metrics` ([Architecture](architecture.md) for the contract).
6. **Trim** — drop extras you do not use; lower `traces_sample_ratio` under
   load.
