import pandas as pd

from src.pipeline.profiling import QualityAccumulator


def test_quality_accumulator_detects_parse_failure():
    raw = pd.DataFrame({
        "Ano": pd.Series(["2024"], dtype="string"),
        "Data": pd.Series(
            ["data-invalida"],
            dtype="string",
        ),
        "ValorEmpenho": pd.Series(
            ["10,00"],
            dtype="string",
        ),
        "ValorLiquidado": pd.Series(
            ["20,00"],
            dtype="string",
        ),
        "ValorPago": pd.Series(
            ["valor-invalido"],
            dtype="string",
        ),
        "ValorRap": pd.Series(
            ["0,00"],
            dtype="string",
        ),
    })

    cleaned = raw.copy()
    cleaned["Ano"] = pd.Series([2024], dtype="Int64")
    cleaned["Data"] = pd.to_datetime([pd.NaT])
    cleaned["ValorEmpenho"] = pd.Series([10.0], dtype="Float64")
    cleaned["ValorLiquidado"] = pd.Series([20.0], dtype="Float64")
    cleaned["ValorPago"] = pd.Series([pd.NA], dtype="Float64")
    cleaned["ValorRap"] = pd.Series([0.0], dtype="Float64")

    quality = QualityAccumulator()
    quality.update(raw, cleaned, expected_year=2024)

    assert quality.parse_failures["Data"] == 1
    assert quality.parse_failures["ValorPago"] == 1
