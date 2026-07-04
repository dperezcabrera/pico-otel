"""Settings for pico-otel (prefix ``otel``, zero-config)."""

from dataclasses import dataclass

from pico_ioc import configured


@configured(target="self", prefix="otel", mapping="tree")
@dataclass
class OtelSettings:
    """``traces_exporter``: ``auto`` (otlp if ``endpoint`` set, else console),
    ``otlp``, ``console`` or ``none``."""

    enabled: bool = True
    service_name: str = "pico-app"
    endpoint: str = ""
    traces_exporter: str = "auto"
    traces_sample_ratio: float = 1.0
    prometheus_metrics: bool = True
    instrument_logging: bool = True
    instrument_sqlalchemy: bool = True
    instrument_celery: bool = True
    instrument_fastapi: bool = True
