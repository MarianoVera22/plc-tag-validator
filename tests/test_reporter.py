"""Tests del formateo de reportes."""

from __future__ import annotations

from plc_tag_validator.models import Severity, ValidationIssue
from plc_tag_validator.reporter import build_report, has_errors


def test_report_no_issues() -> None:
    """Sin problemas, el reporte lo indica claramente."""
    report = build_report([], total_tags=5)
    assert "Sin problemas" in report
    assert "5 tags" in report


def test_report_with_errors_and_warnings() -> None:
    """El reporte separa errores de advertencias."""
    issues = [
        ValidationIssue(Severity.ERROR, "Dirección inválida", tag_name="A"),
        ValidationIssue(Severity.WARNING, "Sin descripción", tag_name="B"),
    ]
    report = build_report(issues, total_tags=2)
    assert "ERRORES (1)" in report
    assert "ADVERTENCIAS (1)" in report


def test_has_errors_true() -> None:
    """has_errors detecta cuando hay al menos un ERROR."""
    issues = [ValidationIssue(Severity.ERROR, "x")]
    assert has_errors(issues) is True


def test_has_errors_false_with_only_warnings() -> None:
    """has_errors es False si solo hay warnings."""
    issues = [ValidationIssue(Severity.WARNING, "x")]
    assert has_errors(issues) is False
