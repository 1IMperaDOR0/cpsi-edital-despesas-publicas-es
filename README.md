# CPSI - Despesas Públicas do Espírito Santo

## Objetivo desta etapa

Esta versão do projeto inclui o **pipeline de dados**, os relatórios agregados e um painel Dash com gráficos para explorar as despesas públicas do Espírito Santo.

Fluxo atual:

```text
CSVs oficiais 2024/2025
        ↓
data_loader.py
        ↓
validação de schema
        ↓
cleaning.py
        ↓
transformations.py
        ↓
quality / profiling
        ↓
camada processada
        ↓
relatórios agregados em src/data/reports/
        ↓
Dash
```

## Estrutura do projeto

```text
cpsi-edital-despesas-publicas-es/
├── app.py
├── requirements.txt
├── src/
│   ├── data/
│   │   ├── despesas_es_2024_completo_parte_01.csv
│   │   ├── ...
│   │   └── despesas_es_2025_completo_parte_04.csv
│   ├── pipeline/
│   │   ├── config.py
│   │   ├── data_loader.py
│   │   ├── schema.py
│   │   ├── cleaning.py
│   │   ├── transformations.py
│   │   ├── profiling.py
│   │   ├── writer.py
│   │   └── runner.py
│   ├── pages/
│   │   ├── painel_principal.py
│   │   ├── overview.py
│   │   ├── despesas.py
│   │   ├── favorecidos.py
│   │   └── rastreabilidade.py
│   └── scripts/
│       ├── inspect_source.py
│       └── run_pipeline.py
├── tests/
└── docs/
```

## Como executar o projeto

Todos os comandos devem ser executados a partir da **raiz do projeto**.

Exemplo no Windows:

```bash
cd c:\AllThings\projects\cpsi-edital-despesas-publicas-es
```

A raiz deve conter arquivos e pastas como:

```text
app.py
requirements.txt
src/
tests/
docs/
```

### Importante sobre `src/pipeline`

Os arquivos em `src/pipeline/` são **módulos internos do projeto**. Eles foram criados para serem importados por outros componentes e, em regra, não devem ser executados diretamente pelo caminho do arquivo.

Evite:

```bash
python src/pipeline/data_loader.py
```

Esse tipo de execução pode causar erros de importação como:

```text
ModuleNotFoundError: No module named 'src.pipeline'
```

Se for necessário executar um módulo diretamente para teste, use a notação de módulo a partir da raiz:

```bash
python -m src.pipeline.data_loader
```

Os pontos de entrada destinados à execução ficam preferencialmente em:

```text
src/scripts/
```

Exemplos:

```bash
python src/scripts/inspect_source.py
python src/scripts/run_pipeline.py --limit-rows-per-source 100
```

## Instalação das dependências

A partir da raiz do projeto:

```bash
pip install -r requirements.txt
```

Recomenda-se utilizar ambiente virtual.

Exemplo no Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Dados de entrada

Os arquivos oficiais devem permanecer em:

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

Os CSVs oficiais são a **fonte da verdade** e não devem ser alterados manualmente.

## Carregando os dados

O módulo responsável por localizar e carregar os arquivos é:

```text
src/pipeline/data_loader.py
```

> `data_loader.py` é um módulo do pipeline. Normalmente ele será importado por outros componentes e não executado diretamente.

### Descobrir as fontes disponíveis

```python
from src.pipeline.data_loader import discover_sources

sources = discover_sources()

for source in sources:
    print(source.key, source.csv_path.name)
```

Resultado esperado:

```text
2024-parte-01 despesas_es_2024_completo_parte_01.csv
2024-parte-02 despesas_es_2024_completo_parte_02.csv
2024-parte-03 despesas_es_2024_completo_parte_03.csv
2024-parte-04 despesas_es_2024_completo_parte_04.csv
2025-parte-01 despesas_es_2025_completo_parte_01.csv
2025-parte-02 despesas_es_2025_completo_parte_02.csv
2025-parte-03 despesas_es_2025_completo_parte_03.csv
2025-parte-04 despesas_es_2025_completo_parte_04.csv
```

### Carregar uma amostra pequena

Para testes, exploração ou depuração, pode-se utilizar `load_data()`:

```python
from src.pipeline.data_loader import load_data

amostra = load_data(
    years=(2024,),
    usecols=["Ano", "Data", "Favorecido", "ValorPago"],
    rows_per_source=500,
)

print(amostra.head())
print(amostra.shape)
```

`load_data()` concatena os dados em memória. Por isso, deve ser usado principalmente para:

- exploração;
- testes;
- depuração;
- conferência visual;
- amostras reduzidas.

Para o processamento completo da base, use o pipeline em chunks.

## Responsabilidade de cada módulo do pipeline

```text
data_loader.py
→ localiza e carrega os arquivos

schema.py
→ valida a estrutura esperada

cleaning.py
→ limpa e converte tipos

transformations.py
→ cria campos derivados permitidos

profiling.py
→ mede qualidade e características dos dados

writer.py
→ grava a camada processada

runner.py
→ coordena a execução completa do pipeline
```

