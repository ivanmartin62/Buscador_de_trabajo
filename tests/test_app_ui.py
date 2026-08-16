from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).parents[1] / "app.py"


def test_app_inicia_con_buscador_general_sin_botones_de_profesion() -> None:
    app = AppTest.from_file(APP).run(timeout=20)

    assert not app.exception
    assert app.text_input[0].label == "¿Qué trabajo estás buscando?"
    etiquetas = {boton.label for boton in app.button}
    assert "Buscar" in etiquetas
    assert "⚖️ Abogado" not in etiquetas
    assert "💻 Programador" not in etiquetas


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
        "Nivel",
        "Ordenar por",
    }


def test_fuentes_distinguen_enlace_publico_de_integracion() -> None:
    app = AppTest.from_file(APP).run(timeout=20)

    assert not app.exception
    assert "Uso en el buscador" in app.dataframe[0].value.columns
    concursar = app.dataframe[0].value.loc[
        app.dataframe[0].value["Fuente"] == "CONCURSAR - Portal de Concursos Públicos"
    ].iloc[0]
    assert concursar["Estado"] == "🟠 Limitada"
    assert concursar["Uso en el buscador"] == "Aún no incluida"
