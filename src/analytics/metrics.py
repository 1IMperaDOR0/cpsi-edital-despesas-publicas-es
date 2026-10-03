from collections.abc import Iterable
import math

import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from scipy import stats


FINANCIAL_COLUMNS = (
    "ValorEmpenho",
    "ValorLiquidado",
    "ValorPago",
    "ValorRap",
)

VARIABLE_CATALOG = pd.DataFrame(
    [
        {
            "Variavel": "Ano",
            "Natureza": "Quantitativa discreta (temporal)",
            "Escala": "Intervalar",
            "Papel": "Recorte temporal",
            "Uso": "Comparar a distribuição dos pagamentos entre 2024 e 2025.",
        },
        {
            "Variavel": "ValorPago",
            "Natureza": "Quantitativa contínua",
            "Escala": "Razão",
            "Papel": "Medida principal",
            "Uso": "Calcular estatísticas, boxplot, probabilidade e intervalo de confiança.",
        },
        {
            "Variavel": "Favorecido",
            "Natureza": "Qualitativa nominal",
            "Escala": "Nominal",
            "Papel": "Dimensão",
            "Uso": "Identificar para quem os recursos foram destinados.",
        },
        {
            "Variavel": "TipoFavorecido",
            "Natureza": "Qualitativa nominal codificada",
            "Escala": "Nominal",
            "Papel": "Dimensão de contexto",
            "Uso": "Distinguir categorias de favorecidos sem assumir um significado não documentado para cada código.",
        },
        {
            "Variavel": "TipoLicitacao",
            "Natureza": "Qualitativa nominal",
            "Escala": "Nominal",
            "Papel": "Dimensão",
            "Uso": "Comparar modalidades/formas de contratação associadas aos pagamentos.",
        },
    ]
)


def _require_columns(
    df: pd.DataFrame,
    columns: Iterable[str],
) -> None:
    """Verifica se todas as colunas necessárias existem no DataFrame."""

    missing = [
        column
        for column in columns
        if column not in df.columns
    ]

    if missing:
        raise KeyError(
            "Colunas obrigatórias ausentes: "
            + ", ".join(missing)
        )


def _validate_financial_types(
    df: pd.DataFrame,
) -> None:
    """
    Garante que as medidas financeiras entregues pelo pipeline
    estejam em formato numérico.

    A camada analítica não deve corrigir silenciosamente problemas
    de tipagem que deveriam ter sido resolvidos pelo pipeline.
    """

    _require_columns(df, FINANCIAL_COLUMNS)

    invalid = [
        column
        for column in FINANCIAL_COLUMNS
        if not is_numeric_dtype(df[column])
    ]

    if invalid:
        raise TypeError(
            "Colunas financeiras não numéricas: "
            + ", ".join(invalid)
        )


def financial_totals(
    df: pd.DataFrame,
) -> pd.Series:
    """
    Calcula os totais financeiros básicos.

    Observações:
    - valores nulos são ignorados pela soma;
    - valores negativos são preservados;
    - nenhuma deduplicação é realizada;
    - as métricas devem ser validadas semanticamente
      antes de serem tratadas como KPIs.
    """

    _validate_financial_types(df)

    return df[list(FINANCIAL_COLUMNS)].sum(
        skipna=True,
        min_count=1,
    )


def financial_quality_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Produz informações de qualidade das quatro medidas financeiras.
    """

    _validate_financial_types(df)

    rows = []

    for column in FINANCIAL_COLUMNS:
        series = df[column]

        rows.append(
            {
                "Metrica": column,
                "Registros": len(series),
                "Preenchidos": int(series.notna().sum()),
                "Ausentes": int(series.isna().sum()),
                "Negativos": int((series < 0).sum()),
                "Zeros": int((series == 0).sum()),
                "Total": series.sum(
                    skipna=True,
                    min_count=1,
                ),
            }
        )

    return pd.DataFrame(rows)


def totals_by_dimension(
    df: pd.DataFrame,
    dimension: str,
) -> pd.DataFrame:
    """
    Calcula as quatro medidas financeiras agrupadas
    por uma dimensão.

    Exemplos de dimensão:
    - Ano
    - AnoMes
    - UnidadeGestora
    - ElementoDespesa
    """

    _require_columns(
        df,
        [dimension, *FINANCIAL_COLUMNS],
    )

    _validate_financial_types(df)

    grouped = df.groupby(
        dimension,
        dropna=False,
        observed=False,
    )

    totals = (
        grouped[list(FINANCIAL_COLUMNS)]
        .sum(min_count=1)
        .reset_index()
    )

    record_counts = (
        grouped
        .size()
        .reset_index(name="Registros")
    )

    result = record_counts.merge(
        totals,
        on=dimension,
        how="left",
    )

    return result


def totals_by_year(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Totais financeiros agrupados por ano."""

    return totals_by_dimension(
        df,
        "Ano",
    ).sort_values("Ano").reset_index(drop=True)


