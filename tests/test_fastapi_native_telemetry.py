"""FastAPI >= 0.142 has built-in OpenTelemetry. With pico-otel managing the
providers, a request must still yield exactly one SERVER span and FastAPI must
not attach a second exporter (it would when OTEL_EXPORTER_OTLP_ENDPOINT is set)."""

import subprocess
import sys
import textwrap

import fastapi
import pytest
from packaging.version import Version

_APP = """
    from pico_fastapi import controller, get

    @controller(prefix="/api")
    class Ping:
        @get("/ping")
        async def ping(self):
            return {"ok": True}
"""

# The global tracer provider can be set once per process: run in a fresh interpreter.
_SCENARIO = """
    import os
    os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = "http://127.0.0.1:9"
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    from opentelemetry import trace
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from pico_ioc import DictSource, configuration, init

    cfg = configuration(DictSource({"otel": {"traces_exporter": "none"}, "fastapi": {"title": "t"}}))
    container = init(modules=["pico_otel", "pico_fastapi", "otelapp"], config=cfg)
    app = container.get(FastAPI)
    provider = trace.get_tracer_provider()
    with TestClient(app) as client:
        processors = len(provider._active_span_processor._span_processors)
        exporter = InMemorySpanExporter()
        provider.add_span_processor(SimpleSpanProcessor(exporter))
        assert client.get("/api/ping").status_code == 200
    server = [s for s in exporter.get_finished_spans() if s.kind == trace.SpanKind.SERVER]
    print(processors, len(server))
    container.shutdown()
"""


@pytest.mark.skipif(Version(fastapi.__version__) < Version("0.142"), reason="no built-in telemetry")
def test_one_exporter_and_one_server_span_per_request_with_native_fastapi_telemetry(tmp_path):
    pytest.importorskip("opentelemetry.exporter.otlp.proto.http")  # what FastAPI would add
    (tmp_path / "otelapp.py").write_text(textwrap.dedent(_APP))
    out = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(_SCENARIO)],
        cwd=tmp_path,
        env={"PYTHONPATH": str(tmp_path), "PICO_BOOT_AUTO_PLUGINS": "false", "PATH": ""},
        capture_output=True,
        text=True,
        check=True,
    )
    processors, server_spans = map(int, out.stdout.split()[-2:])
    assert processors == 0  # pico-otel exports nothing here, and FastAPI added nothing
    assert server_spans == 1
