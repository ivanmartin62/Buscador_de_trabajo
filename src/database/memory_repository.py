"""Repositorio temporal: conserva ofertas sólo durante la sesión en ejecución."""

from collections.abc import MutableSequence

from src.database.repository import Repository
from src.models import OfertaEmpleo


class MemoriaRepository(Repository):
    """Implementación sin archivos ni base de datos.

    Puede recibir una lista administrada por ``st.session_state`` para sobrevivir
    a los reruns de una sesión de Streamlit, pero nunca escribe en disco.
    """

    def __init__(self, ofertas: MutableSequence[OfertaEmpleo] | None = None) -> None:
        self._ofertas = ofertas if ofertas is not None else []

    def listar_ofertas(self) -> list[OfertaEmpleo]:
        return list(self._ofertas)

    def guardar_ofertas(self, ofertas: list[OfertaEmpleo]) -> None:
        self._ofertas.clear()
        self._ofertas.extend(ofertas)
