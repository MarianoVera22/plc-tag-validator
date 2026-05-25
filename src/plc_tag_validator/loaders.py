"""Carga de tags desde archivos CSV y JSON."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from plc_tag_validator.exceptions import LoaderError
from plc_tag_validator.models import DataType, Tag

# Campos obligatorios que esperamos en cada fila
_REQUIRED_FIELDS = {"name", "address", "data_type"}


# @dataclass_unused = None  # (placeholder, lo quitamos abajo)


def _row_to_tag(row: dict[str, str], line: int) -> Tag:
    """Convierte una fila (dict) en un Tag, validando lo mínimo estructural.

    Args:
        row: diccionario con las claves name, address, data_type, description.
        line: número de línea en el archivo (para mensajes de error).

    Returns:
        Un objeto Tag.

    Raises:
        LoaderError: si faltan campos o el data_type no es válido.
    """
    # Verificar campos obligatorios presentes
    missing = _REQUIRED_FIELDS - row.keys()
    if missing:
        raise LoaderError(
            f"Línea {line}: faltan campos obligatorios: {', '.join(sorted(missing))}"
        )

    raw_type = row["data_type"].strip().upper()
    try:
        data_type = DataType(raw_type)
    except ValueError:
        valid = ", ".join(t.value for t in DataType)
        raise LoaderError(
            f"Línea {line}: tipo de dato '{raw_type}' inválido. Válidos: {valid}"
        ) from None

    return Tag(
        name=row["name"],
        address=row["address"],
        data_type=data_type,
        description=row.get("description", ""),
    )


def load_csv(path: Path) -> list[Tag]:
    """Carga tags desde un archivo CSV.

    El CSV debe tener encabezados: name, address, data_type, description (opcional).

    Args:
        path: ruta al archivo CSV.

    Returns:
        Lista de Tags.

    Raises:
        LoaderError: si el archivo no existe o tiene filas inválidas.
    """
    if not path.exists():
        raise LoaderError(f"El archivo no existe: {path}")

    tags: list[Tag] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        # enumerate desde 2: línea 1 es el encabezado
        for line, row in enumerate(reader, start=2):
            tags.append(_row_to_tag(row, line))

    return tags


def load_json(path: Path) -> list[Tag]:
    """Carga tags desde un archivo JSON (lista de objetos).

    Args:
        path: ruta al archivo JSON.

    Returns:
        Lista de Tags.

    Raises:
        LoaderError: si el archivo no existe, no es JSON válido, o tiene entradas inválidas.
    """
    if not path.exists():
        raise LoaderError(f"El archivo no existe: {path}")

    with path.open(encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as exc:
            raise LoaderError(f"JSON inválido en {path}: {exc}") from exc

    if not isinstance(data, list):
        raise LoaderError("El JSON debe ser una lista de objetos de tag")

    tags: list[Tag] = []
    for line, entry in enumerate(data, start=1):
        if not isinstance(entry, dict):
            raise LoaderError(f"Entrada {line}: se esperaba un objeto, no {type(entry).__name__}")
        tags.append(_row_to_tag(entry, line))

    return tags


def load_tags(path: Path) -> list[Tag]:
    """Carga tags detectando el formato por la extensión del archivo.

    Args:
        path: ruta al archivo (.csv o .json).

    Returns:
        Lista de Tags.

    Raises:
        LoaderError: si la extensión no es soportada.
    """
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_csv(path)
    if suffix == ".json":
        return load_json(path)
    raise LoaderError(f"Formato no soportado: '{suffix}'. Usá .csv o .json")


