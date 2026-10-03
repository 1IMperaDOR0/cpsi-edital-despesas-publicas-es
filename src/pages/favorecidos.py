import dash
from dash import Input, Output, callback, dash_table, dcc, html

from src.analytics.charts import (
    beneficiary_pareto_chart,
    payment_boxplot_chart,
    payment_mean_ci_chart,
    probability_chart,
    procurement_types_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, name="Favorecidos e Contratações", order=3)

statistics = load_report("payment_statistics.csv")
concentration = load_report("beneficiary_concentration.csv")
concentration_summary = load_report("beneficiary_concentration_summary.csv")
procurement_types = load_report("payments_by_licitacao_positive.csv")
variable_catalog = load_report("variable_catalog.csv")

overall = statistics.loc[statistics["Escopo"] == "Todos"].iloc[0]
summary = concentration_summary.iloc[0]


def br_currency(value: float) -> str:
    text = f"{float(value):,.2f}"
    return "R$ " + text.replace(",", "X").replace(".", ",").replace("X", ".")


def pct(value: float) -> str:
    return f"{float(value):.2f}%".replace(".", ",")


def integer(value: float) -> str:
    return f"{int(value):,}".replace(",", ".")


STATISTICS_YEARS = sorted(
    statistics.loc[statistics["Escopo"] != "Todos", "Escopo"].astype(str).unique()
)


def statistics_rows(year_scope: str = "Todos"):
    data = statistics.loc[statistics["Escopo"] != "Todos"].copy()
    if year_scope != "Todos":
        data = data.loc[data["Escopo"].astype(str) == year_scope]

    rows = []
    for _, row in data.sort_values("Ano").iterrows():
        rows.append(
            html.Tr(
                [
                    html.Td(str(int(row["Ano"]))),
                    html.Td(integer(row["PagamentosPositivos"])),
                    html.Td(br_currency(row["Media"])),
                    html.Td(br_currency(row["Mediana"])),
                    html.Td(br_currency(row["DesvioPadrao"])),
                    html.Td(br_currency(row["Q1"])),
                    html.Td(br_currency(row["Q3"])),
                    html.Td(pct(row["ProbOutlierSuperior"] * 100)),
                    html.Td(
                        f"{br_currency(row['IC95Inferior'])} — {br_currency(row['IC95Superior'])}"
                    ),
                ]
            )
        )
    return rows


