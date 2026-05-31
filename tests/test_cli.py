"""Tests de la interfaz de línea de comandos."""

from __future__ import annotations

from pathlib import Path

from plc_tag_validator.cli import main

GOOD_CSV = """name,address,data_type,description
Motor_Run,M100.0,BOOL,Marcha
Velocidad,DB10.DBD4,REAL,RPM
"""

BAD_CSV = """name,address,data_type,description
Motor_Run,X999,BOOL,Direccion mala
"""


def test_cli_valid_file_returns_zero(tmp_path: Path) -> None:
    """Un archivo válido devuelve exit code 0."""
    csv_file = tmp_path / "ok.csv"
    csv_file.write_text(GOOD_CSV, encoding="utf-8")
    assert main([str(csv_file)]) == 0


def test_cli_file_with_errors_returns_one(tmp_path: Path) -> None:
    """Un archivo con errores devuelve exit code 1."""
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(BAD_CSV, encoding="utf-8")
    assert main([str(csv_file)]) == 1


def test_cli_missing_file_returns_one(tmp_path: Path) -> None:
    """Un archivo inexistente devuelve exit code 1 sin explotar."""
    assert main([str(tmp_path / "no_existe.csv")]) == 1
