from __future__ import annotations

import pandas as pd

from src.pipeline.config import CURATED_OUTPUT_COLUMNS


def add_time_dimensions(df: pd.DataFrame) -> pd.DataFrame:
    transformed = df.copy()

    transformed["Mes"] = transformed["Data"].dt.month.astype("Int64")
    transformed["AnoMes"] = (
        transformed["Data"]
        .dt.to_period("M")
        .astype("string")
    )

    return transformed


def add_lineage(
    df: pd.DataFrame,
    *,
    source_file: str,
    source_year: int,
    source_part: int,
    source_row_start: int,
) -> pd.DataFrame:
    transformed = df.copy()

    transformed["_source_file"] = source_file
    transformed["_source_year"] = source_year
    transformed["_source_part"] = source_part

    transformed["_source_row"] = pd.Series(
        range(
            source_row_start,
            source_row_start + len(transformed),
        ),
        index=transformed.index,
        dtype="Int64",
    )

    return transformed


def transform_chunk(
    df: pd.DataFrame,
    *,
    source_file: str,
    source_year: int,
    source_part: int,
    source_row_start: int,
) -> pd.DataFrame:
    """
    Adiciona apenas dimensoes analiticas seguras e rastreabilidade.

    Regras financeiras derivadas (por exemplo, taxa de execucao) ficam
    fora desta primeira versao ate que a semantica dos lancamentos seja
    validada pela equipe de analise.
    """
    transformed = add_time_dimensions(df)
    transformed = add_lineage(
        transformed,
        source_file=source_file,
        source_year=source_year,
        source_part=source_part,
        source_row_start=source_row_start,
    )

    return transformed[CURATED_OUTPUT_COLUMNS].copy()
