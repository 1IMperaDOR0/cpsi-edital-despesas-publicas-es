# Handoff do pipeline

## O que esta pronto

- descoberta automatica dos oito ZIPs;
- validacao do inventario 2024/2025;
- validacao das 71 colunas da fonte;
- leitura em chunks diretamente do ZIP;
- conversao controlada de data e valores monetarios;
- limpeza conservadora de texto;
- camada analitica com minimizacao de dados pessoais;
- rastreabilidade ate arquivo/parte/linha da fonte;
- escrita incremental em CSV.GZ;
- suporte opcional a Parquet;
- manifest da execucao;
- relatorio de preenchimento e falhas de parse;
- testes unitarios;
- testes de integracao opcionais com os arquivos reais.

## O que o pipeline propositalmente nao faz ainda

- nao cria o dashboard;
- nao cria KPIs financeiros derivados;
- nao corrige categorias manualmente;
- nao classifica anomalias;
- nao remove supostas duplicidades;
- nao cria banco relacional;
- nao define regra de negocio para as modalidades de licitacao.

Esses pontos dependem de analise e devem ser decididos antes de virar regra
de producao.

## Como outra equipe assume

1. Instalar as dependencias.
2. Colocar os oito ZIPs em `data/raw/`.
3. Rodar `pytest -q`.
4. Rodar os testes de integracao com `DESPESAS_RAW_DIR`.
5. Executar o pipeline em amostra.
6. Conferir `data/reports/quality_summary.csv`.
7. Executar o pipeline completo.
8. Consumir a camada `data/processed/` no servico de dados do Dash.

## Smoke test recomendado

Windows PowerShell:

```powershell
python scripts/run_pipeline.py `
  --input-dir data/raw `
  --output-dir data/processed `
  --reports-dir data/reports `
  --limit-rows-per-source 1000
```

Execucao completa:

```powershell
python scripts/run_pipeline.py `
  --input-dir data/raw `
  --output-dir data/processed `
  --reports-dir data/reports `
  --format parquet
```

## Criterio de aceite para a equipe do painel

O painel nao deve ler os ZIPs brutos. Ele deve consumir apenas a camada
processada criada por este pipeline e respeitar o contrato documentado em
`docs/DATA_CONTRACT.md`.


## Auditoria inicial ja realizada

Antes de iniciar o painel, ler `docs/INITIAL_DATA_AUDIT.md`. O documento
registra limitacoes reais da fonte que afetam diretamente filtros,
rastreabilidade e definicao das categorias de licitacao.
