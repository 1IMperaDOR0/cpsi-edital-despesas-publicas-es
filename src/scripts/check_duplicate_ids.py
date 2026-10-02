from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.config import DEFAULT_RAW_DIR
from src.pipeline.data_loader import discover_sources, iter_raw_chunks


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verifica IDs repetidos sem carregar todas as colunas."
    )
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--chunksize", type=int, default=50_000)
    args = parser.parse_args()

    seen: set[str] = set()
    duplicates = 0
    rows = 0

    for source in discover_sources(args.input_dir):
        for chunk in iter_raw_chunks(
            source,
            chunksize=args.chunksize,
            usecols=["Id"],
        ):
            ids = chunk["Id"].dropna().astype("string").str.strip()

            for value in ids:
                rows += 1
                if value in seen:
                    duplicates += 1
                else:
                    seen.add(value)

    print(f"IDs avaliados: {rows}")
    print(f"IDs repetidos: {duplicates}")


if __name__ == "__main__":
    main()
