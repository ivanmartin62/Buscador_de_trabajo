"""Punto de entrada independiente para futuras actualizaciones programadas."""

from src.services.sources import cargar_fuentes


def main() -> int:
    fuentes = cargar_fuentes()
    activas = [fuente for fuente in fuentes if fuente.estado == "active"]
    if not activas:
        print("0 fuentes procesadas")
        print("No hay fuentes activas: las registradas requieren verificación técnica.")
        print("Modo temporal: las ofertas se mostrarán en memoria y no se persistirán")
        return 0
    # Cada fuente se asociará aquí a su adaptador sólo después de verificarla.
    print(f"{len(activas)} fuentes activas sin adaptador registrado")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
