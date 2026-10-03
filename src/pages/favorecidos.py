import dash
from dash import dcc, html

from src.analytics.charts import (
    beneficiaries_chart,
    procurement_types_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, name="Favorecidos e Contratações", order=2)

beneficiaries = load_report("metrics_by_beneficiary.csv")
procurement_types = load_report("metrics_by_licitacao.csv")

layout = html.Div(
    [
        html.Div(
            [
                html.H1("Favorecidos e Contratações"),
                html.P(
                    "Para quem os recursos foram destinados e como os pagamentos se "
                    "distribuem entre as modalidades de contratação?",
                    className="page-question",
                ),
                html.P(
                    "O ranking apresenta os 15 favorecidos com maior valor pago. "
                    "A distribuição usa as categorias originais do campo TipoLicitacao.",
                    className="page-note",
                ),
            ],
            className="page-intro",
        ),
        html.Div(
            [
                html.Section(
                    [
                        html.H2("Pagamentos por favorecido"),
                        dcc.Graph(
                            id="beneficiaries-ranking",
                            figure=beneficiaries_chart(beneficiaries),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
                html.Section(
                    [
                        html.H2("Pagamentos por tipo de licitação"),
                        dcc.Graph(
                            id="procurement-types",
                            figure=procurement_types_chart(procurement_types),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="dashboard-grid dashboard-grid--1",
        ),
    ],
    className="page-content",
)
