import dash
from dash import html


dash.register_page(__name__, path="/", name="Visão Geral", order=0)

layout = html.Div(
    [
        html.H1("Visão Geral das Despesas Públicas do ES"),
        html.P(
            "Pergunta norteadora: como os valores empenhados, liquidados, "
            "pagos e de restos a pagar evoluem entre 2024 e 2025?"
        ),
        html.P("Esqueleto da página. Indicadores e gráficos serão adicionados depois da validação do pipeline."),
    ]
)
