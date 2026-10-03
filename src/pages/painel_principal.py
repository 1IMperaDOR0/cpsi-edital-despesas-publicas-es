from __future__ import annotations

import pandas as pd
import dash
from dash import Input, Output, callback, dcc, html

from src.analytics.charts import (
    FINANCIAL_LABELS,
    annual_financial_comparison_chart,
    financial_evolution_chart,
    payment_boxplot_chart,
    payment_mean_ci_chart,
)
from src.analytics.report_loader import load_report


dash.register_page(__name__, path="/", name="Painel Principal", order=0)

yearly_totals = load_report("metrics_by_year.csv")
monthly_totals = load_report("metrics_by_month.csv")
payment_statistics = load_report("payment_statistics.csv")

DASHBOARD_YEARS = tuple(
    sorted(yearly_totals["Ano"].dropna().astype(int).astype(str).unique())
)


def format_currency(value: float) -> str:
    if pd.isna(value):
        return "—"
    amount = f"{float(value):,.2f}"
    amount = amount.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {amount}"


def format_currency_compact(value: float) -> str:
    if pd.isna(value):
        return "—"
    amount = float(value)
    magnitude = abs(amount)
    if magnitude >= 1_000_000_000:
        return f"R$ {(amount / 1_000_000_000):.2f} bi".replace(".", ",")
    if magnitude >= 1_000_000:
        return f"R$ {(amount / 1_000_000):.1f} mi".replace(".", ",")
    if magnitude >= 1_000:
        return f"R$ {(amount / 1_000):.1f} mil".replace(".", ",")
    return format_currency(amount)


def format_integer(value: float) -> str:
    if pd.isna(value):
        return "—"
    return f"{int(value):,}".replace(",", ".")


def filtered_statistics(selected_years: list[str]) -> pd.DataFrame:
    annual = payment_statistics.loc[payment_statistics["Escopo"] != "Todos"].copy()
    annual["Escopo"] = annual["Escopo"].astype(str)
    return annual.loc[annual["Escopo"].isin(selected_years)].copy()


def selected_statistics_summary(selected_years: list[str]) -> pd.Series | None:
    if set(selected_years) == set(DASHBOARD_YEARS):
        overall = payment_statistics.loc[payment_statistics["Escopo"] == "Todos"]
        if not overall.empty:
            return overall.iloc[0]
    if len(selected_years) == 1:
        selected = payment_statistics.loc[
            payment_statistics["Escopo"] == selected_years[0]
        ]
        if not selected.empty:
            return selected.iloc[0]
    return None


def statistics_table(statistics: pd.DataFrame):
    columns = [
        ("Ano", lambda row: str(int(row["Ano"]))),
        ("n positivo", lambda row: format_integer(row["PagamentosPositivos"])),
        ("Média", lambda row: format_currency(row["Media"])),
        ("Mediana", lambda row: format_currency(row["Mediana"])),
        ("Desvio padrão", lambda row: format_currency(row["DesvioPadrao"])),
        ("IQR", lambda row: format_currency(row["IQR"])),
        (
            "IC 95% da média",
            lambda row: (
                f"{format_currency(row['IC95Inferior'])} a "
                f"{format_currency(row['IC95Superior'])}"
            ),
        ),
    ]
    if statistics.empty:
        return html.P(
            "Não há pagamentos positivos para o período selecionado.",
            className="section-note",
        )
    return html.Div(
        html.Table(
            [
                html.Thead(html.Tr([html.Th(label) for label, _ in columns])),
                html.Tbody(
                    [
                        html.Tr(
                            [html.Td(render(row)) for _, render in columns]
                        )
                        for _, row in statistics.sort_values("Ano").iterrows()
                    ]
                ),
            ],
            className="stats-table",
        ),
        className="table-scroll",
    )


_initial_statistics = filtered_statistics(list(DASHBOARD_YEARS))
_initial_summary = selected_statistics_summary(list(DASHBOARD_YEARS))


