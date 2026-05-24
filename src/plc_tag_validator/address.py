"""Parser y validador de direcciones Siemens S7.

Soporta los formatos de direccionamiento más comunes:
    - Memoria de marcas (M):     M100.0, MB10, MW20, MD40
    - Entradas (I):              I0.1, IB4, IW64, ID8
    - Salidas (Q):               Q2.3, QB0, QW80, QD12
    - Data Blocks (DB):          DB10.DBX0.0, DB10.DBB2, DB10.DBW4, DB10.DBD8
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from plc_tag_validator.exceptions import InvalidAddressError

# --- Expresiones regulares para cada familia de direcciones ---

# Memoria/Entradas/Salidas con tamaño explícito: MB10, IW64, QD12, etc.
# Grupo 'area' = M|I|Q, 'size' = B|W|D, 'byte' = número
_SIZED_RE = re.compile(r"^(?P<area>[MIQ])(?P<size>[BWD])(?P<byte>\d+)$")

# Acceso a bit: M100.0, I0.1, Q2.3
# 'area' = M|I|Q, 'byte' = número, 'bit' = 0..7
_BIT_RE = re.compile(r"^(?P<area>[MIQ])(?P<byte>\d+)\.(?P<bit>[0-7])$")

# Data Block con bit: DB10.DBX0.0
_DB_BIT_RE = re.compile(r"^DB(?P<db>\d+)\.DBX(?P<byte>\d+)\.(?P<bit>[0-7])$")

# Data Block con tamaño: DB10.DBB2, DB10.DBW4, DB10.DBD8
_DB_SIZED_RE = re.compile(r"^DB(?P<db>\d+)\.DB(?P<size>[BWD])(?P<byte>\d+)$")

# Mapeo de letra de tamaño -> ancho en bits
_SIZE_TO_WIDTH = {"B": 8, "W": 16, "D": 32}


@dataclass(frozen=True, slots=True)
class ParsedAddress:
    """Resultado de parsear una dirección: qué tipo de acceso es y cuántos bits ocupa."""

    raw: str
    bit_width: int
    is_bit: bool


def parse_address(address: str) -> ParsedAddress:
    """Parsea una dirección Siemens y devuelve su estructura.

    Args:
        address: la dirección como string, ej. 'DB10.DBD4'.

    Returns:
        ParsedAddress con el ancho en bits y si es acceso a bit.

    Raises:
        InvalidAddressError: si la dirección no respeta ningún formato conocido.
    """
    addr = address.strip().upper()

    if not addr:
        raise InvalidAddressError(address, "la dirección está vacía")

    # Acceso a bit en memoria/IO: M100.0
    if _BIT_RE.match(addr):
        return ParsedAddress(raw=addr, bit_width=1, is_bit=True)

    # Tamaño explícito en memoria/IO: MW20
    if match := _SIZED_RE.match(addr):
        width = _SIZE_TO_WIDTH[match.group("size")]
        return ParsedAddress(raw=addr, bit_width=width, is_bit=False)

    # Bit dentro de DB: DB10.DBX0.0
    if _DB_BIT_RE.match(addr):
        return ParsedAddress(raw=addr, bit_width=1, is_bit=True)

    # Tamaño dentro de DB: DB10.DBW4
    if match := _DB_SIZED_RE.match(addr):
        width = _SIZE_TO_WIDTH[match.group("size")]
        return ParsedAddress(raw=addr, bit_width=width, is_bit=False)

    raise InvalidAddressError(address, "no coincide con ningún formato Siemens S7")


def is_valid_address(address: str) -> bool:
    """Versión booleana de parse_address: True si la dirección es válida."""
    try:
        parse_address(address)
    except InvalidAddressError:
        return False
    return True
