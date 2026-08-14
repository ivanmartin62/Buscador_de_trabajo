from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


def test_app_inicia_y_busqueda_rapida_usa_campo_global() -> None:
    app = AppTest.from_file(APP).run(timeout=20)

    assert not app.exception
    assert app.text_input[0].label == "¿Qué trabajo estás buscando?"
    boton_abogado = next(boton for boton in app.button if boton.label == "⚖️ Abogado")

    boton_abogado.click().run(timeout=20)

    assert not app.exception
    assert app.text_input[0].value == "abogado"


def test_app_muestra_filtros_y_metricas_reales() -> None:
    app = AppTest.from_file(APP).run(timeout=20)

    assert {metrica.label for metrica in app.metric} == {
        "Oportunidades",
        "Organismos",
        "Fuentes activas",
        "Última actualización",
    }
    assert {selector.label for selector in app.selectbox} == {
        "Provincia",
        "Tipo",
        "Estado",
        "Organismo",
        "Ordenar por",
    }
