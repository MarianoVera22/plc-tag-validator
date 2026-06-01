"""Tests de carga de archivos CSV y JSON."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plc_tag_validator.exceptions import LoaderError
from plc_tag_validator.loaders import load_csv, load_json, load_tags
from plc_tag_validator.models import DataType

CSV_CONTENT = """name,address,data_type,description
Motor_01_Run,M100.0,BOOL,Marcha del motor 1
Temp_Horno,IW64,INT,Temperatura del horno
"""


def test_load_csv_ok(tmp_path: Path) -> None:
    """Un CSV bien formado se carga correctamente."""
    csv_file = tmp_path / "tags.csv"
    csv_file.write_text(CSV_CONTENT, encoding="utf-8")

    tags = load_csv(csv_file)

    assert len(tags) == 2
    assert tags[0].name == "Motor_01_Run"
    assert tags[0].data_type == DataType.BOOL
    assert tags[1].address == "IW64"


def test_load_csv_missing_file(tmp_path: Path) -> None:
    """Cargar un archivo inexistente lanza LoaderError."""
    with pytest.raises(LoaderError, match="no existe"):
        load_csv(tmp_path / "no_existe.csv")


def test_load_csv_invalid_datatype(tmp_path: Path) -> None:
    """Un tipo de dato inválido lanza LoaderError indicando la línea."""
    bad_csv = "name,address,data_type\nFoo,M0.0,FLOATING\n"
    csv_file = tmp_path / "bad.csv"
    csv_file.write_text(bad_csv, encoding="utf-8")

    with pytest.raises(LoaderError, match="Línea 2"):
        load_csv(csv_file)


def test_load_json_ok(tmp_path: Path) -> None:
    """Un JSON bien formado se carga correctamente."""
    data = [
        {"name": "Motor_01_Run", "address": "M100.0", "data_type": "BOOL"},
        {"name": "Temp", "address": "IW64", "data_type": "INT", "description": "Temp"},
    ]
    json_file = tmp_path / "tags.json"
    json_file.write_text(json.dumps(data), encoding="utf-8")

    tags = load_json(json_file)

    assert len(tags) == 2
    assert tags[1].description == "Temp"


def test_load_json_invalid_syntax(tmp_path: Path) -> None:
    """Un JSON con sintaxis rota lanza LoaderError."""
    json_file = tmp_path / "broken.json"
    json_file.write_text("{ this is not valid json", encoding="utf-8")

    with pytest.raises(LoaderError, match="JSON inválido"):
        load_json(json_file)


def test_load_tags_dispatches_by_extension(tmp_path: Path) -> None:
    """load_tags elige el loader según la extensión."""
    csv_file = tmp_path / "tags.csv"
    csv_file.write_text(CSV_CONTENT, encoding="utf-8")
    assert len(load_tags(csv_file)) == 2


def test_load_tags_unsupported_extension(tmp_path: Path) -> None:
    """Una extensión no soportada lanza LoaderError."""
    txt_file = tmp_path / "tags.txt"
    txt_file.write_text("algo", encoding="utf-8")
    with pytest.raises(LoaderError, match="no soportado"):
        load_tags(txt_file)


def test_load_json_not_a_list(tmp_path: Path) -> None:
    """Un JSON que es un objeto (no una lista) lanza LoaderError."""
    json_file = tmp_path / "object.json"
    json_file.write_text("{}")  # ¿qué contenido? un objeto JSON: {}
    with pytest.raises(LoaderError, match="debe ser una lista"):  # ¿qué palabra del mensaje?
        load_json(json_file)
