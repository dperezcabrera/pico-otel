"""The public API is exactly what ``__all__`` declares (stability contract)."""

import pico_otel


def test_public_api_is_declared_and_importable():
    assert set(pico_otel.__all__) == {"OtelBootstrap", "OtelFastApiConfigurer", "OtelSettings"}
    for name in pico_otel.__all__:
        assert getattr(pico_otel, name) is not None
