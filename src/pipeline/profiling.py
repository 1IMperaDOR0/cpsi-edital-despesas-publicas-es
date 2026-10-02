from __future__ import annotations

from collections import Counter

import pandas as pd

from src.pipeline.config import DATE_COLUMNS, FINANCIAL_COLUMNS


TYPED_COLUMNS = DATE_COLUMNS + FINANCIAL_COLUMNS + ["Ano"]


def get_basic_info(df: pd.DataFrame) -> dict:
    return {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows_in_chunk": int(df.duplicated().sum()),
    }


def profile_columns(df: pd.DataFrame) -> pd.DataFrame:
    profile = pd.DataFrame({
        "dtype": df.dtypes.astype(str),
        "non_null": df.notna().sum(),
        "null": df.isna().sum(),
        "null_pct": (df.isna().mean() * 100).round(2),
        "n_unique_in_sample": df.nunique(dropna=True),
    })

    return (
        profile
        .rename_axis("column")
        .reset_index()
        .sort_values(["null_pct", "column"], ascending=[False, True])
    )


class QualityAccumulator:
    """
    Agrega controles de qualidade em streaming.

    Evita carregar o conjunto completo em memoria apenas para calcular
    preenchimento e erros de conversao.
    """

    def __init__(self) -> None:
        self.rows = 0
        self.null_counts: Counter[str] = Counter()
        self.parse_failures: Counter[str] = Counter()
        self.year_mismatch = 0

    def update(
        self,
        raw_df: pd.DataFrame,
        cleaned_df: pd.DataFrame,
        *,
        expected_year: int,
    ) -> None:
        self.rows += len(cleaned_df)

        for column in cleaned_df.columns:
            self.null_counts[column] += int(
                cleaned_df[column].isna().sum()
            )

        for column in TYPED_COLUMNS:
            raw_non_empty = (
                raw_df[column]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
                .notna()
                .sum()
            )
            parsed_non_null = cleaned_df[column].notna().sum()

            self.parse_failures[column] += int(
                max(raw_non_empty - parsed_non_null, 0)
            )

        valid_year = cleaned_df["Ano"].notna()
        self.year_mismatch += int(
            (
                cleaned_df.loc[valid_year, "Ano"]
                != expected_year
            ).sum()
        )

    def to_frame(self) -> pd.DataFrame:
        if self.rows == 0:
            return pd.DataFrame(
                columns=[
                    "column",
                    "null_count",
                    "null_pct",
                    "parse_failures",
                ]
            )

        columns = sorted(self.null_counts)
        rows = []

        for column in columns:
            null_count = self.null_counts[column]
            rows.append({
                "column": column,
                "null_count": null_count,
                "null_pct": round(
                    null_count / self.rows * 100,
                    4,
                ),
                "parse_failures": self.parse_failures[column],
            })

        return pd.DataFrame(rows)
