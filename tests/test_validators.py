"""Tests de las reglas de validación."""

from __future__ import annotations

import pytest

from plc_tag_validator.models import DataType, Severity, Tag
from plc_tag_validator.validators import (
    validate_addresses,
    validate_all,
    validate_descriptions,
    validate_name_length,
    validate_type_address_coherence,
    validate_unique_addresses,
    validate_unique_names,
)


@pytest.fixture
def valid_tags() -> list[Tag]:
    """Un conjunto de tags todos correctos."""
    return [
        Tag("Motor_Run", "M100.0", DataType.BOOL, "Marcha motor"),
        Tag("Velocidad", "DB10.DBD4", DataType.REAL, "Velocidad RPM"),
        Tag("Temperatura", "IW64", DataType.INT, "Temp horno"),
    ]


def test_valid_tags_have_no_issues(valid_tags: list[Tag]) -> None:
    """Tags correctos no generan ningún problema."""
    issues = validate_all(valid_tags)
    assert issues == []


def test_detects_invalid_address() -> None:
    """Una dirección mal formada genera un ERROR."""
    tags = [Tag("Bad", "X999", DataType.BOOL, "desc")]
    issues = validate_addresses(tags)
    assert len(issues) == 1
    assert issues[0].severity == Severity.ERROR


def test_detects_type_address_mismatch() -> None:
    """Un REAL (32 bits) en una dirección de word (16 bits) es ERROR."""
    tags = [Tag("Mismatch", "DB10.DBW4", DataType.REAL, "desc")]
    issues = validate_type_address_coherence(tags)
    assert len(issues) == 1
    assert "Incoherencia" in issues[0].message


def test_detects_duplicate_names() -> None:
    """Nombres repetidos generan un ERROR."""
    tags = [
        Tag("Motor", "M0.0", DataType.BOOL, "uno"),
        Tag("Motor", "M0.1", DataType.BOOL, "dos"),
    ]
    issues = validate_unique_names(tags)
    assert len(issues) == 1
    assert issues[0].severity == Severity.ERROR


def test_detects_duplicate_addresses() -> None:
    """Direcciones repetidas generan un WARNING."""
    tags = [
        Tag("TagA", "M0.0", DataType.BOOL, "uno"),
        Tag("TagB", "M0.0", DataType.BOOL, "dos"),
    ]
    issues = validate_unique_addresses(tags)
    assert len(issues) == 1
    assert issues[0].severity == Severity.WARNING


def test_detects_missing_description() -> None:
    """Un tag sin descripción genera un WARNING."""
    tags = [Tag("NoDesc", "M0.0", DataType.BOOL, "")]
    issues = validate_descriptions(tags)
    assert len(issues) == 1
    assert issues[0].severity == Severity.WARNING

def test_validate_name_length() -> None:
    """Nombres largos generan WARNING, los cortos no."""
    tags = [
        Tag("NombreDeTagConMasDe24Caracteres", "M0.0", DataType.BOOL, "desc largo"),
        Tag("Corto", "M0.1", DataType.BOOL, "desc corto"),
    ]
    issues = validate_name_length(tags)
    assert len(issues) == 1  # solo el largo, no el corto
    assert issues[0].severity == Severity.WARNING


def test_validate_all_combines_issues() -> None:
    """validate_all junta problemas de múltiples reglas."""
    tags = [
        Tag("Dup", "X999", DataType.BOOL, ""),   # dirección inválida + sin desc
        Tag("Dup", "M0.0", DataType.BOOL, "ok"),  # nombre duplicado
    ]
    issues = validate_all(tags)
    # Esperamos: 1 dirección inválida + 1 nombre duplicado + 1 sin descripción
    assert len(issues) >= 3


def test_validate_all_accepts_custom_validators() -> None:
    """validate_all puede recibir una lista custom de validadores."""
    tags = [Tag("Motor", "X999", DataType.BOOL, "desc")]
    # Solo corremos el validador de direcciones, ignorando los demás.
    issues = validate_all(tags, validators=[validate_addresses])
    assert len(issues) == 1
