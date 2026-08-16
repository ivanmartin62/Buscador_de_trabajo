"""Filtros y orden visual sobre resultados ya calculados por el buscador."""

from datetime import date

from src.services.search import ResultadoBusqueda


def filtrar_resultados(
    resultados: list[ResultadoBusqueda],
    provincia: str = "Todas",
    tipo: str = "Todos",
    estado: str = "Todos",
    organismo: str = "Todos",
    nivel: str = "Todos",
) -> list[ResultadoBusqueda]:
    """Aplica filtros opcionales sin alterar el ranking ni los datos de origen."""
    return [
        resultado
        for resultado in resultados
        if (provincia == "Todas" or resultado.oferta.provincia == provincia)
        and (tipo == "Todos" or resultado.oferta.tipo_convocatoria == tipo)
        and (estado == "Todos" or _estado_visible(resultado) == estado)
        and (organismo == "Todos" or resultado.oferta.organismo == organismo)
        and (nivel == "Todos" or resultado.oferta.nivel_gobierno == nivel)
    ]


def ordenar_resultados(
    resultados: list[ResultadoBusqueda], criterio: str
) -> list[ResultadoBusqueda]:
    """Ordena una copia; relevancia conserva el orden producido por MotorBusqueda."""
    if criterio == "Más recientes":
        return sorted(
            resultados,
            key=lambda item: item.oferta.fecha_publicacion or date.min,
            reverse=True,
        )
    if criterio == "Cierre próximo":
        return sorted(
            resultados,
            key=lambda item: (
                item.oferta.fecha_cierre is None,
                item.oferta.fecha_cierre or date.max,
            ),
        )
    return list(resultados)


def _estado_visible(resultado: ResultadoBusqueda) -> str:
    estado = resultado.oferta.estado
    return {
        "abierta": "Abierta",
        "proxima": "Próxima",
        "cerrada": "Cerrada",
    }.get(estado, "Sin fecha")
