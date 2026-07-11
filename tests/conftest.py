import pytest


@pytest.fixture
def make_container(make_container):
    """Extends the plugin fixture: kwargs become the otel config section."""
    plugin_make = make_container

    def _make(**otel_cfg):
        return plugin_make(config={"otel": otel_cfg, "fastapi": {"title": "t"}})

    return _make
