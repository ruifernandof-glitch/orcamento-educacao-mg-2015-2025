"""Cálculo de todos os indicadores da análise.

Cada função devolve um DataFrame que é gravado em ``data/processed`` e
documentado em ``docs/memoria_de_calculo.md``.
"""
import numpy as np
import pandas as pd
from scipy import stats

from . import config as C
from .dados import (COLUNAS_VALOR, filtrar_recorte, fatores_ipca, ler_creditos,
                    ler_dotacao_loa, ler_execucao)


# ---------------------------------------------------------------------------
# 1. Série anual por recorte (nominal e real)
# ---------------------------------------------------------------------------
def classificar(variacao: float) -> str:
    if pd.isna(variacao):
        return "Sem comparação"
    a = abs(variacao)
    if a <= C.LIMIAR_INCREMENTAL:
        return "Incremental/estável (≤5%)"
    if a < C.LIMIAR_PONTUACAO:
        return "Mudança moderada (5%–10%)"
    return "Pontuação candidata (≥10%)"


def serie_anual() -> pd.DataFrame:
    ex = ler_execucao()
    cr = ler_creditos()
    loa = ler_dotacao_loa()
    fat = fatores_ipca()
    anos = range(C.ANO_INICIAL, C.ANO_FINAL + 1)
    partes = []
    for recorte in C.RECORTES:
        e = filtrar_recorte(ex, recorte).groupby("ano")[COLUNAS_VALOR].sum()
        if recorte == "funcao12":
            c = cr
        else:
            c = cr[cr["cd_unidade_orc"] == 1261]
        c = c.groupby("ano")[["vr_credito_inicial", "vr_credito_suplem", "vr_credito_extraord",
                               "vr_credito_especial", "vr_anulacao_credito", "vr_credito_autorizado"]].sum()
        d = loa[loa["recorte"] == recorte].set_index("ano")["dotacao_inicial"]
        df = pd.DataFrame(index=pd.Index(anos, name="ano"))
        df["recorte"] = recorte
        df["dotacao_inicial"] = d
        for col in c.columns:
            df[col] = c[col]
        df.loc[df.index < C.ANO_INICIAL_CREDITOS, c.columns] = np.nan
        df[COLUNAS_VALOR] = e
        df["fator_ipca"] = fat
        for col in ["dotacao_inicial", "vr_credito_autorizado"] + COLUNAS_VALOR:
            df[col + "_real"] = df[col] * df["fator_ipca"]
        df["var_nominal_empenhado"] = df["vr_empenhado"].pct_change(fill_method=None)
        df["var_real_empenhado"] = df["vr_empenhado_real"].pct_change(fill_method=None)
        df["classificacao"] = df["var_real_empenhado"].map(classificar)
        df["taxa_empenhado_autorizado"] = df["vr_empenhado"] / df["vr_credito_autorizado"]
        df["taxa_liquidado_empenhado"] = df["vr_liquidado"] / df["vr_empenhado"]
        df["taxa_pago_liquidado"] = df["vr_pago"] / df["vr_liquidado"]
        partes.append(df.reset_index())
    return pd.concat(partes, ignore_index=True)


# ---------------------------------------------------------------------------
# 2. Persistência: Y_t = α + β Y_{t-1} + ε  (registro M06)
# ---------------------------------------------------------------------------
ESTAGIOS = {
    "dotacao_inicial_real": "Dotação inicial",
    "vr_credito_autorizado_real": "Crédito autorizado",
    "vr_empenhado_real": "Empenhado",
    "vr_liquidado_real": "Liquidado",
    "vr_pago_real": "Pago",
}


def _pares(s: pd.Series) -> pd.DataFrame:
    """Pares (Y_t, Y_{t-1}) somente entre exercícios consecutivos com dado."""
    s = s.dropna()
    prev = s.shift(1)
    consecutivo = pd.Series(s.index, index=s.index).diff() == 1
    return pd.DataFrame({"y": s, "y_ant": prev})[consecutivo].dropna()


