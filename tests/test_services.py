from src.models import OfertaEmpleo
from src.services.aggregator import recolectar
from src.services.deduplicator import deduplicar
from src.database.memory_repository import MemoriaRepository


def oferta(url: str = "https://example.gob.ar/1") -> OfertaEmpleo:
    return OfertaEmpleo(titulo="Concurso", fuente="Oficial", url_original=url)


class ScraperOK:
    source_name = "OK"
    def get_offers(self):
        return [oferta()]


class ScraperCaido:
    source_name = "Caída"
    def get_offers(self):
        raise RuntimeError("sin conexión")


def test_fuente_caida_no_interrumpe_agregador() -> None:
    ofertas, errores = recolectar([ScraperCaido(), ScraperOK()])
    assert len(ofertas) == 1
    assert errores[0].fuente == "Caída"


def test_deduplicacion_por_url_exacta() -> None:
    assert len(deduplicar([oferta(), oferta()])) == 1


def test_repositorio_en_memoria_no_escribe_archivos(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    repositorio = MemoriaRepository()
    convocatoria = oferta()
    repositorio.guardar_ofertas([convocatoria])

    assert repositorio.listar_ofertas() == [convocatoria]
    assert list(tmp_path.iterdir()) == []
