import argparse
import json
import sys
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(
        0,
        str(PROJECT_ROOT),
    )


from src.analytics.metrics import (
    FINANCIAL_COLUMNS,
    financial_quality_summary,
    financial_totals,
    totals_by_month,
    totals_by_unit,
    totals_by_year,
)


PROCESSED_DIR = (
    PROJECT_ROOT
    / "src"
    / "data"
    / "processed"
)

REPORTS_DIR = (
    PROJECT_ROOT
    / "src"
    / "data"
    / "reports"
)


DESIRED_COLUMNS = (
    "Ano",
    "Data",
    "AnoMes",
    "UnidadeGestora",
    "Id",
    *FINANCIAL_COLUMNS,
)


def discover_files(
    file_format: str = "auto",
) -> list[Path]:

    parquet_files = sorted(
        PROCESSED_DIR.glob("*.parquet")
    )

    csv_files = sorted(
        PROCESSED_DIR.glob("*.csv.gz")
    )

    if file_format == "parquet":
        files = parquet_files

    elif file_format == "csv.gz":
        files = csv_files

    else:
        if parquet_files and csv_files:
            raise RuntimeError(
                "Foram encontrados arquivos Parquet "
                "e CSV.GZ em data/processed. "
                "Informe --format parquet ou --format csv.gz "
                "para evitar dupla contagem."
            )

        files = (
            parquet_files
            if parquet_files
            else csv_files
        )

    if not files:
        raise FileNotFoundError(
            "Nenhum arquivo processado encontrado em "
            f"{PROCESSED_DIR}"
        )

    return files


def read_processed_file(
    path: Path,
) -> pd.DataFrame:

    if path.suffix == ".parquet":
        try:
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise RuntimeError(
                "pyarrow é necessário para ler Parquet."
            ) from exc

        available = set(
            pq.ParquetFile(path).schema.names
        )

        columns = [
            column
            for column in DESIRED_COLUMNS
            if column in available
        ]

        return pd.read_parquet(
            path,
            columns=columns,
        )

    return pd.read_csv(
        path,
        compression="gzip",
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
        usecols=lambda column: (
            column in DESIRED_COLUMNS
        ),
        low_memory=False,
    )


def load_processed_data(
    files: list[Path],
) -> tuple[pd.DataFrame, dict]:

    frames = []

    conversion_errors = {
        column: 0
        for column in FINANCIAL_COLUMNS
    }

    conversion_errors["Data"] = 0
    conversion_errors["Ano"] = 0

    for path in files:
        print(
            f"Carregando: {path.name}"
        )

        frame = read_processed_file(path)

        if "Data" in frame.columns:
            original_not_null = (
                frame["Data"].notna()
            )

            converted = pd.to_datetime(
                frame["Data"],
                errors="coerce",
            )

            conversion_errors["Data"] += int(
                (
                    original_not_null
                    & converted.isna()
                ).sum()
            )

            frame["Data"] = converted

        if "Ano" in frame.columns:
            original_not_null = (
                frame["Ano"].notna()
            )

            converted = pd.to_numeric(
                frame["Ano"],
                errors="coerce",
            )

            conversion_errors["Ano"] += int(
                (
                    original_not_null
                    & converted.isna()
                ).sum()
            )

            frame["Ano"] = converted.astype(
                "Int64"
            )

        for column in FINANCIAL_COLUMNS:
            if column not in frame.columns:
                continue

            original_not_null = (
                frame[column].notna()
            )

            converted = pd.to_numeric(
                frame[column],
                errors="coerce",
            )

            conversion_errors[column] += int(
                (
                    original_not_null
                    & converted.isna()
                ).sum()
            )

            frame[column] = converted

        frames.append(frame)

    return (
        pd.concat(
            frames,
            ignore_index=True,
        ),
        conversion_errors,
    )


def validate_year_vs_date(
    df: pd.DataFrame,
) -> int:

    if (
        "Ano" not in df.columns
        or "Data" not in df.columns
    ):
        return 0

    valid = (
        df["Ano"].notna()
        & df["Data"].notna()
    )

    mismatch = (
        df.loc[valid, "Ano"]
        != df.loc[valid, "Data"].dt.year
    )

    return int(mismatch.sum())


def validate_ids(
    df: pd.DataFrame,
) -> dict:

    if "Id" not in df.columns:
        return {
            "id_column_available": False,
            "repeated_id_rows": None,
            "repeated_id_values": None,
        }

    valid_ids = (
        df["Id"]
        .dropna()
        .astype("string")
    )

    duplicated = valid_ids.duplicated(
        keep=False
    )

    repeated_values = (
        valid_ids[duplicated]
        .nunique()
    )

    return {
        "id_column_available": True,
        "repeated_id_rows": int(
            duplicated.sum()
        ),
        "repeated_id_values": int(
            repeated_values
        ),
    }


