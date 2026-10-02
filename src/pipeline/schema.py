from collections.abc import Iterable

from src.pipeline.config import (
    CURATED_OUTPUT_COLUMNS,
    EXPECTED_SOURCE_COLUMNS,
)


class SchemaError(ValueError):
    """Erro de contrato de schema da fonte ou da camada processada."""


def validate_source_columns(
    columns: Iterable[str],
    *,
    strict: bool = True,
) -> None:
    """
    Valida as colunas do arquivo oficial.

    strict=True exige exatamente o conjunto de 71 colunas conhecido.
    A ordem pode mudar sem quebrar o pipeline.
    """
    observed = list(columns)
    observed_set = set(observed)
    expected_set = set(EXPECTED_SOURCE_COLUMNS)

    missing = sorted(expected_set - observed_set)
    extra = sorted(observed_set - expected_set)

    if missing:
        raise SchemaError(
            f"Colunas obrigatorias ausentes na fonte: {missing}"
        )

    if strict and extra:
        raise SchemaError(
            f"Colunas inesperadas na fonte: {extra}"
        )

    if len(observed) != len(observed_set):
        raise SchemaError("Existem nomes de colunas duplicados na fonte.")


def validate_curated_columns(columns: Iterable[str]) -> None:
    """Valida o contrato de saida da camada analitica."""
    observed = list(columns)
    expected = list(CURATED_OUTPUT_COLUMNS)

    if observed != expected:
        missing = [c for c in expected if c not in observed]
        extra = [c for c in observed if c not in expected]
        raise SchemaError(
            "Schema processado diferente do contrato. "
            f"Ausentes={missing}; extras={extra}"
        )
