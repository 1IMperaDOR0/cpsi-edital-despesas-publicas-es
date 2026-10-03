from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.pipeline.config import DEFAULT_CHUNKSIZE, DEFAULT_REPORTS_DIR


FINANCIAL_COLUMN = "ValorPago"
REPORT_DIMENSIONS = {
    "metrics_by_element.csv": ("ElementoDespesa",),
    "metrics_by_subelement.csv": (
        "ElementoDespesa",
        "SubelementoDespesa",
    ),
    "metrics_by_beneficiary.csv": ("Favorecido",),
    "metrics_by_licitacao.csv": ("TipoLicitacao",),
    "metrics_by_process.csv": ("CodigoProcesso",),
}
TRACEABILITY_COLUMNS = ("Documento", "DocumentoEmpenho")
REPORT_ROW_LIMITS = {
    "metrics_by_beneficiary.csv": 100,
    "metrics_by_process.csv": 100,
}


def _iter_processed_chunks(
    path: Path,
    *,
    columns: list[str],
    chunksize: int,
):
    if path.name.endswith(".csv.gz"):
        reader = pd.read_csv(
            path,
            compression="gzip",
            sep=";",
            decimal=",",
            encoding="utf-8-sig",
            usecols=columns,
            chunksize=chunksize,
            low_memory=False,
        )
        yield from reader
        return

    if path.suffix == ".parquet":
        frame = pd.read_parquet(path, columns=columns)
        for start in range(0, len(frame), chunksize):
            yield frame.iloc[start:start + chunksize].copy()
        return

    raise ValueError(f"Formato processado não suportado: {path.name}")


def _aggregate_chunk(
    chunk: pd.DataFrame,
    dimensions: tuple[str, ...],
    *,
    include_document_references: bool = False,
) -> pd.DataFrame:
    cleaned = chunk.copy()
    for column in dimensions:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
            .fillna("Não informado")
        )

    aggregations = {
        "Registros": (dimensions[0], "size"),
        FINANCIAL_COLUMN: (FINANCIAL_COLUMN, "sum"),
    }
    if include_document_references:
        aggregations.update({
            "ReferenciasDocumento": ("Documento", "count"),
            "ReferenciasDocumentoEmpenho": (
                "DocumentoEmpenho",
                "count",
            ),
        })

    return (
        cleaned
        .groupby(list(dimensions), dropna=False, observed=True)
        .agg(**aggregations)
        .reset_index()
    )


def build_dashboard_reports(
    processed_files: list[Path],
    reports_dir: Path = DEFAULT_REPORTS_DIR,
    *,
    chunksize: int = DEFAULT_CHUNKSIZE,
    top_n: int = 100,
) -> list[str]:
    """Gera os agregados usados pelas páginas do painel, sem ler os CSVs brutos."""
    if not processed_files:
        raise FileNotFoundError("Nenhum arquivo processado foi informado.")

    required_columns = {
        FINANCIAL_COLUMN,
        *TRACEABILITY_COLUMNS,
        *(column for dimensions in REPORT_DIMENSIONS.values() for column in dimensions),
    }
    partials: dict[str, list[pd.DataFrame]] = {
        report: [] for report in REPORT_DIMENSIONS
    }

    for path in processed_files:
        path = Path(path)
        available_columns: set[str] | None = None

        for chunk in _iter_processed_chunks(
            path,
            columns=sorted(required_columns),
            chunksize=chunksize,
        ):
            if available_columns is None:
                available_columns = set(chunk.columns)
                missing = sorted(required_columns - available_columns)
                if missing:
                    raise KeyError(
                        f"Colunas ausentes em {path.name}: {', '.join(missing)}"
                    )

            for report_name, dimensions in REPORT_DIMENSIONS.items():
                partials[report_name].append(
                    _aggregate_chunk(
                        chunk,
                        dimensions,
                        include_document_references=(
                            report_name == "metrics_by_process.csv"
                        ),
                    )
                )

    reports_path = Path(reports_dir)
    reports_path.mkdir(parents=True, exist_ok=True)
    generated: list[str] = []

    for report_name, dimensions in REPORT_DIMENSIONS.items():
        report_parts = partials[report_name]
        if not report_parts:
            raise ValueError(f"Não foram encontrados registros para {report_name}.")

        combined = pd.concat(report_parts, ignore_index=True)
        measure_columns = ["Registros", FINANCIAL_COLUMN]
        if report_name == "metrics_by_process.csv":
            measure_columns.extend([
                "ReferenciasDocumento",
                "ReferenciasDocumentoEmpenho",
            ])

        report = (
            combined
            .groupby(list(dimensions), as_index=False, dropna=False)[measure_columns]
            .sum()
            .sort_values(FINANCIAL_COLUMN, ascending=False, na_position="last")
        )

        row_limit = REPORT_ROW_LIMITS.get(report_name, top_n)
        if row_limit is not None:
            report = report.head(row_limit)

        report.to_csv(
            reports_path / report_name,
            index=False,
            encoding="utf-8-sig",
        )
        generated.append(report_name)

    return generated
