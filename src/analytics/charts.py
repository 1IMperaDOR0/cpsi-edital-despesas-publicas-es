from __future__ import annotations

from textwrap import shorten

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


FINANCIAL_LABELS = {
    "ValorEmpenho": "Empenhado",
    "ValorLiquidado": "Liquidado",
    "ValorPago": "Pago",
    "ValorRap": "Restos a pagar",
}
FINANCIAL_COLORS = {
    "Empenhado": "#2563eb",
    "Liquidado": "#0f766e",
    "Pago": "#f59e0b",
    "Restos a pagar": "#8b5cf6",
}
PRIMARY_COLOR = "#0f766e"


def _style_figure(
    figure: go.Figure,
    *,
    height: int = 440,
    top_margin: int = 38,
    legend_y: float = 1.02,
) -> go.Figure:
    figure.update_layout(
        template="plotly_white",
        height=height,
        # Fundo transparente: o cartão (style.css) define a cor no tema claro/escuro.
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin={"l": 24, "r": 24, "t": top_margin, "b": 30},
        font={"family": "Inter, Arial, sans-serif", "color": "#1f2937", "size": 12},
        hoverlabel={"bgcolor": "#111827", "font_color": "#ffffff"},
        legend={"orientation": "h", "yanchor": "bottom", "y": legend_y, "x": 0},
    )
    figure.update_xaxes(showgrid=False, automargin=True)
    figure.update_yaxes(gridcolor="#e5e7eb", zeroline=False, automargin=True)
    return figure


def financial_evolution_chart(
    monthly_totals: pd.DataFrame,
    metric: str | None = None,
) -> go.Figure:
    """Mostra a evolução mensal da medida escolhida ou de todas as medidas."""
    selected_columns = (
        [metric] if metric in FINANCIAL_LABELS else list(FINANCIAL_LABELS)
    )
    columns = ["AnoMes", *selected_columns]
    data = monthly_totals[columns].copy()
    data["Ano"] = data["AnoMes"].astype("string").str[:4]
    data = data.melt(
        id_vars=["AnoMes", "Ano"],
        value_vars=selected_columns,
        var_name="Metrica",
        value_name="Valor",
    )
    data["Metrica"] = data["Metrica"].map(FINANCIAL_LABELS)

    figure = px.line(
        data,
        x="AnoMes",
        y="Valor",
        color="Metrica",
        line_dash="Ano",
        markers=True,
        color_discrete_map=FINANCIAL_COLORS,
        category_orders={"Ano": ["2024", "2025"]},
        labels={"AnoMes": "Mês", "Valor": "Valor (R$)", "Metrica": "Medida", "Ano": "Ano"},
    )
    figure.update_traces(
        hovertemplate="%{x}<br>%{fullData.name}<br>R$ %{y:,.2f}<extra></extra>"
    )
    figure.update_yaxes(tickprefix="R$ ", tickformat="~s")
    figure.update_xaxes(type="category", tickangle=-35)
    figure.update_layout(hovermode="x unified", legend_title_text="")
    figure.update_yaxes(title_text="Valor (R$)")
    return _style_figure(figure, height=480, top_margin=78, legend_y=1.08)


def annual_financial_comparison_chart(
    yearly_totals: pd.DataFrame,
    metric: str | None = None,
) -> go.Figure:
    """Compara a medida escolhida ou todas as medidas entre os anos disponíveis."""
    selected_columns = (
        [metric] if metric in FINANCIAL_LABELS else list(FINANCIAL_LABELS)
    )
    data = yearly_totals[["Ano", *selected_columns]].copy()
    data["Ano"] = data["Ano"].astype("string")
    data = data.melt(
        id_vars="Ano",
        value_vars=selected_columns,
        var_name="Metrica",
        value_name="Valor",
    )
    data["Metrica"] = data["Metrica"].map(FINANCIAL_LABELS)

    figure = px.bar(
        data,
        x="Ano",
        y="Valor",
        color="Metrica",
        barmode="group",
        color_discrete_map=FINANCIAL_COLORS,
        labels={"Ano": "Ano", "Valor": "Valor (R$)", "Metrica": "Medida"},
    )
    figure.update_traces(hovertemplate="%{fullData.name}<br>R$ %{y:,.2f}<extra></extra>")
    figure.update_yaxes(tickprefix="R$ ", tickformat="~s")
    figure.update_layout(barmode="group")
    return _style_figure(figure, height=400, top_margin=68, legend_y=1.05)


