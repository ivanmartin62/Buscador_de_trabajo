"""Configuración central de logs técnicos de la aplicación."""

import logging
import os


def configurar_logging() -> None:
    """Configura una salida uniforme sin exponer detalles técnicos en la UI."""
    nivel = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, nivel, logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
