from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.config import (
    DEFAULT_CHUNKSIZE,
    DEFAULT_PROCESSED_DIR,
    DEFAULT_RAW_DIR,
    DEFAULT_REPORTS_DIR,
)
from src.pipeline.runner import build_dataset


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pipeline das despesas publicas do ES.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_PROCESSED_DIR)
    parser.add_argument("--reports-dir", type=Path, default=DEFAULT_REPORTS_DIR)
    parser.add_argument("--chunksize", type=int, default=DEFAULT_CHUNKSIZE)
    parser.add_argument(
        "--format",
        dest="output_format",
        choices=["csv.gz", "parquet"],
        default="csv.gz",
    )
    parser.add_argument(
        "--limit-rows-per-source",
        type=int,
        default=None,
        help="Use para smoke tests e desenvolvimento.",
    )
    parser.add_argument(
        "--allow-partial-inventory",
        action="store_true",
        help="Permite rodar com apenas alguns CSVs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_dataset(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        reports_dir=args.reports_dir,
        chunksize=args.chunksize,
        output_format=args.output_format,
        limit_rows_per_source=args.limit_rows_per_source,
        require_complete_inventory=not args.allow_partial_inventory,
    )
    print(
        "Pipeline concluido. "
        f"Linhas processadas: {manifest['total_rows_processed']}"
    )


if __name__ == "__main__":
    main()
