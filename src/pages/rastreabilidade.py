import dash
from dash import html


dash.register_page(__name__, name="Rastreabilidade", order=3)

layout = html.Div(
    [
        html.H1("Rastreabilidade dos Registros"),
        html.P(
            "Pergunta norteadora: quais registros, documentos e processos compõem "
            "os valores apresentados no painel?"
        ),
        html.P("Esqueleto da página. A tabela detalhada será criada após a validação dos campos de rastreabilidade."),
    ]
)
