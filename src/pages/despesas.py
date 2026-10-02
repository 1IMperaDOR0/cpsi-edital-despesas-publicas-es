import dash
from dash import html


dash.register_page(__name__, name="Despesas", order=1)

layout = html.Div(
    [
        html.H1("Composição das Despesas"),
        html.P(
            "Pergunta norteadora: em quais elementos e subelementos de despesa "
            "os recursos públicos estão sendo aplicados?"
        ),
        html.P("Esqueleto da página. Sem análises implementadas nesta etapa."),
    ]
)
