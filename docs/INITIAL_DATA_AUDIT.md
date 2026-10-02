# Auditoria inicial dos arquivos reais

## Escopo verificado

A auditoria inicial foi executada sobre os oito CSVs da base de 2024 e
2025.

Resultado do inventario:

- 8 arquivos CSV;
- 4 partes de 2024;
- 4 partes de 2025;
- 71 colunas em todos os arquivos;
- mesmo schema nas 8 partes;
- 1.092.158 registros lidos no total.

## Achados importantes para o painel

### `Orgao`

- 100% ausente nos 1.092.158 registros.
- `CodigoOrgao` esta preenchido em 100% dos registros.

Implicacao: o painel nao deve depender de `Orgao` como dimensao textual nesta
primeira versao. `UnidadeGestora` e uma dimensao nominal mais confiavel. Se a
equipe quiser exibir o nome do orgao, sera necessario obter ou construir um
mapeamento validado para `CodigoOrgao`.

### Processo

- `NumeroProcesso`: 99,9999% ausente.
- `CodigoProcesso`: 0,0299% ausente.
- `ProcessoAssunto`: 98,9529% ausente.
- `Processo`: 98,9545% ausente.

Implicacao: a rastreabilidade principal deve usar `CodigoProcesso`,
`Documento`, `DocumentoEmpenho`, `Id` e os campos de origem do pipeline.
`NumeroProcesso` e `ProcessoAssunto` podem aparecer como informacao
complementar quando existirem, mas nao devem sustentar a jornada principal.

### `TipoLicitacao`

Foram encontrados 18 valores distintos na fonte, e nao cinco modalidades.

Distribuicao observada:

| TipoLicitacao | Registros |
|---|---:|
| NAO APLICAVEL - DEMAIS CASOS | 428.887 |
| NAO APLICAVEL - DIARIAS | 248.568 |
| PREGAO | 211.062 |
| DISPENSA DE LICITACAO | 67.354 |
| INEXIGIVEL | 46.379 |
| INEXIGIBILIDADE DE LICITACAO | 35.243 |
| CONCORRENCIA | 21.476 |
| ADESAO A ATA DE REGISTRO DE PRECOS | 18.415 |
| NAO APLICAVEL - ADIANTAMENTO DE SUPRIMENTO DE FUNDOS | 4.593 |
| CONCURSO | 3.625 |
| REGIME DIFERENCIADO DE CONTRATACOES PUBLICAS (RDC) | 2.057 |
| TOMADA DE PRECOS | 1.619 |
| CONTRATACAO ENVOLVENDO RECURSO DE ORGANISMO FINANCEIRO INTERNACIONAL | 1.034 |
| EMPRESA PUBLICA E SOCIEDADE DE ECONOMIA MISTA (uso exclusivo da Ceasa) | 740 |
| LICITACOES INTERNACIONAIS | 656 |
| CONSULTA | 386 |
| LEILAO | 50 |
| CONVITE | 14 |

Os nomes acima foram simplificados sem acentos apenas neste documento tecnico
para facilitar compatibilidade de texto. O pipeline preserva os valores
originais da fonte.

Implicacao: nao criar uma regra de negocio que limite `TipoLicitacao` a cinco
categorias sem uma definicao formal da equipe de analise.

## Decisoes tomadas no pipeline por causa da auditoria

1. O pipeline preserva categorias de `TipoLicitacao` sem recodificacao.
2. `UnidadeGestora` permanece como dimensao principal para a futura analise
   organizacional.
3. `CodigoProcesso` e tratado como referencia de processo mais confiavel do
   que `NumeroProcesso`.
4. Campos com preenchimento muito baixo continuam disponiveis, mas nao sao
   considerados obrigatorios para a futura jornada do painel.
5. Nenhuma regra de negocio e inferida a partir de campos quase vazios.

## Proximo passo analitico recomendado

Antes de criar KPIs no Dash, executar um profiling completo da camada
processada para:

- cardinalidade de UnidadeGestora;
- distribuicao de ElementoDespesa e SubelementoDespesa;
- distribuicao de Favorecido;
- comportamento de ValorEmpenho, ValorLiquidado, ValorPago e ValorRap;
- duplicidade do campo `Id`;
- consistencia temporal entre `Ano` e `Data`;
- comparacao 2024 x 2025.
