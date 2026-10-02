import pandas as pd

from src.pipeline.config import CURATED_SOURCE_COLUMNS
from src.pipeline.transformations import transform_chunk


def test_transform_adds_time_and_lineage_columns():
    data = {
        column: pd.Series([pd.NA], dtype="string")
        for column in CURATED_SOURCE_COLUMNS
    }
    df = pd.DataFrame(data)

    df["Ano"] = pd.Series([2024], dtype="Int64")
    df["Data"] = pd.to_datetime(["2024-12-23"])
    for column in [
        "ValorEmpenho",
        "ValorLiquidado",
        "ValorPago",
        "ValorRap",
    ]:
        df[column] = pd.Series([0.0], dtype="Float64")

    transformed = transform_chunk(
        df,
        source_file="fonte.zip",
        source_year=2024,
        source_part=1,
        source_row_start=2,
    )

    assert transformed.loc[0, "Mes"] == 12
    assert transformed.loc[0, "AnoMes"] == "2024-12"
    assert transformed.loc[0, "_source_file"] == "fonte.zip"
    assert transformed.loc[0, "_source_row"] == 2


def test_curated_output_excludes_personal_identifier():
    assert "CpfCnpjNis" not in CURATED_SOURCE_COLUMNS
