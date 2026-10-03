import dash
from dash import Input, Output, callback, dcc, html

from src.analytics.charts import (
    expenses_by_element_chart,
    expenses_by_subelement_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, name="Despesas", order=2)

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
                    "Os rankings usam valores pagos agregados de 2024 e 2025. Ajuste a "
                    "quantidade de categorias ou busque por nome.",
                    className="page-note",
                ),
            ],
            className="page-intro",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Categorias no ranking", htmlFor="expenses-top-n"),
                        dcc.RadioItems(
                            id="expenses-top-n",
                            options=[{"label": str(value), "value": value} for value in (5, 10, 15)],
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
                        html.Label("Buscar elemento ou subelemento", htmlFor="expenses-category-search"),
                        dcc.Input(
                            id="expenses-category-search",
                            type="search",
                            placeholder="Digite parte do nome da categoria",
                            className="filter-input",
                        ),
                    ],
                    className="filter-group filter-group--search",
                ),
            ],
            className="page-filter-row",
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


@callback(
    Output("expenses-by-element", "figure"),
    Output("expenses-by-subelement", "figure"),
    Input("expenses-top-n", "value"),
    Input("expenses-category-search", "value"),
)
def update_expense_charts(top_n, search):
    limit = int(top_n or 15)
    query = (search or "").strip()
    filtered_elements = elements
    filtered_subelements = subelements

    if query:
        subelement_names = (
            subelements["ElementoDespesa"].astype("string")
            + " "
            + subelements["SubelementoDespesa"].astype("string")
        )
        subelement_match = subelement_names.str.contains(
            query, case=False, na=False, regex=False
        )
        filtered_subelements = subelements.loc[subelement_match]
        matching_parents = set(filtered_subelements["ElementoDespesa"])
        element_names = elements["ElementoDespesa"].astype("string")
        element_match = element_names.str.contains(
            query, case=False, na=False, regex=False
        ) | element_names.isin(matching_parents)
        filtered_elements = elements.loc[element_match]

    element_figure = expenses_by_element_chart(filtered_elements.head(limit))
    subelement_figure = expenses_by_subelement_chart(filtered_subelements.head(limit))
    if query and filtered_elements.empty:
        element_figure.add_annotation(
            text="Nenhum elemento encontrado.", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False,
        )
    if query and filtered_subelements.empty:
        subelement_figure.add_annotation(
            text="Nenhum subelemento encontrado.", x=0.5, y=0.5,
            xref="paper", yref="paper", showarrow=False,
        )
    return element_figure, subelement_figure
