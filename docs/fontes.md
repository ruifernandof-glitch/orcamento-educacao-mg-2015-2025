# Fontes e proveniência

| Fonte | Conteúdo utilizado | Período | Situação | Endereço |
|---|---|---|---|---|
| Portal de Dados Abertos MG – Despesa pública | Empenhado, liquidado, pago e classificadores SIAFI | 2015–2025 | Coletado em 17/08/2026 | https://dados.mg.gov.br/dataset/despesa |
| Portal de Dados Abertos MG – Proposta e alterações da LOA | Créditos iniciais, suplementares, especiais, extraordinários e anulações | 2020–2025 | Coletado em 17/08/2026 | https://dados.mg.gov.br/dataset/proposta-lei-orcamentaria |
| Leis Orçamentárias Anuais de MG (11 arquivos consolidados) | Dotação inicial da Função 12 e da UO 1261 | 2015, 2017–2025 | Transcrito na base bruta LOA | `data/original/Base_Bruta_LOA_MG_Educacao.xlsx` |
| ALMG – LOA 2025, Volume I | Validação da Função 12 (R$ 21.243.913.011) | 2025 | Validado | https://mediaserver.almg.gov.br/acervo/405/297/2405297.pdf |
| ALMG – LOA 2025, Volume IIA | Validação da UO 1261 (R$ 19.602.245.472) | 2025 | Validado | https://mediaserver.almg.gov.br/acervo/405/298/2405298.pdf |
| ALMG – Relatório de Controle Interno 2020 | Validação independente da execução | 2020 | Validado | https://mediaserver.almg.gov.br/acervo/553/233/1553233.pdf |
| SEF/MG – RREO, Anexo 8 | MDE, Fundeb e mínimo constitucional | 2015–2025 | **Não incorporado** (agenda futura) | https://www.fazenda.mg.gov.br/governo/contadoria_geral/lrf/ |
| IBGE – IPCA | Deflação para preços de dez./2025 | 2015–2025 | Coletado | https://www.ibge.gov.br/estatisticas/economicas/precos-e-custos/9256-indice-nacional-de-precos-ao-consumidor-amplo.html |

## Cadeia de custódia

1. As duas planilhas em `data/original/` são as entregues pelo pesquisador, sem nenhuma alteração. Seus hashes SHA-256 estão em `data/original/SHA256SUMS`; confira com `sha256sum -c SHA256SUMS`.
2. `scripts/00_extrair_brutos.py` copia apenas os **dados de entrada** dessas planilhas para `data/raw/*.csv`. Nenhuma fórmula ou resultado da planilha original é usado como entrada.
3. `scripts/run_all.py` recalcula tudo a partir de `data/raw` e grava em `data/processed` e `outputs`.
4. `outputs/conferencia_planilha_original.csv` compara os resultados recalculados com os da planilha original.

## Validações feitas na base bruta das LOAs

As validações estão registradas na aba `09_Verificacao` da base bruta. Entre elas:

- a soma dos componentes é igual ao total impresso na fonte;
- a soma das subfunções e a soma das UOs são iguais ao total da Função 12 (2019–2025);
- a reclassificação 122 → 368 em 2020 foi confirmada como artefato;
- a reclassificação 364 → 122 em 2025 (UEMG e Unimontes) foi confirmada;
- a migração do programa “Mãos à Obra” da subfunção 361 para a 368 entre 2021 e 2022 foi confirmada;
- a quebra de denominador em 2023 (encargos especiais) foi confirmada.
