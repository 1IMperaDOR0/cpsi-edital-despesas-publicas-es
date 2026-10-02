import dash
from dash import Dash, dcc, html

app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder="src/pages",
    assets_folder="src/assets",
    suppress_callback_exceptions=True,
)

server = app.server

def create_navigation():
    return html.Nav( 
        html.Div(
            [
                html.Div(
                    "CPSI — Edital Despesas Públicas ES",
                    className="navbar-brand",
                ),

                html.Div(
                    [
                        dcc.Link(
                            page["name"],
                            href=page["relative_path"],
                            className="navbar-link",
                        )
                        for page in dash.page_registry.values()
                    ],
                    className="navbar-links",
                ),
            ],
            className="navbar-content"
        ),
        className="navbar",
    )

app.layout = html.Div(
    [
        create_navigation(),

        html.Main(
            dash.page_container,
            className="app-content",
        ),
    ],
    className="app-shell",
)

if __name__ == "__main__":
    app.run(debug=True)