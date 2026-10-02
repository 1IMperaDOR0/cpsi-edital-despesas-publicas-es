from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.config import DEFAULT_RAW_DIR
from src.pipeline.data_loader import (
    discover_sources,
    get_source_columns,
    validate_source_inventory,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Inspeciona o inventario e schema dos CSVs oficiais."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_RAW_DIR)
    args = parser.parse_args()

    sources = discover_sources(args.input_dir)
    validate_source_inventory(sources)

    first_columns = None

    for source in sources:
        columns = get_source_columns(source)
        first_columns = first_columns or columns
        print(
            f"{source.key}: {len(columns)} colunas; "
            f"schema_igual={columns == first_columns}; "
            f"arquivo={source.csv_path.name}"
        )


if __name__ == "__main__":
    main()
