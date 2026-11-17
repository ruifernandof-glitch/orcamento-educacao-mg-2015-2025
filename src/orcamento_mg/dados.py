"""Leitura dos dados brutos e deflação."""
import numpy as np
import pandas as pd

from . import config as C

COLUNAS_VALOR = ["vr_empenhado", "vr_liquidado", "vr_pago"]


def ler_execucao() -> pd.DataFrame:
    """Execução detalhada (ano × UO × subfunção × programa × ação × fonte).

    A tabela empilha duas extrações: as colunas booleanas ``recorte_funcao12``
    e ``recorte_see1261`` indicam a que recorte cada linha pertence. Uma linha
    pode pertencer aos dois. Use sempre :func:`filtrar_recorte`; nunca some
    os dois recortes.
    """
    return pd.read_csv(C.DADOS_BRUTOS / "execucao_detalhada.csv")


def filtrar_recorte(ex: pd.DataFrame, recorte: str) -> pd.DataFrame:
    if recorte not in C.RECORTES:
        raise ValueError(f"recorte desconhecido: {recorte}")
    return ex[ex[f"recorte_{recorte}"].astype(bool)].copy()


def ler_creditos() -> pd.DataFrame:
    return pd.read_csv(C.DADOS_BRUTOS / "creditos_detalhados.csv")


def ler_dotacao_loa() -> pd.DataFrame:
    return pd.read_csv(C.DADOS_BRUTOS / "dotacao_inicial_loa.csv")


def fatores_ipca() -> pd.Series:
    """Fator que leva valores de cada ano a preços de dezembro do ano-base.

    fator(t) = Π_{k=t+1}^{ano-base} (1 + IPCA_k);  fator(ano-base) = 1.
    O valor nominal do ano t multiplicado pelo fator(t) fica expresso em
    preços de dezembro do ano-base (aproximação anual, registro M02).
    """
    ipca = pd.read_csv(C.DADOS_BRUTOS / "ipca_anual.csv").set_index("ano")["ipca_variacao_anual"]
    anos = sorted(ipca.index)
    fatores = {}
    for t in anos:
        posteriores = [a for a in anos if t < a <= C.ANO_BASE_DEFLACAO]
        fatores[t] = float(np.prod([1 + ipca[a] for a in posteriores])) if posteriores else 1.0
    return pd.Series(fatores, name="fator_ipca")
