from __future__ import annotations

from pathlib import Path
import gzip

import pandas as pd


class CsvGzipWriter:
    """Escrita incremental de CSV comprimido, um arquivo por fonte."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = Path(output_path)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self._handle = None
        self._header_written = False

    def __enter__(self):
        self._handle = gzip.open(
            self.output_path,
            mode="wt",
            encoding="utf-8",
            newline="",
        )
        return self

    def write(self, df: pd.DataFrame) -> None:
        if self._handle is None:
            raise RuntimeError("Writer deve ser usado como context manager.")

        df.to_csv(
            self._handle,
            index=False,
            sep=";",
            decimal=",",
            header=not self._header_written,
        )
        self._header_written = True

    def __exit__(self, exc_type, exc, tb):
        if self._handle is not None:
            self._handle.close()


class ParquetChunkWriter:
    """
    Escrita particionada em Parquet.

    Cada chunk vira um arquivo independente, evitando manter o dataset
    inteiro em memoria.
    """

    def __init__(self, output_dir: Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._chunk_index = 0

    def __enter__(self):
        return self

    def write(self, df: pd.DataFrame) -> None:
        output_path = (
            self.output_dir
            / f"part-{self._chunk_index:05d}.parquet"
        )
        df.to_parquet(
            output_path,
            index=False,
            engine="pyarrow",
        )
        self._chunk_index += 1

    def __exit__(self, exc_type, exc, tb):
        return False
