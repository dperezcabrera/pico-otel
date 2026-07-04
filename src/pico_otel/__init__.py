"""pico-otel: OpenTelemetry auto-instrumentation for the Pico ecosystem.

Install it and your pico-boot app gets tracing (FastAPI, SQLAlchemy, Celery —
whichever are present), log correlation and Prometheus metrics wired into the
registry that pico-actuator serves at ``/actuator/metrics``. Configuration
under the ``otel`` prefix; zero-config by default.

Public API:
    Settings: OtelSettings
    Components: OtelBootstrap, OtelFastApiConfigurer
"""

from .bootstrap import OtelBootstrap, OtelFastApiConfigurer
from .config import OtelSettings

__all__ = ["OtelSettings", "OtelBootstrap", "OtelFastApiConfigurer"]
