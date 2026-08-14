"""Interfaz del buscador; la recolección se ejecuta por separado."""

import streamlit as st
from src.database.memory_repository import MemoriaRepository
from src.services.search import MotorBusqueda
from src.services.sources import cargar_fuentes


st.set_page_config(
    page_title="Empleo Público Argentina",
    page_icon="🇦🇷",
    layout="wide",
)

st.title("Buscador de Trabajo")
st.subheader("Oportunidades publicadas en fuentes oficiales de Argentina")

tab_busqueda, tab_fuentes, tab_acerca = st.tabs(
    ["🔎 Buscar", "🏛️ Fuentes oficiales", "ℹ️ Acerca del proyecto"]
)

with tab_busqueda:
    with st.form("busqueda", clear_on_submit=False):
        consulta = st.text_input(
            "🔎 ¿Qué trabajo estás buscando?",
            placeholder="Ej.: abogado, programador, ingeniería, administración...",
        )
        st.form_submit_button("Buscar", type="primary")

    if "ofertas" not in st.session_state:
        st.session_state.ofertas = []
    repositorio = MemoriaRepository(st.session_state.ofertas)
    ofertas = repositorio.listar_ofertas()
    resultados = MotorBusqueda().buscar(consulta, ofertas)
    if consulta:
        directas = sum(resultado.tipo == "directa" for resultado in resultados)
        st.subheader(f'Encontramos {len(resultados)} oportunidades para "{consulta}"')
        st.caption(f"{directas} coincidencias directas · {len(resultados) - directas} relacionadas")
    else:
        st.subheader("Últimas convocatorias")

    if not resultados:
        st.info(
            "Todavía no hay ofertas recopiladas que coincidan con la búsqueda. "
            "Las fuentes del primer lote están pendientes de verificación técnica. "
            "En esta etapa los resultados se mantendrán sólo en memoria."
        )
    for resultado in resultados:
        oferta = resultado.oferta
        etiqueta = "🎯 Coincidencia directa" if resultado.tipo == "directa" else "🔎 Coincidencia relacionada"
        with st.container(border=True):
            st.caption(etiqueta)
            st.subheader(oferta.titulo)
            st.write(oferta.organismo or "Organismo no informado")
            st.write(f"📍 {oferta.localidad or oferta.provincia or 'Ubicación no informada'}")
            st.write(f"🏛 {oferta.nivel_gobierno or 'Nivel no informado'}")
            st.write(f"⏳ Cierra: {oferta.fecha_cierre.strftime('%d/%m/%Y') if oferta.fecha_cierre else 'sin fecha informada'}")
            if resultado.coincidencias:
                st.caption("Coincidió por: " + " · ".join(resultado.coincidencias))
            st.link_button("VER CONVOCATORIA OFICIAL", str(oferta.url_original))
            st.caption(f"Fuente: {oferta.fuente}")

with tab_fuentes:
    st.header("Fuentes oficiales")
    fuentes = cargar_fuentes()
    st.dataframe(
        [
            {
                "Fuente": fuente.nombre,
                "Organismo": fuente.organismo,
                "Jurisdicción": fuente.nivel,
                "Método": fuente.metodo,
                "Estado": fuente.estado,
                "URL oficial": fuente.url,
            }
            for fuente in fuentes
        ],
        hide_index=True,
        use_container_width=True,
    )
    st.warning("Las fuentes pendientes no se consultan hasta verificar URL, condiciones y estructura.")

with tab_acerca:
    st.header("Acerca del proyecto")
    st.write(
        "Este proyecto reúne convocatorias y oportunidades laborales publicadas "
        "en sitios oficiales argentinos. La información puede cambiar: verificá "
        "siempre la convocatoria original antes de postularte."
    )

st.divider()
st.caption(
    "Este sitio no pertenece al Gobierno argentino ni a los organismos listados. "
    "La información se recopila de fuentes públicas oficiales. Verificá siempre "
    "requisitos, fechas y condiciones en la publicación original."
)
