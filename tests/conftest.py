import pytest
from pico_ioc import DictSource, configuration, init


@pytest.fixture
def make_container():
    created = []

    def _make(**otel_cfg):
        cfg = configuration(DictSource({"otel": otel_cfg, "fastapi": {"title": "t"}}))
        c = init(modules=["pico_otel"], config=cfg)
        created.append(c)
        return c

    yield _make
    for c in created:
        c.shutdown()
