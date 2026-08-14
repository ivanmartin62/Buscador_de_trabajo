# Empleo Público Argentina

Aplicación web para consultar convocatorias y concursos públicos argentinos en un
solo lugar. El proyecto está en desarrollo incremental; la etapa actual establece
la base técnica antes de conectar la primera fuente.

## Problema

Las convocatorias públicas argentinas se encuentran distribuidas entre numerosos
organismos y sitios oficiales. Encontrarlas exige visitar páginas diferentes y
entender formatos que no son uniformes.

## Solución

Una plataforma que recopila, valida y normaliza convocatorias para permitir su
consulta desde un solo lugar, conservando siempre el vínculo oficial original.

## Estado y características

**Etapa 1 — estructura inicial:**

- modelo común `OfertaEmpleo`, validado con Pydantic;
- interfaz mínima, responsive, construida con Streamlit;
- paquetes separados para fuentes, servicios, persistencia y utilidades;
- configuración segura para desarrollo y pruebas automatizadas.

La búsqueda, filtros, actualización y persistencia se habilitarán cuando exista
una fuente oficial verificada. No se muestran datos ficticios como convocatorias.

> Las capturas de pantalla se agregarán cuando la primera fuente esté integrada.

## Arquitectura

```text
fuentes oficiales -> scrapers -> agregador -> normalización/deduplicación
                                                    |
                                                    v
                             Repository -> Streamlit
                              SQLite        app.py
                              PostgreSQL (futuro)
```

`app.py` sólo presenta datos y ejecuta casos de uso. Cada fuente tendrá un adaptador
independiente. La abstracción `Repository` permitirá usar SQLite localmente y migrar
a PostgreSQL/Supabase sin incorporar SQL en la interfaz.

## Tecnologías

- Python 3.12 o una versión estable compatible
- Streamlit
- Pydantic
- HTTPX y Beautiful Soup (reservados para fuentes verificadas)
- pytest
- SQLite para desarrollo; PostgreSQL/Supabase planificado

Playwright y pandas no se incluyen: se agregarán sólo si una fuente demuestra que
son necesarios.

## Instalación

```bash
git clone <URL-DEL-REPOSITORIO>
cd Buscador_de_trabajo
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

En Windows PowerShell, reemplazar la activación por:

```powershell
.\.venv\Scripts\Activate.ps1
```

No se necesitan secretos actualmente. Si se añade configuración local, copiar
`.env.example` a `.env`; el segundo archivo está excluido de Git.

## Ejecución

```bash
streamlit run app.py
```

Streamlit mostrará la URL local (normalmente `http://localhost:8501`).

## Testing

```bash
pytest
```

Los futuros parsers se probarán contra fixtures HTML/JSON pequeños para que la
suite no dependa de la disponibilidad de sitios externos.

## Estructura

```text
.
├── app.py
├── src/
│   ├── models/       # modelo normalizado
│   ├── scrapers/     # adaptadores independientes por fuente
│   ├── services/     # agregación y reglas de negocio
│   ├── database/     # contratos e implementaciones de persistencia
│   └── utils/        # fechas, logging y utilidades
├── tests/
├── AGENTS.md
└── requirements.txt
```

## Fuentes

### Soportadas

Todavía ninguna. La primera se seleccionará sólo después de verificar en el sitio
oficial si ofrece API, JSON, RSS, HTML estático o contenido dinámico.

### Planificadas

- Cartelera Central de Empleo Público
- Portal Empleo
- organismos de Defensa y Fuerzas Armadas
- Poder Judicial, Consejo de la Magistratura y Ministerios Públicos
- universidades nacionales y organismos descentralizados
- provincias y Ciudad Autónoma de Buenos Aires

## Buscador global

La búsqueda se ejecuta sobre ofertas mantenidas temporalmente en memoria, no contra
los sitios remotos ni sobre una base de datos. Streamlit conserva esa lista sólo
durante la sesión activa; al reiniciar la aplicación se pierde. Esta decisión es
intencional para la etapa actual y el contrato `Repository` permite agregar
persistencia más adelante sin reescribir la interfaz.
Normaliza mayúsculas, acentos y puntuación, expande términos configurados en
`config/synonyms.json` y ordena coincidencias directas y relacionadas por relevancia.
Una consulta vacía muestra las convocatorias más recientes.
El campo principal está habilitado y ejecuta la búsqueda al presionar Enter o el
botón **Buscar**. Mientras no haya un scraper activo, acepta la consulta pero informa
que todavía no existen ofertas oficiales recopiladas.

