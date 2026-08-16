"""Adaptador preliminar para páginas de convocatorias de Argentina.gob.ar."""

from pathlib import Path
from typing import Any
import json

from bs4 import BeautifulSoup
import httpx

from src.models import OfertaEmpleo
from src.scrapers.base import BaseScraper

USER_AGENT = (
    "EmpleoPublicoArgentina/0.2 "
    "(buscador educativo; https://github.com/ivanmartin62/Buscador_de_trabajo)"
)


class ArgentinaGobArScraper(BaseScraper):
    """Obtiene una convocatoria sin asumir selectores específicos del portal."""

    def __init__(self, url: str, timeout: float = 15.0) -> None:
        self.url = url
        self.timeout = timeout

    @property
    def source_name(self) -> str:
        return "Argentina.gob.ar - Convocatorias de empleo público"

    def fetch(self) -> str:
        respuesta = httpx.get(
            self.url,
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": USER_AGENT, "Accept": "text/html"},
        )
        respuesta.raise_for_status()
        return respuesta.text

    def parse(self, raw_data: Any) -> list[OfertaEmpleo]:
        if not isinstance(raw_data, str):
            raise TypeError("La respuesta de Argentina.gob.ar debe ser HTML")
        soup = BeautifulSoup(raw_data, "html.parser")
        titulo = self._extraer_titulo(soup)
        contenido = soup.find("main") or soup.body
        texto = contenido.get_text(" ", strip=True) if contenido else ""
        if not titulo or not texto:
            raise ValueError("La página oficial no contiene título y texto utilizables")
        return [
            OfertaEmpleo(
                titulo=titulo,
                descripcion=texto,
                tipo_convocatoria="Concurso",
                nivel_gobierno="Nacional",
                fuente=self.source_name,
                url_original=self.url,
                url_fuente=self.url,
            )
        ]

    @staticmethod
    def _extraer_titulo(soup: BeautifulSoup) -> str | None:
        encabezado = soup.find("h1")
        if encabezado and encabezado.get_text(strip=True):
            return encabezado.get_text(" ", strip=True)
        meta = soup.find("meta", property="og:title")
        if meta and meta.get("content"):
            return str(meta["content"]).strip()
        return soup.title.get_text(" ", strip=True) if soup.title else None


def cargar_urls(ruta: Path | str = "config/convocatorias_argentina_gob_ar.json") -> list[str]:
    with Path(ruta).open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return [str(url) for url in datos]
