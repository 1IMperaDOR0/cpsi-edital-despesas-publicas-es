from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

from src.pipeline.cleaning import clean_chunk
from src.pipeline.config import CURATED_SOURCE_COLUMNS, DEFAULT_CHUNKSIZE
from src.pipeline.data_loader import (
    discover_sources,
    iter_raw_chunks,
    validate_source_inventory,
    validate_source_schema,
)
from src.pipeline.profiling import QualityAccumulator
from src.pipeline.schema import validate_curated_columns
from src.pipeline.transformations import transform_chunk
from src.pipeline.writer import CsvGzipWriter, ParquetChunkWriter


def _make_writer(*, output_dir: Path, source_key: str, output_format: str):
    if output_format == "csv.gz":
        return CsvGzipWriter(output_dir / f"{source_key}.csv.gz")

    if output_format == "parquet":
        return ParquetChunkWriter(output_dir / source_key)

    raise ValueError("output_format deve ser 'csv.gz' ou 'parquet'")


def build_dataset(
    *,
    input_dir: Path,
    output_dir: Path,
    reports_dir: Path,
    chunksize: int = DEFAULT_CHUNKSIZE,
    output_format: str = "csv.gz",
    limit_rows_per_source: int | None = None,
    require_complete_inventory: bool = True,
) -> dict:
    """Executa o pipeline completo em streaming sobre os CSVs oficiais."""
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    reports_dir = Path(reports_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    sources = discover_sources(input_dir)

    if require_complete_inventory:
        validate_source_inventory(sources)

    for source in sources:
        validate_source_schema(source, strict=True)

    quality = QualityAccumulator()
    manifest_sources = []
    total_rows = 0

    for source in sources:
        source_rows = 0
        source_row_start = 2  # linha 1 = cabecalho no CSV

        writer = _make_writer(
            output_dir=output_dir,
            source_key=source.key,
            output_format=output_format,
        )

        with writer:
            for raw_chunk in iter_raw_chunks(
                source,
                chunksize=chunksize,
                nrows=limit_rows_per_source,
                usecols=CURATED_SOURCE_COLUMNS,
            ):
                cleaned = clean_chunk(raw_chunk)

                quality.update(raw_chunk, cleaned, expected_year=source.year)

                transformed = transform_chunk(
                    cleaned,
                    source_file=source.csv_path.name,
                    source_year=source.year,
                    source_part=source.part,
                    source_row_start=source_row_start,
                )

                validate_curated_columns(transformed.columns)
                writer.write(transformed)

                rows = len(transformed)
                source_rows += rows
                total_rows += rows
                source_row_start += rows

        manifest_sources.append(
            {
                "source_file": source.csv_path.name,
                "year": source.year,
                "part": source.part,
                "rows_processed": source_rows,
            }
        )

    quality_path = reports_dir / "quality_summary.csv"
    quality.to_frame().to_csv(quality_path, index=False)

    manifest = {
        "pipeline_version": "0.2.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_dir": str(input_dir.resolve()),
        "output_dir": str(output_dir.resolve()),
        "output_format": output_format,
        "chunksize": chunksize,
        "limit_rows_per_source": limit_rows_per_source,
        "total_rows_processed": total_rows,
        "year_mismatch_count": quality.year_mismatch,
        "sources": manifest_sources,
        "quality_report": str(quality_path.resolve()),
        "design_notes": [
            "A camada analitica exclui CPF/CNPJ e dados bancarios.",
            "Nenhuma linha e removida silenciosamente.",
            "Categorias de negocio nao sao corrigidas sem evidencia.",
            "Metricas financeiras derivadas ainda nao fazem parte do pipeline.",
        ],
    }

    manifest_path = reports_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return manifest
