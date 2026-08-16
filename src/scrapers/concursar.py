"""Parser defensivo para el DOM público del portal CONCURSAR."""

import re
from typing import Any
import unicodedata
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag
import httpx

from src.models import EstadoOferta, OfertaEmpleo
from src.scrapers.base import BaseScraper

URL_CONCURSAR = "https://concursar.miportal.gob.ar/"
ESTADOS = {
    "inscripcion cerrada": EstadoOferta.CERRADA,
    "proximo a abrir inscripcion": EstadoOferta.PROXIMA,
    "inscripcion abierta": EstadoOferta.ABIERTA,
}


class ConcursarScraper(BaseScraper):
    """Interpreta tarjetas sin depender de los XPath absolutos de presentación."""

    def __init__(self, timeout: float = 15.0) -> None:
        self.timeout = timeout

    @property
    def source_name(self) -> str:
        return "CONCURSAR - Portal de Concursos Públicos"

    def fetch(self) -> str:
        respuesta = httpx.get(
            URL_CONCURSAR,
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "EmpleoPublicoArgentina/0.2 (buscador educativo)",
                "Accept": "text/html",
            },
        )
        respuesta.raise_for_status()
        return respuesta.text

    def parse(self, raw_data: Any) -> list[OfertaEmpleo]:
        if not isinstance(raw_data, str):
            raise TypeError("La respuesta de CONCURSAR debe ser HTML")
        soup = BeautifulSoup(raw_data, "html.parser")
        ofertas: list[OfertaEmpleo] = []
        for indicador in soup.find_all("span"):
            estado = _estado_desde_texto(indicador.get_text(" ", strip=True))
            if estado is None:
                continue
            tarjeta = _buscar_tarjeta(indicador)
            if tarjeta is None:
                continue
            oferta = _normalizar_tarjeta(tarjeta, estado, self.source_name)
            if oferta:
                ofertas.append(oferta)
        if not ofertas:
            raise ValueError(
                "CONCURSAR no expuso tarjetas en el HTML recibido; puede requerir JavaScript"
            )
        return ofertas


def _buscar_tarjeta(indicador: Tag) -> Tag | None:
    """Sube por el DOM hasta hallar el bloque que reúne datos y acción oficial."""
    for ancestro in indicador.parents:
        if not isinstance(ancestro, Tag) or ancestro.name in {"body", "html"}:
            break
        if ancestro.find("ul") and ancestro.find(["button", "a"]):
            return ancestro
    return None


def _normalizar_tarjeta(
    tarjeta: Tag, estado: EstadoOferta, fuente: str
) -> OfertaEmpleo | None:
    encabezado = tarjeta.find(["h1", "h2", "h3", "h4", "h5"])
    items = [item.get_text(" ", strip=True) for item in tarjeta.find_all("li")]
    titulo = encabezado.get_text(" ", strip=True) if encabezado else None
    if not titulo and items:
        titulo = items[0]
    if not titulo:
        return None
    enlace = tarjeta.find("a", href=True)
    url_original = urljoin(URL_CONCURSAR, str(enlace["href"])) if enlace else URL_CONCURSAR
    descripcion = items[0] if items else None
    cantidad = _extraer_cantidad(items[1]) if len(items) > 1 else None
    return OfertaEmpleo(
        titulo=titulo,
        descripcion=descripcion,
        tipo_convocatoria="Concurso",
        nivel_gobierno="Nacional",
        cantidad_vacantes=cantidad,
        fuente=fuente,
        url_original=url_original,
        url_fuente=URL_CONCURSAR,
        estado=estado,
    )


def _estado_desde_texto(texto: str) -> EstadoOferta | None:
    normalizado = _sin_acentos(texto)
    return next((estado for etiqueta, estado in ESTADOS.items() if etiqueta in normalizado), None)


def _extraer_cantidad(texto: str) -> int | None:
    coincidencia = re.search(r"\b(\d+)\b", texto.replace(".", ""))
    return int(coincidencia.group(1)) if coincidencia else None


def _sin_acentos(texto: str) -> str:
    return "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto.casefold())
        if not unicodedata.combining(caracter)
    )
