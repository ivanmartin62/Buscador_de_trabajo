"""Búsqueda local, explicable y desacoplada de la recolección web."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
import unicodedata

from src.models import OfertaEmpleo

PESOS = {
    "titulo": 100,
    "profesion": 90,
    "especialidad": 80,
    "carrera": 75,
    "requisitos": 50,
    "funciones": 45,
    "conocimientos": 45,
    "tecnologias": 45,
    "descripcion": 30,
    "categoria": 25,
    "organismo": 20,
    "localidad": 15,
    "provincia": 15,
}


def normalizar_texto(texto: str | None) -> str:
    """Elimina acentos y puntuación, unifica caja y espacios."""
    if not texto:
        return ""
    sin_acentos = "".join(
        caracter
        for caracter in unicodedata.normalize("NFKD", texto.casefold())
        if not unicodedata.combining(caracter)
    )
    return " ".join(re.sub(r"[^a-z0-9]+", " ", sin_acentos).split())


def contiene_termino(contenido: str, termino: str) -> bool:
    """Busca palabras o frases completas para evitar coincidencias accidentales."""
    return f" {termino} " in f" {contenido} "


def cargar_sinonimos(ruta: Path | None = None) -> dict[str, list[str]]:
    ruta = ruta or Path(__file__).parents[2] / "config" / "synonyms.json"
    with ruta.open(encoding="utf-8") as archivo:
        datos = json.load(archivo)
    return {
        normalizar_texto(clave): [normalizar_texto(valor) for valor in valores]
        for clave, valores in datos.items()
    }


@dataclass(frozen=True)
class ResultadoBusqueda:
    oferta: OfertaEmpleo
    puntaje: int
    tipo: str
    coincidencias: tuple[str, ...]


class MotorBusqueda:
    """Rankea ofertas ya recolectadas; nunca realiza solicitudes HTTP."""

    def __init__(self, sinonimos: dict[str, list[str]] | None = None) -> None:
        self.sinonimos = sinonimos or cargar_sinonimos()

    def buscar(self, consulta: str, ofertas: list[OfertaEmpleo]) -> list[ResultadoBusqueda]:
        consulta_normalizada = normalizar_texto(consulta)
        if not consulta_normalizada:
            ordenadas = sorted(
                ofertas, key=lambda oferta: oferta.fecha_publicacion or oferta.fecha_recoleccion.date(), reverse=True
            )
            return [ResultadoBusqueda(oferta, 0, "reciente", ()) for oferta in ordenadas]

        terminos_directos = consulta_normalizada.split()
        relacionados = self._terminos_relacionados(consulta_normalizada, terminos_directos)
        resultados = [
            resultado
            for oferta in ofertas
            if (resultado := self._evaluar(oferta, terminos_directos, relacionados))
        ]
        return sorted(
            resultados,
            key=lambda resultado: (
                -resultado.puntaje,
                resultado.oferta.fecha_cierre is None,
                resultado.oferta.fecha_cierre,
            ),
        )

    def _terminos_relacionados(self, consulta: str, palabras: list[str]) -> set[str]:
        relacionados: set[str] = set()
        for clave, variantes in self.sinonimos.items():
            if clave == consulta or clave in palabras:
                relacionados.update(variantes)
        return relacionados

    def _evaluar(self, oferta: OfertaEmpleo, directos: list[str], relacionados: set[str]) -> ResultadoBusqueda | None:
        puntaje = 0
        encontrados_directos: set[str] = set()
        encontrados_relacionados: set[str] = set()
        for campo, peso in PESOS.items():
            contenido = normalizar_texto(getattr(oferta, campo, None))
            if not contenido:
                continue
            directos_campo = {
                termino for termino in directos if contiene_termino(contenido, termino)
            }
            relacionados_campo = {
                termino
                for termino in relacionados
                if contiene_termino(contenido, termino)
            }
            puntaje += peso * len(directos_campo)
            puntaje += int(peso * 0.7) * len(relacionados_campo)
            encontrados_directos.update(directos_campo)
            encontrados_relacionados.update(relacionados_campo)
        if not encontrados_directos and not encontrados_relacionados:
            return None
        cobertura = len(encontrados_directos) / len(directos)
        puntaje += int(cobertura * 40)
        tipo = "directa" if cobertura == 1 else "relacionada"
        coincidencias = tuple(sorted(encontrados_directos | encontrados_relacionados))
        return ResultadoBusqueda(oferta, puntaje, tipo, coincidencias)
