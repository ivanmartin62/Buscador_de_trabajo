from src.services.sources import RegistroFuentes, cargar_fuentes, cargar_jurisdicciones


def test_fuentes_judiciales_pendientes_no_inventan_url() -> None:
    judiciales = {
        fuente.id: fuente
        for fuente in cargar_fuentes()
        if fuente.id
        in {
            "poder_judicial_nacion",
            "consejo_magistratura_nacion",
            "ministerio_publico_fiscal_nacion",
            "ministerio_publico_defensa_nacion",
        }
    }

    assert len(judiciales) == 4
    assert all(fuente.estado == "pending" for fuente in judiciales.values())
    assert all(fuente.url is None for fuente in judiciales.values())


def test_argentina_gob_ar_es_la_unica_fuente_activa() -> None:
    activas = [fuente for fuente in cargar_fuentes() if fuente.estado == "active"]

    assert [fuente.id for fuente in activas] == ["argentina_gob_ar_convocatorias"]


def test_registra_todas_las_jurisdicciones_argentinas() -> None:
    jurisdicciones = cargar_jurisdicciones()

    assert len(jurisdicciones) == 24
    assert "Tucumán" in jurisdicciones
    assert "Ciudad Autónoma de Buenos Aires" in jurisdicciones


def test_concursar_limitada_y_fuentes_tucuman_pendientes() -> None:
    fuentes = {fuente.id: fuente for fuente in cargar_fuentes()}

    assert fuentes["concursar_nacion"].url == "https://concursar.miportal.gob.ar/"
    assert fuentes["concursar_nacion"].estado == "limited"
    assert fuentes["concursar_nacion"].metodo == "portal_interactivo_sin_api_publica"
    assert fuentes["poder_judicial_tucuman"].url is None
    assert fuentes["ministerio_publico_fiscal_tucuman"].estado == "pending"


def test_registro_central_expone_solo_fuentes_activas() -> None:
    registro = RegistroFuentes.desde_archivo()

    assert [fuente.id for fuente in registro.activas()] == [
        "argentina_gob_ar_convocatorias"
    ]
    assert registro.obtener("concursar_nacion").estado == "limited"
    assert registro.obtener("inexistente") is None
