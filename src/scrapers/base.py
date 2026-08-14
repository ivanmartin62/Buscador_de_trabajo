"""Interfaz común para adaptadores de fuentes oficiales."""

from abc import ABC, abstractmethod
from typing import Any
from src.models import OfertaEmpleo


class BaseScraper(ABC):
    @property
    @abstractmethod
    def source_name(self) -> str: ...

    @abstractmethod
    def fetch(self) -> Any: ...

    @abstractmethod
    def parse(self, raw_data: Any) -> list[OfertaEmpleo]: ...

    def get_offers(self) -> list[OfertaEmpleo]:
        return self.parse(self.fetch())
