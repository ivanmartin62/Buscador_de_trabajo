from pathlib import Path

import pytest

from src.scrapers.concursar import ConcursarScraper
from src.services.search import MotorBusqueda


FIXTURE = Path(__file__).parent / "fixtures" / "concursar.html"


def test_parser_extrae_estado_cantidad_y_enlace() -> None:
    ofertas = ConcursarScraper().parse(FIXTURE.read_text(encoding="utf-8"))

    assert len(ofertas) == 2
    assert ofertas[0].estado == "proxima"
    assert ofertas[0].cantidad_vacantes == 50
    assert str(ofertas[0].url_original) == "https://concursar.miportal.gob.ar/concursos/123"
    assert ofertas[1].estado == "cerrada"


def test_abogado_encuentra_requisito_de_abogacia() -> None:
    ofertas = ConcursarScraper().parse(FIXTURE.read_text(encoding="utf-8"))

    resultados = MotorBusqueda().buscar("abogado", ofertas)

    assert [resultado.oferta.titulo for resultado in resultados] == [
        "Profesional para Asuntos Jurídicos"
    ]


def test_html_sin_tarjetas_informa_posible_javascript() -> None:
    with pytest.raises(ValueError, match="puede requerir JavaScript"):
        ConcursarScraper().parse("<html><body><div id='app'></div></body></html>")
