from src.ui.components import escapar_markdown


def test_texto_remoto_no_se_interpreta_como_markdown() -> None:
    texto = "[Oferta](https://sitio-no-oficial.example) **urgente**"

    escapado = escapar_markdown(texto)

    assert escapado == (
        r"\[Oferta\]\(https://sitio\-no\-oficial\.example\) \*\*urgente\*\*"
    )
