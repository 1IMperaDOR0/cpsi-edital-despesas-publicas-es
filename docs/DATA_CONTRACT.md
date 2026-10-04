# Contrato de Dados — Camada Processada

## Objetivo

Este documento define o contrato entre os CSVs oficiais, o pipeline, a camada analítica e o painel.

Os arquivos oficiais em `src/data/` continuam sendo a **fonte da verdade**. A camada processada existe para padronizar tipos, reduzir exposição desnecessária de dados, registrar proveniência e fornecer uma interface estável para análises posteriores.

## Fluxo

```text
src/data/*.csv
      ↓
pipeline
      ↓
src/data/processed/
      ↓
analytics / validate_metrics.py
      ↓
src/data/reports/
      ↓
Dash
```

O painel não deve aplicar novamente regras de limpeza nem ler os CSVs brutos em cada callback.

## Regras de tratamento

1. Nenhuma linha é removida silenciosamente.
2. Valores ausentes não são imputados automaticamente.
3. Categorias de negócio não são recodificadas sem regra documentada.
4. Os quatro valores financeiros são convertidos para tipo numérico.
5. `Data` é convertida para datetime.
6. Códigos e identificadores são preservados como texto quando necessário para evitar perda de zeros à esquerda.
7. Campos pessoais ou bancários sem necessidade analítica não entram na camada curada.
8. Cada registro recebe metadados de proveniência.
9. Zeros e valores negativos são preservados.
10. Métricas derivadas não fazem parte da limpeza; ficam na camada `analytics`.

## Medidas financeiras

Campos preservados:

```text
ValorEmpenho
ValorLiquidado
ValorPago
ValorRap
```

Definições de origem:

- `ValorEmpenho`: valor reservado para pagamento de produto ou serviço.
- `ValorLiquidado`: valor associado a produto entregue ou serviço prestado e atestado.
- `ValorPago`: valor pago ao favorecido.
- `ValorRap`: valor pago no período cujo empenho ocorreu em ano anterior.

### Regra de uso

Esses campos podem ser somados tecnicamente nos recortes usados pelo painel, mas sua relação não deve ser interpretada como uma sequência linear única sem validação semântica.

Em especial, não assumir automaticamente:

```text
ValorEmpenho >= ValorLiquidado >= ValorPago
```

nem definir como KPI, sem regra adicional:

```text
ValorPago / ValorEmpenho
ValorLiquidado / ValorEmpenho
```

## Dimensões principais preservadas

### Tempo

```text
Ano
Data
Mes
AnoMes
```

### Favorecido e contratação

```text
TipoFavorecido
Favorecido
IdFavorecido
TipoLicitacao
Modalidade
NumeroLicitacao
AnoLicitacao
Contrato
```

`TipoLicitacao` e `Modalidade` são campos distintos da fonte e não devem ser tratados como sinônimos sem uma regra de negócio explícita.

### Classificação da despesa

```text
CategoriaEconomica
GrupoDespesa
ElementoDespesa
DescricaoElementoDespesa
SubelementoDespesa
Fonte
Funcao
SubFuncao
Programa
Acao
```

### Unidade administrativa

```text
CodigoUnidadeGestora
UnidadeGestora
CodigoOrgao
Orgao
```

Na base auditada, `Orgao` está vazio; `UnidadeGestora` deve ser a dimensão nominal principal enquanto não houver um mapeamento validado de `CodigoOrgao`.

### Processo e documentos

```text
HistoricoDocumento
Documento
DocumentoEmpenho
CodigoProcesso
Processo
ProcessoAssunto
NumeroProcesso
Id
```

A rastreabilidade principal deve priorizar `CodigoProcesso`, `Documento`, `DocumentoEmpenho`, `Id` e os campos de proveniência. `NumeroProcesso`, `Processo` e `ProcessoAssunto` têm baixo preenchimento e são complementares.

## Dimensões derivadas

```text
Mes
AnoMes
```

Esses campos são derivados de `Data` e não alteram a semântica da fonte.

## Proveniência

Cada registro processado recebe:

```text
_source_file
_source_year
_source_part
_source_row
```

`_source_row` aponta para a linha aproximada no CSV de origem e considera o cabeçalho como linha 1.

A proveniência deve ser preservada quando uma análise precisar chegar ao registro de origem.

## Minimização de dados

Por padrão, não entram na camada analítica campos desnecessários para as perguntas da POC, especialmente:

```text
CpfCnpjNis
BancoOrigem
AgenciaOrigem
DomicilioBancarioOrigem
```

A exclusão desses campos reduz exposição de identificadores pessoais e dados bancários sem prejudicar as análises previstas.

## Qualidade conhecida

Na auditoria da base completa:

- 8 arquivos foram identificados;
- 1.092.158 registros foram processados;
- as 8 partes apresentam o mesmo schema de 71 colunas;
- `Ano` e `Data` não apresentaram divergência de ano na validação final;
- `Id` não apresentou valores repetidos na validação final;
- as quatro medidas financeiras não apresentaram falhas de conversão na camada processada.

Limitações relevantes:

- `Orgao`: 100% ausente;
- `NumeroProcesso`: praticamente todo ausente;
- `Processo` e `ProcessoAssunto`: preenchimento muito baixo;
- `TipoLicitacao`: 18 valores distintos observados na fonte;
- existem valores financeiros negativos e grande quantidade de zeros.

## Interface para o painel

O Dash deve consumir os relatórios agregados de:

```text
src/data/reports/
```

Relatórios principais:

```text
metrics_by_year.csv
metrics_by_month.csv
metrics_by_unit.csv
metrics_by_element.csv
metrics_by_subelement.csv
metrics_by_beneficiary.csv
metrics_by_licitacao.csv
metrics_by_process.csv
payment_statistics.csv
beneficiary_concentration.csv
beneficiary_concentration_summary.csv
payments_by_licitacao_positive.csv
variable_catalog.csv
```

A camada de apresentação não deve alterar fórmulas, remover registros ou criar regras de negócio novas.

## Alterações futuras no contrato

Qualquer mudança que altere o significado de um campo, exclua registros ou recodifique categorias deve:

1. ser documentada;
2. possuir teste automatizado quando aplicável;
3. registrar impacto nos relatórios existentes;
4. atualizar `METRICS.md` e `HANDOFF.md` quando afetar o painel.
