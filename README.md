# CPSI — Despesas Públicas do Espírito Santo

POC acadêmica de um painel de transparência para explorar despesas públicas do Governo do Espírito Santo referentes a 2024 e 2025.

O projeto transforma os CSVs oficiais em uma camada tratada, gera relatórios analíticos pré-calculados e apresenta os resultados em uma aplicação web construída com Dash e Plotly.

## Público e proposta de valor

O público prioritário é formado por cidadãos e jornalistas que desejam acompanhar e compreender a aplicação de recursos públicos sem manipular diretamente os arquivos brutos. Pesquisadores, gestores e profissionais de controle também podem utilizar a solução como apoio à exploração e à rastreabilidade dos registros.

A proposta de valor é oferecer uma consulta simples, visual e auditável, permitindo comparar períodos e medidas financeiras, explorar categorias de gasto e favorecidos e chegar aos registros que sustentam os resultados apresentados.

## Questões analíticas

A POC foi organizada em torno de quatro perguntas:

1. Como os valores empenhados, liquidados, pagos e de restos a pagar evoluem entre 2024 e 2025?
2. Em quais elementos e subelementos de despesa os recursos públicos estão sendo aplicados?
3. Como os pagamentos se distribuem entre os favorecidos e os tipos de licitação? Existe concentração relevante dos valores pagos?
4. Quais registros, documentos e processos compõem os valores apresentados no painel?

## Arquitetura

```text
CSVs oficiais 2024/2025
        ↓
data_loader.py
        ↓
schema.py
        ↓
cleaning.py
        ↓
transformations.py
        ↓
profiling.py
        ↓
src/data/processed/
        ↓
validate_metrics.py
        ↓
src/data/reports/
        ↓
Dash + Plotly
```

Responsabilidades:

- **Fonte:** 8 CSVs oficiais, 4 de 2024 e 4 de 2025.
- **Pipeline:** descoberta, validação de schema, leitura em chunks, limpeza, transformação, qualidade e proveniência.
- **Camada processada:** arquivos CSV.GZ ou Parquet com dados tratados.
- **Analytics:** métricas e relatórios agregados produzidos a partir da camada processada.
- **Apresentação:** Dash + Plotly consumindo relatórios agregados, sem carregar os CSVs brutos em cada interação.

## Estrutura principal

```text
cpsi-edital-despesas-publicas-es/
├── app.py
├── requirements.txt
├── docs/
│   ├── DATA_CONTRACT.md
│   ├── HANDOFF.md
│   ├── INITIAL_DATA_AUDIT.md
│   └── METRICS.md
├── src/
│   ├── analytics/
│   │   └── metrics.py
│   ├── assets/
│   ├── data/
│   │   ├── despesas_es_2024_completo_parte_01.csv
│   │   ├── ...
│   │   ├── despesas_es_2025_completo_parte_04.csv
│   │   ├── processed/
│   │   └── reports/
│   ├── pages/
│   │   ├── painel_principal.py
│   │   ├── overview.py
│   │   ├── despesas.py
│   │   ├── favorecidos.py
│   │   └── rastreabilidade.py
│   ├── pipeline/
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   ├── schema.py
│   │   ├── cleaning.py
│   │   ├── transformations.py
│   │   ├── profiling.py
│   │   ├── writer.py
│   │   └── runner.py
│   └── scripts/
│       ├── inspect_source.py
│       ├── run_pipeline.py
│       └── validate_metrics.py
└── tests/
```

## Pré-requisitos

- Python 3.12 recomendado para reproduzir o ambiente usado no deploy atual.
- Dependências declaradas em `requirements.txt`.

A partir da raiz do projeto:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

Linux/macOS:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Dados de entrada

Os 8 CSVs oficiais devem ficar diretamente em:

```text
src/data/
```

Arquivos esperados:

```text
despesas_es_2024_completo_parte_01.csv
despesas_es_2024_completo_parte_02.csv
despesas_es_2024_completo_parte_03.csv
despesas_es_2024_completo_parte_04.csv
despesas_es_2025_completo_parte_01.csv
despesas_es_2025_completo_parte_02.csv
despesas_es_2025_completo_parte_03.csv
despesas_es_2025_completo_parte_04.csv
```

Os arquivos oficiais são a fonte da verdade e não devem ser editados manualmente.

## Importante sobre `src/pipeline`

