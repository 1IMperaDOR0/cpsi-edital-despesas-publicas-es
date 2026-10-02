import dash
from dash import html


dash.register_page(__name__, name="Favorecidos e Contratações", order=2)

layout = html.Div(
    [
        html.H1("Favorecidos e Contratações"),
        html.P(
            "Pergunta norteadora: para quem os recursos foram destinados e "
            "como os pagamentos se distribuem entre as modalidades de contratação?"
        ),
        html.P("Esqueleto da página. Sem ranking ou interpretação de irregularidade nesta etapa."),
    ]
)
