# Catálogo de Métricas

## Objetivo

Este documento registra as métricas e estatísticas calculadas pela camada `src/analytics/metrics.py`, seus escopos, status e limitações.

A regra principal é separar **cálculo tecnicamente correto** de **interpretação de negócio**.

## Status usados

- **VALIDADA TECNICAMENTE:** fórmula, tipos, agregação e reconciliação foram testados na base completa.
- **VALIDADA PARA USO ANALÍTICO:** além da validação técnica, o recorte e a interpretação estão explicitamente definidos.
- **CANDIDATA:** cálculo possível, mas ainda depende de regra de negócio ou validação semântica.
- **NÃO RECOMENDADA SEM REGRA ADICIONAL:** não deve virar KPI apenas por parecer matematicamente intuitiva.

---

## 1. Totais financeiros

### Total Empenhado

**Status:** VALIDADA TECNICAMENTE

**Campo:** `ValorEmpenho`

**Fórmula:**

```text
SUM(ValorEmpenho)
```

**Resultado global:** R$ 22.260.089.498,27

**Observações:**

- valores negativos são preservados;
- zeros são preservados;
- nulos não são imputados;
- nenhum registro é deduplicado pela função de soma.

### Total Liquidado

**Status:** VALIDADA TECNICAMENTE

**Campo:** `ValorLiquidado`

**Fórmula:**

```text
SUM(ValorLiquidado)
```

**Resultado global:** R$ 20.159.865.427,63

### Total Pago

**Status:** VALIDADA TECNICAMENTE

**Campo:** `ValorPago`

**Fórmula:**

```text
SUM(ValorPago)
```

**Resultado global:** R$ 21.612.307.088,15

Esse total é líquido dos movimentos positivos e negativos presentes na coluna.

### Total RAP

**Status:** VALIDADA TECNICAMENTE

**Campo:** `ValorRap`

**Fórmula:**

```text
SUM(ValorRap)
```

**Resultado global:** R$ 2.160.152.532,38

`ValorRap` representa pagamento realizado no período com empenho de ano anterior e não deve ser somado aos demais campos como se fosse uma etapa independente de uma mesma sequência sem justificar a regra.

---

## 2. Totais por ano

**Status:** VALIDADA TECNICAMENTE

| Ano | Registros | ValorEmpenho | ValorLiquidado | ValorPago | ValorRap |
|---|---:|---:|---:|---:|---:|
| 2024 | 505.950 | R$ 7.220.650.612,93 | R$ 8.234.487.893,88 | R$ 10.337.098.858,62 | R$ 1.452.428.885,56 |
| 2025 | 586.208 | R$ 15.039.438.885,34 | R$ 11.925.377.533,75 | R$ 11.275.208.229,53 | R$ 707.723.646,82 |

A reconciliação entre os totais gerais e a soma dos grupos anuais foi aprovada para as quatro medidas.

### Limitação

Em 2024, `ValorLiquidado` e `ValorPago` são maiores que `ValorEmpenho`. Isso impede interpretar automaticamente as relações entre essas medidas como taxas de execução do mesmo conjunto anual de despesas.

---

## 3. Qualidade das medidas financeiras

**Status:** VALIDADA TECNICAMENTE

| Métrica | Ausentes | Negativos | Zeros |
|---|---:|---:|---:|
| ValorEmpenho | 0 | 19.443 | 973.509 |
| ValorLiquidado | 0 | 212.801 | 497.558 |
| ValorPago | 0 | 22.633 | 753.496 |
| ValorRap | 0 | 1.038 | 1.051.911 |

Esses valores são informação de qualidade e ajudam a evitar tratamentos incorretos.

---

## 4. Pagamentos positivos

Algumas análises de distribuição utilizam apenas registros com:

```text
ValorPago > 0
```

Isso é um **recorte analítico** e não substitui o total líquido de `ValorPago`.

### Quantidade de pagamentos positivos

**Status:** VALIDADA PARA USO ANALÍTICO

```text
COUNT(ValorPago > 0)
```

Resultado global: **316.029 registros**.

### Proporção de registros com pagamento positivo

**Status:** VALIDADA PARA USO ANALÍTICO

```text
registros com ValorPago > 0 / total de registros
```

Resultado global: **28,94%**.

Interpretação correta: proporção empírica de registros da base com `ValorPago > 0`.

Não interpretar como probabilidade causal de pagamento de uma despesa.

### Soma dos pagamentos positivos

**Status:** VALIDADA PARA USO ANALÍTICO

```text
SUM(ValorPago WHERE ValorPago > 0)
```

Resultado global: **R$ 22.795.053.118,57**.

Esse valor é maior que o total líquido de `ValorPago` porque os movimentos negativos foram excluídos.

---

## 5. Estatística descritiva de `ValorPago > 0`

**Status:** VALIDADA PARA USO ANALÍTICO

Escopo global:

| Estatística | Resultado |
|---|---:|
| Média | R$ 72.129,62 |
| Mediana | R$ 1.290,98 |
| Q1 | R$ 213,22 |
| Q3 | R$ 7.272,11 |
| IQR | R$ 7.058,89 |
| Máximo | R$ 144.809.753,87 |