Os arquivos em `src/pipeline/` são módulos internos. Eles devem ser importados pelo projeto e, em regra, não executados diretamente pelo caminho do arquivo.

Evite:

```bash
python src/pipeline/data_loader.py
```

Os pontos de entrada de execução ficam em `src/scripts/`.

## Fluxo de execução recomendado

### 1. Verificar as fontes

```bash
python src/scripts/inspect_source.py
```

### 2. Rodar os testes

```bash
pytest -q
```

No snapshot revisado desta versão:

```text
24 passed, 2 skipped
```

Os testes marcados como integração podem depender da presença dos arquivos reais.

### 3. Smoke test do pipeline

```bash
python src/scripts/run_pipeline.py --limit-rows-per-source 100
```

Com 8 fontes, o esperado é processar aproximadamente 800 registros.

### 4. Executar o pipeline completo

CSV compactado:

```bash
python src/scripts/run_pipeline.py --format csv.gz
```

Parquet:

```bash
python src/scripts/run_pipeline.py --format parquet
```

As saídas são gravadas em:

```text
src/data/processed/
src/data/reports/
```

### 5. Gerar e validar as métricas

```bash
python src/scripts/validate_metrics.py
```

Esse script lê a camada processada, valida as medidas financeiras e gera os relatórios usados pelo painel.

Principais relatórios:

```text
metrics_quality.csv
metrics_validation.json
metrics_by_year.csv
metrics_by_month.csv
metrics_by_unit.csv
metrics_by_element.csv
metrics_by_subelement.csv
metrics_by_beneficiary.csv
metrics_by_licitacao.csv
metrics_by_process.csv
variable_catalog.csv
payment_statistics.csv
beneficiary_concentration.csv
beneficiary_concentration_summary.csv
payments_by_licitacao_positive.csv
```

## Executar o painel

```bash
python app.py
```

O `app.py` utiliza a variável de ambiente `PORT` quando disponível e, localmente, usa a porta 8050 por padrão.

## Páginas

### Painel Principal — `/`

Página executiva com contexto da base, indicadores gerais, séries temporais e estatísticas descritivas.

### Visão Geral — `/visao-geral`

Responde à evolução de `ValorEmpenho`, `ValorLiquidado`, `ValorPago` e `ValorRap` em 2024 e 2025.

### Despesas — `/despesas`

Explora elementos e subelementos de despesa.

### Favorecidos e Contratações — `/favorecidos`

Explora favorecidos, concentração de pagamentos, tipos de licitação, boxplot, probabilidade empírica e intervalo de confiança para o recorte documentado.

### Rastreabilidade — `/rastreabilidade`

Relaciona os resultados aos registros, documentos e processos disponíveis na base.

## Deploy no Render

O projeto está preparado para um **Web Service** no Render.

Build Command:

```bash
pip install -r requirements.txt
```

Start Command recomendado:

```bash
gunicorn app:server --bind 0.0.0.0:$PORT --workers 1 --timeout 120
```

Também é possível iniciar a POC com:

```bash
python app.py
```

Como o painel consome arquivos de `src/data/reports/`, esses relatórios precisam estar disponíveis no ambiente de deploy. Se o pipeline não for executado durante o build, os relatórios necessários devem ser versionados no repositório ou fornecidos por outra fonte persistente.

## Regras de interpretação

- Valores negativos e zeros não são removidos automaticamente.
- `ValorRap` não deve ser somado ou comparado aos demais campos como se todos representassem a mesma etapa de uma única despesa sem considerar sua definição.
- Razões como `ValorPago / ValorEmpenho` não devem ser chamadas automaticamente de taxa de execução.
- Resultados de boxplot e concentração são evidências descritivas e não prova de fraude ou irregularidade.
- Estatísticas baseadas em `ValorPago > 0` devem ser identificadas explicitamente como tal.

Consulte `docs/METRICS.md` para definições, escopos e limitações.

## Documentação

- `docs/DATA_CONTRACT.md`: contrato da camada processada.
- `docs/INITIAL_DATA_AUDIT.md`: achados de qualidade da fonte.
- `docs/METRICS.md`: definições e status das métricas.
- `docs/HANDOFF.md`: estado atual, reprodução e continuidade do projeto.

## Solução

- Solution URL: [GitHub Repository](https://github.com/1IMperaDOR0/cpsi-edital-despesas-publicas-es)
- Live Site URL: [CPSI Solution](https://cpsi-edital-despesas-publicas-es.onrender.com/despesas)
