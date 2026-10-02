import pandas as pd

from src.pipeline.cleaning import clean_chunk


def test_cleaning_converts_types_and_preserves_ids():
    df = pd.DataFrame({
        "Ano": pd.Series(["2024"], dtype="string"),
        "Data": pd.Series(
            ["23/12/2024 00:00:00"],
            dtype="string",
        ),
        "ValorEmpenho": pd.Series(
            ["1.234,5600"],
            dtype="string",
        ),
        "ValorLiquidado": pd.Series(
            ["100,0000"],
            dtype="string",
        ),
        "ValorPago": pd.Series(
            ["88,0000"],
            dtype="string",
        ),
        "ValorRap": pd.Series(
            ["0,0000"],
            dtype="string",
        ),
        "IdFavorecido": pd.Series(
            ["00123"],
            dtype="string",
        ),
        "Favorecido": pd.Series(
            ["  TESTE  "],
            dtype="string",
        ),
    })

    cleaned = clean_chunk(df)

    assert cleaned.loc[0, "Ano"] == 2024
    assert cleaned.loc[0, "Data"].year == 2024
    assert cleaned.loc[0, "ValorEmpenho"] == 1234.56
    assert cleaned.loc[0, "ValorPago"] == 88.0
    assert cleaned.loc[0, "IdFavorecido"] == "00123"
    assert cleaned.loc[0, "Favorecido"] == "TESTE"


def test_cleaning_does_not_impute_missing_values():
    df = pd.DataFrame({
        "Ano": pd.Series(["2024"], dtype="string"),
        "Data": pd.Series(
            ["23/12/2024 00:00:00"],
            dtype="string",
        ),
        "ValorEmpenho": pd.Series([pd.NA], dtype="string"),
        "ValorLiquidado": pd.Series([pd.NA], dtype="string"),
        "ValorPago": pd.Series([pd.NA], dtype="string"),
        "ValorRap": pd.Series([pd.NA], dtype="string"),
        "Favorecido": pd.Series([pd.NA], dtype="string"),
    })

    cleaned = clean_chunk(df)

    assert cleaned["ValorPago"].isna().all()
    assert cleaned["Favorecido"].isna().all()
