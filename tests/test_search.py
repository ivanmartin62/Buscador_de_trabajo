from datetime import date

from src.models import OfertaEmpleo
from src.services.search import MotorBusqueda, contiene_termino, normalizar_texto


def oferta(titulo: str, **datos: str) -> OfertaEmpleo:
    return OfertaEmpleo(
        titulo=titulo,
        fuente="Fixture oficial",
        url_original=f"https://example.gob.ar/{titulo.replace(' ', '-').lower()}",
        **datos,
    )


def test_normaliza_acentos_mayusculas_y_puntuacion() -> None:
    assert normalizar_texto("  INGENIERÍA, Pública  ") == "ingenieria publica"


def test_terminos_cortos_no_coinciden_dentro_de_otra_palabra() -> None:
    assert contiene_termino("especialista it", "it")
    assert not contiene_termino("ministerio publico", "it")


def test_abogado_rankea_directo_antes_que_juridico() -> None:
    resultados = MotorBusqueda().buscar(
        "abogado", [oferta("Profesional Jurídico"), oferta("Abogado")]
    )
    assert [resultado.oferta.titulo for resultado in resultados] == ["Abogado", "Profesional Jurídico"]
    assert [resultado.tipo for resultado in resultados] == ["directa", "relacionada"]


def test_procurador_encuentra_termino_legal_relacionado() -> None:
    assert MotorBusqueda().buscar("procurador", [oferta("Asesor legal")])[0].tipo == "relacionada"


def test_programador_sin_importar_mayusculas_encuentra_desarrollador() -> None:
    resultados = MotorBusqueda().buscar("PROGRAMADOR", [oferta("Desarrollador Backend")])
    assert resultados[0].tipo == "relacionada"


def test_varias_palabras_priorizan_mayor_cobertura() -> None:
    resultados = MotorBusqueda().buscar(
        "programador python",
        [oferta("Desarrollador Backend"), oferta("Programador Python")],
    )
    assert resultados[0].oferta.titulo == "Programador Python"


def test_estudiante_ingenieria_y_ciberseguridad() -> None:
    motor = MotorBusqueda()
    pasantia = oferta("Pasantía técnica", requisitos="Estudiante avanzado de Ingeniería")
    seguridad = oferta("Analista SOC", especialidad="Seguridad de la información")
    assert motor.buscar("estudiante de ingeniería", [pasantia])
    assert motor.buscar("ciberseguridad", [seguridad])


def test_busqueda_vacia_muestra_mas_recientes() -> None:
    recientes = MotorBusqueda().buscar(
        "", [oferta("Vieja", fecha_publicacion=date(2025, 1, 1)), oferta("Nueva", fecha_publicacion=date(2026, 1, 1))]
    )
    assert recientes[0].oferta.titulo == "Nueva"
