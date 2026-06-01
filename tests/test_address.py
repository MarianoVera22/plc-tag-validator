"""Tests del parser de direcciones Siemens."""

from __future__ import annotations

import pytest

from plc_tag_validator.address import is_valid_address, parse_address
from plc_tag_validator.exceptions import InvalidAddressError

# Cada tupla: (dirección, ancho_esperado_en_bits, es_bit)
VALID_ADDRESSES = [
    ("M100.0", 1, True),
    ("MD100", 32, False),
    ("I0.1", 1, True),
    ("Q2.3", 1, True),
    ("MB10", 8, False),
    ("MW20", 16, False),
    ("MD40", 32, False),
    ("IW64", 16, False),
    ("QD12", 32, False),
    ("DB10.DBX0.0", 1, True),
    ("DB10.DBB2", 8, False),
    ("DB10.DBW4", 16, False),
    ("DB10.DBD8", 32, False),
    ("db10.dbd8", 32, False),  # minúsculas: deben normalizarse
]


@pytest.mark.parametrize("address,expected_width,expected_is_bit", VALID_ADDRESSES)
def test_parse_valid_addresses(address: str, expected_width: int, expected_is_bit: bool) -> None:
    """Las direcciones válidas se parsean con el ancho y tipo correctos."""
    result = parse_address(address)
    assert result.bit_width == expected_width
    assert result.is_bit == expected_is_bit


INVALID_ADDRESSES = [
    "",  # vacía
    "   ",  # solo espacios
    "X100",  # área inexistente
    "M100.8",  # bit fuera de rango (0-7)
    "DB10.DBXX0.0",  # typo: DBXX
    "MW",  # falta el número
    "DB.DBW4",  # falta número de DB
    "REAL",  # un tipo de dato, no una dirección
]


@pytest.mark.parametrize("address", INVALID_ADDRESSES)
def test_parse_invalid_addresses(address: str) -> None:
    """Las direcciones inválidas lanzan InvalidAddressError."""
    with pytest.raises(InvalidAddressError):
        parse_address(address)


@pytest.mark.parametrize("address", INVALID_ADDRESSES)
def test_is_valid_returns_false(address: str) -> None:
    """is_valid_address devuelve False para direcciones inválidas."""
    assert is_valid_address(address) is False


def test_invalid_address_keeps_original_in_exception() -> None:
    """La excepción conserva la dirección original que falló."""
    with pytest.raises(InvalidAddressError) as exc_info:
        parse_address("X999")
    assert exc_info.value.address == "X999"
