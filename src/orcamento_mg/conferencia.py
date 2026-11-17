"""Confronta os resultados reproduzidos com a planilha original de análise.

Cada linha registra: indicador, valor na planilha original, valor reproduzido,
diferença e situação ('confere', 'diverge – explicado' ou 'diverge').
As divergências explicadas estão descritas em docs/divergencias.md.
"""
import numpy as np
import pandas as pd
from openpyxl import load_workbook

from . import config as C

TOL_REL = 1e-6


def _linhas(ws):
    return [r for r in ws.iter_rows(values_only=True)]


def conferir_com_planilha_original(serie, pers, sens, hhi, painel, rast):
    wb = load_workbook(C.PLANILHA_ANALISE, data_only=True)
    out = []

    def reg(grupo, indicador, original, reproduzido, explicacao=""):
        if original is None or (isinstance(original, float) and np.isnan(original)):
            return
        dif = reproduzido - original
        ok = abs(dif) <= TOL_REL * max(1.0, abs(original)) or abs(dif) < 1e-6
        situ = "confere" if ok else ("diverge – explicado" if explicacao else "diverge")
        out.append({"grupo": grupo, "indicador": indicador, "original": original, "reproduzido": reproduzido,
                    "diferenca": dif, "situacao": situ, "explicacao": explicacao if not ok else ""})

    # 1. Memória de cálculo anual (valores nominais, reais e variação)
    rot = {"Função 12 - Educação": "funcao12", "UO 1261 - SEE/MG": "see1261"}
    for r in _linhas(wb["Memoria_Calculo"]):
        if not isinstance(r[0], int):
            continue
        s = serie[(serie.recorte == rot[r[1]]) & (serie.ano == r[0])].iloc[0]
        a = f"{rot[r[1]]} {r[0]}"
        reg("Série anual", f"{a} empenhado", r[4], s.vr_empenhado)
        reg("Série anual", f"{a} liquidado", r[5], s.vr_liquidado)
        reg("Série anual", f"{a} pago", r[6], s.vr_pago)
        reg("Série anual", f"{a} fator IPCA", r[7], s.fator_ipca)
        reg("Série anual", f"{a} empenhado real", r[10], s.vr_empenhado_real)
        if isinstance(r[14], float):
            reg("Série anual", f"{a} Δ empenho real", r[14], s.var_real_empenhado)
        if r[2]:
            reg("Série anual", f"{a} dotação inicial", r[2], s.dotacao_inicial)
        if r[3]:
            reg("Série anual", f"{a} crédito autorizado", r[3], s.vr_credito_autorizado)

    # 2. Regressões (a planilha usou valores nominais)
    nomes = {"dotacao_inicial": "Dotação inicial", "vr_credito_autorizado": "Crédito autorizado",
             "vr_empenhado": "Empenhado", "vr_liquidado": "Liquidado", "vr_pago": "Pago"}
    nom = pers[pers.base == "nominal"]
    for r in _linhas(wb["Testes_Estatisticos"]):
        if r and r[1] in nomes:
            rc = "funcao12" if str(r[0]).startswith("Função") else "see1261"
            p = nom[(nom.recorte == rc) & (nom.estagio == nomes[r[1]])].iloc[0]
            exp = ("A planilha pareou 2015→2017, saltando o ano sem dado (2016); o repositório usa só anos consecutivos."
                   if (rc == "funcao12" and r[1] == "dotacao_inicial") else "")
            reg("Persistência (nominal)", f"{rc} {r[1]} n", r[2], p.n_pares, exp)
            reg("Persistência (nominal)", f"{rc} {r[1]} β", r[4], p.beta, exp)
            reg("Persistência (nominal)", f"{rc} {r[1]} R²", r[5], p.r2, exp)

    # 3. Sensibilidade
    for r in _linhas(wb["Testes_Estatisticos"]):
        if r and isinstance(r[1], float) and r[1] in C.LIMIARES_SENSIBILIDADE:
            rc = "funcao12" if str(r[0]).startswith("Função") else "see1261"
            sv = sens[(sens.recorte == rc) & (np.isclose(sens.limiar, r[1]))].iloc[0]
            reg("Sensibilidade", f"{rc} limiar {r[1]:.0%}", r[2], sv.nao_incrementais)

    # 4. HHI
    for r in _linhas(wb["Concentracao_HHI"]):
        if isinstance(r[0], int):
            h = hhi[hhi.ano == r[0]].iloc[0]
            reg("HHI", f"HHI {r[0]}", r[1], h.hhi)
            reg("HHI", f"subfunções com empenho {r[0]}", r[2], h.n_subfuncoes)

    # 5. Variações por subfunção
    pi = painel.set_index(["ano", "cd_subfuncao"])
    for r in _linhas(wb["Painel_Subfuncoes"]):
        if isinstance(r[0], int) and isinstance(r[10], float):
            v = pi.loc[(r[0], r[1]), "var_real"]
            if np.isnan(v):
                out.append({"grupo": "Subfunções", "indicador": f"{r[0]} {r[1]} {r[2]} Δ real", "original": r[10],
                            "reproduzido": np.nan, "diferenca": np.nan, "situacao": "diverge – explicado",
                            "explicacao": "Subfunção sem execução no ano anterior: a planilha comparou com dois anos antes; "
                                          "o repositório não calcula variação entre anos não consecutivos."})
            else:
                reg("Subfunções", f"{r[0]} {r[1]} {r[2]} Δ real", r[10], v)

    # 6. Rastreamento por ação
    from .dados import filtrar_recorte, ler_execucao
    ex = filtrar_recorte(ler_execucao(), "funcao12")
    nomes_por_acao = ex.groupby(["ano", "cd_unidade_orc", "cd_acao"])["nm_acao"].nunique()
    renomeadas = set(nomes_por_acao[nomes_por_acao > 1].index)
    ri = rast.set_index(["ano", "cd_unidade_orc", "cd_acao"])
    for r in _linhas(wb["Rastreamento_Acoes"]):
        if isinstance(r[0], int) and isinstance(r[9], float) and not np.isnan(r[9]):
            k = (r[0], r[1], r[7])
            if k in ri.index:
                exp = ("Ação renomeada dentro do exercício (dois nomes para o mesmo código): a planilha separou os "
                       "registros pelo nome; o repositório agrega pelo código da ação." if k in renomeadas else "")
                reg("Rastreamento", f"{r[0]} ação {r[7]} {r[8]}", r[9], float(ri.loc[k, "contribuicao_real"]), exp)
    return pd.DataFrame(out)
