"""Interfaz Streamlit del buscador; la recolección permanece en servicios."""

from datetime import datetime, timezone

import streamlit as st

from src.database.memory_repository import MemoriaRepository
from src.models import OfertaEmpleo
from src.services.live_offers import consultar_ofertas_oficiales
from src.services.search import MotorBusqueda
from src.services.sources import RegistroFuentes, cargar_estados, cargar_jurisdicciones
from src.ui.components import (
    aplicar_estilos,
    mostrar_portada,
    mostrar_tarjeta,
)
from src.ui.filters import filtrar_resultados, ordenar_resultados
from src.utils.logging_config import configurar_logging


@st.cache_data(ttl=3600, show_spinner=False)
def actualizar_ofertas_temporales():
    """Evita repetir solicitudes oficiales durante una hora."""
    return consultar_ofertas_oficiales()


def limpiar_filtros() -> None:
    for clave in (
        "filtro_provincia",
        "filtro_tipo",
        "filtro_estado",
        "filtro_organismo",
        "filtro_nivel",
    ):
        st.session_state[clave] = "Todas" if clave == "filtro_provincia" else "Todos"
    st.session_state.orden_resultados = "Relevancia"


def opciones(campo: str, ofertas: list[OfertaEmpleo]) -> list[str]:
    valores = {getattr(oferta, campo) for oferta in ofertas if getattr(oferta, campo)}
    return sorted(valores)


st.set_page_config(
    page_title="Buscador de Trabajo | Fuentes oficiales",
    page_icon="🇦🇷",
    layout="wide",
    initial_sidebar_state="collapsed",
)
configurar_logging()
aplicar_estilos()
mostrar_portada()

st.session_state.setdefault("ofertas", [])
st.session_state.setdefault("consulta_global", "")
st.session_state.setdefault("ultima_actualizacion", None)

tab_busqueda, tab_fuentes, tab_acerca = st.tabs(
    ["Buscar oportunidades", "Fuentes oficiales", "Acerca del proyecto"]
)

with tab_busqueda:
    registro = RegistroFuentes.desde_archivo()
    fuentes_activas = registro.activas()

    columna_busqueda, columna_boton = st.columns([5, 1], vertical_alignment="bottom")
    with columna_busqueda:
        consulta = st.text_input(
            "¿Qué trabajo estás buscando?",
            placeholder=(
                "Puesto, profesión, carrera, tecnología, organismo o palabra clave"
            ),
            key="consulta_global",
            help="Escribí una palabra y presioná Enter, o utilizá el botón Buscar.",
        )
    with columna_boton:
        st.button("Buscar", type="primary", width="stretch")

    if st.button(
        "🔄 Actualizar fuentes",
        help="Consulta las fuentes oficiales y conserva los resultados temporalmente.",
    ):
        with st.spinner("Actualizando fuentes oficiales..."):
            ofertas_nuevas, errores_fuente = actualizar_ofertas_temporales()
        if ofertas_nuevas:
            st.session_state.ofertas = ofertas_nuevas
            st.session_state.ultima_actualizacion = datetime.now(timezone.utc)
        if ofertas_nuevas:
            st.success(
                f"Actualización completada: {len(ofertas_nuevas)} convocatorias disponibles."
            )
        if errores_fuente:
            st.warning(
                "Algunas fuentes no pudieron actualizarse. "
                "Los resultados disponibles siguen siendo consultables."
            )
        if not ofertas_nuevas and errores_fuente:
            st.info(
                "No se reemplazaron los resultados anteriores porque ninguna fuente "
                "respondió correctamente."
            )

    ofertas = MemoriaRepository(st.session_state.ofertas).listar_ofertas()
    organismos = {oferta.organismo for oferta in ofertas if oferta.organismo}
    ultima = st.session_state.ultima_actualizacion
    metricas = st.columns(4)
    metricas[0].metric("Oportunidades", len(ofertas))
    metricas[1].metric("Organismos", len(organismos))
    metricas[2].metric("Fuentes activas", len(fuentes_activas))
    metricas[3].metric(
        "Última actualización",
        ultima.strftime("%d/%m · %H:%M") if ultima else "Pendiente",
    )

    resultados = MotorBusqueda().buscar(consulta, ofertas)
    with st.expander("Filtros y orden", expanded=False):
        filtros_principales = st.columns(3)
        provincia = filtros_principales[0].selectbox(
            "Provincia", ["Todas", *opciones("provincia", ofertas)], key="filtro_provincia"
        )
        organismo = filtros_principales[1].selectbox(
            "Organismo", ["Todos", *opciones("organismo", ofertas)], key="filtro_organismo"
        )
        tipo = filtros_principales[2].selectbox(
            "Tipo", ["Todos", *opciones("tipo_convocatoria", ofertas)], key="filtro_tipo"
        )
        filtros_secundarios = st.columns(3)
        estado = filtros_secundarios[0].selectbox(
            "Estado", ["Todos", "Abierta", "Próxima", "Cerrada", "Sin fecha"], key="filtro_estado"
        )
        nivel = filtros_secundarios[1].selectbox(
            "Nivel",
            ["Todos", *opciones("nivel_gobierno", ofertas)],
            key="filtro_nivel",
        )
        orden = filtros_secundarios[2].selectbox(
            "Ordenar por",
            ["Relevancia", "Más recientes", "Cierre próximo"],
            key="orden_resultados",
        )
        st.button("Limpiar filtros", on_click=limpiar_filtros)

    resultados = filtrar_resultados(
        resultados, provincia, tipo, estado, organismo, nivel
    )
    resultados = ordenar_resultados(resultados, orden)

    if consulta:
        directas = sum(resultado.tipo == "directa" for resultado in resultados)
        st.subheader(f'{len(resultados)} oportunidades para “{consulta}”')
        st.caption(
            f"{directas} coincidencias directas · "
            f"{len(resultados) - directas} relacionadas"
        )
    else:
        st.subheader("Oportunidades recientes")
        st.caption("Actualizá las fuentes para consultar las publicaciones disponibles.")

    if not resultados:
        if consulta:
            st.info(
                f'🔍 No encontramos oportunidades para “{consulta}”. '
                "Probá con otra palabra o limpiá los filtros. Si todavía no actualizaste "
                "las fuentes, hacelo antes de buscar."
            )
        else:
            st.info(
                "Todavía no hay oportunidades cargadas en esta sesión. "
                "Usá “Actualizar fuentes” para consultar las publicaciones disponibles."
            )
    for resultado in resultados:
        mostrar_tarjeta(resultado)

