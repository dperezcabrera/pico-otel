"""Wires the OpenTelemetry SDK and available instrumentors at container startup.

Everything optional is import-guarded: each instrumentor activates only when
its package is installed (extras: ``fastapi``, ``sqlalchemy``, ``celery``,
``otlp``, ``prometheus``). Setup is idempotent — a second container in the
same process reuses the already-installed providers.
"""

import logging

from opentelemetry import metrics, trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
from pico_ioc import component, configure

from .config import OtelSettings

logger = logging.getLogger(__name__)


def _already_configured() -> bool:
    return isinstance(trace.get_tracer_provider(), TracerProvider)


def _make_exporter(settings: OtelSettings):
    mode = settings.traces_exporter
    if mode == "auto":
        mode = "otlp" if settings.endpoint else "console"
    if mode == "none":
        return None
    if mode == "otlp":
        try:
            from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
        except ImportError:
            logger.warning("otlp exporter requested but not installed (pip install pico-otel[otlp]); using console")
            return ConsoleSpanExporter()
        return OTLPSpanExporter(endpoint=settings.endpoint or None)
    if mode == "console":
        return ConsoleSpanExporter()
    logger.warning("unknown otel.traces_exporter %r; exporting disabled", mode)
    return None


@component
class OtelBootstrap:
    """Idempotent SDK setup + auto-instrumentation of installed libraries."""

    def __init__(self, settings: OtelSettings):
        self.settings = settings

    @configure
    def setup(self) -> None:
        s = self.settings
        if not s.enabled:
            return
        if not _already_configured():
            resource = Resource.create({"service.name": s.service_name})
            provider = TracerProvider(resource=resource, sampler=TraceIdRatioBased(s.traces_sample_ratio))
            exporter = _make_exporter(s)
            if exporter is not None:
                provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            self._setup_metrics(resource)
        self._instrument()

    def _setup_metrics(self, resource) -> None:
        if not self.settings.prometheus_metrics:
            return
        try:
            from opentelemetry.exporter.prometheus import PrometheusMetricReader
            from opentelemetry.sdk.metrics import MeterProvider
        except ImportError:
            logger.info("prometheus metrics skipped: pip install pico-otel[prometheus]")
            return
        # PrometheusMetricReader writes to prometheus_client's default
        # registry — the same one pico-actuator serves at /actuator/metrics.
        metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[PrometheusMetricReader()]))

    def _instrument(self) -> None:
        s = self.settings
        if s.instrument_logging:
            self._apply("opentelemetry.instrumentation.logging", "LoggingInstrumentor")
        if s.instrument_sqlalchemy:
            self._apply("opentelemetry.instrumentation.sqlalchemy", "SQLAlchemyInstrumentor")
        if s.instrument_celery:
            self._apply("opentelemetry.instrumentation.celery", "CeleryInstrumentor")

    @staticmethod
    def _apply(module: str, cls_name: str) -> None:
        try:
            mod = __import__(module, fromlist=[cls_name])
        except ImportError:
            return
        instrumentor = getattr(mod, cls_name)()
        if not instrumentor.is_instrumented_by_opentelemetry:
            instrumentor.instrument()


@component
class OtelFastApiConfigurer:
    """Instruments the FastAPI app; collected structurally by pico-fastapi
    via ``List[FastApiConfigurer]`` (no import of pico-fastapi needed)."""

    priority = -100

    def __init__(self, settings: OtelSettings):
        self.settings = settings

    def configure_app(self, app) -> None:
        if not (self.settings.enabled and self.settings.instrument_fastapi):
            return
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        except ImportError:
            logger.info("fastapi instrumentation skipped: pip install pico-otel[fastapi]")
            return
        FastAPIInstrumentor.instrument_app(app)
