from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.analytics.metrics import (
    VARIABLE_CATALOG,
    beneficiary_concentration,
    descriptive_payment_statistics,
)
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
DATA_SCIENCE_COLUMNS = (
    "Ano",
    "ValorPago",
    "Favorecido",
    "TipoLicitacao",
)


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


def _write_data_science_reports(
    positive_data: pd.DataFrame,
    total_records: int,
    records_by_year: dict[int, int],
    reports_path: Path,
) -> list[str]:
    """Gera relatórios de estatística, probabilidade, boxplot e IC usados no painel."""

    generated: list[str] = []

    variable_file = "variable_catalog.csv"
    VARIABLE_CATALOG.to_csv(
        reports_path / variable_file,
        index=False,
        encoding="utf-8-sig",
    )
    generated.append(variable_file)

    statistics_rows: list[dict] = [
        {
            "Escopo": "Todos",
            "Ano": pd.NA,
            **descriptive_payment_statistics(
                positive_data["ValorPago"],
                total_records=total_records,
            ),
        }
    ]

    for year in sorted(records_by_year):
        year_values = positive_data.loc[
            positive_data["Ano"] == year,
            "ValorPago",
        ]
        statistics_rows.append(
            {
                "Escopo": str(year),
                "Ano": year,
                **descriptive_payment_statistics(
                    year_values,
                    total_records=records_by_year[year],
                ),
            }
        )

    statistics = pd.DataFrame(statistics_rows)
    statistics_file = "payment_statistics.csv"
    statistics.to_csv(
        reports_path / statistics_file,
        index=False,
        encoding="utf-8-sig",
    )
    generated.append(statistics_file)

    concentration, concentration_summary = beneficiary_concentration(
        positive_data[["Favorecido", "ValorPago"]],
        top_n=10,
    )
    concentration_file = "beneficiary_concentration.csv"
    concentration.head(100).to_csv(
        reports_path / concentration_file,
        index=False,
        encoding="utf-8-sig",
    )
    generated.append(concentration_file)

    concentration_summary_file = "beneficiary_concentration_summary.csv"
    pd.DataFrame([concentration_summary]).to_csv(
        reports_path / concentration_summary_file,
        index=False,
        encoding="utf-8-sig",
    )
    generated.append(concentration_summary_file)

    procurement = positive_data.copy()
    procurement["TipoLicitacao"] = (
        procurement["TipoLicitacao"]
        .astype("string")
        .str.strip()
        .fillna("Não informado")
    )
    procurement_report = (
        procurement.groupby("TipoLicitacao", dropna=False)
        .agg(
            ValorPago=("ValorPago", "sum"),
            Registros=("ValorPago", "size"),
        )
        .reset_index()
        .sort_values("ValorPago", ascending=False)
    )
    total_procurement = float(procurement_report["ValorPago"].sum())
    procurement_report["ParticipacaoPct"] = (
        procurement_report["ValorPago"] / total_procurement * 100
        if total_procurement
        else 0.0
    )
    procurement_file = "payments_by_licitacao_positive.csv"
    procurement_report.to_csv(
        reports_path / procurement_file,
        index=False,
        encoding="utf-8-sig",
    )
    generated.append(procurement_file)

    return generated


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
        *DATA_SCIENCE_COLUMNS,
        *(column for dimensions in REPORT_DIMENSIONS.values() for column in dimensions),
    }
    partials: dict[str, list[pd.DataFrame]] = {
        report: [] for report in REPORT_DIMENSIONS
    }
    positive_parts: list[pd.DataFrame] = []
    total_records = 0
    records_by_year: dict[int, int] = {}

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

            total_records += len(chunk)
            years = pd.to_numeric(chunk["Ano"], errors="coerce")
            year_counts = years.dropna().astype(int).value_counts()
            for year, count in year_counts.items():
                records_by_year[int(year)] = records_by_year.get(int(year), 0) + int(count)

            ds_chunk = chunk[list(DATA_SCIENCE_COLUMNS)].copy()
            ds_chunk["Ano"] = pd.to_numeric(ds_chunk["Ano"], errors="coerce").astype("Int64")
            ds_chunk["ValorPago"] = pd.to_numeric(ds_chunk["ValorPago"], errors="coerce")
            ds_chunk = ds_chunk.loc[ds_chunk["ValorPago"] > 0]
            if not ds_chunk.empty:
                positive_parts.append(ds_chunk)

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

    if positive_parts:
        positive_data = pd.concat(positive_parts, ignore_index=True)
    else:
        positive_data = pd.DataFrame(columns=DATA_SCIENCE_COLUMNS)

    generated.extend(
        _write_data_science_reports(
            positive_data,
            total_records,
            records_by_year,
            reports_path,
        )
    )

    return generated
