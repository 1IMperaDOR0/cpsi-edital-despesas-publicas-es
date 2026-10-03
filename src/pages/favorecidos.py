import dash
from dash import dash_table, dcc, html

from src.analytics.charts import (
    beneficiary_pareto_chart,
    payment_boxplot_chart,
    payment_mean_ci_chart,
    probability_chart,
    procurement_types_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, name="Favorecidos e Contratações", order=2)

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


stat_rows = []
for _, row in statistics.loc[statistics["Escopo"] != "Todos"].sort_values("Ano").iterrows():
    stat_rows.append(
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
                    "pagamento ou ajustes/estornos.",
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
                        dcc.Graph(
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
                        dcc.Graph(
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
                    "e a média isolada pode ser puxada por pagamentos muito altos.",
                    className="section-note",
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
                                html.Tbody(stat_rows),
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
