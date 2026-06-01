"""Reglas de validación sobre listas de tags.

Cada validador recibe la lista completa de tags y devuelve los problemas
encontrados. Esto permite reglas que miran un tag aislado (formato de dirección)
y reglas que miran el conjunto (duplicados).
"""

from __future__ import annotations

from collections import Counter
from typing import Protocol

from plc_tag_validator.address import parse_address
from plc_tag_validator.exceptions import InvalidAddressError
from plc_tag_validator.models import DataType, Severity, Tag, ValidationIssue

# Anchos de bit esperados por tipo de dato (para chequear coherencia con la dirección)
_BOOL_TYPES = {DataType.BOOL}
_WORD_TYPES = {DataType.INT, DataType.WORD}  # 16 bits
_DWORD_TYPES = {DataType.DINT, DataType.DWORD, DataType.REAL}  # 32 bits
_BYTE_TYPES = {DataType.BYTE}  # 8 bits


class Validator(Protocol):
    """Contrato que debe cumplir cualquier validador.

    Un validador es cualquier objeto llamable que toma la lista de tags
    y devuelve una lista de problemas detectados.
    """

    def __call__(self, tags: list[Tag]) -> list[ValidationIssue]: ...


def validate_addresses(tags: list[Tag]) -> list[ValidationIssue]:
    """Verifica que cada dirección respete el formato Siemens S7."""
    issues: list[ValidationIssue] = []
    for tag in tags:
        try:
            parse_address(tag.address)
        except InvalidAddressError as exc:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Dirección inválida '{tag.address}': {exc.reason}",
                    tag_name=tag.name,
                )
            )
    return issues


def validate_type_address_coherence(tags: list[Tag]) -> list[ValidationIssue]:
    """Verifica que el tipo de dato sea coherente con el ancho de la dirección.

    Ej: un REAL (32 bits) no puede estar en una dirección de word (16 bits).
    """
    issues: list[ValidationIssue] = []
    for tag in tags:
        try:
            parsed = parse_address(tag.address)
        except InvalidAddressError:
            # Si la dirección es inválida, ya lo reporta validate_addresses.
            continue

        expected_width = tag.data_type.bit_width
        if parsed.bit_width != expected_width:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=(
                        f"Incoherencia: tipo {tag.data_type.value} "
                        f"({expected_width} bits) en dirección '{tag.address}' "
                        f"({parsed.bit_width} bits)"
                    ),
                    tag_name=tag.name,
                )
            )
    return issues


def validate_unique_names(tags: list[Tag]) -> list[ValidationIssue]:
    """Detecta nombres de tag duplicados."""
    issues: list[ValidationIssue] = []
    name_counts = Counter(tag.name for tag in tags)
    for name, count in name_counts.items():
        if count > 1:
            issues.append(
                ValidationIssue(
                    severity=Severity.ERROR,
                    message=f"Nombre duplicado '{name}' (aparece {count} veces)",
                    tag_name=name,
                )
            )
    return issues


def validate_unique_addresses(tags: list[Tag]) -> list[ValidationIssue]:
    """Detecta direcciones duplicadas (dos tags apuntando al mismo lugar)."""
    issues: list[ValidationIssue] = []
    addr_counts = Counter(tag.address for tag in tags)
    for address, count in addr_counts.items():
        if count > 1:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    message=f"Dirección duplicada '{address}' (usada por {count} tags)",
                )
            )
    return issues


def validate_descriptions(tags: list[Tag]) -> list[ValidationIssue]:
    """Advierte sobre tags sin descripción (no es error, pero conviene tenerla)."""
    issues: list[ValidationIssue] = []
    for tag in tags:
        if not tag.description:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    message="Tag sin descripción",
                    tag_name=tag.name,
                )
            )
    return issues


def validate_name_length(tags: list[Tag]) -> list[ValidationIssue]:
    """Advierte sobre nombres con mas de 24 caracteres"""
    issues: list[ValidationIssue] = []
    for tag in tags:
        if len(tag.name) > 24:
            issues.append(
                ValidationIssue(
                    severity=Severity.WARNING,
                    message="Nombre con mas de 24 caracteres",
                    tag_name=tag.name,
                )
            )
    return issues


# Lista de todos los validadores que se ejecutan por defecto.
DEFAULT_VALIDATORS: list[Validator] = [
    validate_addresses,
    validate_type_address_coherence,
    validate_unique_names,
    validate_unique_addresses,
    validate_descriptions,
    validate_name_length,
]


def validate_all(
    tags: list[Tag], validators: list[Validator] | None = None
) -> list[ValidationIssue]:
    """Ejecuta todos los validadores sobre la lista de tags y junta los problemas.

    Args:
        tags: lista de tags a validar.
        validators: lista de validadores a usar. Si es None, usa DEFAULT_VALIDATORS.

    Returns:
        Lista combinada de todos los problemas encontrados.
    """
    active = validators if validators is not None else DEFAULT_VALIDATORS
    all_issues: list[ValidationIssue] = []
    for validator in active:
        all_issues.extend(validator(tags))
    return all_issues
