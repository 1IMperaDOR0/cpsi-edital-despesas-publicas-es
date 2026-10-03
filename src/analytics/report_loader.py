from pathlib import Path

import pandas as pd

from src.pipeline.config import DEFAULT_REPORTS_DIR


def load_report(
    filename: str,
    reports_dir: Path = DEFAULT_REPORTS_DIR,
) -> pd.DataFrame:
    """Carrega um CSV agregado da pasta de relatórios do pipeline."""
    path = Path(reports_dir) / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Relatório não encontrado: {path}. "
            "Execute `python src/scripts/validate_metrics.py` para gerá-lo."
        )

    return pd.read_csv(path, encoding="utf-8-sig")
