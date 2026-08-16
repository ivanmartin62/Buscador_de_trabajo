"""Actualización manual de fuentes para el modo temporal sin base de datos."""

from src.services.live_offers import consultar_ofertas_oficiales
from src.services.sources import RegistroFuentes


def main() -> int:
    """Consulta adaptadores activos y muestra un resumen sin persistir resultados."""
    activas = RegistroFuentes.desde_archivo().activas()
    if not activas:
        print("0 fuentes activas")
        print("No hay fuentes verificadas para consultar.")
        return 0

    ofertas, errores = consultar_ofertas_oficiales()
    print(f"{len(activas)} fuentes activas")
    print(f"{len(ofertas)} ofertas normalizadas")
    print(f"{len(errores)} consultas con error")
    print("Modo temporal: los resultados no se guardaron en una base de datos")
    return 1 if errores and not ofertas else 0


if __name__ == "__main__":
    raise SystemExit(main())
