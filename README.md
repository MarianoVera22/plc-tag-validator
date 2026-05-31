# PLC Tag Validator

[![Tests](https://github.com/MarianoVera22/plc-tag-validator/actions/workflows/ci.yml/badge.svg)](https://github.com/MarianoVera22/plc-tag-validator/actions/workflows/ci.yml)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Herramienta CLI para validar archivos de configuración de tags de PLC al estilo Siemens S7.
Detecta direcciones mal formadas, incoherencias entre tipo de dato y dirección, nombres duplicados
y otros problemas comunes **antes** de cargar la configuración en planta.

## ¿Por qué?

En proyectos de automatización industrial, los tags de PLC suelen vivir en archivos CSV o JSON
exportados desde TIA Portal, Excel u otras herramientas. Errores tipográficos o inconsistencias
en esos archivos pueden costar horas durante la puesta en marcha. Esta herramienta los detecta
en segundos.

## Características

- Parser de direcciones Siemens S7 (`M100.0`, `DB10.DBD4`, `IW64`, etc.)
- Validación de coherencia tipo–dirección (un `REAL` no puede vivir en una `DBW`)
- Detección de nombres y direcciones duplicadas
- Validación de longitud de nombres (límite clásico de 24 caracteres)
- Soporte de archivos CSV y JSON
- Salida con códigos de retorno estándar (integrable en CI/CD)
- Type-checked con `mypy --strict`, linteado con `ruff`, ~95% test coverage

## Instalación

Requiere Python 3.13+ y [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/MarianoVera22/plc-tag-validator.git
cd plc-tag-validator
uv sync
```

## Uso

```bash
uv run plc-tag-validator examples/tags_ok.csv
```

### Formato de entrada esperado (CSV)

```csv
name,address,data_type,description
Motor_01_Run,M100.0,BOOL,Marcha del motor 1
Motor_01_Velocidad,DB10.DBD4,REAL,Velocidad en RPM
Temp_Horno,IW64,INT,Temperatura del horno
```

### Ejemplo de salida

Tags analizados: 4
ERRORES (2):
[ERROR] 'Motor_Run': Dirección inválida 'X999': no coincide con ningún formato Siemens S7
[ERROR] 'Velocidad': Incoherencia: tipo REAL (32 bits) en dirección 'DB10.DBW4' (16 bits)
ADVERTENCIAS (1):
[WARNING] 'SinDescripcion': Tag sin descripción
Resumen: 4 tags, 2 errores, 1 advertencias

## Tipos de dato soportados

`BOOL`, `BYTE`, `INT`, `WORD`, `DINT`, `DWORD`, `REAL`

## Formatos de dirección soportados

| Formato | Ejemplo | Descripción |
|---|---|---|
| Bit de memoria | `M100.0` | Marca, bit individual |
| Byte/Word/DWord de memoria | `MB10`, `MW20`, `MD40` | Marca con tamaño |
| Bit de entrada/salida | `I0.1`, `Q2.3` | Imagen de proceso |
| Word/DWord de I/O | `IW64`, `QD12` | Imagen con tamaño |
| Bit en DB | `DB10.DBX0.0` | Bit dentro de un Data Block |
| Tamaño en DB | `DB10.DBB2`, `DB10.DBW4`, `DB10.DBD8` | Byte/Word/DWord en DB |

## Desarrollo

```bash
uv sync                              # instalar dependencias
uv run pytest                        # correr tests
uv run mypy src                      # verificar tipos
uv run ruff check .                  # lintear
uv run ruff check --fix .            # arreglar lo auto-arreglable
```

## Arquitectura

src/plc_tag_validator/
├── models.py        # Tag, DataType, ValidationIssue, Severity
├── address.py       # Parser de direcciones Siemens
├── exceptions.py    # Excepciones del dominio
├── loaders.py       # Carga de archivos CSV/JSON
├── validators.py    # Reglas de validación (extensibles vía Protocol)
├── reporter.py      # Formateo de salida
└── cli.py           # Punto de entrada CLI

## Licencia

MIT