def _payment_ranking_chart(
    data: pd.DataFrame,
    *,
    label_column: str,
    top_n: int,
    extra_hover_columns: tuple[str, ...] = (),
    height_per_row: int = 34,
) -> go.Figure:
    columns = [label_column, "ValorPago", "Registros", *extra_hover_columns]
    ranking = (
        data[columns]
        .nlargest(top_n, "ValorPago")
        .sort_values("ValorPago", ascending=True)
        .copy()
    )
    axis_label = "__Rotulo"
    ranking[axis_label] = ranking[label_column].map(
        lambda value: shorten(str(value), width=48, placeholder="…")
    )

    figure = px.bar(
        ranking,
        x="ValorPago",
        y=axis_label,
        orientation="h",
        custom_data=[label_column, "Registros", *extra_hover_columns],
        labels={axis_label: "", "ValorPago": "Valor pago (R$)"},
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    hover_lines = [
        "%{customdata[0]}",
        "R$ %{x:,.2f}",
        "Registros: %{customdata[1]:,}",
    ]
    hover_lines.extend(
        f"{column}: %{{customdata[{index}]:,}}"
        for index, column in enumerate(extra_hover_columns, start=2)
    )
    figure.update_traces(
        hovertemplate="<br>".join(hover_lines) + "<extra></extra>"
    )
    figure.update_xaxes(tickprefix="R$ ", tickformat="~s", tickangle=0)
    figure.update_yaxes(title_text=None)
    figure.update_layout(
        showlegend=False,
        yaxis={"categoryorder": "total ascending", "automargin": True},
    )
    return _style_figure(
        figure,
        height=max(360, min(760, len(ranking) * height_per_row + 110)),
    )


def expenses_by_element_chart(elements: pd.DataFrame) -> go.Figure:
    return _payment_ranking_chart(
        elements,
        label_column="ElementoDespesa",
        top_n=15,
    )


def expenses_by_subelement_chart(subelements: pd.DataFrame) -> go.Figure:
    data = subelements.copy()
    data["Subelemento"] = (
        data["SubelementoDespesa"].astype("string")
        + " — "
        + data["ElementoDespesa"].astype("string")
    )
    return _payment_ranking_chart(
        data,
        label_column="Subelemento",
        top_n=15,
    )


def beneficiaries_chart(beneficiaries: pd.DataFrame) -> go.Figure:
    return _payment_ranking_chart(
        beneficiaries,
        label_column="Favorecido",
        top_n=15,
    )


def procurement_types_chart(procurement_types: pd.DataFrame) -> go.Figure:
    return _payment_ranking_chart(
        procurement_types,
        label_column="TipoLicitacao",
        top_n=20,
        height_per_row=30,
    )


def processes_chart(processes: pd.DataFrame) -> go.Figure:
    data = processes.rename(columns={
        "ReferenciasDocumento": "Registros com documento",
        "ReferenciasDocumentoEmpenho": "Registros com documento de empenho",
    })
    return _payment_ranking_chart(
        data,
        label_column="CodigoProcesso",
        top_n=15,
        extra_hover_columns=(
            "Registros com documento",
            "Registros com documento de empenho",
        ),
    )


def traceability_coverage_chart(quality_summary: pd.DataFrame) -> go.Figure:
    field_labels = {
        "CodigoProcesso": "Código do processo",
        "Documento": "Documento",
        "DocumentoEmpenho": "Documento de empenho",
        "Id": "ID do registro",
    }
    data = quality_summary.loc[
        quality_summary["column"].isin(field_labels)
    ].copy()
    data["Cobertura"] = (100 - pd.to_numeric(data["null_pct"])).clip(0, 100)
    data["Campo"] = data["column"].map(field_labels)
    data = data.sort_values("Cobertura", ascending=True)

    figure = px.bar(
        data,
        x="Cobertura",
        y="Campo",
        orientation="h",
        text=data["Cobertura"].map(lambda value: f"{value:.2f}%"),
        labels={"Cobertura": "Registros preenchidos (%)", "Campo": "Campo"},
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    figure.update_traces(
        textposition="inside",
        textfont_color="#ffffff",
        hovertemplate="%{y}<br>%{x:.2f}% dos registros preenchidos<extra></extra>",
    )
    figure.update_xaxes(range=[0, 100], ticksuffix="%", dtick=20)
    figure.update_yaxes(title_text=None)
    figure.update_layout(
        showlegend=False,
    )
    return _style_figure(figure, height=360)


def beneficiary_pareto_chart(concentration: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Pareto: valor pago por favorecido e participação acumulada."""
    from plotly.subplots import make_subplots

    data = concentration.head(top_n).copy()
    data = data.sort_values("ValorPagoPositivo", ascending=False)
    data["Rotulo"] = data["Favorecido"].map(
        lambda value: shorten(str(value), width=36, placeholder="…")
    )

    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(
        go.Bar(
            x=data["Rotulo"],
            y=data["ValorPagoPositivo"],
            name="Valor pago",
            customdata=data[["Favorecido", "ParticipacaoPct"]],
            hovertemplate=(
                "%{customdata[0]}<br>"
                "Valor pago: R$ %{y:,.2f}<br>"
                "Participação: %{customdata[1]:.2f}%<extra></extra>"
            ),
        ),
        secondary_y=False,
    )
    figure.add_trace(
        go.Scatter(
            x=data["Rotulo"],
            y=data["ParticipacaoAcumuladaPct"],
            name="Participação acumulada",
            mode="lines+markers",
            hovertemplate="Acumulado: %{y:.2f}%<extra></extra>",
        ),
        secondary_y=True,
    )

    figure.update_xaxes(title_text="Favorecido", tickangle=-35)
    figure.update_yaxes(
        title_text="Valor pago (R$)",
        tickprefix="R$ ",
        tickformat="~s",
        secondary_y=False,
    )
    figure.update_yaxes(
        title_text="Participação acumulada (%)",
        range=[0, 100],
        ticksuffix="%",
        secondary_y=True,
    )
    figure.update_layout(
        hovermode="x unified",
        legend_title_text="",
    )
    return _style_figure(figure, height=500, top_margin=78, legend_y=1.08)


def payment_boxplot_chart(statistics: pd.DataFrame) -> go.Figure:
    """Boxplot pré-calculado de ValorPago positivo, comparando cada ano separadamente."""
    data = (
        statistics.loc[statistics["Escopo"] != "Todos"]
        .copy()
        .sort_values("Ano")
    )
    data["AnoLabel"] = data["Ano"].astype("Int64").astype("string")

    # Em boxplots com quartis pré-calculados, o eixo categórico precisa ser
    # informado explicitamente. Sem `x`, o Plotly coloca todas as caixas na
    # mesma posição (categoria 0), sobrepondo 2024 e 2025.
    customdata = [
        [int(row["OutliersSuperiores"]), float(row["ProbOutlierSuperior"]) * 100]
        for _, row in data.iterrows()
    ]

    figure = go.Figure(
        go.Box(
            x=data["AnoLabel"].tolist(),
            q1=data["Q1"].tolist(),
            median=data["Mediana"].tolist(),
            q3=data["Q3"].tolist(),
            lowerfence=data["LimiteInferiorBoxplot"].tolist(),
            upperfence=data["LimiteSuperiorBoxplot"].tolist(),
            mean=data["Media"].tolist(),
            sd=data["DesvioPadrao"].tolist(),
            boxpoints=False,
            customdata=customdata,
            hovertemplate=(
                "Ano: %{x}<br>"
                "Q1: R$ %{q1:,.2f}<br>"
                "Mediana: R$ %{median:,.2f}<br>"
                "Q3: R$ %{q3:,.2f}<br>"
                "Limite superior (1,5×IQR): R$ %{upperfence:,.2f}<br>"
                "Outliers superiores: %{customdata[0]:,} (%{customdata[1]:.2f}%)"
                "<extra></extra>"
            ),
            name="ValorPago",
        )
    )

    figure.update_xaxes(
        title_text="Ano",
        type="category",
        categoryorder="array",
        categoryarray=data["AnoLabel"].tolist(),
    )
    figure.update_yaxes(
        title_text="Valor pago positivo (R$)",
        tickprefix="R$ ",
        tickformat="~s",
    )
    figure.update_layout(showlegend=False)
    return _style_figure(figure, height=440)


def payment_mean_ci_chart(statistics: pd.DataFrame) -> go.Figure:
    """Média de ValorPago positivo e IC bilateral de 95% por ano."""
    data = statistics.loc[statistics["Escopo"] != "Todos"].copy().sort_values("Ano")
    data["AnoLabel"] = data["Ano"].astype("Int64").astype("string")
    data["ErroSuperior"] = data["IC95Superior"] - data["Media"]
    data["ErroInferior"] = data["Media"] - data["IC95Inferior"]

    figure = go.Figure(
        go.Scatter(
            x=data["AnoLabel"],
            y=data["Media"],
            mode="markers+lines",
            error_y={
                "type": "data",
                "symmetric": False,
                "array": data["ErroSuperior"],
                "arrayminus": data["ErroInferior"],
                "visible": True,
                "thickness": 2,
                "width": 8,
            },
            customdata=data[["IC95Inferior", "IC95Superior", "PagamentosPositivos"]],
            hovertemplate=(
                "Ano %{x}<br>"
                "Média: R$ %{y:,.2f}<br>"
                "IC 95%: R$ %{customdata[0]:,.2f} a R$ %{customdata[1]:,.2f}<br>"
                "n positivo: %{customdata[2]:,}<extra></extra>"
            ),
            name="Média e IC 95%",
        )
    )
    figure.update_xaxes(title_text="Ano", type="category")
    figure.update_yaxes(
        title_text="Média do valor pago positivo (R$)",
        tickprefix="R$ ",
        tickformat="~s",
    )
    figure.update_layout(showlegend=False)
    return _style_figure(figure, height=420)


def probability_chart(
    statistics: pd.DataFrame,
    concentration_summary: pd.DataFrame,
) -> go.Figure:
    """Probabilidades empíricas calculadas por frequência relativa."""
    overall = statistics.loc[statistics["Escopo"] == "Todos"].iloc[0]
    concentration = concentration_summary.iloc[0]
    data = pd.DataFrame(
        {
            "Evento": [
                "Registro tem pagamento positivo",
                "Pagamento positivo é outlier superior",
                "Registro positivo pertence ao Top 10",
            ],
            "Probabilidade": [
                overall["ProbPagamentoPositivo"] * 100,
                overall["ProbOutlierSuperior"] * 100,
                concentration["TopNParticipacaoRegistrosPct"],
            ],
        }
    )

    figure = px.bar(
        data,
        x="Probabilidade",
        y="Evento",
        orientation="h",
        text=data["Probabilidade"].map(lambda value: f"{value:.2f}%"),
        labels={"Probabilidade": "Probabilidade empírica (%)", "Evento": ""},
        color_discrete_sequence=[PRIMARY_COLOR],
    )
    figure.update_traces(
        textposition="outside",
        hovertemplate="%{y}<br>%{x:.2f}%<extra></extra>",
    )
    figure.update_xaxes(range=[0, 100], ticksuffix="%")
    figure.update_layout(showlegend=False)
    return _style_figure(figure, height=360)