def persistencia(serie: pd.DataFrame, base: str = "real") -> pd.DataFrame:
    """Regressão do valor do exercício t sobre o valor de t−1.

    ``base="real"`` (padrão, coerente com a metodologia) usa valores a preços
    de dez./2025; ``base="nominal"`` reproduz a planilha original de análise,
    que estimou as regressões em valores correntes (ver docs/divergencias.md).
    Só entram pares de exercícios consecutivos (2015→2017 não é par).
    """
    linhas = []
    for recorte in C.RECORTES:
        s = serie[serie["recorte"] == recorte].set_index("ano")
        for col, nome in ESTAGIOS.items():
            if base == "nominal":
                col = col.replace("_real", "")
            p = _pares(s[col])
            if len(p) < 3:
                continue
            niv = stats.linregress(p["y_ant"], p["y"])
            log = stats.linregress(np.log(p["y_ant"]), np.log(p["y"]))
            linhas.append({
                "base": base, "recorte": recorte, "estagio": nome, "n_pares": len(p),
                "anos": f"{p.index.min() - 1}–{p.index.max()}",
                "alfa": niv.intercept, "beta": niv.slope, "erro_padrao_beta": niv.stderr,
                "r2": niv.rvalue ** 2, "p_beta": niv.pvalue,
                "beta_log": log.slope, "r2_log": log.rvalue ** 2, "p_beta_log": log.pvalue,
            })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 3. Sensibilidade aos limiares (registro M09)
