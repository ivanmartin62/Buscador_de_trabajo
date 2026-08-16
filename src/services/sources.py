"""Lectura del registro declarativo y estados operativos de fuentes."""

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class Fuente:
    id: str
    nombre: str
    organismo: str
    nivel: str
    provincia: str | None
    url: str | None
    tipo: str
    metodo: str
    estado: str
    ultima_revision: str | None
    nota: str | None = None


@dataclass(frozen=True)
class EstadoFuente:
    last_attempt: str | None = None
    last_success: str | None = None
    status: str = "pending"
    number_of_offers: int = 0
    error_message: str | None = None


def cargar_fuentes(ruta: Path | str = "config/sources.json") -> list[Fuente]:
    with Path(ruta).open(encoding="utf-8") as archivo:
        return [Fuente(**item) for item in json.load(archivo)]


def cargar_jurisdicciones(
    ruta: Path | str = "config/jurisdicciones.json",
) -> list[str]:
    """Carga las 23 provincias y CABA sin asociarles URLs no verificadas."""
    with Path(ruta).open(encoding="utf-8") as archivo:
        return [str(nombre) for nombre in json.load(archivo)]


def cargar_estados(ruta: Path | str = "data/source_status.json") -> dict[str, EstadoFuente]:
    archivo_estado = Path(ruta)
    if not archivo_estado.exists():
        return {}
    with archivo_estado.open(encoding="utf-8") as archivo:
        return {clave: EstadoFuente(**valor) for clave, valor in json.load(archivo).items()}