layout = html.Div(
    [
        html.Div(
            [
                html.H1("Favorecidos e Contratações"),
                html.P(
                    "Como os pagamentos se distribuem entre os favorecidos e as modalidades "
                    "de contratação? Existe concentração relevante dos valores pagos?",
                    className="page-question",
                ),
                html.P(
                    "A análise combina categorização de variáveis, estatística descritiva, "
                    "boxplot, probabilidade empírica e intervalo de confiança. Para essas "
                    "medidas, são considerados pagamentos com ValorPago > 0; zeros e valores "
                    "negativos permanecem na base original e podem representar ausência de "
                    "pagamento ou ajustes/estornos. Os controles em cada seção ajustam o "
                    "ranking, a modalidade pesquisada ou o ano da análise estatística. "
                    "Rankings e modalidades abrangem 2024 e 2025.",
                    className="page-note",
                ),
            ],
            className="page-intro",
        ),
        html.Section(
            [
                html.H2("Categorização das variáveis"),
                html.P(
                    "A classificação estatística ajuda a definir quais operações e gráficos "
                    "fazem sentido para cada campo: medidas quantitativas permitem resumos "
                    "numéricos; categorias nominais são comparadas por frequência ou valor.",
                    className="section-note",
                ),
                dash_table.DataTable(
                    data=variable_catalog.to_dict("records"),
                    columns=[
                        {"name": column, "id": column}
                        for column in variable_catalog.columns
                    ],
                    style_table={"overflowX": "auto"},
                    style_cell={
                        "textAlign": "left",
                        "whiteSpace": "normal",
                        "height": "auto",
                        "padding": "10px",
                        "fontFamily": "Arial, sans-serif",
                        "fontSize": "13px",
                    },
                    style_header={
                        "fontWeight": "700",
                        "backgroundColor": "#eef5f5",
                    },
                    style_data_conditional=[
                        {
                            "if": {"row_index": "odd"},
                            "backgroundColor": "#fafcfc",
                        }
                    ],
                ),
            ],
            className="chart-card",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Span("Registros analisados"),
                        html.Strong(integer(overall["RegistrosTotais"])),
                    ],
                    className="kpi-card",
                ),
                html.Div(
                    [
                        html.Span("Pagamentos positivos"),
                        html.Strong(integer(overall["PagamentosPositivos"])),
                    ],
                    className="kpi-card",
                ),
                html.Div(
                    [
                        html.Span("Total positivo pago"),
                        html.Strong(br_currency(overall["TotalPagoPositivo"])),
                    ],
                    className="kpi-card",
                ),
                html.Div(
                    [
                        html.Span("Top 10 — participação no valor"),
                        html.Strong(pct(summary["TopNParticipacaoValorPct"])),
                    ],
                    className="kpi-card",
                ),
            ],
            className="kpi-grid",
        ),
        html.Div(
            [
                html.Section(
                    [
                        html.H2("Concentração — Pareto dos favorecidos"),
                        html.P(
                            "As barras mostram os maiores favorecidos por valor pago positivo; "
                            "a linha mostra a participação acumulada no total. O Pareto permite "
                            "avaliar se uma parcela pequena dos favorecidos concentra grande "
                            "parte dos pagamentos.",
                            className="section-note",
                        ),
                        html.Div(
                            [
                                html.Label("Favorecidos exibidos", htmlFor="beneficiary-top-n"),
                                dcc.RadioItems(
                                    id="beneficiary-top-n",
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
                            className="filter-group page-inline-filter",
                        ),
                        dcc.Graph(
                            id="beneficiary-pareto",
                            figure=beneficiary_pareto_chart(concentration),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
                html.Section(
                    [
                        html.H2("Pagamentos por tipo de licitação"),
                        html.P(
                            "O gráfico de barras é adequado porque TipoLicitacao é uma variável "
                            "qualitativa nominal e o objetivo é comparar magnitudes entre categorias.",
                            className="section-note",
                        ),
                        html.Div(
                            [
                                html.Label("Buscar modalidade", htmlFor="procurement-search"),
                                dcc.Input(
                                    id="procurement-search",
                                    type="search",
                                    placeholder="Digite parte do nome da modalidade",
                                    className="filter-input",
                                ),
                            ],
                            className="filter-group page-inline-filter page-inline-filter--wide",
                        ),
                        dcc.Graph(
                            id="procurement-types-chart",
                            figure=procurement_types_chart(procurement_types),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="dashboard-grid dashboard-grid--1",
        ),
        html.Section(
            [
                html.H2("Estatística descritiva de ValorPago"),
                html.P(
                    "Média, mediana, desvio padrão e quartis são apresentados em conjunto. "
                    "Isso é importante porque distribuições financeiras podem ser assimétricas "
                    "e a média isolada pode ser puxada por pagamentos muito altos. O filtro "
                    "de ano atualiza a tabela, o boxplot e o intervalo de confiança.",
                    className="section-note",
                ),
                html.Div(
                    [
                        html.Label("Ano da análise estatística", htmlFor="beneficiary-statistics-year"),
                        dcc.RadioItems(
                            id="beneficiary-statistics-year",
                            options=[
                                {"label": "Todos", "value": "Todos"},
                                *[
                                    {"label": year, "value": year}
                                    for year in STATISTICS_YEARS
                                ],
                            ],
                            value="Todos",
                            inline=True,
                            labelStyle={"display": "inline-flex"},
                            className="pill-options",
                        ),
                    ],
                    className="filter-group page-inline-filter",
                ),
                html.Div(
                    [
                        html.Table(
                            [
                                html.Thead(
                                    html.Tr(
                                        [
                                            html.Th("Ano"),
                                            html.Th("n positivo"),
                                            html.Th("Média"),
                                            html.Th("Mediana"),
                                            html.Th("Desvio padrão"),
                                            html.Th("Q1"),
                                            html.Th("Q3"),
                                            html.Th("Outliers sup."),
                                            html.Th("IC 95% da média"),
                                        ]
                                    )
                                ),
                                html.Tbody(
                                    statistics_rows(),
                                    id="beneficiary-statistics-rows",
                                ),
                            ],
                            className="stats-table",
                        )
                    ],
                    className="table-scroll",
                ),
            ],
            className="chart-card",
        ),
        html.Div(
            [
                html.Section(
                    [
                        html.H2("Boxplot — distribuição dos pagamentos"),
                        html.P(
                            "O boxplot resume mediana, Q1, Q3 e os limites de Tukey (1,5×IQR). "
                            "Valores acima do limite são outliers estatísticos, mas isso não "
                            "significa fraude ou irregularidade.",
                            className="section-note",
                        ),
                        dcc.Graph(
                            id="beneficiary-boxplot",
                            figure=payment_boxplot_chart(statistics),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
                html.Section(
                    [
                        html.H2("Intervalo de confiança de 95%"),
                        html.P(
                            "A estimativa usa a média dos pagamentos positivos, erro padrão e "
                            "distribuição t-Student. O IC é usado como aplicação inferencial "
                            "didática sobre a média; os totais observados na base não precisam "
                            "de intervalo de confiança para serem descritos.",
                            className="section-note",
                        ),
                        dcc.Graph(
                            id="beneficiary-confidence-interval",
                            figure=payment_mean_ci_chart(statistics),
                            config={"displayModeBar": False, "responsive": True},
                        ),
                    ],
                    className="chart-card",
                ),
            ],
            className="dashboard-grid dashboard-grid--2",
        ),
        html.Section(
            [
                html.H2("Probabilidade empírica"),
                html.P(
                    "As probabilidades são frequências relativas observadas na base. "
                    "P(ValorPago > 0) usa todos os registros; as demais são condicionais ao "
                    "conjunto de pagamentos positivos. Elas descrevem a base analisada e não "
                    "representam causalidade nem previsão futura.",
                    className="section-note",
                ),
                dcc.Graph(
                    figure=probability_chart(statistics, concentration_summary),
                    config={"displayModeBar": False, "responsive": True},
                ),
                html.Div(
                    [
                        html.Div(
                            [
                                html.Strong(pct(overall["ProbPagamentoPositivo"] * 100)),
                                html.Span("P(ValorPago > 0)"),
                            ],
                            className="probability-card",
                        ),
                        html.Div(
                            [
                                html.Strong(pct(overall["ProbOutlierSuperior"] * 100)),
                                html.Span(
                                    "P(outlier superior | ValorPago > 0), pelo critério 1,5×IQR"
                                ),
                            ],
                            className="probability-card",
                        ),
                        html.Div(
                            [
                                html.Strong(pct(summary["TopNParticipacaoRegistrosPct"])),
                                html.Span(
                                    "P(registro pertencer ao Top 10 favorecidos | ValorPago > 0)"
                                ),
                            ],
                            className="probability-card",
                        ),
                    ],
                    className="probability-grid",
                ),
            ],
            className="chart-card",
        ),
        html.Section(
            [
                html.H2("Interpretação crítica"),
                html.Ul(
                    [
                        html.Li(
                            f"Os 10 maiores favorecidos concentram "
                            f"{pct(summary['TopNParticipacaoValorPct'])} do valor total dos "
                            "pagamentos positivos."
                        ),
                        html.Li(
                            f"A mediana geral é {br_currency(overall['Mediana'])}, enquanto "
                            f"a média é {br_currency(overall['Media'])}. A diferença entre "
                            "essas medidas ajuda a identificar assimetria na distribuição."
                        ),
                        html.Li(
                            f"Pelo critério do boxplot, "
                            f"{pct(overall['ProbOutlierSuperior'] * 100)} dos pagamentos "
                            "positivos ficam acima do limite superior de 1,5×IQR."
                        ),
                        html.Li(
                            "Favorecido não deve ser interpretado automaticamente como empresa "
                            "privada: a base pode conter pessoas, órgãos, entidades e outros "
                            "tipos de recebedores."
                        ),
                        html.Li(
                            "Os resultados descrevem os registros oficiais disponíveis de 2024 "
                            "e 2025 e herdam eventuais limitações de qualidade e classificação "
                            "da fonte de dados."
                        ),
                    ]
                ),
            ],
            className="interpretation-card",
        ),
    ],
    className="page-content",
)


@callback(
    Output("beneficiary-pareto", "figure"),
    Input("beneficiary-top-n", "value"),
)
def update_beneficiary_ranking(top_n):
    return beneficiary_pareto_chart(concentration, top_n=int(top_n or 15))


@callback(
    Output("procurement-types-chart", "figure"),
    Input("procurement-search", "value"),
)
def update_procurement_types(search):
    query = (search or "").strip()
    data = procurement_types
    if query:
        matches = data["TipoLicitacao"].astype("string").str.contains(
            query, case=False, na=False, regex=False
        )
        data = data.loc[matches]

    figure = procurement_types_chart(data)
    if query and data.empty:
        figure.add_annotation(
            text="Nenhuma modalidade encontrada.",
            x=0.5,
            y=0.5,
            xref="paper",
            yref="paper",
            showarrow=False,
        )
    return figure


@callback(
    Output("beneficiary-statistics-rows", "children"),
    Output("beneficiary-boxplot", "figure"),
    Output("beneficiary-confidence-interval", "figure"),
    Input("beneficiary-statistics-year", "value"),
)
def update_beneficiary_statistics(year_scope):
    annual = statistics.loc[statistics["Escopo"] != "Todos"].copy()
    if year_scope and year_scope != "Todos":
        annual = annual.loc[annual["Escopo"].astype(str) == year_scope]
    return (
        statistics_rows(year_scope or "Todos"),
        payment_boxplot_chart(annual),
        payment_mean_ci_chart(annual),
    )
