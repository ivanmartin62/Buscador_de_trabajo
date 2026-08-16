"""Deduplicación conservadora: sólo elimina coincidencias exactas fuertes."""

from src.models import OfertaEmpleo
from src.services.search import normalizar_texto


def clave_exacta(oferta: OfertaEmpleo) -> tuple[str, ...]:
    if oferta.id:
        return ("id", oferta.fuente, oferta.id)
    return ("url", str(oferta.url_original).rstrip("/"))


def deduplicar(ofertas: list[OfertaEmpleo]) -> list[OfertaEmpleo]:
    unicas: dict[tuple[str, ...], OfertaEmpleo] = {}
    for oferta in ofertas:
        clave = clave_exacta(oferta)
        if clave not in unicas:
            unicas[clave] = oferta
    return list(unicas.values())


def es_probable_duplicado(a: OfertaEmpleo, b: OfertaEmpleo) -> bool:
    """Señala para revisión, sin eliminar, una coincidencia contextual fuerte."""
    return bool(
        a.fecha_cierre
        and a.fecha_cierre == b.fecha_cierre
        and normalizar_texto(a.titulo) == normalizar_texto(b.titulo)
        and normalizar_texto(a.organismo) == normalizar_texto(b.organismo)
    )