La recolección queda separada mediante:

```bash
python -m src.update_sources
```

El comando no consulta fuentes `pending`. Antes de activar un adaptador se verifican
la URL oficial, `robots.txt`, las condiciones y el formato real de publicación.

## Fuentes soportadas

| Fuente | Jurisdicción | Método | Estado |
|---|---|---|---|
| Convocatorias de Argentina.gob.ar aportadas al proyecto | Nacional | HTML semántico | `active` |
| Cartelera Central de Empleo Público | Nacional | Pendiente de verificación | `pending` |
| Portal Empleo | Nacional | Pendiente de verificación | `pending` |
| Boletín Oficial | Nacional | Pendiente de evaluación selectiva | `pending` |
| Poder Judicial de la Nación | Nacional | Pendiente de verificación | `pending` |
| Consejo de la Magistratura | Nacional | Pendiente de verificación | `pending` |
| Ministerio Público Fiscal | Nacional | Pendiente de verificación | `pending` |
| Ministerio Público de la Defensa | Nacional | Pendiente de verificación | `pending` |

El inventario está en `config/sources.json`. La primera integración consulta las
páginas de convocatorias de Argentina.gob.ar aportadas al proyecto y conserva su
texto visible en memoria. El parser usa elementos HTML semánticos y siempre enlaza
la publicación original. Las demás fuentes continúan pendientes porque el entorno
bloqueó con HTTP 403 su verificación externa.

La actualización se inicia con **Actualizar ofertas oficiales** y se cachea durante
una hora para evitar solicitudes repetidas. Si una página contiene términos como
`Abogacía`, `Derecho` o `estudiante avanzado`, el motor puede encontrarla mediante
la búsqueda `abogado` como coincidencia relacionada. Esta coincidencia ayuda a
descubrir la convocatoria, pero el usuario siempre debe revisar los requisitos y el
carácter interno o abierto del concurso en la fuente oficial.

Una búsqueda sin resultados no demuestra que no haya convocatorias publicadas:
significa que todavía no existe una fuente activa que haya aportado ofertas a la
memoria de la aplicación.

Para comprobar las URLs registradas desde un entorno con red:

```bash
python scripts/check_sources.py
```

## Limitaciones actuales

- La memoria comienza vacía hasta activar el primer scraper verificado.
- Las ofertas no se guardan: desaparecen cuando se reinicia la sesión o aplicación.
- La calidad y disponibilidad dependerán de lo que publique cada organismo.
- Un despliegue efímero no debe tratar SQLite como almacenamiento permanente.

## Despliegue en Streamlit Community Cloud

Cuando el MVP tenga una fuente funcional:

1. subir el repositorio a GitHub sin `.env`, bases locales ni credenciales;
2. ingresar en Streamlit Community Cloud y elegir **Create app**;
3. seleccionar repositorio, rama y `app.py` como archivo principal;
4. configurar secretos en el panel de Streamlit, nunca en Git;
5. desplegar y comprobar logs, actualización y enlaces oficiales.

Para persistencia durable se configurará PostgreSQL/Supabase mediante una variable
de entorno; SQLite queda limitado al desarrollo local.

## Alertas futuras

El agregador podrá emitir un evento al detectar una convocatoria nueva. Un servicio
independiente comparará palabras clave guardadas y entregará la alerta por correo,
Telegram u otro canal. Esto mantiene notificaciones fuera de scrapers y de la UI.

## Roadmap

### V0.1

- una fuente oficial, scraper y normalización;
- Streamlit y buscador.

### V0.2

- múltiples fuentes y filtros;
- deduplicación y SQLite local.

### V0.3

- PostgreSQL/Supabase;
- actualizaciones automatizadas e histórico.

### V0.4

- búsquedas guardadas, alertas y notificaciones.

### V1.0

- cobertura amplia del empleo público argentino;
- estadísticas, monitoreo de fuentes e interfaz estable.
