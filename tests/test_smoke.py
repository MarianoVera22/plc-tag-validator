"""Smoke test: verifica que el paquete se puede importar."""

import plc_tag_validator


def test_package_imports() -> None:
    """El paquete debe poder importarse sin errores."""
    assert plc_tag_validator is not None