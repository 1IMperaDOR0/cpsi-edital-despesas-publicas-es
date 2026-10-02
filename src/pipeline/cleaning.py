from __future__ import annotations

import pandas as pd

from src.pipeline.config import FINANCIAL_COLUMNS


def _strip_string_series(series: pd.Series) -> pd.Series:
    result = series.astype("string").str.strip()
    return result.mask(result.eq(""), pd.NA)


def normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove espacos nas bordas e transforma strings vazias em ausentes.

    O conteudo e a caixa dos textos sao preservados; o pipeline nao
    corrige categorias de negocio sem evidencia.
    """
    cleaned = df.copy()

    for column in cleaned.columns:
        if column in FINANCIAL_COLUMNS or column == "Data":
            continue

        if pd.api.types.is_string_dtype(cleaned[column].dtype):
            cleaned[column] = _strip_string_series(cleaned[column])

    return cleaned


def parse_brazilian_number(series: pd.Series) -> pd.Series:
    """
    Converte numero no formato pt-BR para float.

    Exemplos:
    - 88,0000 -> 88.0
    - 1.234,56 -> 1234.56
    """
    text = _strip_string_series(series)
    normalized = (
        text
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )

    return pd.to_numeric(normalized, errors="coerce").astype("Float64")


def parse_types(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    cleaned["Ano"] = pd.to_numeric(
        _strip_string_series(cleaned["Ano"]),
        errors="coerce",
    ).astype("Int64")

    cleaned["Data"] = pd.to_datetime(
        _strip_string_series(cleaned["Data"]),
        format="%d/%m/%Y %H:%M:%S",
        errors="coerce",
    )

    for column in FINANCIAL_COLUMNS:
        cleaned[column] = parse_brazilian_number(cleaned[column])

    return cleaned


def clean_chunk(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpeza conservadora da fonte.

    Importante:
    - nao remove linhas;
    - nao deduplica silenciosamente;
    - nao imputa valores ausentes;
    - nao altera categorias de negocio.
    """
    cleaned = normalize_text_columns(df)
    cleaned = parse_types(cleaned)
    return cleaned
