from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.pipeline.config import EXPECTED_SOURCE_COLUMNS


@pytest.fixture
def source_rows() -> list[dict[str, str]]:
    base = {column: "" for column in EXPECTED_SOURCE_COLUMNS}

    row1 = base.copy()
    row1.update({
        "Ano": "2024",
        "Data": "23/12/2024 00:00:00",
        "ValorEmpenho": "1.234,5600",
        "ValorLiquidado": "100,0000",
        "ValorPago": "88,0000",
        "ValorRap": "0,0000",
        "CpfCnpjNis": "###.743.147-##",
        "Favorecido": "  TESTE FORNECEDOR  ",
        "IdFavorecido": "00123",
        "TipoLicitacao": " PREGÃO ",
        "UnidadeGestora": "UG TESTE",
        "ElementoDespesa": "MATERIAL DE CONSUMO",
        "SubelementoDespesa": "PAPEL",
        "NumeroProcesso": "2024-ABC",
        "Id": "1",
    })

    row2 = base.copy()
    row2.update({
        "Ano": "2024",
        "Data": "24/12/2024 00:00:00",
        "ValorEmpenho": "0,0000",
        "ValorLiquidado": "",
        "ValorPago": "10,5000",
        "ValorRap": "0,0000",
        "Favorecido": "OUTRO FORNECEDOR",
        "IdFavorecido": "00456",
        "TipoLicitacao": "DISPENSA DE LICITAÇÃO",
        "UnidadeGestora": "UG TESTE",
        "ElementoDespesa": "SERVIÇOS",
        "SubelementoDespesa": "",
        "NumeroProcesso": "",
        "Id": "2",
    })

    return [row1, row2]


@pytest.fixture
def raw_source_dir(tmp_path: Path, source_rows: list[dict[str, str]]) -> Path:
    raw_dir = tmp_path / "data"
    raw_dir.mkdir()

    for year in (2024, 2025):
        for part in range(1, 5):
            csv_path = raw_dir / f"despesas_es_{year}_completo_parte_{part:02d}.csv"

            rows = []
            for source in source_rows:
                row = source.copy()
                row["Ano"] = str(year)
                row["Data"] = row["Data"].replace("2024", str(year), 1)
                rows.append(row)

            with csv_path.open(
                "w",
                encoding="utf-8-sig",
                newline="",
            ) as handle:
                writer = csv.DictWriter(
                    handle,
                    fieldnames=EXPECTED_SOURCE_COLUMNS,
                    delimiter=";",
                )
                writer.writeheader()
                writer.writerows(rows)

    return raw_dir
