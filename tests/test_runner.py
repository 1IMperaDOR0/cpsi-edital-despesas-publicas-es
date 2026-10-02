import json

import pandas as pd

from src.pipeline.runner import build_dataset


def test_pipeline_builds_outputs_and_manifest(
    tmp_path,
    raw_source_dir,
):
    output_dir = tmp_path / "processed"
    reports_dir = tmp_path / "reports"

    manifest = build_dataset(
        input_dir=raw_source_dir,
        output_dir=output_dir,
        reports_dir=reports_dir,
        chunksize=1,
        output_format="csv.gz",
    )

    assert manifest["total_rows_processed"] == 16
    assert manifest["year_mismatch_count"] == 0
    assert len(manifest["sources"]) == 8

    output_files = sorted(output_dir.glob("*.csv.gz"))
    assert len(output_files) == 8

    sample = pd.read_csv(
        output_files[0],
        sep=";",
        compression="gzip",
    )

    assert len(sample) == 2
    assert "_source_file" in sample.columns
    assert "CpfCnpjNis" not in sample.columns

    stored_manifest = json.loads(
        (reports_dir / "manifest.json").read_text(
            encoding="utf-8"
        )
    )
    assert stored_manifest["total_rows_processed"] == 16
    assert (reports_dir / "quality_summary.csv").exists()
