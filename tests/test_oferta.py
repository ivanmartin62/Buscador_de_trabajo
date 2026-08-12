from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models import EstadoOferta, OfertaEmpleo


def test_oferta_acepta_campos_desconocidos_vacios() -> None:
    oferta = OfertaEmpleo(
        titulo="  Analista de sistemas  ",
        fuente="Organismo oficial",
        url_original="https://www.argentina.gob.ar/convocatorias/1",
    )

    assert oferta.titulo == "Analista de sistemas"
    assert oferta.organismo is None
    assert oferta.estado == EstadoOferta.DESCONOCIDO
    assert oferta.fecha_recoleccion.tzinfo is not None


def test_oferta_rechaza_url_no_http() -> None:
    with pytest.raises(ValidationError):
        OfertaEmpleo(
            titulo="Cargo",
            fuente="Fuente",
            url_original="javascript:alert(1)",
        )


def test_oferta_rechaza_fecha_recoleccion_sin_zona_horaria() -> None:
    with pytest.raises(ValidationError):
        OfertaEmpleo(
            titulo="Cargo",
            fuente="Fuente",
            url_original="https://example.gob.ar/cargo",
            fecha_recoleccion=datetime(2026, 8, 12),
        )


def test_oferta_acepta_fecha_recoleccion_con_zona_horaria() -> None:
    fecha = datetime(2026, 8, 12, tzinfo=timezone.utc)
    oferta = OfertaEmpleo(
        titulo="Cargo",
        fuente="Fuente",
        url_original="https://example.gob.ar/cargo",
        fecha_recoleccion=fecha,
    )

    assert oferta.fecha_recoleccion == fecha

