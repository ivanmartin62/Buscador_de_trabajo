"""Componentes Streamlit reutilizables; no contienen scraping ni búsqueda."""

from datetime import datetime
from typing import Callable

import streamlit as st

from src.models import OfertaEmpleo
from src.services.search import ResultadoBusqueda

BUSQUEDAS_RAPIDAS = (
    ("⚖️ Abogado", "abogado"),
    ("💻 Programador", "programador"),
    ("🎓 Ingeniería", "ingeniería"),
    ("🖥️ Sistemas", "sistemas"),
    ("🔐 Ciberseguridad", "ciberseguridad"),
    ("📊 Administración", "administración"),
    ("📦 Logística", "logística"),
)


def aplicar_estilos() -> None:
    """Añade una capa CSS pequeña sobre el tema oficial de Streamlit."""
    st.markdown(
        """
        <style>
        .block-container {max-width: 1180px; padding-top: 2rem; padding-bottom: 3rem;}
        .hero {padding: 1.6rem 1.8rem; background: #eff6ff; border: 1px solid #dbeafe;
               border-radius: 1rem; margin-bottom: 1.25rem;}
        .hero-kicker {color: #2563eb; font-size: .78rem; font-weight: 700;
                      letter-spacing: .12em; text-transform: uppercase;}
        .hero h1 {color: #172554; margin: .35rem 0; font-size: clamp(2rem, 5vw, 3.2rem);}
        .hero p {color: #475569; font-size: 1.08rem; margin: 0; max-width: 720px;}
        [data-testid="stMetric"] {background: white; border: 1px solid #e2e8f0;
                                  padding: .9rem 1rem; border-radius: .8rem;}
        [data-testid="stVerticalBlockBorderWrapper"] {background: white;}
        .source-note {color: #64748b; font-size: .9rem;}
        @media (max-width: 640px) {
          .block-container {padding: 1rem .8rem 2rem;}
          .hero {padding: 1.2rem;}
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def mostrar_portada() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="hero-kicker">Fuentes oficiales de Argentina</div>
          <h1>Buscador de Trabajo</h1>
          <p>Encontrá oportunidades laborales y concursos públicos desde una sola
          búsqueda. Múltiples organismos, siempre con acceso a la publicación original.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def mostrar_busquedas_rapidas(al_seleccionar: Callable[[str], None]) -> None:
    st.caption("Probá una búsqueda rápida")
    for inicio, fin in ((0, 4), (4, 7)):
        columnas = st.columns(fin - inicio)
        for columna, (etiqueta, consulta) in zip(
            columnas, BUSQUEDAS_RAPIDAS[inicio:fin], strict=True
        ):
            columna.button(
                etiqueta,
                key=f"rapida_{consulta}",
                width="stretch",
                on_click=al_seleccionar,
                args=(consulta,),
            )


def etiqueta_estado(oferta: OfertaEmpleo) -> str:
    return {
        "abierta": "🟢 ABIERTA",
        "proxima": "🟡 PRÓXIMA",
        "cerrada": "🔴 CERRADA",
    }.get(oferta.estado, "⚪ SIN FECHA")


def mostrar_tarjeta(resultado: ResultadoBusqueda) -> None:
    oferta = resultado.oferta
    coincidencia = (
        "🎯 Coincidencia directa"
        if resultado.tipo == "directa"
        else "🔎 Coincidencia relacionada"
    )
    with st.container(border=True):
        cabecera, tipo = st.columns([2, 1])
        cabecera.caption(f"{etiqueta_estado(oferta)} · {coincidencia}")
        tipo.caption(oferta.tipo_convocatoria or "Convocatoria")
        st.subheader(oferta.titulo)
        st.markdown(f"**{oferta.organismo or 'Organismo no informado'}**")

        ubicacion = " · ".join(
            parte for parte in (oferta.provincia, oferta.localidad) if parte
        ) or "Ubicación no informada"
        datos = st.columns(3)
        datos[0].write(f"📍 {ubicacion}")
        datos[1].write(f"🏛️ {oferta.nivel_gobierno or 'Nivel no informado'}")
        datos[2].write(
            "⏳ Cierra: "
            + (oferta.fecha_cierre.strftime("%d/%m/%Y") if oferta.fecha_cierre else "sin fecha")
        )
        if resultado.coincidencias:
            st.caption("Coincidió por: " + " · ".join(resultado.coincidencias))

        with st.expander("Ver detalles"):
            _mostrar_detalles(oferta)
        st.link_button(
            "Ver convocatoria oficial →",
            str(oferta.url_original),
            type="primary",
        )


def _mostrar_detalles(oferta: OfertaEmpleo) -> None:
    if oferta.descripcion:
        st.markdown("**Descripción**")
        st.write(oferta.descripcion)
    if oferta.requisitos:
        st.markdown("**Requisitos**")
        st.write(oferta.requisitos)
    campos = {
        "Profesión": oferta.profesion,
        "Especialidad": oferta.especialidad,
        "Publicado": _fecha(oferta.fecha_publicacion),
        "Fuente": oferta.fuente,
    }
    for etiqueta, valor in campos.items():
        if valor:
            st.write(f"**{etiqueta}:** {valor}")


def _fecha(valor: datetime | object | None) -> str | None:
    return valor.strftime("%d/%m/%Y") if hasattr(valor, "strftime") else None
