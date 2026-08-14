from pathlib import Path

from src.scrapers.argentina_gob_ar import ArgentinaGobArScraper
from src.services.search import MotorBusqueda


FIXTURE = Path(__file__).parent / "fixtures" / "argentina_gob_ar_convocatoria.html"
URL = "https://www.argentina.gob.ar/convocatoria-de-prueba"


def test_parser_conserva_texto_requisitos_y_url_oficial() -> None:
    scraper = ArgentinaGobArScraper(URL)
    ofertas = scraper.parse(FIXTURE.read_text(encoding="utf-8"))

    assert len(ofertas) == 1
    assert ofertas[0].titulo == "Convocatoria interna - Ministerio de Defensa"
    assert "Abogacía" in ofertas[0].descripcion
    assert str(ofertas[0].url_original).rstrip("/") == URL


def test_abogado_encuentra_convocatoria_por_requisitos() -> None:
    oferta = ArgentinaGobArScraper(URL).parse(FIXTURE.read_text(encoding="utf-8"))[0]

    resultados = MotorBusqueda().buscar("abogado", [oferta])

    assert resultados
    assert "abogacia" in resultados[0].coincidencias
    assert resultados[0].tipo == "relacionada"
