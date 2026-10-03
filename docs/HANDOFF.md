# Handoff do pipeline

## O que esta pronto

- descoberta automatica dos oito CSVs oficiais;
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
- relatorios agregados consumidos pelo painel Dash;
- paginas do painel com graficos de evolucao, despesas, favorecidos e rastreabilidade;
- testes unitarios;
- testes de integracao opcionais com os arquivos reais.

## O que o pipeline propositalmente nao faz ainda

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
2. Colocar os oito CSVs oficiais em `src/data/`.
3. Rodar `pytest -q`.
4. Rodar os testes de integracao com `DESPESAS_RAW_DIR`.
5. Executar o pipeline em amostra.
6. Conferir `src/data/reports/quality_summary.csv`.
7. Executar o pipeline completo.
8. Rodar `python src/scripts/validate_metrics.py` para atualizar os agregados do painel.
9. Iniciar o Dash com `python app.py`.

## Smoke test recomendado

Windows PowerShell:

```powershell
python src/scripts/run_pipeline.py `
  --input-dir src/data `
  --output-dir src/data/processed `
  --reports-dir src/data/reports `
  --limit-rows-per-source 1000
```

Execucao completa:

```powershell
python src/scripts/run_pipeline.py `
  --input-dir src/data `
  --output-dir src/data/processed `
  --reports-dir src/data/reports `
  --format parquet
```

## Criterio de aceite para a equipe do painel

O painel nao deve ler os ZIPs brutos nem carregar a camada processada completa.
Ele consome os CSVs agregados em `src/data/reports/`, gerados a partir da
camada processada, e respeita o contrato documentado em `docs/DATA_CONTRACT.md`.


## Auditoria inicial ja realizada

Antes de iniciar o painel, ler `docs/INITIAL_DATA_AUDIT.md`. O documento
registra limitacoes reais da fonte que afetam diretamente filtros,
rastreabilidade e definicao das categorias de licitacao.
