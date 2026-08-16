import httpx

from scripts.check_sources import comprobar_fuente
from src.services.sources import Fuente


def fuente(metodo: str = "api") -> Fuente:
    return Fuente(
        id="api_oficial",
        nombre="API oficial",
        organismo="Organismo",
        nivel="Nacional",
        provincia=None,
        url="https://api.example.gob.ar/ofertas",
        tipo="empleo",
        metodo=metodo,
        estado="active",
        ultima_revision=None,
    )


def test_comprueba_api_json_sin_trafico_real() -> None:
    transporte = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={"ofertas": []},
            headers={"content-type": "application/json"},
            request=request,
        )
    )
    with httpx.Client(transport=transporte) as cliente:
        resultado = comprobar_fuente(fuente(), cliente)

    assert resultado.estado_http == 200
    assert resultado.json_valido is True
    assert resultado.content_type == "application/json"


def test_detecta_respuesta_json_invalida() -> None:
    transporte = httpx.MockTransport(
        lambda request: httpx.Response(200, text="no es json", request=request)
    )
    with httpx.Client(transport=transporte) as cliente:
        resultado = comprobar_fuente(fuente("json"), cliente)

    assert resultado.json_valido is False


def test_fuente_sin_url_no_realiza_peticion() -> None:
    sin_url = Fuente(**{**fuente().__dict__, "url": None})
    with httpx.Client() as cliente:
        resultado = comprobar_fuente(sin_url, cliente)

    assert resultado.estado_http is None
    assert resultado.error == "sin URL verificada"
