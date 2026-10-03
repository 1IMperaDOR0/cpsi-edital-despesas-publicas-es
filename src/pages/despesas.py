import dash
from dash import dcc, html

from src.analytics.charts import (
    expenses_by_element_chart,
    expenses_by_subelement_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, name="Despesas", order=1)

elements = load_report("metrics_by_element.csv")
subelements = load_report("metrics_by_subelement.csv")

layout = html.Div(
    [
        html.Div(
            [
                html.H1("Composição das Despesas"),
                html.P(
                    "Em quais elementos e subelementos de despesa os recursos públicos "
                    "estão sendo aplicados?",
                    className="page-question",
                ),
                html.P(
                    "Os rankings usam o valor pago e mostram as 15 categorias com maior total.",
                    className="page-note",
                ),
            ],
            className="page-intro",
        ),
        html.Div(
            [
                html.Section(
                    [
                        html.H2("Por elemento de despesa"),
                        dcc.Graph(
                            id="expenses-by-element",
                            figure=expenses_by_element_chart(elements),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
                html.Section(
                    [
                        html.H2("Por subelemento de despesa"),
                        dcc.Graph(
                            id="expenses-by-subelement",
                            figure=expenses_by_subelement_chart(subelements),
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
