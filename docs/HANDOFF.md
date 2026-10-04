# Handoff — CPSI Despesas Públicas ES

## Objetivo

Este documento permite que outra equipe continue o checkpoint sem reconstruir o trabalho de engenharia de dados e análise já realizado.

A continuidade deve partir da camada processada, dos relatórios agregados, das funções de métricas e da aplicação Dash existentes.

## Estado atual

### Engenharia de dados

Concluído:

- descoberta dos 8 CSVs oficiais;
- validação do inventário 2024/2025;
- validação do schema de 71 colunas;
- processamento em chunks;
- conversão de datas e medidas financeiras;
- limpeza conservadora de texto;
- minimização de dados pessoais e bancários;
- campos de proveniência;
- saída em CSV.GZ e suporte a Parquet;
- manifest e relatório de qualidade;
- testes unitários e de integração.

### Analytics

Concluído:

- totais financeiros;
- agregados por ano, mês e unidade gestora;
- agregados por elemento e subelemento;
- agregados por favorecido e tipo de licitação;
- relatório de processos para rastreabilidade;
- estatística descritiva de pagamentos positivos;
- boxplot e regra de outliers;
- intervalo de confiança da média dos pagamentos positivos;
- concentração por favorecido;
- catálogo de variáveis.

### Aplicação

Concluído:

- Painel Principal;
- Visão Geral;
- Despesas;
- Favorecidos e Contratações;
- Rastreabilidade;
- navegação e tema claro/escuro;
- consumo de relatórios agregados em vez da base completa.

## Validação atual

No snapshot revisado:

```text
24 passed, 2 skipped
```

Base processada:

```text
1.092.158 registros
2024: 505.950
2025: 586.208
```

Validações da camada de métricas:

- 0 erros de conversão nos campos financeiros, `Ano` e `Data`;
- 0 divergências entre `Ano` e o ano de `Data`;
- 0 IDs repetidos;
- reconciliação anual aprovada para as quatro medidas financeiras.

## Como reproduzir

Todos os comandos devem ser executados a partir da raiz do projeto.

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Conferir as fontes

```bash
python src/scripts/inspect_source.py
```

### 3. Rodar testes

```bash
pytest -q
```

### 4. Smoke test

```bash
python src/scripts/run_pipeline.py --limit-rows-per-source 100
```

### 5. Pipeline completo

```bash
python src/scripts/run_pipeline.py --format csv.gz
```

ou:

```bash
python src/scripts/run_pipeline.py --format parquet
```

### 6. Gerar relatórios analíticos

```bash
python src/scripts/validate_metrics.py
```

### 7. Iniciar o painel

```bash
python app.py
```

## Diretórios de trabalho

### Fonte

```text
src/data/*.csv
```

Os 8 CSVs oficiais são a fonte da verdade.

### Camada processada

```text
src/data/processed/
```

Essa é a interface entre o pipeline e a camada analítica.

### Relatórios consumidos pelo painel

```text
src/data/reports/
```

O Dash não deve ler os CSVs oficiais nem a camada processada completa em cada callback.

## Questões e páginas

### Painel Principal

Página executiva de entrada. Resume o recorte, apresenta indicadores gerais e introduz as análises estatísticas.

### Visão Geral

Pergunta:

> Como os valores empenhados, liquidados, pagos e de restos a pagar evoluem entre 2024 e 2025?

### Despesas

Pergunta:

> Em quais elementos e subelementos de despesa os recursos públicos estão sendo aplicados?

### Favorecidos e Contratações

Pergunta:

> Como os pagamentos se distribuem entre os favorecidos e os tipos de licitação? Existe concentração relevante dos valores pagos?

### Rastreabilidade

Pergunta:

> Quais registros, documentos e processos compõem os valores apresentados no painel?

## Métricas já disponíveis

Consulte `docs/METRICS.md` para fórmulas e limitações.

### Validadas tecnicamente

```text
Soma de ValorEmpenho
Soma de ValorLiquidado
Soma de ValorPago
Soma de ValorRap
Totais por ano
Totais por mês
Totais por UnidadeGestora
```

### Validadas para uso analítico em recorte explícito

Escopo principal:

```text
ValorPago > 0
```

Disponíveis:

- quantidade e proporção de registros com pagamento positivo;
- soma dos pagamentos positivos;
- média, mediana, quartis e desvio-padrão;
- regra de boxplot;
- intervalo de confiança de 95% da média;
- concentração por favorecido;
- distribuição do valor positivo por `TipoLicitacao`.

## Números de referência da validação

Totais líquidos da base:

