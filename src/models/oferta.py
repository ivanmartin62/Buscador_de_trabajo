"""Modelo común para convocatorias provenientes de fuentes heterogéneas."""

from datetime import date, datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class EstadoOferta(StrEnum):
    """Estados conocidos; `DESCONOCIDO` evita inferir información ausente."""

    ABIERTA = "abierta"
    CERRADA = "cerrada"
    DESCONOCIDO = "desconocido"


class OfertaEmpleo(BaseModel):
    """Representación normalizada de una convocatoria pública.

    Los campos que una fuente no publica permanecen en ``None``. Sólo el título,
    la fuente y el enlace oficial son imprescindibles para mostrar un resultado.
    """

    model_config = ConfigDict(str_strip_whitespace=True, use_enum_values=True)

    id: str | None = None
    titulo: str = Field(min_length=1)
    organismo: str | None = None
    descripcion: str | None = None
    categoria: str | None = None
    provincia: str | None = None
    localidad: str | None = None
    modalidad: str | None = None
    tipo_convocatoria: str | None = None
    fecha_publicacion: date | None = None
    fecha_apertura: date | None = None
    fecha_cierre: date | None = None
    requisitos: str | None = None
    profesion: str | None = None
    cantidad_vacantes: int | None = Field(default=None, ge=0)
    fuente: str = Field(min_length=1)
    url_original: HttpUrl
    fecha_recoleccion: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    estado: EstadoOferta = EstadoOferta.DESCONOCIDO

    @field_validator("fecha_recoleccion")
    @classmethod
    def exigir_zona_horaria(cls, valor: datetime) -> datetime:
        """Evita guardar instantes ambiguos en futuras capas de persistencia."""

        if valor.tzinfo is None or valor.utcoffset() is None:
            raise ValueError("fecha_recoleccion debe incluir zona horaria")
        return valor

