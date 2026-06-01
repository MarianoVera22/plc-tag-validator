"""Excepciones específicas del dominio de validación de tags."""

from __future__ import annotations


class PlcValidatorError(Exception):
    """Excepción base de la librería. Todas las demás heredan de esta."""


class InvalidAddressError(PlcValidatorError):
    """La dirección no respeta el formato Siemens S7."""

    def __init__(self, address: str, reason: str = "formato inválido") -> None:
        self.address = address
        self.reason = reason
        super().__init__(f"Dirección inválida '{address}': {reason}")


class LoaderError(PlcValidatorError):
    """Error al cargar o parsear un archivo de tags."""