A diferença elevada entre média e mediana indica forte assimetria à direita na distribuição de pagamentos positivos.

---

## 6. Boxplot de pagamentos positivos

**Status:** VALIDADA PARA USO ANALÍTICO

Regra utilizada:

```text
IQR = Q3 - Q1
limite superior = Q3 + 1,5 × IQR
```

Resultado global:

- limite superior: aproximadamente R$ 17.860,45;
- 49.549 registros positivos acima desse limite;
- aproximadamente 15,68% dos pagamentos positivos classificados como outliers superiores pela regra do boxplot.

### Limitação obrigatória

Um outlier estatístico não é prova de fraude, erro ou irregularidade. Ele apenas indica que o valor está distante da região central da distribuição segundo a regra escolhida.

---

## 7. Intervalo de confiança da média dos pagamentos positivos

**Status:** VALIDADA PARA USO ANALÍTICO

Método atual: intervalo bilateral de 95% para a média usando distribuição t de Student e erro-padrão amostral.

Escopo global:

```text
média: R$ 72.129,62
IC 95%: [R$ 68.586,12 ; R$ 75.673,13]
```

### Interpretação

O intervalo se refere à média dos registros com `ValorPago > 0` no recorte analisado pelo código.

Não é um intervalo de confiança para o total de despesas do Estado e não deve ser apresentado dessa forma.

---

## 8. Concentração por favorecido

**Status:** VALIDADA PARA USO ANALÍTICO

Escopo: apenas `ValorPago > 0`.

Resultados atuais:

- 21.961 favorecidos com pagamento positivo;
- os 10 favorecidos com maior soma de pagamentos positivos concentram aproximadamente **45,01%** do valor positivo;
- esses mesmos 10 favorecidos representam aproximadamente **8,72%** dos registros positivos.

### Limitação

Concentração financeira não é sinônimo de irregularidade. A interpretação deve considerar natureza do favorecido, volume contratual, unidade gestora e contexto administrativo.

---

## 9. Distribuição por `TipoLicitacao`

**Status:** VALIDADA PARA USO ANALÍTICO

Escopo atual: soma de `ValorPago` para registros com `ValorPago > 0`, agrupada pelo valor original de `TipoLicitacao`.

Principais participações observadas:

| TipoLicitacao | Participação no valor positivo |
|---|---:|
| NÃO APLICÁVEL - DEMAIS CASOS | 78,14% |
| PREGÃO | 8,32% |
| CONCORRÊNCIA | 5,14% |
| DISPENSA DE LICITAÇÃO | 2,38% |
| REGIME DIFERENCIADO DE CONTRATAÇÕES PÚBLICAS (RDC) | 2,02% |

A categoria `NÃO APLICÁVEL - DEMAIS CASOS` domina o valor positivo. Portanto, leituras sobre contratação devem evitar interpretar toda a base como se cada registro estivesse associado a um processo licitatório convencional.

Nenhuma categoria é agrupada ou corrigida automaticamente.

---

## 10. Métricas candidatas

As métricas abaixo ainda exigem regra de negócio ou investigação adicional:

### Variação anual

```text
(Valor_2025 - Valor_2024) / Valor_2024
```

**Status:** CANDIDATA

Pode ser utilizada como variação matemática de uma mesma medida entre anos, desde que o rótulo seja explícito. Não deve ser confundida com eficiência.

### Participação por categoria

```text
valor da categoria / valor total do mesmo recorte
```

**Status:** CANDIDATA

Pode ser aplicada a elemento, subelemento, unidade gestora ou favorecido, desde que numerador e denominador usem exatamente o mesmo filtro e definição de valor.

---

## 11. Métricas não recomendadas sem regra adicional

### Taxa de execução

Exemplo intuitivo, porém não validado:

```text
ValorPago / ValorEmpenho
```

**Status:** NÃO RECOMENDADA SEM REGRA ADICIONAL

### Taxa de liquidação

```text
ValorLiquidado / ValorEmpenho
```

**Status:** NÃO RECOMENDADA SEM REGRA ADICIONAL

### Saldo orçamentário

Qualquer fórmula baseada apenas em subtração entre as quatro medidas requer validação da granularidade e da relação temporal dos registros.

---

## 12. Funções disponíveis

Arquivo:

```text
src/analytics/metrics.py
```

Funções públicas atuais:

```text
financial_totals()
financial_quality_summary()
totals_by_dimension()
totals_by_year()
totals_by_month()
totals_by_unit()
confidence_interval_mean()
descriptive_payment_statistics()
beneficiary_concentration()
```

---

## 13. Relatórios gerados

Arquivo de entrada da etapa:

```text
src/data/processed/
```

Comando:

```bash
python src/scripts/validate_metrics.py
```

Saídas principais:

```text
src/data/reports/metrics_quality.csv
src/data/reports/metrics_validation.json
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

## 14. Regra para novas métricas

Antes de uma nova métrica virar KPI do painel, documentar:

1. nome;
2. objetivo;
3. fórmula;
4. campos usados;
5. filtros e recorte;
6. nível de agregação;
7. tratamento de zeros, negativos e ausentes;
8. teste automatizado;
9. limitação de interpretação;
10. página em que será utilizada.
