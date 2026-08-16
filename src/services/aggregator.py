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
            logger.info("Consultando fuente %s", scraper.source_name)
            ofertas_fuente = scraper.get_offers()
            ofertas.extend(ofertas_fuente)
            logger.info(
                "%s: %d ofertas encontradas", scraper.source_name, len(ofertas_fuente)
            )
        except Exception as error:  # frontera de aislamiento entre fuentes
            logger.exception("No fue posible consultar %s", scraper.source_name)
            errores.append(ErrorFuente(scraper.source_name, str(error)))
    return ofertas, errores
