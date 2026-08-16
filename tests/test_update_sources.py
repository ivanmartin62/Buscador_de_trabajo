from src.models import OfertaEmpleo
from src.services.aggregator import ErrorFuente
from src import update_sources


def test_actualizacion_cli_resume_resultados_sin_persistir(monkeypatch, capsys) -> None:
    oferta = OfertaEmpleo(
        titulo="Profesional jurídico",
        fuente="Fuente oficial",
        url_original="https://example.gob.ar/concurso",
    )
    monkeypatch.setattr(
        update_sources,
        "consultar_ofertas_oficiales",
        lambda: ([oferta], [ErrorFuente("Otra fuente", "no disponible")]),
    )

    codigo = update_sources.main()
    salida = capsys.readouterr().out

    assert codigo == 0
    assert "1 ofertas normalizadas" in salida
    assert "1 consultas con error" in salida
    assert "no se guardaron" in salida
