"""Comprueba fuentes registradas sin modificar automáticamente el catálogo."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.services.sources import Fuente, cargar_fuentes


@dataclass(frozen=True)
class ResultadoComprobacion:
    fuente_id: str
    estado_http: int | None
    url_final: str | None
    content_type: str | None
    json_valido: bool | None
    error: str | None = None


def comprobar_fuente(
    fuente: Fuente, cliente: httpx.Client
) -> ResultadoComprobacion:
    """Verifica HTTP y, para API/JSON, que la respuesta sea JSON válido."""
    if not fuente.url:
        return ResultadoComprobacion(
            fuente.id, None, None, None, None, "sin URL verificada"
        )
    try:
        metodo = "GET" if fuente.metodo in {"api", "json"} else "HEAD"
        respuesta = cliente.request(metodo, fuente.url)
        if metodo == "HEAD" and respuesta.status_code == 405:
            respuesta = cliente.get(fuente.url)
        content_type = respuesta.headers.get("content-type")
        json_valido: bool | None = None
        if fuente.metodo in {"api", "json"}:
            try:
                respuesta.json()
                json_valido = True
            except ValueError:
                json_valido = False
        return ResultadoComprobacion(
            fuente.id,
            respuesta.status_code,
            str(respuesta.url),
            content_type,
            json_valido,
        )
    except httpx.HTTPError as error:
        return ResultadoComprobacion(
            fuente.id, None, fuente.url, None, None, str(error)
        )


def main() -> None:
    encabezados = {"User-Agent": "EmpleoPublicoArgentina/0.2 (verificador educativo)"}
    with httpx.Client(timeout=10, follow_redirects=True, headers=encabezados) as cliente:
        for fuente in cargar_fuentes():
            resultado = comprobar_fuente(fuente, cliente)
            if resultado.error:
                print(f"{resultado.fuente_id}: PENDIENTE/ERROR {resultado.error}")
                continue
            detalle_json = (
                f" JSON válido={resultado.json_valido}"
                if resultado.json_valido is not None
                else ""
            )
            print(
                f"{resultado.fuente_id}: HTTP {resultado.estado_http} "
                f"-> {resultado.url_final} [{resultado.content_type or 'sin content-type'}]"
                f"{detalle_json}"
            )
    print(f"Comprobación: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
