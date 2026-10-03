import pandas as pd
import pytest

from src.analytics.metrics import (
    financial_quality_summary,
    financial_totals,
    totals_by_month,
    totals_by_unit,
    totals_by_year,
)


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "Ano": [
                2024,
                2024,
                2025,
                2025,
            ],
            "AnoMes": [
                "2024-01",
                "2024-02",
                "2025-01",
                "2025-02",
            ],
            "UnidadeGestora": [
                "UG A",
                "UG A",
                "UG B",
                "UG B",
            ],
            "ValorEmpenho": [
                100.0,
                200.0,
                300.0,
                None,
            ],
            "ValorLiquidado": [
                80.0,
                150.0,
                250.0,
                50.0,
            ],
            "ValorPago": [
                70.0,
                120.0,
                200.0,
                -10.0,
            ],
            "ValorRap": [
                0.0,
                10.0,
                20.0,
                30.0,
            ],
        }
    )


def test_financial_totals(sample_df):
    result = financial_totals(sample_df)

    assert result["ValorEmpenho"] == 600.0
    assert result["ValorLiquidado"] == 530.0
    assert result["ValorPago"] == 380.0
    assert result["ValorRap"] == 60.0


def test_financial_quality_summary(sample_df):
    result = financial_quality_summary(sample_df)

    empenho = result[
        result["Metrica"] == "ValorEmpenho"
    ].iloc[0]

    pago = result[
        result["Metrica"] == "ValorPago"
    ].iloc[0]

    assert empenho["Ausentes"] == 1
    assert pago["Negativos"] == 1


def test_totals_by_year(sample_df):
    result = totals_by_year(sample_df)

    year_2024 = result[
        result["Ano"] == 2024
    ].iloc[0]

    year_2025 = result[
        result["Ano"] == 2025
    ].iloc[0]

    assert year_2024["ValorPago"] == 190.0
    assert year_2025["ValorPago"] == 190.0

    assert year_2024["Registros"] == 2
    assert year_2025["Registros"] == 2


def test_totals_by_month(sample_df):
    result = totals_by_month(sample_df)

    assert len(result) == 4

    assert result.iloc[0]["AnoMes"] == "2024-01"
    assert result.iloc[-1]["AnoMes"] == "2025-02"


def test_totals_by_unit(sample_df):
    result = totals_by_unit(sample_df)

    ug_a = result[
        result["UnidadeGestora"] == "UG A"
    ].iloc[0]

    assert ug_a["ValorPago"] == 190.0
    assert ug_a["ValorEmpenho"] == 300.0
    assert ug_a["Registros"] == 2


def test_missing_financial_column_raises_error(sample_df):
    df = sample_df.drop(
        columns=["ValorPago"]
    )

    with pytest.raises(KeyError):
        financial_totals(df)


def test_non_numeric_financial_column_raises_error(
    sample_df,
):
    df = sample_df.copy()

    df["ValorPago"] = df["ValorPago"].astype(
        "string"
    )

    with pytest.raises(TypeError):
        financial_totals(df)