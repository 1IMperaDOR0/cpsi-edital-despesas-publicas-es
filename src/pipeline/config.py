from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Os CSVs oficiais ficam no proprio projeto, em src/data, conforme a
# estrutura atual do repositorio. Saidas do pipeline ficam fora de src para
# separar fonte, codigo e artefatos gerados.
DEFAULT_RAW_DIR = PROJECT_ROOT / "src" / "data"
DEFAULT_PROCESSED_DIR = PROJECT_ROOT / "src" / "data" / "processed"
DEFAULT_REPORTS_DIR = PROJECT_ROOT / "src" / "data" / "reports"

CSV_SEPARATOR = ";"
CSV_ENCODING = "utf-8-sig"
DEFAULT_CHUNKSIZE = 50_000

SOURCE_YEARS = (2024, 2025)
SOURCE_PARTS = (1, 2, 3, 4)

FINANCIAL_COLUMNS = [
    "ValorEmpenho",
    "ValorLiquidado",
    "ValorPago",
    "ValorRap",
]

DATE_COLUMNS = ["Data"]

EXPECTED_SOURCE_COLUMNS = [
    "Ano",
    "Data",
    "ValorEmpenho",
    "ValorLiquidado",
    "ValorPago",
    "ValorRap",
    "CpfCnpjNis",
    "TipoFavorecido",
    "CargoFuncao",
    "Favorecido",
    "IdFavorecido",
    "TipoLicitacao",
    "HistoricoDocumento",
    "Documento",
    "DocumentoEmpenho",
    "CodigoProcesso",
    "Processo",
    "ProcessoAssunto",
    "CodigoFuncionalProgramatica",
    "CodigoCategoriaEconomica",
    "CategoriaEconomica",
    "CodigoUnidadeGestora",
    "UnidadeGestora",
    "CodigoGrupoDespesa",
    "GrupoDespesa",
    "CodigoElementoDespesa",
    "ElementoDespesa",
    "DescricaoElementoDespesa",
    "CodigoSubtitulo",
    "Subtitulo",
    "CodigoFonte",
    "Fonte",
    "CodigoDetalhamentoFonte",
    "DetalhamentoFonte",
    "CodigoOrgao",
    "Orgao",
    "CodigoFuncao",
    "Funcao",
    "CodigoSubFuncao",
    "SubFuncao",
    "CodigoPrograma",
    "Programa",
    "CodigoAcao",
    "Acao",
    "CodigoModalidade",
    "Modalidade",
    "CodigoSubelementoDespesa",
    "SubelementoDespesa",
    "CodigoGestaoEmitente",
    "CodigoPlanoOrcamentario",
    "PlanoOrcamentario",
    "NumeroProcesso",
    "CodigoConvenioRecebido",
    "CodigoConvenioConcedido",
    "Embasamento",
    "CredorRetencao",
    "NomeCredorRetencao",
    "TipoRetencao",
    "NomeTipoRetencao",
    "NumeroLicitacao",
    "AnoLicitacao",
    "BancoOrigem",
    "AgenciaOrigem",
    "DomicilioBancarioOrigem",
    "IdUso",
    "DescricaoIdUso",
    "Emenda",
    "Esfera",
    "DescricaoEsfera",
    "Contrato",
    "Id",
]

# Contrato de dados da futura camada analitica.
# Mantemos apenas o que tem potencial de uso no painel e excluimos, por
# padrao, identificadores pessoais e bancarios que nao sao necessarios.
CURATED_SOURCE_COLUMNS = [
    "Ano",
    "Data",
    "ValorEmpenho",
    "ValorLiquidado",
    "ValorPago",
    "ValorRap",
    "TipoFavorecido",
    "Favorecido",
    "IdFavorecido",
    "TipoLicitacao",
    "HistoricoDocumento",
    "Documento",
    "DocumentoEmpenho",
    "CodigoProcesso",
    "Processo",
    "ProcessoAssunto",
    "CodigoCategoriaEconomica",
    "CategoriaEconomica",
    "CodigoUnidadeGestora",
    "UnidadeGestora",
    "CodigoGrupoDespesa",
    "GrupoDespesa",
    "CodigoElementoDespesa",
    "ElementoDespesa",
    "DescricaoElementoDespesa",
    "CodigoSubtitulo",
    "Subtitulo",
    "CodigoFonte",
    "Fonte",
    "CodigoOrgao",
    "Orgao",
    "CodigoFuncao",
    "Funcao",
    "CodigoSubFuncao",
    "SubFuncao",
    "CodigoPrograma",
    "Programa",
    "CodigoAcao",
    "Acao",
    "CodigoModalidade",
    "Modalidade",
    "CodigoSubelementoDespesa",
    "SubelementoDespesa",
    "NumeroProcesso",
    "NumeroLicitacao",
    "AnoLicitacao",
    "Contrato",
    "Id",
]

DERIVED_COLUMNS = [
    "Mes",
    "AnoMes",
]

LINEAGE_COLUMNS = [
    "_source_file",
    "_source_year",
    "_source_part",
    "_source_row",
]

CURATED_OUTPUT_COLUMNS = (
    CURATED_SOURCE_COLUMNS + DERIVED_COLUMNS + LINEAGE_COLUMNS
)
