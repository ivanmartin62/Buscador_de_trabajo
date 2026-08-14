"""Ejecución tolerante a fallos de scrapers activos."""

from dataclasses import dataclass
import logging
from src.models import OfertaEmpleo
from src.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ErrorFuente:
    fuente: str
    mensaje: str


def recolectar(scrapers: list[BaseScraper]) -> tuple[list[OfertaEmpleo], list[ErrorFuente]]:
    ofertas: list[OfertaEmpleo] = []
    errores: list[ErrorFuente] = []
    for scraper in scrapers:
        try:
            ofertas.extend(scraper.get_offers())
        except Exception as error:  # frontera de aislamiento entre fuentes
            logger.exception("No fue posible consultar %s", scraper.source_name)
            errores.append(ErrorFuente(scraper.source_name, str(error)))
    return ofertas, errores
