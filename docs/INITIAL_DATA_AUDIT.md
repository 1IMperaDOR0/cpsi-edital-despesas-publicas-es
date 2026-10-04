# Auditoria Inicial dos Dados

## Escopo

A auditoria foi executada sobre os oito CSVs oficiais de despesas de 2024 e 2025 usados pela POC.

Inventário validado:

- 8 arquivos CSV;
- 4 partes de 2024;
- 4 partes de 2025;
- 71 colunas em cada arquivo;
- mesmo schema nas 8 partes;
- 1.092.158 registros no total.

Distribuição de registros:

| Ano | Registros |
|---|---:|
| 2024 | 505.950 |
| 2025 | 586.208 |
| **Total** | **1.092.158** |

## Validação estrutural final

A camada processada apresentou:

- 0 erros de conversão em `Ano`, `Data`, `ValorEmpenho`, `ValorLiquidado`, `ValorPago` e `ValorRap`;
- 0 inconsistências entre `Ano` e o ano de `Data`;
- 0 linhas com `Id` repetido;
- reconciliação aprovada entre os totais gerais e a soma dos totais anuais.

A diferença residual de ponto flutuante observada em `ValorLiquidado` foi inferior a R$ 0,01 e ficou dentro da tolerância da validação.

## Achados de preenchimento

### `Orgao`

- 100% ausente nos 1.092.158 registros auditados.
- `CodigoOrgao` está preenchido na fonte.

**Implicação:** não usar `Orgao` como dimensão textual principal. Utilizar `UnidadeGestora` até existir um mapeamento validado para `CodigoOrgao`.

### Processo

Preenchimento observado:

- `NumeroProcesso`: 99,9999% ausente;
- `CodigoProcesso`: aproximadamente 0,0299% ausente;
- `ProcessoAssunto`: aproximadamente 98,9529% ausente;
- `Processo`: aproximadamente 98,9545% ausente.

**Implicação:** priorizar `CodigoProcesso`, `Documento`, `DocumentoEmpenho`, `Id` e metadados de proveniência na página de rastreabilidade.

`NumeroProcesso`, `Processo` e `ProcessoAssunto` podem ser apresentados quando existirem, mas não devem sustentar uma funcionalidade obrigatória.

## `TipoLicitacao`

Foram observados 18 valores distintos:

| TipoLicitacao | Registros |
|---|---:|
| NÃO APLICÁVEL - DEMAIS CASOS | 428.887 |
| NÃO APLICÁVEL - DIÁRIAS | 248.568 |
| PREGÃO | 211.062 |
| DISPENSA DE LICITAÇÃO | 67.354 |
| INEXIGÍVEL | 46.379 |
| INEXIGIBILIDADE DE LICITAÇÃO | 35.243 |
| CONCORRÊNCIA | 21.476 |
| ADESÃO À ATA DE REGISTRO DE PREÇOS | 18.415 |
| NÃO APLICÁVEL - ADIANTAMENTO DE SUPRIMENTO DE FUNDOS | 4.593 |
| CONCURSO | 3.625 |
| REGIME DIFERENCIADO DE CONTRATAÇÕES PÚBLICAS (RDC) | 2.057 |
| TOMADA DE PREÇOS | 1.619 |
| CONTRATAÇÃO ENVOLVENDO RECURSO DE ORGANISMO FINANCEIRO INTERNACIONAL | 1.034 |
| EMPRESA PÚBLICA E SOCIEDADE DE ECONOMIA MISTA (uso exclusivo da Ceasa) | 740 |
| LICITAÇÕES INTERNACIONAIS | 656 |
| CONSULTA | 386 |
| LEILÃO | 50 |
| CONVITE | 14 |

**Implicação:** não reduzir automaticamente `TipoLicitacao` para um número fixo de categorias sem uma regra formal.

Também é importante não confundir `TipoLicitacao` com `Modalidade`, pois são campos distintos na fonte.

## Medidas financeiras

Qualidade da camada processada:

| Métrica | Preenchidos | Ausentes | Negativos | Zeros |
|---|---:|---:|---:|---:|
| ValorEmpenho | 1.092.158 | 0 | 19.443 | 973.509 |
| ValorLiquidado | 1.092.158 | 0 | 212.801 | 497.558 |
| ValorPago | 1.092.158 | 0 | 22.633 | 753.496 |
| ValorRap | 1.092.158 | 0 | 1.038 | 1.051.911 |

Os valores negativos e zeros são preservados. Eles podem representar movimentos legítimos, estornos, ajustes ou ausência de movimentação naquela etapa e não devem ser removidos sem investigação.

## Totais técnicos

| Métrica | Total |
|---|---:|
| ValorEmpenho | R$ 22.260.089.498,27 |
| ValorLiquidado | R$ 20.159.865.427,63 |
| ValorPago | R$ 21.612.307.088,15 |
| ValorRap | R$ 2.160.152.532,38 |

Por ano:

| Ano | ValorEmpenho | ValorLiquidado | ValorPago | ValorRap |
|---|---:|---:|---:|---:|
| 2024 | R$ 7.220.650.612,93 | R$ 8.234.487.893,88 | R$ 10.337.098.858,62 | R$ 1.452.428.885,56 |
| 2025 | R$ 15.039.438.885,34 | R$ 11.925.377.533,75 | R$ 11.275.208.229,53 | R$ 707.723.646,82 |

### Implicação analítica

Em 2024, `ValorLiquidado` e `ValorPago` superam `ValorEmpenho` no mesmo recorte anual. Portanto, não é seguro interpretar os quatro campos como uma cadeia linear simples do mesmo conjunto de despesas dentro do ano.

Razões como `ValorPago / ValorEmpenho` ou `ValorLiquidado / ValorEmpenho` não devem receber automaticamente nomes como "taxa de execução" ou "taxa de liquidação".

## Recorte de pagamentos positivos

Algumas análises estatísticas usam explicitamente:

```text
ValorPago > 0
```

Nesse recorte:

- 316.029 registros têm pagamento positivo;
- isso representa aproximadamente 28,94% dos registros;
- soma dos pagamentos positivos: R$ 22.795.053.118,57;
- mediana do pagamento positivo: R$ 1.290,98;
- média do pagamento positivo: R$ 72.129,62.

A soma de pagamentos positivos é maior que o total líquido de `ValorPago` porque os registros negativos são excluídos desse recorte.

## Decisões adotadas

1. Preservar zeros e negativos.
2. Não recodificar `TipoLicitacao` automaticamente.
3. Usar `UnidadeGestora` como dimensão administrativa nominal principal.
4. Priorizar `CodigoProcesso` e documentos na rastreabilidade.
5. Excluir identificadores pessoais e campos bancários da camada analítica quando não necessários.
6. Manter as estatísticas de pagamentos positivos identificadas como um recorte específico.
7. Tratar outliers como observações estatísticas, não como indício automático de irregularidade.

## Próximas verificações úteis

- aprofundar a interpretação dos movimentos negativos;
- investigar a relação entre `ValorPago` e `ValorRap`;
- validar recortes específicos por `UnidadeGestora`;
- revisar concentração por favorecido antes de qualquer interpretação de risco;
- documentar qualquer nova métrica derivada em `METRICS.md`.
