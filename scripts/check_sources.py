"""Comprueba URLs registradas sin modificar el catálogo."""

from datetime import datetime, timezone
import httpx

from src.services.sources import cargar_fuentes


def main() -> None:
    encabezados = {"User-Agent": "EmpleoPublicoArgentina/0.2 (verificador educativo)"}
    with httpx.Client(timeout=10, follow_redirects=True, headers=encabezados) as cliente:
        for fuente in cargar_fuentes():
            try:
                respuesta = cliente.head(fuente.url)
                print(f"{fuente.id}: HTTP {respuesta.status_code} -> {respuesta.url}")
            except httpx.HTTPError as error:
                print(f"{fuente.id}: ERROR {error}")
    print(f"Comprobación: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
