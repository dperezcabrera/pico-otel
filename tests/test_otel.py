import pytest
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from pico_boot import init
from pico_fastapi import controller, get
from pico_ioc import DictSource, configuration
from starlette.testclient import TestClient


def test_bootstrap_sets_sdk_provider_with_service_name(make_container):
    make_container(service_name="svc-under-test", traces_exporter="none")
    provider = trace.get_tracer_provider()
    assert isinstance(provider, TracerProvider)
    assert provider.resource.attributes["service.name"] == "svc-under-test"


def test_spans_are_recorded(make_container):
    make_container(traces_exporter="none")
    exporter = InMemorySpanExporter()
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))
    with trace.get_tracer("test").start_as_current_span("unit-span"):
        pass
    assert "unit-span" in [s.name for s in exporter.get_finished_spans()]


def test_second_container_does_not_reconfigure(make_container):
    make_container(service_name="first", traces_exporter="none")
    first = trace.get_tracer_provider()
    make_container(service_name="second", traces_exporter="none")
    assert trace.get_tracer_provider() is first


@controller(prefix="/api")
class Ping:
    @get("/ping")
    async def ping(self):
        return {"pong": True}


@pytest.mark.pico_auto_plugins
def test_fastapi_requests_produce_spans():
    """Verifies entry-point auto-discovery itself; only reproducible in the
    isolated tox venv (the shared dev venv drags every installed plugin in)."""
    import sys

    exporter = InMemorySpanExporter()
    cfg = configuration(
        DictSource(
            {
                "otel": {"traces_exporter": "none"},
                "fastapi": {"title": "t"},
                "celery": {"broker_url": "memory://", "backend_url": "cache+memory://"},
                "auth_client": {"enabled": False},
            }
        )
    )
    container = init(modules=[sys.modules[__name__]], config=cfg)
    trace.get_tracer_provider().add_span_processor(SimpleSpanProcessor(exporter))
    app = container.get(FastAPI)
    with TestClient(app) as client:
        assert client.get("/api/ping").status_code == 200
    names = [s.name for s in exporter.get_finished_spans()]
    assert any("/api/ping" in n for n in names), names
    container.shutdown()


def test_prometheus_metrics_reach_default_registry(make_container):
    from opentelemetry import metrics
    from prometheus_client import REGISTRY

    make_container(traces_exporter="none")
    counter = metrics.get_meter("test").create_counter("pico_test_counter")
    counter.add(3)
    sample_names = {s.name for m in REGISTRY.collect() for s in m.samples}
    assert any("pico_test_counter" in n for n in sample_names)