layout = html.Div(
    [
        html.Div(
            [
                html.H1("Do dado público à leitura rastreável"),
                html.P(
                    "Um panorama das despesas do Governo do Espírito Santo em 2024 e "
                    "2025: quando os valores aparecem, como se distribuem e onde "
                    "encontrar o caminho até os registros.",
                    className="page-question",
                ),
                html.P(
                    "A soma dos campos financeiros reproduz os valores registrados. "
                    "A semântica e o nível seguro de agregação ainda exigem validação "
                    "antes que esses totais sejam tratados como indicadores contábeis.",
                    className="page-note",
                ),
            ],
            className="page-intro",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Ano", htmlFor="main-dashboard-years"),
                        dcc.Checklist(
                            id="main-dashboard-years",
                            options=[
                                {"label": year, "value": year}
                                for year in DASHBOARD_YEARS
                            ],
                            value=list(DASHBOARD_YEARS),
                            inline=True,
                            labelStyle={"display": "inline-flex"},
                            className="main-year-options",
                        ),
                    ],
                    className="filter-group",
                ),
                html.Div(
                    [
                        html.Label(
                            "Medida financeira",
                            htmlFor="main-dashboard-measure",
                        ),
                        dcc.RadioItems(
                            id="main-dashboard-measure",
                            options=[
                                {"label": label, "value": column}
                                for column, label in FINANCIAL_LABELS.items()
                            ],
                            value="ValorPago",
                            inline=True,
                            labelStyle={"display": "inline-flex"},
                            className="main-measure-options",
                        ),
                    ],
                    className="filter-group",
                ),
                html.Span(
                    f"2024 e 2025 · Pago",
                    id="main-filter-summary",
                    className="badge main-filter-summary",
                ),
            ],
            className="filter-bar main-filter-bar",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Span("Registros no recorte"),
                        html.Strong(
                            format_integer(yearly_totals["Registros"].sum()),
                            id="main-kpi-records",
                        ),
                        html.P("Registros processados", className="kpi-hint"),
                    ],
                    className="kpi-card",
                ),
                html.Div(
                    [
                        html.Span("Total — Pago", id="main-kpi-measure-label"),
                        html.Strong(
                            format_currency_compact(yearly_totals["ValorPago"].sum()),
                            id="main-kpi-paid",
                        ),
                        html.P(
                            "Inclui registros zerados e negativos",
                            className="kpi-hint",
                        ),
                    ],
                    className="kpi-card kpi-card--pago",
                ),
                html.Div(
                    [
                        html.Span("Pagamentos positivos"),
                        html.Strong(
                            format_integer(_initial_statistics["PagamentosPositivos"].sum()),
                            id="main-kpi-positive-count",
                        ),
                        html.P("ValorPago maior que zero", className="kpi-hint"),
                    ],
                    className="kpi-card",
                ),
                html.Div(
                    [
                        html.Span("Mediana por pagamento positivo"),
                        html.Strong(
                            format_currency(_initial_summary["Mediana"])
                            if _initial_summary is not None else "—",
                            id="main-kpi-median",
                        ),
                        html.P(
                            "Menos sensível a valores extremos",
                            className="kpi-hint",
                        ),
                    ],
                    className="kpi-card",
                ),
                html.Div(
                    [
                        html.Span("Desvio padrão positivo"),
                        html.Strong(
                            format_currency(_initial_summary["DesvioPadrao"])
                            if _initial_summary is not None else "—",
                            id="main-kpi-sd",
                        ),
                        html.P("Dispersão em torno da média", className="kpi-hint"),
                    ],
                    className="kpi-card",
                ),
            ],
            className="kpi-grid",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Span("01 · Origem", className="story-beat__eyebrow"),
                        html.H2("Uma base pública ampla"),
                        html.P(
                            "O pipeline consolida oito arquivos oficiais de 2024 e "
                            "2025 em mais de um milhão de registros, preservando a "
                            "origem de cada linha."
                        ),
                    ],
                    className="story-beat",
                ),
                html.Div(
                    [
                        html.Span("02 · Leitura", className="story-beat__eyebrow"),
                        html.H2("Valores contam partes diferentes"),
                        html.P(
                            "Empenho, liquidação, pagamento e restos a pagar mostram "
                            "a execução por ângulos diferentes. Pagamentos positivos "
                            "permitem estudar mediana, dispersão e incerteza da média."
                        ),
                    ],
                    className="story-beat",
                ),
                html.Div(
                    [
                        html.Span("03 · Evidência", className="story-beat__eyebrow"),
                        html.H2("Do agregado ao registro"),
                        html.P(
                            "As páginas analíticas detalham a aplicação dos recursos, "
                            "os favorecidos, as contratações e os processos associados."
                        ),
                    ],
                    className="story-beat",
                ),
            ],
            className="story-beat-grid",
        ),
        html.Section(
            [
                html.H2("Como os valores se movem"),
                html.P(
                    "Escolha a medida financeira para comparar os anos e acompanhar "
                    "os totais mensais do recorte. Os pontos são somas dos registros "
                    "em cada mês; os gráficos estatísticos abaixo mantêm foco em "
                    "pagamentos positivos.",
                    className="section-note",
                ),
                html.Div(
                    [
                        html.Section(
                            [
                                html.H2("Comparação anual"),
                                dcc.Graph(
                                    id="main-annual-chart",
                                    figure=annual_financial_comparison_chart(yearly_totals, metric="ValorPago"),
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                            ],
                            className="chart-card",
                        ),
                        html.Section(
                            [
                                html.H2("Evolução mensal"),
                                dcc.Graph(
                                    id="main-monthly-chart",
                                    figure=financial_evolution_chart(monthly_totals, metric="ValorPago"),
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                            ],
                            className="chart-card",
                        ),
                    ],
                    className="dashboard-grid dashboard-grid--2",
                ),
            ],
            className="page-content",
        ),
        html.Section(
            [
                html.H2("O que a distribuição revela"),
                html.P(
                    "O boxplot resume a dispersão dos pagamentos positivos por ano. "
                    "A tabela reúne desvio padrão e intervalo interquartil (IQR); "
                    "o gráfico ao lado estima a média com intervalo t de 95%.",
                    className="section-note",
                ),
                html.Div(
                    [
                        html.Section(
                            [
                                html.H2("Dispersão dos pagamentos positivos"),
                                dcc.Graph(
                                    id="main-boxplot",
                                    figure=payment_boxplot_chart(_initial_statistics),
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                            ],
                            className="chart-card",
                        ),
                        html.Section(
                            [
                                html.H2("Média e intervalo de confiança"),
                                dcc.Graph(
                                    id="main-ci-chart",
                                    figure=payment_mean_ci_chart(_initial_statistics),
                                    config={"displayModeBar": False, "responsive": True},
                                ),
                            ],
                            className="chart-card",
                        ),
                    ],
                    className="dashboard-grid dashboard-grid--2",
                ),
                html.Div(
                    [
                        html.H2("Resumo estatístico por ano"),
                        html.P(
                            "As estatísticas de distribuição consideram somente "
                            "ValorPago > 0; zeros e negativos continuam incluídos "
                            "nos totais agregados e na base.",
                            className="section-note",
                        ),
                        html.Div(
                            statistics_table(_initial_statistics),
                            id="main-stats-table",
                        ),
                    ],
                    className="chart-card",
                ),
                html.Div(
                    [
                        html.H2("Leitura deste recorte"),
                        html.Ul(id="main-story-insights", children=[]),
                    ],
                    className="interpretation-card",
                ),
                html.P(
                    "O IC de 95% é uma estimativa didática para a média dos pagamentos "
                    "positivos, calculada com t-Student. Como a base observada cobre os "
                    "registros disponíveis do período, o intervalo não é necessário "
                    "para descrever o total observado e não deve ser interpretado como "
                    "previsão de gastos futuros.",
                    className="page-note",
                ),
            ],
            className="page-content",
        ),
        html.Section(
            [
                html.H2("Continue a exploração"),
                html.P(
                    "Cada página aprofunda uma etapa da história e permite chegar a "
                    "categorias, favorecidos ou referências administrativas.",
                    className="section-note",
                ),
                html.Div(
                    [
                        dcc.Link(
                            [html.Span("Evolução das quatro medidas"), html.Strong("Visão Geral →")],
                            href="/visao-geral",
                            className="story-link-card",
                        ),
                        dcc.Link(
                            [html.Span("Elementos e subelementos"), html.Strong("Despesas →")],
                            href="/despesas",
                            className="story-link-card",
                        ),
                        dcc.Link(
                            [html.Span("Favorecidos e contratações"), html.Strong("Favorecidos →")],
                            href="/favorecidos",
                            className="story-link-card",
                        ),
                        dcc.Link(
                            [html.Span("Processos e documentos"), html.Strong("Rastreabilidade →")],
                            href="/rastreabilidade",
                            className="story-link-card",
                        ),
                    ],
                    className="story-link-grid",
                ),
            ],
            className="chart-card",
        ),
    ],
    className="page-content",
)


@callback(
    Output("main-dashboard-years", "value"),
    Output("main-kpi-measure-label", "children"),
    Output("main-kpi-records", "children"),
    Output("main-kpi-paid", "children"),
    Output("main-kpi-positive-count", "children"),
    Output("main-kpi-median", "children"),
    Output("main-kpi-sd", "children"),
    Output("main-filter-summary", "children"),
    Output("main-annual-chart", "figure"),
    Output("main-monthly-chart", "figure"),
    Output("main-boxplot", "figure"),
    Output("main-ci-chart", "figure"),
    Output("main-stats-table", "children"),
    Output("main-story-insights", "children"),
    Input("main-dashboard-years", "value"),
    Input("main-dashboard-measure", "value"),
)
def update_main_dashboard(selected_years, selected_measure):
    requested = {str(year) for year in (selected_years or [])}
    years = [year for year in DASHBOARD_YEARS if year in requested]
    if not years:
        years = list(DASHBOARD_YEARS)
    measure = selected_measure if selected_measure in FINANCIAL_LABELS else "ValorPago"
    measure_label = FINANCIAL_LABELS[measure]

    annual = yearly_totals.loc[
        yearly_totals["Ano"].astype(int).astype(str).isin(years)
    ].copy()
    monthly = monthly_totals.loc[
        monthly_totals["AnoMes"].astype(str).str[:4].isin(years)
    ].copy()
    statistics = filtered_statistics(years)
    summary = selected_statistics_summary(years)

    records_count = annual["Registros"].sum()
    measure_total = annual[measure].sum()
    positive_count = statistics["PagamentosPositivos"].sum()
    median = format_currency(summary["Mediana"]) if summary is not None else "Por ano"
    standard_deviation = (
        format_currency(summary["DesvioPadrao"]) if summary is not None else "Por ano"
    )
    period = " e ".join(years)
    highest_month = monthly.sort_values(measure, ascending=False).iloc[0]
    insights = [
        html.Li(
            f"No recorte {period}, há {format_integer(records_count)} registros e "
            f"a soma registrada de {measure_label} é {format_currency_compact(measure_total)}."
        ),
        html.Li(
            f"O maior total mensal de {measure_label} ocorreu em {highest_month['AnoMes']}: "
            f"{format_currency_compact(highest_month[measure])}."
        ),
    ]
    if summary is not None:
        mean_value = float(summary["Media"])
        median_value = float(summary["Mediana"])
        distribution_text = (
            f"Nos pagamentos positivos, a média ({format_currency(mean_value)}) "
            f"fica acima da mediana ({format_currency(median_value)}), sinal de "
            "assimetria à direita e influência de pagamentos altos."
            if mean_value > median_value
            else (
                f"Nos pagamentos positivos, a média ({format_currency(mean_value)}) "
                f"e a mediana ({format_currency(median_value)}) resumem o centro "
                "da distribuição por perspectivas diferentes."
            )
        )
        insights.append(html.Li(distribution_text))
    if len(years) > 1:
        largest_year = annual.sort_values(measure, ascending=False).iloc[0]
        insights.append(
            html.Li(
                f"Entre os anos filtrados, {int(largest_year['Ano'])} tem a maior "
                f"soma registrada de {measure_label}: "
                f"{format_currency_compact(largest_year[measure])}."
            )
        )

    return (
        years,
        f"Total — {measure_label}",
        format_integer(records_count),
        format_currency_compact(measure_total),
        format_integer(positive_count),
        median,
        standard_deviation,
        f"{period} · {measure_label}",
        annual_financial_comparison_chart(annual, metric=measure),
        financial_evolution_chart(monthly, metric=measure),
        payment_boxplot_chart(statistics),
        payment_mean_ci_chart(statistics),
        statistics_table(statistics),
        insights,
    )
