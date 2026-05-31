"""Interfaz de línea de comandos para el validador de tags de PLC."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from plc_tag_validator.exceptions import PlcValidatorError
from plc_tag_validator.loaders import load_tags
from plc_tag_validator.reporter import build_report, has_errors
from plc_tag_validator.validators import validate_all

logger = logging.getLogger(__name__)


def _build_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de la CLI."""
    parser = argparse.ArgumentParser(
        prog="plc-tag-validator",
        description="Valida archivos de configuración de tags de PLC (estilo Siemens S7).",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Ruta al archivo de tags (.csv o .json)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Muestra información de depuración",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Punto de entrada de la CLI.

    Args:
        argv: argumentos de línea de comandos. Si es None, usa sys.argv.

    Returns:
        Código de salida: 0 si todo OK (sin errores), 1 si hay errores o fallos.
    """
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        logger.debug("Cargando tags desde %s", args.file)
        tags = load_tags(args.file)
        logger.debug("Cargados %d tags", len(tags))

        issues = validate_all(tags)
        report = build_report(issues, total_tags=len(tags))
        print(report)

        return 1 if has_errors(issues) else 0

    except PlcValidatorError as exc:
        # Errores esperados de nuestra librería: mensaje limpio, sin traceback.
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