def reconciliation_by_year(
    totals: pd.Series,
    by_year: pd.DataFrame,
) -> dict:

    result = {}

    for column in FINANCIAL_COLUMNS:
        overall = totals[column]

        grouped = by_year[column].sum(
            skipna=True,
            min_count=1,
        )

        if pd.isna(overall) and pd.isna(grouped):
            difference = 0.0

        else:
            difference = float(
                abs(overall - grouped)
            )

        result[column] = {
            "difference": difference,
            "ok": difference < 0.01,
        }

    return result


def main() -> None:

    parser = argparse.ArgumentParser(
        description=(
            "Valida as métricas financeiras "
            "sobre a camada processada."
        )
    )

    parser.add_argument(
        "--format",
        choices=[
            "auto",
            "parquet",
            "csv.gz",
        ],
        default="auto",
    )

    args = parser.parse_args()

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    files = discover_files(
        args.format
    )

    print(
        f"\nArquivos encontrados: {len(files)}"
    )

    df, conversion_errors = (
        load_processed_data(files)
    )

    if df.empty:
        raise RuntimeError(
            "A camada processada foi carregada, "
            "mas nenhum registro ficou disponível."
        )

    print(
        f"Registros carregados: {len(df):,}"
    )

    print(
        "Colunas carregadas:",
        df.columns.tolist(),
    )

    totals = financial_totals(df)

    quality = financial_quality_summary(df)

    by_year = totals_by_year(df)

    by_month = totals_by_month(df)

    by_unit = totals_by_unit(df)

    year_date_mismatch = (
        validate_year_vs_date(df)
    )

    id_validation = validate_ids(df)

    reconciliation = (
        reconciliation_by_year(
            totals,
            by_year,
        )
    )
    missing_financial_columns = [
        column
        for column in FINANCIAL_COLUMNS
        if column not in df.columns
    ]

    if missing_financial_columns:
        raise RuntimeError(
            "Os arquivos foram encontrados, mas as "
            "colunas financeiras não foram carregadas: "
            + ", ".join(missing_financial_columns)
            + ". Verifique separador, encoding e schema "
            "dos arquivos processados."
        )
    
    quality.to_csv(
        REPORTS_DIR
        / "metrics_quality.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_year.to_csv(
        REPORTS_DIR
        / "metrics_by_year.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_month.to_csv(
        REPORTS_DIR
        / "metrics_by_month.csv",
        index=False,
        encoding="utf-8-sig",
    )

    by_unit.to_csv(
        REPORTS_DIR
        / "metrics_by_unit.csv",
        index=False,
        encoding="utf-8-sig",
    )

    validation = {
        "processed_files": [
            path.name
            for path in files
        ],
        "rows": int(len(df)),
        "years": (
            sorted(
                int(year)
                for year in (
                    df["Ano"]
                    .dropna()
                    .unique()
                )
            )
            if "Ano" in df.columns
            else []
        ),
        "conversion_errors": (
            conversion_errors
        ),
        "year_date_mismatch": (
            year_date_mismatch
        ),
        **id_validation,
        "reconciliation_by_year": (
            reconciliation
        ),
    }

    if (
        "Data" in df.columns
        and df["Data"].notna().any()
    ):
        validation["date_min"] = str(
            df["Data"].min()
        )

        validation["date_max"] = str(
            df["Data"].max()
        )

    with open(
        REPORTS_DIR
        / "metrics_validation.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            validation,
            file,
            ensure_ascii=False,
            indent=2,
        )

    print("\n=== TOTAIS ===")

    for column, value in totals.items():
        print(
            f"{column}: {value:,.2f}"
        )

    print("\n=== POR ANO ===")
    print(
        by_year.to_string(
            index=False
        )
    )

    print(
        "\n=== QUALIDADE DAS MÉTRICAS ==="
    )

    print(
        quality.to_string(
            index=False
        )
    )

    print(
        "\n=== VALIDAÇÕES ==="
    )

    print(
        "Inconsistências Ano x Data:",
        year_date_mismatch,
    )

    print(
        "IDs repetidos:",
        id_validation,
    )

    print(
        "Reconciliação total x anos:",
        reconciliation,
    )

    print(
        "\nRelatórios salvos em:"
    )

    print(REPORTS_DIR)


if __name__ == "__main__":
    main()