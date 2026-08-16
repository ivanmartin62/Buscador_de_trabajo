"""Composición de fuentes activas para el modo temporal sin base de datos."""

from src.models import OfertaEmpleo
from src.scrapers.argentina_gob_ar import ArgentinaGobArScraper, cargar_urls
from src.services.aggregator import ErrorFuente, recolectar
from src.services.deduplicator import deduplicar


def consultar_ofertas_oficiales() -> tuple[list[OfertaEmpleo], list[ErrorFuente]]:
    """Consulta las páginas configuradas y devuelve resultados sólo en memoria."""
    scrapers = [ArgentinaGobArScraper(url) for url in cargar_urls()]
    ofertas, errores = recolectar(scrapers)
    return deduplicar(ofertas), errores
