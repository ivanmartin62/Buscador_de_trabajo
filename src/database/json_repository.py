"""Persistencia JSON simple para desarrollo y despliegues demostrativos."""

import json
from pathlib import Path
from src.database.repository import Repository
from src.models import OfertaEmpleo


class JSONRepository(Repository):
    def __init__(self, ruta: Path | str = "data/ofertas.json") -> None:
        self.ruta = Path(ruta)

    def listar_ofertas(self) -> list[OfertaEmpleo]:
        if not self.ruta.exists():
            return []
        with self.ruta.open(encoding="utf-8") as archivo:
            return [OfertaEmpleo.model_validate(item) for item in json.load(archivo)]

    def guardar_ofertas(self, ofertas: list[OfertaEmpleo]) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        temporal = self.ruta.with_suffix(".tmp")
        temporal.write_text(
            json.dumps([oferta.model_dump(mode="json") for oferta in ofertas], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporal.replace(self.ruta)
