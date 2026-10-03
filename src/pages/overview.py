import dash
from dash import dcc, html

from src.analytics.charts import (
    annual_financial_comparison_chart,
    financial_evolution_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, path="/visao-geral", name="Visão Geral", order=1)

monthly_totals = load_report("metrics_by_month.csv")
yearly_totals = load_report("metrics_by_year.csv")

layout = html.Div(
    [
        html.Div(
            [
                html.H1("Visão Geral das Despesas Públicas do ES"),
                html.P(
                    "Como os valores empenhados, liquidados, pagos e de restos a pagar "
                    "evoluem entre 2024 e 2025?",
                    className="page-question",
                ),
            ],
            className="page-intro",
        ),
        html.Section(
            [
                html.H2("Evolução mensal"),
                dcc.Graph(
                    id="financial-evolution",
                    figure=financial_evolution_chart(monthly_totals),
                    config={"displayModeBar": False, "responsive": True},
                ),
            ],
            className="chart-card",
        ),
        html.Section(
            [
                html.H2("Comparação entre anos"),
                dcc.Graph(
                    id="annual-financial-comparison",
                    figure=annual_financial_comparison_chart(yearly_totals),
                    config={"displayModeBar": False, "responsive": True},
                ),
            ],
            className="chart-card",
        ),
    ],
    className="page-content",
)
