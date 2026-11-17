# Dados

| Pasta | Conteúdo | Pode editar? |
|---|---|---|
| `original/` | Planilhas entregues pelo pesquisador, intactas. Hashes em `SHA256SUMS` | **Não** |
| `raw/` | Dados de entrada em CSV, extraídos por `scripts/00_extrair_brutos.py` | Não (são regenerados) |
| `processed/` | Indicadores calculados por `scripts/run_all.py` | Não (são regenerados) |

- `original/Analise_Completa_Orcamento_Educacao_MG_2015_2025.xlsx`: base integrada de execução (SIAFI-MG) e créditos, coletada em 17/08/2026, com as abas de análise originais.
- `original/Base_Bruta_LOA_MG_Educacao.xlsx`: dotação inicial transcrita das 11 LOAs de MG, com fontes, verificações e pendências.

Para conferir a integridade: `cd data/original && sha256sum -c SHA256SUMS`.

O significado de cada coluna está em [`docs/dicionario_de_dados.md`](../docs/dicionario_de_dados.md).
