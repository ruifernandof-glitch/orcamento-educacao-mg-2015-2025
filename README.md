# Orçamento da Educação de Minas Gerais, 2015–2025: incrementalismo e equilíbrio pontuado

Base de dados, código e memória de cálculo da dissertação de mestrado
**“Incrementalismo e dinâmica política do orçamento educacional: uma análise da alocação de recursos da educação no Estado de Minas Gerais”**
(Programa de Pós-Graduação em Administração, Centro Universitário Unihorizontes, 2026).

- **Autor:** Eduardo César da Silveira Sousa
- **Orientador:** Prof. Dr. Rui Fernando Correia Ferreira
- **Área de concentração:** Organização e Estratégia · **Linha de pesquisa:** Estratégia, Inovação e Competitividade

Este repositório permite que qualquer pessoa **refaça, a partir dos dados oficiais, todos os números, tabelas e figuras** do capítulo de resultados, e confira cada cálculo.

---

## O que a análise faz

A pesquisa examina se o orçamento executado da **Função 12 – Educação** do Estado de Minas Gerais (e, como teste de robustez, da **UO 1261 – Secretaria de Estado de Educação**) se comporta como prevê o **incrementalismo** (dependência do orçamento anterior e ajustes marginais) ou o **equilíbrio pontuado** (longos períodos de estabilidade interrompidos por mudanças desproporcionais).

| Indicador | O que mede | Onde está |
|---|---|---|
| Série real 2015–2025 | Empenhado, liquidado e pago a preços de dez./2025 (IPCA) | `data/processed/serie_anual.csv` |
| Persistência | Regressão de Yₜ sobre Yₜ₋₁, em valores reais e nominais | `data/processed/persistencia_regressoes.csv` |
| Sensibilidade | Classificação das variações pelos limiares de 5%, 10% e 15% | `data/processed/sensibilidade_limiares.csv` |
| Distribuição | Assimetria, curtose e Shapiro–Wilk das variações por subfunção | `data/processed/distribuicao_subfuncoes.csv` |
| Concentração | Índice de Herfindahl–Hirschman (HHI) por subfunção | `data/processed/concentracao_hhi.csv` |
| Rastreamento | Contribuição de cada ação orçamentária para a variação anual | `data/processed/rastreamento_acoes.csv` |
| Execução | Empenhado/autorizado, liquidado/empenhado, pago/liquidado | `data/processed/serie_anual.csv` |

### Principais resultados

