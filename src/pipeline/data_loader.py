from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from collections.abc import Iterator

import pandas as pd

from src.pipeline.config import (
    CSV_ENCODING,
    CSV_SEPARATOR,
    CURATED_SOURCE_COLUMNS,
    DEFAULT_CHUNKSIZE,
    DEFAULT_RAW_DIR,
    SOURCE_PARTS,
    SOURCE_YEARS,
)
from src.pipeline.schema import validate_source_columns


SOURCE_FILENAME_RE = re.compile(
    r"^despesas_es_(?P<year>\d{4})_completo_parte_(?P<part>\d{2})\.csv$",
    flags=re.IGNORECASE,
)


@dataclass(frozen=True)
class SourceFile:
    """Representa uma das partes oficiais de despesas de 2024/2025."""

    csv_path: Path
    year: int
    part: int

    @property
    def key(self) -> str:
        return f"{self.year}-parte-{self.part:02d}"


def _parse_source_name(csv_path: Path) -> tuple[int, int] | None:
    match = SOURCE_FILENAME_RE.match(csv_path.name)
    if not match:
        return None
    return int(match.group("year")), int(match.group("part"))


def discover_sources(input_dir: Path = DEFAULT_RAW_DIR) -> list[SourceFile]:
    """
    Descobre os CSVs oficiais em ``src/data`` (ou em outro diretorio).

    Arquivos que nao seguem o padrao oficial sao ignorados. Isso permite
    manter outros arquivos auxiliares na pasta sem quebrarem o pipeline.
    """
    input_dir = Path(input_dir)

    if not input_dir.exists():
        raise FileNotFoundError(f"Diretorio de dados nao encontrado: {input_dir}")

    sources: list[SourceFile] = []

    for csv_path in sorted(input_dir.glob("despesas_es_*_completo_parte_*.csv")):
        parsed = _parse_source_name(csv_path)
        if parsed is None:
            continue

        year, part = parsed
        sources.append(SourceFile(csv_path=csv_path, year=year, part=part))

    if not sources:
        raise FileNotFoundError(
            f"Nenhum CSV de despesas encontrado em {input_dir}. "
            "Esperado: despesas_es_2024_completo_parte_01.csv, etc."
        )

    return sorted(sources, key=lambda source: (source.year, source.part))


def validate_source_inventory(
    sources: list[SourceFile],
    *,
    years: tuple[int, ...] = SOURCE_YEARS,
    parts: tuple[int, ...] = SOURCE_PARTS,
) -> None:
    """Garante que as oito partes esperadas estejam presentes, sem extras."""
    observed = {(source.year, source.part) for source in sources}
    expected = {(year, part) for year in years for part in parts}

    missing = sorted(expected - observed)
    extra = sorted(observed - expected)

    if missing or extra:
        raise ValueError(
            "Inventario de arquivos incompleto ou inesperado. "
            f"Ausentes={missing}; extras={extra}"
        )


def get_source_columns(source: SourceFile) -> list[str]:
    """Le apenas o cabecalho de um CSV; nao carrega o arquivo inteiro."""
    df = pd.read_csv(
        source.csv_path,
        sep=CSV_SEPARATOR,
        encoding=CSV_ENCODING,
        nrows=0,
    )
    return list(df.columns)


def validate_source_schema(source: SourceFile, *, strict: bool = True) -> None:
    """Valida o schema da fonte contra o contrato conhecido."""
    validate_source_columns(get_source_columns(source), strict=strict)


def iter_raw_chunks(
    source: SourceFile,
    *,
    chunksize: int = DEFAULT_CHUNKSIZE,
    nrows: int | None = None,
    usecols: list[str] | None = None,
) -> Iterator[pd.DataFrame]:
    """
    Le um CSV oficial em blocos para evitar colocar ~1 milhao de registros
    completos na memoria de uma vez.

    Todos os campos entram inicialmente como string. Conversoes de tipos
    pertencem a camada ``cleaning.py``.
    """
    selected = usecols or CURATED_SOURCE_COLUMNS

    reader = pd.read_csv(
        source.csv_path,
        sep=CSV_SEPARATOR,
        encoding=CSV_ENCODING,
        dtype="string",
        usecols=selected,
        chunksize=chunksize,
        nrows=nrows,
        keep_default_na=True,
        na_values=[""],
        low_memory=False,
    )

    yield from reader


def load_data(
    input_dir: Path = DEFAULT_RAW_DIR,
    *,
    years: tuple[int, ...] | None = None,
    usecols: list[str] | None = None,
    rows_per_source: int | None = None,
) -> pd.DataFrame:
    """
    Funcao de conveniencia para notebooks, exploracoes e testes locais.

    Para o pipeline completo, prefira ``iter_raw_chunks`` / ``runner.py``.
    ``rows_per_source`` e util para trabalhar com amostras sem consumir muita
    memoria. Se ficar ``None``, todos os registros dos arquivos selecionados
    serao concatenados em memoria.
    """
    sources = discover_sources(input_dir)

    if years is not None:
        wanted = set(years)
        sources = [source for source in sources if source.year in wanted]

    if not sources:
        raise ValueError("Nenhuma fonte corresponde aos anos solicitados.")

    frames: list[pd.DataFrame] = []
    selected = usecols or CURATED_SOURCE_COLUMNS

    for source in sources:
        for chunk in iter_raw_chunks(
            source,
            chunksize=DEFAULT_CHUNKSIZE,
            nrows=rows_per_source,
            usecols=selected,
        ):
            chunk = chunk.copy()
            chunk["_source_file"] = source.csv_path.name
            chunk["_source_year"] = source.year
            chunk["_source_part"] = source.part
            frames.append(chunk)

    return pd.concat(frames, ignore_index=True)
