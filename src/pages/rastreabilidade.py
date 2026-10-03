import dash
from dash import dcc, html

from src.analytics.charts import (
    processes_chart,
    traceability_coverage_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, name="Rastreabilidade", order=4)

processes = load_report("metrics_by_process.csv")
quality_summary = load_report("quality_summary.csv")

layout = html.Div(
    [
        html.Div(
            [
                html.H1("Rastreabilidade dos Registros"),
                html.P(
                    "Quais registros, documentos e processos compõem os valores "
                    "apresentados no painel?",
                    className="page-question",
                ),
                html.P(
                    "O gráfico de processos destaca os 15 maiores valores pagos; "
                    "ao passar o cursor, veja os registros com documento e documento de empenho.",
                    className="page-note",
                ),
            ],
            className="page-intro",
        ),
        html.Div(
            [
                html.Section(
                    [
                        html.H2("Processos associados aos pagamentos"),
                        dcc.Graph(
                            id="processes-by-payment",
                            figure=processes_chart(processes),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
                html.Section(
                    [
                        html.H2("Preenchimento das referências"),
                        dcc.Graph(
                            id="traceability-field-coverage",
                            figure=traceability_coverage_chart(quality_summary),
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
