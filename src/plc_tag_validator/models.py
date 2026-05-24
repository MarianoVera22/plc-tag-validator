"""Modelos de dominio: tipos de dato y representación de un tag de PLC."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DataType(Enum):
    """Tipos de dato soportados en PLCs Siemens S7."""

    BOOL = "BOOL"
    BYTE = "BYTE"
    INT = "INT"
    WORD = "WORD"
    DINT = "DINT"
    DWORD = "DWORD"
    REAL = "REAL"

    @property
    def bit_width(self) -> int:
        """Cantidad de bits que ocupa el tipo en memoria."""
        widths = {
            DataType.BOOL: 1,
            DataType.BYTE: 8,
            DataType.INT: 16,
            DataType.WORD: 16,
            DataType.DINT: 32,
            DataType.DWORD: 32,
            DataType.REAL: 32,
        }
        return widths[self]


class Severity(Enum):
    """Nivel de severidad de un problema detectado."""

    ERROR = "ERROR"
    WARNING = "WARNING"


@dataclass(frozen=True, slots=True)
class Tag:
    """Un tag (variable) de PLC, tal como aparece en el archivo de configuración."""

    name: str
    address: str
    data_type: DataType
    description: str = ""

    def __post_init__(self) -> None:
        """Normaliza campos de texto tras la creación."""
        # Como el dataclass es frozen, usamos object.__setattr__ para mutar.
        object.__setattr__(self, "name", self.name.strip())
        object.__setattr__(self, "address", self.address.strip().upper())
        object.__setattr__(self, "description", self.description.strip())


@dataclass(frozen=True, slots=True)
class ValidationIssue:
    """Un problema detectado durante la validación."""

    severity: Severity
    message: str
    line: int | None = None
    tag_name: str | None = None
