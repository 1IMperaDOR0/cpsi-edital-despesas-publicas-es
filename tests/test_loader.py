from src.pipeline.config import EXPECTED_SOURCE_COLUMNS
from src.pipeline.data_loader import (
    discover_sources,
    get_source_columns,
    iter_raw_chunks,
    load_data,
    validate_source_inventory,
)


def test_discovers_eight_expected_sources(raw_source_dir):
    sources = discover_sources(raw_source_dir)

    assert len(sources) == 8
    assert sources[0].year == 2024
    assert sources[0].part == 1
    assert sources[-1].year == 2025
    assert sources[-1].part == 4

    validate_source_inventory(sources)


def test_source_header_matches_contract(raw_source_dir):
    source = discover_sources(raw_source_dir)[0]
    columns = get_source_columns(source)

    assert columns == EXPECTED_SOURCE_COLUMNS


def test_loader_reads_csv_in_chunks(raw_source_dir):
    source = discover_sources(raw_source_dir)[0]
    chunks = list(iter_raw_chunks(source, chunksize=1, nrows=2))

    assert len(chunks) == 2
    assert chunks[0].iloc[0]["Favorecido"].strip() == "TESTE FORNECEDOR"


def test_load_data_can_load_small_sample(raw_source_dir):
    df = load_data(
        raw_source_dir,
        years=(2024,),
        usecols=["Ano", "Favorecido", "ValorPago"],
        rows_per_source=1,
    )

    assert len(df) == 4
    assert set(df["_source_year"].unique()) == {2024}
    assert "_source_file" in df.columns