# ---------------------------------------------------------------------------
def sensibilidade(serie: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for recorte in C.RECORTES:
        v = serie.loc[serie["recorte"] == recorte, "var_real_empenhado"].dropna()
        for lim in C.LIMIARES_SENSIBILIDADE:
            nao_inc = int((v.abs() > lim).sum())
            linhas.append({
                "recorte": recorte, "limiar": lim, "n_variacoes": len(v),
                "incrementais": len(v) - nao_inc, "nao_incrementais": nao_inc,
                "proporcao_nao_incremental": nao_inc / len(v),
                "anos_nao_incrementais": ", ".join(str(int(a)) for a in
                    serie.loc[(serie["recorte"] == recorte) & (serie["var_real_empenhado"].abs() > lim), "ano"]),
            })
    return pd.DataFrame(linhas)


# ---------------------------------------------------------------------------
# 4. Painel por subfunção, distribuição e HHI (registros M07 e M08)
# ---------------------------------------------------------------------------
def painel_subfuncoes(recorte: str = "funcao12") -> pd.DataFrame:
    ex = filtrar_recorte(ler_execucao(), recorte)
    fat = fatores_ipca()
    p = (ex.groupby(["ano", "cd_subfuncao", "nm_subfuncao"])[COLUNAS_VALOR].sum().reset_index())
    p["total_ano"] = p.groupby("ano")["vr_empenhado"].transform("sum")
    p["participacao"] = p["vr_empenhado"] / p["total_ano"]
    p["fator_ipca"] = p["ano"].map(fat)
    p["empenhado_real"] = p["vr_empenhado"] * p["fator_ipca"]
    p = p.sort_values(["cd_subfuncao", "ano"])
    ant = p.groupby("cd_subfuncao")[["ano", "empenhado_real"]].shift(1)
    consecutivo = (p["ano"] - ant["ano"]) == 1
    p["empenhado_real_ano_anterior"] = ant["empenhado_real"].where(consecutivo)
    p["var_real"] = p["empenhado_real"] / p["empenhado_real_ano_anterior"] - 1
    p["contribuicao_real"] = p["empenhado_real"] - p["empenhado_real_ano_anterior"]
    p["na_distribuicao"] = p["empenhado_real_ano_anterior"] >= C.PISO_BASE_SUBFUNCAO
    return p.sort_values(["ano", "cd_subfuncao"]).reset_index(drop=True)


def distribuicao(painel: pd.DataFrame, excluir_anos=(), log=False) -> dict:
    """Estatísticas da distribuição das variações reais por subfunção.

    Assimetria e curtose excedente usam os estimadores corrigidos para
    amostra (``bias=False``), idênticos às funções DISTORÇÃO/CURT do Excel e do
    LibreOffice, para que a memória de cálculo em planilha reproduza o Python.
    """
    v = painel.loc[painel["na_distribuicao"] & ~painel["ano"].isin(excluir_anos), "var_real"].dropna()
    if log:
        v = np.log1p(v)
    return {
        "n": int(len(v)), "media": v.mean(), "mediana": v.median(), "desvio_padrao": v.std(ddof=1),
        "assimetria": stats.skew(v, bias=False), "curtose_excedente": stats.kurtosis(v, bias=False),
        "shapiro_w": stats.shapiro(v).statistic, "shapiro_p": stats.shapiro(v).pvalue,
        "prop_abs_ge_10": float((v.abs() >= 0.10).mean()), "prop_abs_ge_50": float((v.abs() >= 0.50).mean()),
    }


def tabela_distribuicao(painel: pd.DataFrame) -> pd.DataFrame:
    cenarios = {
        "Principal (variação simples, todos os anos)": dict(),
        "Sem 2020 (reclassificação 122→368)": dict(excluir_anos=(2020,)),
        "Variação logarítmica, todos os anos": dict(log=True),
        "Variação logarítmica, sem 2020": dict(excluir_anos=(2020,), log=True),
    }
    return pd.DataFrame([{"cenario": k, **distribuicao(painel, **kw)} for k, kw in cenarios.items()])


def hhi(painel: pd.DataFrame) -> pd.DataFrame:
    h = (painel.assign(p2=painel["participacao"] ** 2).groupby("ano")
         .agg(hhi=("p2", "sum"), n_subfuncoes=("cd_subfuncao", lambda s: int((painel.loc[s.index, "vr_empenhado"] > 0).sum()))))
    return h.reset_index()


# ---------------------------------------------------------------------------
# 5. Rastreamento por ação (decomposição contábil)
# ---------------------------------------------------------------------------
def rastreamento_acoes(recorte: str = "funcao12") -> pd.DataFrame:
    """Contribuição de cada ação: empenho real(t) − empenho real(t−1).

    A comparação é feita por (UO, ação). Ações sem correspondência no ano
    anterior são marcadas como 'código novo' (contribuição = valor integral);
    ações que deixam de existir aparecem como 'código extinto' (contribuição =
    − valor integral do ano anterior). Isso torna visível a quebra de
    codificação, em vez de descartá-la.
    """
    ex = filtrar_recorte(ler_execucao(), recorte)
    fat = fatores_ipca()
    chave = ["cd_unidade_orc", "nm_unidade_orc", "cd_acao"]
    a = ex.groupby(["ano"] + chave).agg(
        nm_acao=("nm_acao", "first"), cd_subfuncao=("cd_subfuncao", "first"),
        nm_subfuncao=("nm_subfuncao", "first"), vr_empenhado=("vr_empenhado", "sum")).reset_index()
    a["empenhado_real"] = a["vr_empenhado"] * a["ano"].map(fat)
    linhas = []
    for t in range(C.ANO_INICIAL + 1, C.ANO_FINAL + 1):
        cur = a[a["ano"] == t].set_index(["cd_unidade_orc", "cd_acao"])
        ant = a[a["ano"] == t - 1].set_index(["cd_unidade_orc", "cd_acao"])
        idx = cur.index.union(ant.index)
        for k in idx:
            vc = cur["empenhado_real"].get(k, np.nan)
            va = ant["empenhado_real"].get(k, np.nan)
            ref = cur.loc[k] if k in cur.index else ant.loc[k]
            if np.isnan(va):
                situacao, contrib = "código novo", vc
            elif np.isnan(vc):
                situacao, contrib = "código extinto", -va
            else:
                situacao, contrib = "comparável", vc - va
            if (0 if np.isnan(vc) else vc) == 0 and (0 if np.isnan(va) else va) == 0:
                continue
            linhas.append({"ano": t, "cd_unidade_orc": k[0], "nm_unidade_orc": ref["nm_unidade_orc"],
                           "cd_acao": k[1], "nm_acao": ref["nm_acao"], "cd_subfuncao": ref["cd_subfuncao"],
                           "nm_subfuncao": ref["nm_subfuncao"], "empenhado_real_ano_anterior": va,
                           "empenhado_real": vc, "contribuicao_real": contrib, "situacao": situacao})
    r = pd.DataFrame(linhas)
    r["abs"] = r["contribuicao_real"].abs()
    return r.sort_values(["ano", "abs"], ascending=[True, False]).drop(columns="abs").reset_index(drop=True)


def resumo_quebra_codificacao(rastreio: pd.DataFrame) -> pd.DataFrame:
    """Quanto da variação de cada ano vem de códigos novos/extintos."""
    g = rastreio.groupby(["ano", "situacao"])["contribuicao_real"].agg(["count", "sum"]).unstack(fill_value=0)
    g.columns = [f"{b}_{a}".replace(" ", "_") for a, b in g.columns]
    return g.reset_index()