def totals_by_month(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Totais financeiros agrupados por ano/mês."""

    return totals_by_dimension(
        df,
        "AnoMes",
    ).sort_values("AnoMes").reset_index(drop=True)


def totals_by_unit(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Totais financeiros agrupados por Unidade Gestora."""

    result = totals_by_dimension(
        df,
        "UnidadeGestora",
    )

    return result.sort_values(
        "ValorPago",
        ascending=False,
        na_position="last",
    ).reset_index(drop=True)


def _as_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").dropna().astype(float)


def confidence_interval_mean(
    values: Iterable[float] | pd.Series,
    confidence: float = 0.95,
) -> tuple[float, float, float]:
    """IC bilateral para a média usando t-Student e desvio amostral."""

    series = _as_numeric(pd.Series(values))
    n = len(series)
    if n == 0:
        return (math.nan, math.nan, math.nan)

    mean = float(series.mean())
    if n == 1:
        return (mean, mean, mean)

    sem = float(stats.sem(series, nan_policy="omit"))
    if not np.isfinite(sem) or sem == 0:
        return (mean, mean, mean)

    lower, upper = stats.t.interval(
        confidence=confidence,
        df=n - 1,
        loc=mean,
        scale=sem,
    )
    return (mean, float(lower), float(upper))


def descriptive_payment_statistics(
    values: Iterable[float] | pd.Series,
    *,
    total_records: int | None = None,
    confidence: float = 0.95,
) -> dict[str, float | int]:
    """Estatística descritiva, boxplot, probabilidade empírica e IC para ValorPago > 0."""

    series = _as_numeric(pd.Series(values))
    positive = series[series > 0]

    if total_records is None:
        total_records = len(series)

    n = len(positive)
    if n == 0:
        return {
            "RegistrosTotais": int(total_records),
            "PagamentosPositivos": 0,
            "ProbPagamentoPositivo": 0.0,
            "TotalPagoPositivo": 0.0,
            "Media": math.nan,
            "Mediana": math.nan,
            "DesvioPadrao": math.nan,
            "Minimo": math.nan,
            "Q1": math.nan,
            "Q3": math.nan,
            "IQR": math.nan,
            "LimiteInferiorBoxplot": math.nan,
            "LimiteSuperiorBoxplot": math.nan,
            "OutliersSuperiores": 0,
            "ProbOutlierSuperior": math.nan,
            "Maximo": math.nan,
            "IC95Inferior": math.nan,
            "IC95Superior": math.nan,
        }

    q1 = float(positive.quantile(0.25))
    median = float(positive.quantile(0.50))
    q3 = float(positive.quantile(0.75))
    iqr = q3 - q1
    lower_fence = max(0.0, q1 - 1.5 * iqr)
    upper_fence = q3 + 1.5 * iqr
    outliers_upper = int((positive > upper_fence).sum())
    mean, ci_lower, ci_upper = confidence_interval_mean(
        positive,
        confidence=confidence,
    )

    return {
        "RegistrosTotais": int(total_records),
        "PagamentosPositivos": int(n),
        "ProbPagamentoPositivo": float(n / total_records) if total_records else math.nan,
        "TotalPagoPositivo": float(positive.sum()),
        "Media": mean,
        "Mediana": median,
        "DesvioPadrao": float(positive.std(ddof=1)) if n > 1 else 0.0,
        "Minimo": float(positive.min()),
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "LimiteInferiorBoxplot": lower_fence,
        "LimiteSuperiorBoxplot": upper_fence,
        "OutliersSuperiores": outliers_upper,
        "ProbOutlierSuperior": float(outliers_upper / n),
        "Maximo": float(positive.max()),
        "IC95Inferior": ci_lower,
        "IC95Superior": ci_upper,
    }


def beneficiary_concentration(
    frame: pd.DataFrame,
    *,
    top_n: int = 10,
) -> tuple[pd.DataFrame, dict[str, float | int]]:
    """Mede concentração monetária entre favorecidos usando pagamentos positivos."""

    required = {"Favorecido", "ValorPago"}
    missing = required - set(frame.columns)
    if missing:
        raise KeyError("Colunas ausentes: " + ", ".join(sorted(missing)))

    data = frame[["Favorecido", "ValorPago"]].copy()
    data["ValorPago"] = pd.to_numeric(data["ValorPago"], errors="coerce")
    data = data[data["ValorPago"] > 0]
    data["Favorecido"] = (
        data["Favorecido"]
        .astype("string")
        .str.strip()
        .fillna("Não informado")
    )

    grouped = (
        data.groupby("Favorecido", dropna=False)
        .agg(
            ValorPagoPositivo=("ValorPago", "sum"),
            RegistrosPositivos=("ValorPago", "size"),
        )
        .reset_index()
        .sort_values("ValorPagoPositivo", ascending=False)
        .reset_index(drop=True)
    )

    total_value = float(grouped["ValorPagoPositivo"].sum())
    total_records = int(grouped["RegistrosPositivos"].sum())

    if total_value > 0:
        grouped["ParticipacaoPct"] = grouped["ValorPagoPositivo"] / total_value * 100
        grouped["ParticipacaoAcumuladaPct"] = grouped["ParticipacaoPct"].cumsum()
    else:
        grouped["ParticipacaoPct"] = 0.0
        grouped["ParticipacaoAcumuladaPct"] = 0.0

    top = grouped.head(top_n)
    top_value = float(top["ValorPagoPositivo"].sum())
    top_records = int(top["RegistrosPositivos"].sum())

    summary = {
        "Favorecidos": int(len(grouped)),
        "TotalPagoPositivo": total_value,
        "TopN": int(top_n),
        "TopNParticipacaoValorPct": float(top_value / total_value * 100) if total_value else 0.0,
        "TopNParticipacaoRegistrosPct": float(top_records / total_records * 100) if total_records else 0.0,
    }
    return grouped, summary
