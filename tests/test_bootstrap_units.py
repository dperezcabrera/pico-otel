"""Unit tests for the import-guarded branches of bootstrap.py.

The e2e tests in test_otel.py can only exercise one SDK setup per
process (providers are set-once globals); these tests cover the
exporter/metrics/instrumentor fallbacks by patching the globals away.
"""

import sys

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter

from pico_otel.bootstrap import OtelBootstrap, OtelFastApiConfigurer, _make_exporter
from pico_otel.config import OtelSettings

# --- _make_exporter ---


def test_exporter_none_mode():
    assert _make_exporter(OtelSettings(traces_exporter="none")) is None


def test_exporter_console_mode():
    assert isinstance(_make_exporter(OtelSettings(traces_exporter="console")), ConsoleSpanExporter)


def test_exporter_auto_without_endpoint_is_console():
    assert isinstance(_make_exporter(OtelSettings(traces_exporter="auto")), ConsoleSpanExporter)


def test_exporter_auto_with_endpoint_wants_otlp_falls_back_when_missing(caplog):
    # otlp extra is deliberately not installed in the test env
    with caplog.at_level("WARNING"):
        exporter = _make_exporter(OtelSettings(traces_exporter="auto", endpoint="http://collector:4317"))
    assert isinstance(exporter, ConsoleSpanExporter)
    assert "not installed" in caplog.text


def test_exporter_otlp_gets_endpoint(monkeypatch):
    import types

    class FakeOTLP:
        def __init__(self, endpoint=None):
            self.endpoint = endpoint

    mod = types.ModuleType("opentelemetry.exporter.otlp.proto.grpc.trace_exporter")
    mod.OTLPSpanExporter = FakeOTLP
    monkeypatch.setitem(sys.modules, "opentelemetry.exporter.otlp.proto.grpc.trace_exporter", mod)

    exporter = _make_exporter(OtelSettings(traces_exporter="otlp", endpoint="http://collector:4317"))
    assert isinstance(exporter, FakeOTLP)
    assert exporter.endpoint == "http://collector:4317"

    assert _make_exporter(OtelSettings(traces_exporter="otlp")).endpoint is None


def test_exporter_unknown_mode_disables_export(caplog):
    with caplog.at_level("WARNING"):
        assert _make_exporter(OtelSettings(traces_exporter="jaeger")) is None
    assert "unknown" in caplog.text


# --- setup ---


def _fresh_sdk(monkeypatch):
    """Pretend no provider is configured yet and capture what setup installs."""
    from opentelemetry import metrics, trace

    installed = {}
    monkeypatch.setattr(trace, "get_tracer_provider", lambda: object())
    monkeypatch.setattr(trace, "set_tracer_provider", lambda p: installed.setdefault("tracer", p))
    monkeypatch.setattr(metrics, "set_meter_provider", lambda p: installed.setdefault("meter", p))
    return installed


def test_setup_disabled_is_a_noop(monkeypatch):
    installed = _fresh_sdk(monkeypatch)
    OtelBootstrap(OtelSettings(enabled=False)).setup()
    assert installed == {}


def test_setup_installs_provider_with_exporter(monkeypatch):
    installed = _fresh_sdk(monkeypatch)
    OtelBootstrap(OtelSettings(traces_exporter="console", service_name="unit-svc")).setup()
    provider = installed["tracer"]
    assert isinstance(provider, TracerProvider)
    assert provider.resource.attributes["service.name"] == "unit-svc"
    assert "meter" in installed


def test_setup_without_exporter_skips_span_processor(monkeypatch):
    installed = _fresh_sdk(monkeypatch)
    OtelBootstrap(OtelSettings(traces_exporter="none")).setup()
    assert isinstance(installed["tracer"], TracerProvider)


def test_setup_metrics_disabled(monkeypatch):
    installed = _fresh_sdk(monkeypatch)
    OtelBootstrap(OtelSettings(traces_exporter="none", prometheus_metrics=False)).setup()
    assert "meter" not in installed


def test_setup_metrics_skipped_when_exporter_missing(monkeypatch, caplog):
    installed = _fresh_sdk(monkeypatch)
    import opentelemetry.exporter as otel_exporter

    monkeypatch.delattr(otel_exporter, "prometheus", raising=False)
    monkeypatch.setitem(sys.modules, "opentelemetry.exporter.prometheus", None)
    with caplog.at_level("INFO"):
        OtelBootstrap(OtelSettings(traces_exporter="none")).setup()
    assert "meter" not in installed
    assert "prometheus metrics skipped" in caplog.text


def test_instrument_flags_off_apply_nothing(monkeypatch):
    _fresh_sdk(monkeypatch)
    called = []
    monkeypatch.setattr(OtelBootstrap, "_apply", staticmethod(lambda mod, cls: called.append(mod)))
    OtelBootstrap(
        OtelSettings(
            traces_exporter="none",
            instrument_logging=False,
            instrument_sqlalchemy=False,
            instrument_celery=False,
        )
    ).setup()
    assert called == []


def test_apply_missing_instrumentation_is_silent():
    OtelBootstrap._apply("opentelemetry.instrumentation.does_not_exist", "NopeInstrumentor")


def test_apply_instruments_once():
    class Instrumentor:
        instrumented = 0

        def __init__(self):
            self.is_instrumented_by_opentelemetry = Instrumentor.instrumented > 0

        def instrument(self):
            Instrumentor.instrumented += 1

    import types

    mod = types.ModuleType("fake_instrumentation")
    mod.FakeInstrumentor = Instrumentor
    sys.modules["fake_instrumentation"] = mod
    try:
        OtelBootstrap._apply("fake_instrumentation", "FakeInstrumentor")
        OtelBootstrap._apply("fake_instrumentation", "FakeInstrumentor")
    finally:
        del sys.modules["fake_instrumentation"]
    assert Instrumentor.instrumented == 1


# --- OtelFastApiConfigurer ---


def test_configurer_disabled_does_not_touch_app():
    OtelFastApiConfigurer(OtelSettings(enabled=False)).configure_app(app=None)
    OtelFastApiConfigurer(OtelSettings(instrument_fastapi=False)).configure_app(app=None)


def test_configurer_skips_when_instrumentation_missing(monkeypatch, caplog):
    import opentelemetry.instrumentation as otel_instr

    monkeypatch.delattr(otel_instr, "fastapi", raising=False)
    monkeypatch.setitem(sys.modules, "opentelemetry.instrumentation.fastapi", None)
    with caplog.at_level("INFO"):
        OtelFastApiConfigurer(OtelSettings()).configure_app(app=None)
    assert "fastapi instrumentation skipped" in caplog.text


def test_configurer_instruments_app(monkeypatch):
    from opentelemetry.instrumentation import fastapi as fastapi_instr

    seen = []
    monkeypatch.setattr(fastapi_instr.FastAPIInstrumentor, "instrument_app", staticmethod(seen.append))
    app = object()
    OtelFastApiConfigurer(OtelSettings()).configure_app(app)
    assert seen == [app]
