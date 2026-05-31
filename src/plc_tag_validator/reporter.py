"""Formateo de los resultados de validación para mostrar al usuario."""

from __future__ import annotations

from plc_tag_validator.models import Severity, ValidationIssue


def _format_issue(issue: ValidationIssue) -> str:
    """Formatea un solo problema como una línea de texto."""
    parts = [f"[{issue.severity.value}]"]
    if issue.tag_name:
        parts.append(f"'{issue.tag_name}':")
    parts.append(issue.message)
    return "  " + " ".join(parts)


def build_report(issues: list[ValidationIssue], total_tags: int) -> str:
    """Construye el reporte de texto completo a partir de los problemas detectados.

    Args:
        issues: lista de problemas encontrados por los validadores.
        total_tags: cantidad total de tags analizados.

    Returns:
        El reporte formateado como un único string multilínea.
    """
    errors = [i for i in issues if i.severity is Severity.ERROR]
    warnings = [i for i in issues if i.severity is Severity.WARNING]

    lines: list[str] = []
    lines.append(f"Tags analizados: {total_tags}")
    lines.append("")

    if errors:
        lines.append(f"ERRORES ({len(errors)}):")
        lines.extend(_format_issue(i) for i in errors)
        lines.append("")

    if warnings:
        lines.append(f"ADVERTENCIAS ({len(warnings)}):")
        lines.extend(_format_issue(i) for i in warnings)
        lines.append("")

    if not issues:
        lines.append("Sin problemas. Todos los tags son válidos.")
        lines.append("")

    lines.append(
        f"Resumen: {total_tags} tags, {len(errors)} errores, {len(warnings)} advertencias"
    )

    return "\n".join(lines)


def has_errors(issues: list[ValidationIssue]) -> bool:
    """Devuelve True si hay al menos un problema de severidad ERROR."""
    return any(i.severity is Severity.ERROR for i in issues)