with tab_fuentes:
    st.header("Fuentes oficiales")
    registro = RegistroFuentes.desde_archivo()
    fuentes = registro.listar()
    estados_operativos = cargar_estados()
    activas = len(registro.activas())
    st.write(
        f"La cobertura está preparada para **{len(cargar_jurisdicciones())} jurisdicciones**. "
        f"Actualmente hay **{activas} fuente(s) activa(s)**."
    )
    etiquetas_estado = {
        "active": "🟢 Activa",
        "pending": "🟡 Pendiente",
        "limited": "🟠 Limitada",
        "disabled": "⚪ Deshabilitada",
        "broken": "🔴 Error",
    }
    etiquetas_metodo = {
        "api": "API",
        "json": "JSON",
        "rss": "RSS",
        "xml": "XML",
        "html": "Página web",
        "html_semantico": "Página web",
        "javascript": "Aplicación web",
        "portal_interactivo_sin_api_publica": "Portal interactivo",
        "pendiente_verificacion": "Por verificar",
    }
    st.dataframe(
        [
            {
                "Fuente": fuente.nombre,
                "Organismo": fuente.organismo,
                "Jurisdicción": fuente.provincia or fuente.nivel,
                "Método": etiquetas_metodo.get(fuente.metodo, fuente.metodo),
                "Estado": etiquetas_estado.get(fuente.estado, fuente.estado),
                "Uso en el buscador": (
                    "Incluida" if fuente.estado == "active" else "Aún no incluida"
                ),
                "Última revisión": fuente.ultima_revision or "Sin datos",
                "Ofertas": (
                    estados_operativos[fuente.id].number_of_offers
                    if fuente.id in estados_operativos
                    else "Sin datos"
                ),
                "Enlace oficial": fuente.url,
            }
            for fuente in fuentes
        ],
        column_config={
            "Enlace oficial": st.column_config.LinkColumn(
                "Enlace oficial", display_text="Abrir fuente ↗"
            )
        },
        hide_index=True,
        width="stretch",
    )
    st.caption(
        "Las fuentes pendientes no se consultan hasta verificar su URL, condiciones "
        "y estructura de publicación. Que un enlace se pueda abrir no significa que "
        "sus concursos ya estén incluidos en el buscador."
    )

with tab_acerca:
    st.header("Acerca del proyecto")
    st.write(
        "Buscador de Trabajo reúne oportunidades laborales y concursos publicados "
        "en fuentes oficiales argentinas para que puedan consultarse desde un solo lugar."
    )
    st.info(
        "La información puede cambiar. Verificá siempre requisitos, fechas y "
        "condiciones en la publicación oficial antes de postularte."
    )
    st.caption(
        "Este proyecto no pertenece al Gobierno argentino ni a los organismos listados."
    )

st.divider()
st.caption(
    "Información recopilada de fuentes públicas oficiales. "
    "Verificá siempre la convocatoria original antes de postularte."
)
