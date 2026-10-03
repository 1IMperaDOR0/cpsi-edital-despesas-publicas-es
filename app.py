import dash
from dash import ALL, Input, Output, dcc, html

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="src/pages",
    assets_folder="src/assets",
    suppress_callback_exceptions=True,
    title="CPSI — Despesas Públicas ES",
)

server = app.server

# Declara o idioma da página (evita a tradução automática do navegador) e aplica
# o tema salvo antes da renderização, para a tela não "piscar" ao carregar.
THEME_BOOTSTRAP = """
        <script>
            (function () {
                var theme;
                try { theme = localStorage.getItem("cpsi-theme"); } catch (e) {}
                if (theme !== "light" && theme !== "dark") {
                    theme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
                }
                document.documentElement.setAttribute("data-theme", theme);
            })();
        </script>
        {%css%}"""
app.index_string = (
    app.index_string
    .replace("<html>", '<html lang="pt-BR" translate="no">', 1)
    .replace("{%css%}", THEME_BOOTSTRAP, 1)
)

def create_navigation():
    return html.Nav(
        html.Div(
            [
                dcc.Link(
                    [
                        html.Span(className="navbar-logo", **{"aria-hidden": "true"}),
                        html.Span(
                            [
                                html.Span("Despesas Públicas ES", className="navbar-title"),
                                html.Span("CPSI · Painel de transparência", className="navbar-subtitle"),
                            ],
                            className="navbar-brand-text",
                        ),
                    ],
                    href="/",
                    className="navbar-brand",
                ),

                html.Div(
                    [
                        dcc.Link(
                            page["name"],
                            href=page["relative_path"],
                            id={"type": "navbar-link", "index": page["relative_path"]},
                            className="navbar-link",
                        )
                        for page in dash.page_registry.values()
                    ],
                    className="navbar-links",
                ),

                html.Button(
                    html.Span(className="theme-toggle__icon"),
                    id="theme-toggle",
                    className="theme-toggle",
                    title="Alternar tema claro/escuro",
                    **{"aria-label": "Alternar tema claro/escuro"},
                ),
            ],
            className="navbar-content"
        ),
        className="navbar",
    )

def create_footer():
    return html.Footer(
        html.Div(
            [
                html.Span("CPSI — Edital de Despesas Públicas do Espírito Santo"),
                html.Span("Dados de despesas do Governo do ES · 2024–2025", className="page-footer__muted"),
            ],
            className="page-footer__content",
        ),
        className="page-footer",
    )

app.layout = html.Div(
    [
        dcc.Location(id="url"),
        create_navigation(),

        html.Main(
            dash.page_container,
            className="app-content",
        ),

        create_footer(),
    ],
    className="app-shell",
)

@app.callback(
    Output({"type": "navbar-link", "index": ALL}, "className"),
    Input("url", "pathname"),
)
def highlight_active_link(pathname):
    """Marca com a classe "active" o link da página aberta."""
    return [
        "navbar-link active" if page["relative_path"] == pathname else "navbar-link"
        for page in dash.page_registry.values()
    ]

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8050)),
        debug=False,
    )
