"""Parâmetros metodológicos e caminhos do projeto.

Todos os critérios operacionais ficam aqui, num só lugar, para que qualquer
alteração (p. ex., outro limiar ou outro piso) seja feita uma única vez e
registrada no controle de versão.
"""
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DADOS_ORIGINAIS = RAIZ / "data" / "original"
DADOS_BRUTOS = RAIZ / "data" / "raw"
DADOS_PROCESSADOS = RAIZ / "data" / "processed"
TABELAS = RAIZ / "outputs" / "tabelas"
FIGURAS = RAIZ / "outputs" / "figuras"

PLANILHA_ANALISE = DADOS_ORIGINAIS / "Analise_Completa_Orcamento_Educacao_MG_2015_2025.xlsx"
PLANILHA_LOA = DADOS_ORIGINAIS / "Base_Bruta_LOA_MG_Educacao.xlsx"

# Período e recortes (registro M01 e M02 do log metodológico)
ANO_INICIAL, ANO_FINAL = 2015, 2025
ANO_BASE_DEFLACAO = 2025          # preços de dezembro de 2025
RECORTES = {
    "funcao12": "Função 12 – Educação",
    "see1261": "UO 1261 – SEE/MG",
}

# Classificação das variações reais anuais (registros M03 a M05)
LIMIAR_INCREMENTAL = 0.05          # |Δ| ≤ 5%
LIMIAR_PONTUACAO = 0.10            # |Δ| ≥ 10%
LIMIARES_SENSIBILIDADE = (0.05, 0.10, 0.15)   # registro M09

# Distribuição das variações por subfunção (registro M07)
PISO_BASE_SUBFUNCAO = 1_000_000.0  # base real do ano anterior ≥ R$ 1 milhão

# Créditos autorizados detalhados só existem a partir de 2020
ANO_INICIAL_CREDITOS = 2020
