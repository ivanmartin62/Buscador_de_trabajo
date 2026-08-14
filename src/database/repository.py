"""Contrato de persistencia independiente de la interfaz."""

from abc import ABC, abstractmethod
from src.models import OfertaEmpleo


class Repository(ABC):
    @abstractmethod
    def listar_ofertas(self) -> list[OfertaEmpleo]:
        """Devuelve las ofertas indexadas."""

    @abstractmethod
    def guardar_ofertas(self, ofertas: list[OfertaEmpleo]) -> None:
        """Reemplaza el índice persistido."""
