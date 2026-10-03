# CPSI - Despesas Públicas do Espírito Santo

## Objetivo desta etapa

Esta versão do projeto está focada no **pipeline de dados** e em deixar um contrato simples e documentado para que vocês possam assumir posteriormente a análise e o painel em Dash.

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
Dash (etapa futura)
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
data/processed/
data/reports/
```

Entre os relatórios esperados:

```text
data/reports/manifest.json
data/reports/quality_summary.csv
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

Para a futura aplicação analítica, a preferência é utilizar a camada processada, e não os CSVs oficiais diretamente.

## Regra para o futuro painel Dash

O Dash não deve ler ou tratar diretamente os CSVs oficiais.

Arquitetura esperada:

```text
src/data/*.csv
       ↓
   Pipeline
       ↓
data/processed/
       ↓
    Dash
```

Isso separa as responsabilidades entre as equipes.

A equipe responsável pelo painel deve receber dados já:

- identificados;
- validados;
- tipados;
- tratados;
- documentados;
- rastreáveis.

## Páginas Dash - apenas esqueleto

Nesta etapa ainda não foram implementados gráficos, callbacks ou KPIs definitivos.

As páginas existem apenas para representar a futura jornada analítica.

### 1. Visão Geral

**Pergunta norteadora:**

> Como os valores empenhados, liquidados, pagos e de restos a pagar evoluem entre 2024 e 2025?

Arquivo:

```text
src/pages/overview.py
```

### 2. Despesas

**Pergunta norteadora:**

> Em quais elementos e subelementos de despesa os recursos públicos estão sendo aplicados?

Arquivo:

```text
src/pages/despesas.py
```

### 3. Favorecidos e Contratações

**Pergunta norteadora:**

> Para quem os recursos foram destinados e como os pagamentos se distribuem entre as modalidades de contratação?

Arquivo:

```text
src/pages/favorecidos.py
```

### 4. Rastreabilidade

**Pergunta norteadora:**

> Quais registros, documentos e processos compõem os valores apresentados no painel?

Arquivo:

```text
src/pages/rastreabilidade.py
```

## Ordem recomendada de validação

Antes de avançar para gráficos e callbacks, execute nesta ordem:

```text
1. Instalar dependências
       ↓
2. python src/scripts/inspect_source.py
       ↓
3. pytest -q
       ↓
4. python src/scripts/run_pipeline.py --limit-rows-per-source 100
       ↓
5. Conferir os arquivos gerados
       ↓
6. Fazer exploração dos dados
       ↓
7. Definir métricas e KPIs
       ↓
8. Implementar o Dash
```

## Próxima etapa recomendada

Depois que o pipeline estiver validado localmente, a próxima etapa deve ser a exploração da camada processada.

A primeira exploração deve verificar:

- quantidade de registros;
- tipos das colunas;
- valores ausentes;
- duplicidades;
- cardinalidade das dimensões;
- comportamento de `ValorEmpenho`;
- comportamento de `ValorLiquidado`;
- comportamento de `ValorPago`;
- comportamento de `ValorRap`;
- distribuição de `UnidadeGestora`;
- distribuição de `Favorecido`;
- distribuição de `TipoLicitacao`;
- distribuição de `ElementoDespesa`;
- distribuição de `SubelementoDespesa`;
- comparação entre 2024 e 2025.

Somente depois dessa validação devem ser definidos os indicadores definitivos do painel.

## Documentação complementar

Consulte também:

```text
docs/DATA_CONTRACT.md
docs/HANDOFF.md
docs/INITIAL_DATA_AUDIT.md
```

O contrato de dados documenta quais campos são preservados, quais transformações são permitidas e quais decisões analíticas ainda precisam de validação.

A auditoria inicial registra os principais achados encontrados nos arquivos reais antes da construção do painel.
