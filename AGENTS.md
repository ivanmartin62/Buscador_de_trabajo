# Guía para agentes

## Objetivo

Construir **Empleo Público Argentina**, una aplicación que reúne convocatorias de
fuentes oficiales argentinas y conserva siempre el enlace a la publicación original.

## Arquitectura

- `app.py`: composición y presentación en Streamlit; no contiene scraping ni SQL.
- `src/models`: modelos comunes validados con Pydantic.
- `src/scrapers`: un adaptador por fuente, todos detrás de una interfaz común.
- `src/services`: agregación, normalización y deduplicación.
- `src/database`: interfaz de repositorio e implementaciones de persistencia.
- `src/utils`: fechas, logging y utilidades compartidas.
- `src/ui`: componentes visuales y filtros de presentación; no contiene scraping.
- `tests`: pruebas unitarias; los parsers usan fixtures y no dependen de Internet.
- `config`: inventario declarativo de fuentes y sinónimos del buscador.
- `data`: reservado para estados o fixtures; la UI actual mantiene ofertas en memoria.

## Convenciones

- Usar nombres claros en español, type hints y funciones pequeñas.
- No inventar datos ausentes: representarlos con `None`.
- No mezclar scraping, persistencia o reglas de negocio con la UI.
- No guardar secretos; usar variables de entorno y actualizar `.env.example`.
- Validar URLs y tratar el texto remoto como datos, nunca como código.
- Registrar detalles técnicos y mostrar mensajes comprensibles en la interfaz.

## Comandos

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
pytest
python -m src.update_sources
python scripts/check_sources.py
```

## Agregar un scraper

1. Confirmar que la fuente es oficial y revisar sus términos y `robots.txt`.
2. Preferir API, JSON o RSS; recurrir a HTML estático sólo si no hay una opción
   estructurada. No eludir autenticación, CAPTCHA ni medidas anti-bot.
3. Crear un módulo independiente que implemente la interfaz base. Configurar
   User-Agent identificable, timeout, pocos reintentos y logging.
4. Normalizar al modelo `OfertaEmpleo` sin inventar valores.
5. Incorporar fixtures pequeños y pruebas del parser sin tráfico real.
6. Hacer que los fallos de esa fuente no interrumpan las demás.
7. Preservar la compatibilidad de los scrapers existentes y ejecutar `pytest`
   después de cualquier cambio relevante.
8. No marcar una fuente como `active` hasta verificar URL, contenido, método y
   condiciones. Una fuente sin verificar permanece `pending` y no se consulta.

## Búsqueda y persistencia

- `MotorBusqueda` trabaja exclusivamente sobre ofertas indexadas; nunca hace HTTP.
- Mantener sinónimos en `config/synonyms.json`, no dentro de `app.py`.
- La UI depende de `MemoriaRepository`, sin archivos ni SQL en esta etapa. Conservar
  el contrato `Repository` para una persistencia futura.
- Los resultados siempre conservan un enlace HTTP/HTTPS a la publicación oficial.
