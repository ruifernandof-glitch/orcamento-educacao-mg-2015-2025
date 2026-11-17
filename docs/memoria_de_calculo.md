# Memória de cálculo

Este documento descreve **como cada número foi obtido**, com um exemplo numérico tirado dos próprios dados. O código correspondente está em `src/orcamento_mg/indicadores.py`, e a mesma conta, em forma de fórmula de planilha, está em `outputs/memoria_de_calculo.xlsx`.

Notação: *t* é o exercício; *Y* é um valor orçamentário (dotação, autorizado, empenhado, liquidado ou pago); *s* é a subfunção; *a* é a ação.

---

## 1. Agregação anual

Para cada recorte, soma-se o campo de interesse de todas as linhas do ano em `execucao_detalhada.csv`, filtradas pelo recorte (`recorte_funcao12` ou `recorte_see1261`):

$$Y_t = \sum_{i \in \text{recorte},\ \text{ano}=t} y_i$$

O crédito autorizado é a soma de `vr_credito_autorizado` em `creditos_detalhados.csv` (todas as UOs para a Função 12; `cd_unidade_orc = 1261` para a SEE). A dotação inicial vem de `dotacao_inicial_loa.csv`.

**Exemplo (Função 12, 2020):** empenhado = R$ 9.656.860.748,98; crédito autorizado = R$ 12.814.557.372,72.

## 2. Deflação pelo IPCA (registro M02)

$$\text{fator}_t = \prod_{k=t+1}^{2025} (1 + \text{IPCA}_k), \qquad \text{fator}_{2025} = 1$$

$$Y_t^{\text{real}} = Y_t \times \text{fator}_t$$

**Exemplo:** fator₂₀₂₀ = 1,1006 × 1,0579 × 1,0462 × 1,0483 × 1,0426 = 1,331350.
Empenho real 2020 = 9.656.860.748,98 × 1,331350 = **R$ 12.856.658.747,84**.

> Na planilha: aba `IPCA`, coluna C, `=C(t+1)*(1+B(t+1))`.

## 3. Variação real anual

$$\Delta_t = \frac{Y_t^{\text{real}}}{Y_{t-1}^{\text{real}}} - 1 = \frac{1 + \Delta_t^{\text{nominal}}}{1 + \text{IPCA}_t} - 1$$

**Exemplo (2021):** 18.428.835.881,35 / 12.856.658.747,84 − 1 = **+43,34%**.
Verificação pela segunda forma: (1 + 57,76%) / (1 + 10,06%) − 1 = +43,34%.

## 4. Classificação (registros M03 a M05)

| Condição | Classe |
|---|---|
| \|Δ\| ≤ 5% | Incremental/estável |
| 5% < \|Δ\| < 10% | Mudança moderada |
| \|Δ\| ≥ 10% | Pontuação candidata |

**Sensibilidade (M09):** conta-se quantas das 10 variações têm \|Δ\| acima de 5%, 10% e 15%. Resultado na Função 12: **7, 3 e 1** (2021 é a única acima de 15%).

> Na planilha: aba `Serie_F12`, coluna O, e aba `Sensibilidade`, com `CONT.SES`. Os limiares estão em `Parametros` e podem ser alterados.

## 5. Taxas de execução

$$\frac{\text{Empenhado}_t}{\text{Autorizado}_t}, \qquad \frac{\text{Liquidado}_t}{\text{Empenhado}_t}, \qquad \frac{\text{Pago}_t}{\text{Liquidado}_t}$$

**Exemplo (2020):** 9.656.860.748,98 / 12.814.557.372,72 = **75,36%**. A primeira razão só existe para 2020–2025; as demais, para todo o período.

## 6. Persistência (registro M06)

Regressão linear por mínimos quadrados ordinários, só com **pares de anos consecutivos**:

$$Y_t = \alpha + \beta\, Y_{t-1} + \varepsilon_t$$

Também é estimada em logaritmos (ln *Y*ₜ sobre ln *Y*ₜ₋₁). São reportados β, erro-padrão de β, R², p-valor de β e n.

| Base | Recorte | Estágio | n | β | EP(β) | R² | p(β) |
|---|---|---|---|---|---|---|---|
| **real** | Função 12 | Empenhado | 10 | 0,818 | 0,245 | 0,582 | 0,010 |
| **real** | Função 12 | Liquidado | 10 | 0,933 | 0,201 | 0,730 | 0,002 |
| **real** | Função 12 | Pago | 10 | 0,952 | 0,186 | 0,767 | < 0,001 |
| nominal | Função 12 | Empenhado | 10 | 1,009 | 0,153 | 0,844 | < 0,001 |

