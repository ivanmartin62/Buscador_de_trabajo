"""Interfaz mínima de Empleo Público Argentina."""

import streamlit as st


st.set_page_config(
    page_title="Empleo Público Argentina",
    page_icon="🇦🇷",
    layout="wide",
)

st.title("Empleo Público Argentina")
st.subheader("Convocatorias y concursos públicos reunidos en un solo lugar.")
st.info(
    "Esta primera etapa prepara la aplicación. La conexión con la primera fuente "
    "oficial se incorporará en la próxima etapa."
)

st.text_input(
    "Buscar puesto, profesión, organismo o palabra clave",
    placeholder="Ej.: sistemas, logística o Ministerio de Defensa",
    disabled=True,
)

columnas = st.columns(4)
columnas[0].metric("Convocatorias encontradas", 0)
columnas[1].metric("Convocatorias abiertas", 0)
columnas[2].metric("Organismos", 0)
columnas[3].metric("Fuentes consultadas", 0)

st.caption("Última actualización: pendiente")
st.write("No hay convocatorias cargadas todavía.")

