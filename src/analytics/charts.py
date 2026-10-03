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
        margin={"l": 24, "r": 24, "t": top_margin, "b": 30},
        font={"family": "Arial, sans-serif", "color": "#1f2937", "size": 12},
        hoverlabel={"bgcolor": "#111827", "font_color": "#ffffff"},
        legend={"orientation": "h", "yanchor": "bottom", "y": legend_y, "x": 0},
    )
    figure.update_xaxes(showgrid=False, automargin=True)
    figure.update_yaxes(gridcolor="#e5e7eb", zeroline=False, automargin=True)
    return figure


def financial_evolution_chart(monthly_totals: pd.DataFrame) -> go.Figure:
    """Mostra a evolução mensal das quatro medidas financeiras em 2024 e 2025."""
    columns = ["AnoMes", *FINANCIAL_LABELS]
    data = monthly_totals[columns].copy()
    data["Ano"] = data["AnoMes"].astype("string").str[:4]
    data = data.melt(
        id_vars=["AnoMes", "Ano"],
        value_vars=list(FINANCIAL_LABELS),
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


def annual_financial_comparison_chart(yearly_totals: pd.DataFrame) -> go.Figure:
    """Compara os totais das medidas financeiras entre os anos disponíveis."""
    data = yearly_totals[["Ano", *FINANCIAL_LABELS]].copy()
    data["Ano"] = data["Ano"].astype("string")
    data = data.melt(
        id_vars="Ano",
        value_vars=list(FINANCIAL_LABELS),
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