## Inspeção rápida da fonte

Antes de processar os dados, execute:

```bash
python src/scripts/inspect_source.py
```

O script deve verificar o inventário e o schema sem carregar a base inteira em memória.

Resultado esperado: identificação dos 8 arquivos, com o mesmo conjunto de colunas.

## Testes automatizados

Execute:

```bash
pytest -q
```

Para executar apenas os testes de integração com os arquivos reais:

```bash
pytest -q -m integration
```

Os testes devem validar, entre outros pontos:

- descoberta das fontes;
- presença das partes de 2024 e 2025;
- consistência de schema;
- conversão de tipos;
- comportamento da limpeza;
- transformações;
- execução do pipeline.

## Smoke test do pipeline

Antes de processar a base completa, execute uma amostra pequena:

```bash
python src/scripts/run_pipeline.py --limit-rows-per-source 100
```

Com 8 arquivos, o resultado esperado é aproximadamente:

```text
800 registros processados
```

Esse teste serve para confirmar o funcionamento do fluxo completo:

```text
CSV
 ↓
data_loader
 ↓
schema
 ↓
cleaning
 ↓
transformations
 ↓
quality / profiling
 ↓
writer
```

## Saídas do pipeline

A execução gera arquivos em:

```text
src/data/processed/
src/data/reports/
```

Os relatórios incluem:

```text
src/data/reports/manifest.json
src/data/reports/quality_summary.csv
src/data/reports/metrics_by_year.csv
src/data/reports/metrics_by_month.csv
src/data/reports/metrics_by_unit.csv
src/data/reports/metrics_by_element.csv
src/data/reports/metrics_by_subelement.csv
src/data/reports/metrics_by_beneficiary.csv
src/data/reports/metrics_by_licitacao.csv
src/data/reports/metrics_by_process.csv
```

## Pipeline completo

Somente depois que testes e smoke test estiverem funcionando corretamente, execute a base completa.

### Saída CSV compactada

```bash
python src/scripts/run_pipeline.py --format csv.gz
```

### Saída Parquet

```bash
python src/scripts/run_pipeline.py --format parquet
```

Depois de gerar a camada processada, crie os relatórios usados pelo painel:

```bash
python src/scripts/validate_metrics.py
```

O script calcula os totais financeiros e os agregados por despesa, favorecido, tipo de licitação e processo. O painel lê esses CSVs prontos em `src/data/reports/`; ele não carrega a base completa no navegador.

## Painel Dash

O Dash não lê nem trata diretamente os CSVs oficiais. O fluxo atual é:

```text
src/data/*.csv
       ↓
   Pipeline
       ↓
src/data/processed/
       ↓
validate_metrics.py
       ↓
src/data/reports/*.csv
       ↓
    Dash
```

Para iniciar o painel, execute na raiz do projeto:

```bash
python app.py
```

A página inicial apresenta a narrativa geral do projeto. As quatro páginas analíticas respondem às perguntas que orientam o painel:

### Painel Principal

Apresenta o contexto da base, indicadores gerais, evolução dos valores, dispersão dos pagamentos e intervalos de confiança. Os filtros de ano e medida financeira atualizam o recorte e as séries temporais.

Arquivo e rota: src/pages/painel_principal.py — /

### 1. Visão Geral

**Pergunta:**

> Como os valores empenhados, liquidados, pagos e de restos a pagar evoluem entre 2024 e 2025?

Arquivo e rota: src/pages/overview.py — /visao-geral

### 2. Despesas

**Pergunta:**

> Em quais elementos e subelementos de despesa os recursos públicos estão sendo aplicados?

Arquivo e rota: src/pages/despesas.py — /despesas

### 3. Favorecidos e Contratações

**Pergunta:**

> Para quem os recursos foram destinados e como os pagamentos se distribuem entre as modalidades de contratação?

Arquivo e rota: src/pages/favorecidos.py — /favorecidos

### 4. Rastreabilidade

**Pergunta:**

> Quais registros, documentos e processos compõem os valores apresentados no painel?

Arquivo e rota: src/pages/rastreabilidade.py — /rastreabilidade

## Fluxo recomendado

Execute nesta ordem para atualizar os dados do painel:

```text
1. Instalar dependências
       ↓
2. python src/scripts/inspect_source.py
       ↓
3. python src/scripts/run_pipeline.py
       ↓
4. python src/scripts/validate_metrics.py
       ↓
5. python app.py
```

## Observação sobre as métricas

Os gráficos apresentam agregações dos valores como constam nos registros. A documentação do contrato ainda recomenda validar a semântica e o nível seguro de soma dessas medidas antes de tratá-las como KPIs definitivos.

## Documentação complementar

Consulte também:

```text
docs/DATA_CONTRACT.md
docs/HANDOFF.md
docs/INITIAL_DATA_AUDIT.md
```

O contrato de dados documenta quais campos são preservados, quais transformações são permitidas e quais decisões analíticas ainda precisam de validação.

A auditoria inicial registra os principais achados encontrados nos arquivos reais antes da construção do painel.
