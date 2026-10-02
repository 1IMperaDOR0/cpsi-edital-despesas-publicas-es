import pytest

from src.pipeline.config import EXPECTED_SOURCE_COLUMNS
from src.pipeline.schema import SchemaError, validate_source_columns


def test_valid_source_schema_is_accepted():
    validate_source_columns(EXPECTED_SOURCE_COLUMNS)


def test_missing_source_column_fails():
    columns = [
        c
        for c in EXPECTED_SOURCE_COLUMNS
        if c != "ValorPago"
    ]

    with pytest.raises(SchemaError):
        validate_source_columns(columns)


def test_unexpected_source_column_fails_in_strict_mode():
    columns = EXPECTED_SOURCE_COLUMNS + ["NovaColuna"]

    with pytest.raises(SchemaError):
        validate_source_columns(columns, strict=True)
