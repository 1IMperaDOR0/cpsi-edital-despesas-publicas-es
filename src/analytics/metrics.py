from collections.abc import Iterable

import pandas as pd
from pandas.api.types import is_numeric_dtype


FINANCIAL_COLUMNS = (
    "ValorEmpenho",
    "ValorLiquidado",
    "ValorPago",
    "ValorRap",
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