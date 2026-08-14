from src.services.sources import cargar_fuentes


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
