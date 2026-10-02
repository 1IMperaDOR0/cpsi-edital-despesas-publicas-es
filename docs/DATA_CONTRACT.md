# Contrato de dados - camada analitica

## Objetivo

A camada processada existe para alimentar a análise exploratoria e, depois,
o painel Dash. Ela não substitui os CSVs oficiais em `src/data`, que continuam sendo a
fonte da verdade.

## Regras desta primeira versão

1. Nenhuma linha é removida silenciosamente.
2. Valores ausentes não são imputados.
3. Categorias de negocio não são corrigidas sem evidencia.
4. Valores monetarios são convertidos do formato brasileiro para numero.
5. `Data` e convertida para datetime.
6. Identificadores como `IdFavorecido`, codigos e numero de processo ficam
   como texto para preservar zeros a esquerda quando existirem.
7. `CpfCnpjNis` e campos bancarios não entram na camada analitica.
8. Cada registro recebe origem do arquivo, ano, parte e linha aproximada no
   CSV de origem.
9. Indicadores financeiros derivados ainda não são calculados nesta camada.

## Dimensoes principais preservadas

- Ano e Data
- Favorecido e IdFavorecido
- TipoLicitacao
- Orgao e UnidadeGestora
- GrupoDespesa
- ElementoDespesa
- SubelementoDespesa
- Funcao e SubFuncao
- Programa e Acao
- Modalidade
- Processo, NumeroProcesso e documentos
- NumeroLicitacao e Contrato

## Medidas preservadas

- ValorEmpenho
- ValorLiquidado
- ValorPago
- ValorRap

## Dimensoes derivadas

- Mes
- AnoMes

## Rastreabilidade

- `_source_file`
- `_source_year`
- `_source_part`
- `_source_row`

`_source_row` considera a primeira linha do CSV como cabecalho. Assim, o
primeiro registro de dados recebe o numero 2.

## Decisoes que ainda precisam de validacao analitica

Antes de criar KPIs definitivos, a equipe de análise deve confirmar:

- se os valores representam movimentos ou estados acumulados;
- em qual nivel de agregacao e seguro somar cada medida;
- como `ValorRap` deve ser comparado com os demais valores;
- quais categorias de `TipoLicitacao` entram na jornada principal;
- se ha duplicidade real, repeticao legitima de movimentos ou ambos;
- quais campos devem ser usados para a chave logica de uma despesa.


## Observacoes validadas nos arquivos reais

- `Orgao` esta ausente em todos os registros auditados; use
  `UnidadeGestora` como dimensão textual principal ate existir um mapeamento
  validado para `CodigoOrgao`.
- `NumeroProcesso` quase não e preenchido; priorize `CodigoProcesso` para
  rastreabilidade.
- `ProcessoAssunto` deve ser tratado como campo opcional.
- `TipoLicitacao` possui 18 valores distintos na fonte e não deve ser
  reduzido automaticamente para cinco categorias.
