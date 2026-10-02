from __future__ import annotations

import os
from pathlib import Path

import pytest

from src.pipeline.cleaning import clean_chunk
from src.pipeline.config import CURATED_SOURCE_COLUMNS, DEFAULT_RAW_DIR
from src.pipeline.data_loader import (
    discover_sources,
    iter_raw_chunks,
    validate_source_inventory,
    validate_source_schema,
)
from src.pipeline.transformations import transform_chunk


RAW_ENV = "DESPESAS_RAW_DIR"


def _real_raw_dir() -> Path:
    return Path(os.environ.get(RAW_ENV, DEFAULT_RAW_DIR))


def _skip_if_missing(raw_dir: Path) -> None:
    if not raw_dir.exists() or not list(raw_dir.glob("despesas_es_*_completo_parte_*.csv")):
        pytest.skip(
            f"CSVs reais nao encontrados em {raw_dir}. "
            f"Defina {RAW_ENV} se estiverem em outro local."
        )


@pytest.mark.integration
def test_real_files_have_expected_inventory_and_schema():
    raw_dir = _real_raw_dir()
    _skip_if_missing(raw_dir)

    sources = discover_sources(raw_dir)
    validate_source_inventory(sources)
    assert len(sources) == 8

    for source in sources:
        validate_source_schema(source, strict=True)


@pytest.mark.integration
def test_real_files_first_rows_pass_pipeline():
    raw_dir = _real_raw_dir()
    _skip_if_missing(raw_dir)

    sources = discover_sources(raw_dir)

    for source in sources:
        raw_chunk = next(
            iter_raw_chunks(
                source,
                chunksize=100,
                nrows=100,
                usecols=CURATED_SOURCE_COLUMNS,
            )
        )
        cleaned = clean_chunk(raw_chunk)

        transformed = transform_chunk(
            cleaned,
            source_file=source.csv_path.name,
            source_year=source.year,
            source_part=source.part,
            source_row_start=2,
        )

        assert len(transformed) == 100
        assert "CpfCnpjNis" not in transformed.columns
        assert transformed["_source_year"].eq(source.year).all()