A especificação **real** é a declarada na metodologia. A nominal é reportada porque reproduz a planilha original; ver [divergências, item 1](divergencias.md#1-regressões-de-persistência-estimadas-em-valores-nominais).

> Na planilha: aba `Persistencia`, com `INCLINAÇÃO`, `INTERCEPÇÃO` e `RQUAD` sobre as linhas 3–12 (Yₜ) e 2–11 (Yₜ₋₁).

## 7. Painel por subfunção e distribuição das variações (registro M07)

Para cada subfunção *s* e ano *t*:

$$\Delta_{s,t} = \frac{Y_{s,t}^{\text{real}}}{Y_{s,t-1}^{\text{real}}} - 1$$

calculada **somente se** *s* teve execução em *t* − 1 (anos consecutivos) e $Y_{s,t-1}^{\text{real}} \ge$ R$ 1 milhão (piso que evita variações explosivas sobre bases residuais).

**Exemplo (Ensino Fundamental, 2021):** 9.221.822.425,33 / 6.615.090.310,13 − 1 = **+39,41%**.

Sobre as 138 variações que entram, calculam-se: média, mediana, desvio-padrão, assimetria e curtose excedente (estimadores corrigidos para amostra, iguais a `DISTORÇÃO` e `CURT` da planilha), teste de Shapiro–Wilk e proporções com \|Δ\| ≥ 10% e ≥ 50%.

| Cenário | n | Mediana | Assimetria | Curtose exc. | Shapiro p | \|Δ\| ≥ 10% |
|---|---|---|---|---|---|---|
| Principal | 138 | −0,33% | 8,03 | 71,69 | < 0,001 | 72,5% |
| Sem 2020 | 127 | −0,27% | 7,22 | 57,55 | < 0,001 | 71,7% |
| Log, todos os anos | 138 | −0,33% | 1,05 | 6,70 | < 0,001 | 73,9% |
| Log, sem 2020 | 127 | −0,27% | 0,54 | 6,40 | < 0,001 | 72,4% |

## 8. Concentração – HHI (registro M08)

$$\text{HHI}_t = \sum_s \left( \frac{Y_{s,t}}{\sum_s Y_{s,t}} \right)^2$$

O HHI vai de 1/*S* (gasto igualmente dividido entre *S* subfunções) a 1 (tudo em uma só). Como as participações são do mesmo ano, nominal e real dão o mesmo resultado.

**Exemplo (2025):** participações principais de 0,3683 (Ensino Fundamental), 0,2405 (Ensino Médio), 0,1199 (Educação Básica) e 0,0817 (Educação Especial).
HHI = 0,1356 + 0,0578 + 0,0144 + 0,0067 + 0,0062 (demais) = **0,2208**.

## 9. Rastreamento por ação (decomposição contábil)

$$C_{a,t} = Y_{a,t}^{\text{real}} - Y_{a,t-1}^{\text{real}}$$

A chave de comparação é **(UO, código da ação)**, e não o nome, que pode mudar no mesmo ano. A soma das contribuições de todas as ações é igual à variação real total do recorte. As ações são classificadas assim:

- `comparável`: o código existe nos dois anos;
- `código novo`: só existe em *t* (contribuição = valor integral);
- `código extinto`: só existe em *t* − 1 (contribuição = −valor integral).

**Exemplo (ação 2065, Proventos dos Profissionais do Magistério – Ensino Fundamental, 2021):** 5.375.198.759,98 − 3.516.087.427,08 = **+R$ 1,859 bi**.

**Quebra de codificação.** Em 2020, **nenhuma** das ações é comparável com 2019 (91 extintas, 61 novas). Em 2016 e 2024, menos de 15% são comparáveis. Esses anos coincidem com o início de novos PPAGs. Ver `quebra_codificacao_acoes.csv`.

## 10. Recortes

A Função 12 inclui todas as UOs com despesa classificada em Educação (SEE, UEMG, Unimontes, PMMG/Colégios Tiradentes, Fundação Helena Antipoff, SEJUSP, entre outras). A SEE responde por 92% a 95% do empenho da função. A análise da SEE serve de teste de robustez: se o padrão aparece nos dois recortes, não é efeito de unidades periféricas.