| Métrica | Total |
|---|---:|
| ValorEmpenho | R$ 22.260.089.498,27 |
| ValorLiquidado | R$ 20.159.865.427,63 |
| ValorPago | R$ 21.612.307.088,15 |
| ValorRap | R$ 2.160.152.532,38 |

Pagamentos positivos:

- 316.029 registros;
- 28,94% da base;
- soma positiva de R$ 22.795.053.118,57;
- mediana de R$ 1.290,98;
- média de R$ 72.129,62;
- IC95% da média: aproximadamente R$ 68.586,12 a R$ 75.673,13.

Concentração:

- 21.961 favorecidos com pagamento positivo;
- Top 10 concentram aproximadamente 45,01% do valor positivo.

## Limitações que não podem ser esquecidas

### Valores financeiros

Existem muitos zeros e movimentos negativos. Eles são preservados e não devem ser descartados automaticamente.

Em 2024, `ValorLiquidado` e `ValorPago` superam `ValorEmpenho`. Não usar diretamente razões entre esses campos como taxa de execução sem uma regra de negócio validada.

### `ValorRap`

Representa pagamento do período associado a empenho de exercício anterior. Não tratá-lo como uma etapa adicional do mesmo fluxo anual sem justificar a interpretação.

### Processo

- `NumeroProcesso` quase não é preenchido;
- `Processo` e `ProcessoAssunto` têm preenchimento muito baixo;
- priorizar `CodigoProcesso`, `Documento`, `DocumentoEmpenho`, `Id` e proveniência.

### Órgão

`Orgao` está vazio na base auditada. Priorizar `UnidadeGestora`.

### Licitação

`TipoLicitacao` possui 18 valores observados. Não reduzir automaticamente para um conjunto menor.

`TipoLicitacao` e `Modalidade` são campos diferentes.

### Estatística

- boxplot identifica valores extremos pela regra estatística, não fraude;
- concentração não implica irregularidade;
- o intervalo de confiança atual se refere à média dos registros com pagamento positivo;
- a proporção de `ValorPago > 0` é uma frequência empírica da base, não uma probabilidade causal.

## Artefatos importantes

Código:

```text
src/pipeline/
src/analytics/metrics.py
src/scripts/run_pipeline.py
src/scripts/validate_metrics.py
src/pages/
```

Documentação:

```text
docs/DATA_CONTRACT.md
docs/INITIAL_DATA_AUDIT.md
docs/METRICS.md
docs/HANDOFF.md
README.md
```

Relatórios:

```text
src/data/reports/metrics_validation.json
src/data/reports/metrics_quality.csv
src/data/reports/metrics_by_year.csv
src/data/reports/metrics_by_month.csv
src/data/reports/metrics_by_unit.csv
src/data/reports/metrics_by_element.csv
src/data/reports/metrics_by_subelement.csv
src/data/reports/metrics_by_beneficiary.csv
src/data/reports/metrics_by_licitacao.csv
src/data/reports/metrics_by_process.csv
src/data/reports/payment_statistics.csv
src/data/reports/beneficiary_concentration.csv
src/data/reports/beneficiary_concentration_summary.csv
src/data/reports/payments_by_licitacao_positive.csv
src/data/reports/variable_catalog.csv
```

## Deploy no Render

O projeto está pronto para Web Service com:

Build Command:

```bash
pip install -r requirements.txt
```

Start Command recomendado:

```bash
gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

Alternativa para a POC:

```bash
python app.py
```

O pacote `gunicorn` já está declarado em `requirements.txt`.

O deploy precisa ter acesso aos arquivos de `src/data/reports/`. Se eles não forem versionados, será necessário providenciar uma etapa externa que os gere ou disponibilize antes da inicialização da aplicação.

## O que a próxima equipe deve fazer

Prioridade sugerida:

1. revisar `METRICS.md` antes de adicionar novos KPIs;
2. manter as quatro perguntas analíticas como referência de produto;
3. validar qualquer nova métrica com teste e documentação;
4. melhorar os filtros e a jornada sem duplicar regras de análise nos callbacks;
5. reforçar rastreabilidade de pelo menos um resultado da POC;
6. validar responsividade e acessibilidade;
7. preparar demonstração com dados e limitações visíveis;
8. manter README, contrato de dados e handoff atualizados a cada mudança relevante.

## Regra de continuidade

A próxima equipe não precisa reconstruir o pipeline.

O trabalho deve continuar a partir de:

```text
src/data/processed/
src/data/reports/
src/analytics/metrics.py
src/pages/
docs/METRICS.md
```

Novas regras de negócio não devem ser criadas diretamente no front-end.