- **Trajetória:** o empenho real da Função 12 passou de R$ 15,31 bi (2015) para R$ 21,58 bi (2025), com contração em 2020 (−10,73%), salto em 2021 (+43,34%), expansão em 2022 (+11,21%) e estabilidade de 2023 a 2025.
- **Persistência:** em valores reais, β = 0,818 (EP 0,245; R² = 0,58; p = 0,010; n = 10). Em valores nominais, β = 1,009 e R² = 0,844. Ver [divergências](docs/divergencias.md#1-regressões-de-persistência-estimadas-em-valores-nominais).
- **Limiares:** 7, 3 e 1 das 10 variações superam 5%, 10% e 15%. Apenas 2021 é excepcional sob qualquer critério.
- **Distribuição:** 138 variações por subfunção, mediana −0,33%, curtose excedente 71,7, Shapiro–Wilk p < 0,001. Sem as variações de 2020, a curtose cai para 57,5.
- **Concentração:** o HHI cai de 0,375 (2015) para 0,221 (2025).
- **Recodificação:** em 2016, 2020 e 2024 (inícios de PPAG) quase nenhuma ação é comparável com o ano anterior. **Em 2020, nenhuma.** Parte das variações por subfunção nesses anos é artefato de classificação.

---

## Estrutura

```
├── data/
│   ├── original/     Planilhas entregues pelo pesquisador (intactas) + SHA256SUMS
│   ├── raw/          Dados de entrada em CSV, sem cálculo (gerados pela etapa 0)
│   └── processed/    Indicadores calculados (gerados pelo pipeline)
├── src/orcamento_mg/ Código: leitura, deflação, indicadores, figuras, tabelas, memória
├── scripts/          00_extrair_brutos.py e run_all.py
├── outputs/
│   ├── tabelas/      Tabelas da dissertação em CSV (padrão brasileiro, ; e vírgula)
│   ├── figuras/      Figuras 1 a 5 (PNG, 300 dpi)
│   ├── memoria_de_calculo.xlsx           Memória de cálculo com fórmulas vivas
│   └── conferencia_planilha_original.csv Confronto número a número com a planilha original
├── docs/             Dicionário de dados, memória de cálculo, fontes, logs, divergências
└── tests/            Testes automatizados de reprodução
```

## Como reproduzir

Requisitos: Python 3.10 ou superior. LibreOffice é opcional (usado apenas no teste que recalcula a planilha de memória).

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/00_extrair_brutos.py   # planilhas originais → data/raw/*.csv
python scripts/run_all.py             # data/raw → data/processed, outputs/
pytest -q                             # confere os números da dissertação
```

Ou simplesmente `make tudo`.

O pipeline leva menos de um minuto. A saída final lista o resultado da conferência com a planilha original: **483 valores conferem exatamente e 9 divergem por razões documentadas**; nenhum diverge sem explicação.

## Memória de cálculo

São três formas complementares de auditar os números:

1. **[docs/memoria_de_calculo.md](docs/memoria_de_calculo.md):** cada fórmula, com um exemplo numérico real.
2. **[outputs/memoria_de_calculo.xlsx](outputs/memoria_de_calculo.xlsx):** planilha em que todo valor derivado é uma fórmula do Excel/LibreOffice (deflação, variações, classificação, regressões, HHI, distribuição). Os parâmetros (limiares e piso) estão em células amarelas e podem ser alterados.
3. **[outputs/conferencia_planilha_original.csv](outputs/conferencia_planilha_original.csv):** cada indicador da planilha original ao lado do valor reproduzido.

## Fontes de dados

| Dado | Fonte | Período |
|---|---|---|
| Empenhado, liquidado, pago | Portal de Dados Abertos de MG – [Despesa pública](https://dados.mg.gov.br/dataset/despesa) (SIAFI-MG) | 2015–2025 |
| Créditos iniciais, adicionais e anulações | Portal de Dados Abertos de MG – [Proposta e alterações da LOA](https://dados.mg.gov.br/dataset/proposta-lei-orcamentaria) | 2020–2025 |
| Dotação inicial | Leis Orçamentárias Anuais de MG (base bruta em `data/original`) | 2015, 2017–2025 |
| IPCA | [IBGE](https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html) | 2015–2025 |

Coleta realizada em 17/08/2026. A proveniência completa está em [docs/fontes.md](docs/fontes.md).

## Limitações

A série anual oferece apenas dez variações interanuais. Os créditos autorizados detalhados cobrem só 2020–2025, e o IPCA não é um índice de custos educacionais. As mudanças de codificação (2016, 2020, 2024) produzem rupturas aparentes por subfunção. Os resultados são **descritivos e não causais**: identificam quando e onde houve mudança, não por quê. Ver [docs/divergencias.md](docs/divergencias.md) e [docs/log_metodologico.md](docs/log_metodologico.md).

## Como citar

Use o botão **“Cite this repository”** do GitHub (arquivo [CITATION.cff](CITATION.cff)) ou:

> Sousa, E. C. da S., & Ferreira, R. F. C. (2026). *Orçamento da Educação de Minas Gerais, 2015–2025: base de dados, código e memória de cálculo* (Versão 1.0.0) [Conjunto de dados e software]. Centro Universitário Unihorizontes.

## Licenças

- **Código** (`src/`, `scripts/`, `tests/`): [MIT](LICENSE).
- **Dados e documentação** (`data/`, `outputs/`, `docs/`): [CC BY 4.0](LICENSE-DATA.md), a mesma licença dos dados abertos de Minas Gerais.
