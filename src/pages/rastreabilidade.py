import dash
from dash import Input, Output, callback, dcc, html

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
                    "Os processos agregam valores pagos de 2024 e 2025. Use os filtros "
                    "para limitar o ranking por código e escolher os campos de referência.",
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
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Label("Processos exibidos", htmlFor="processes-top-n"),
                                        dcc.RadioItems(
                                            id="processes-top-n",
                                            options=[
                                                {"label": str(value), "value": value}
                                                for value in (5, 10, 15)
                                            ],
                                            value=15,
                                            inline=True,
                                            labelStyle={"display": "inline-flex"},
                                            className="pill-options",
                                        ),
                                    ],
                                    className="filter-group",
                                ),
                                html.Div(
                                    [
                                        html.Label("Buscar código do processo", htmlFor="process-search"),
                                        dcc.Input(
                                            id="process-search",
                                            type="search",
                                            placeholder="Digite parte do código",
                                            className="filter-input",
                                        ),
                                    ],
                                    className="filter-group filter-group--search",
                                ),
                            ],
                            className="page-filter-row",
                        ),
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
                        html.Div(
                            [
                                html.Label("Campos exibidos", htmlFor="traceability-fields"),
                                dcc.Checklist(
                                    id="traceability-fields",
                                    options=[
                                        {"label": "Processo", "value": "CodigoProcesso"},
                                        {"label": "Documento", "value": "Documento"},
                                        {"label": "Empenho", "value": "DocumentoEmpenho"},
                                        {"label": "ID", "value": "Id"},
                                    ],
                                    value=[
                                        "CodigoProcesso",
                                        "Documento",
                                        "DocumentoEmpenho",
                                        "Id",
                                    ],
                                    inline=True,
                                    labelStyle={"display": "inline-flex"},
                                    className="pill-options",
                                ),
                            ],
                            className="filter-group page-inline-filter",
                        ),
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


@callback(
    Output("processes-by-payment", "figure"),
    Input("processes-top-n", "value"),
    Input("process-search", "value"),
)
def update_processes_chart(top_n, search):
    limit = int(top_n or 15)
    query = (search or "").strip()
    data = processes
    if query:
        matches = data["CodigoProcesso"].astype("string").str.contains(
            query, case=False, na=False, regex=False
        )
        data = data.loc[matches]

    figure = processes_chart(data.head(limit))
    if query and data.empty:
        figure.add_annotation(
            text="Nenhum processo encontrado.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
    return figure


@callback(
    Output("traceability-field-coverage", "figure"),
    Input("traceability-fields", "value"),
)
def update_traceability_coverage(fields):
    selected = set(fields or [])
    data = quality_summary.loc[quality_summary["column"].isin(selected)]
    figure = traceability_coverage_chart(data)
    if not selected:
        figure.add_annotation(
            text="Selecione ao menos um campo.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
    return figure
