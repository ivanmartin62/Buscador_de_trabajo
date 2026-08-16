from datetime import date

from src.models import OfertaEmpleo
from src.services.search import ResultadoBusqueda
from src.ui.filters import filtrar_resultados, ordenar_resultados


def resultado(
    titulo: str,
    *,
    provincia: str | None = None,
    organismo: str | None = None,
    nivel_gobierno: str | None = None,
    fecha_publicacion: date | None = None,
    fecha_cierre: date | None = None,
) -> ResultadoBusqueda:
    oferta = OfertaEmpleo(
        titulo=titulo,
        provincia=provincia,
        organismo=organismo,
        nivel_gobierno=nivel_gobierno,
        fecha_publicacion=fecha_publicacion,
        fecha_cierre=fecha_cierre,
        fuente="Fuente oficial",
        url_original="https://example.gob.ar/convocatoria",
    )
    return ResultadoBusqueda(oferta, 100, "directa", (titulo.lower(),))


def test_filtros_secundarios_reducen_resultados() -> None:
    resultados = [
        resultado(
            "Abogado",
            provincia="Tucumán",
            organismo="Poder Judicial",
            nivel_gobierno="Provincial",
        ),
        resultado("Programador", provincia="Córdoba", organismo="Municipio"),
    ]

    filtrados = filtrar_resultados(
        resultados,
        provincia="Tucumán",
        organismo="Poder Judicial",
        nivel="Provincial",
    )

    assert [item.oferta.titulo for item in filtrados] == ["Abogado"]


def test_orden_por_fecha_reciente_y_cierre_proximo() -> None:
    resultados = [
        resultado(
            "Primera",
            fecha_publicacion=date(2026, 1, 1),
            fecha_cierre=date(2026, 9, 10),
        ),
        resultado(
            "Segunda",
            fecha_publicacion=date(2026, 2, 1),
            fecha_cierre=date(2026, 9, 5),
        ),
    ]

    assert ordenar_resultados(resultados, "Más recientes")[0].oferta.titulo == "Segunda"
    assert ordenar_resultados(resultados, "Cierre próximo")[0].oferta.titulo == "Segunda"
