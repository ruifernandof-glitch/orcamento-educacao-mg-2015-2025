"""Tabelas no formato da dissertação (números em padrão brasileiro).

Gera CSVs prontos para colar no Word (separador ';', vírgula decimal).
A numeração segue a versão revisada da dissertação.
"""
import pandas as pd

from . import config as C


def br(x, casas=2):
    if pd.isna(x):
        return "—"
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def pct(x, casas=2, sinal=True):
    if pd.isna(x):
        return "—"
    s = f"{x * 100:+.{casas}f}%" if sinal else f"{x * 100:.{casas}f}%"
    return s.replace(".", ",").replace("-", "−")


def _salvar(df, pasta, nome):
    df.to_csv(pasta / nome, sep=";", index=False, encoding="utf-8-sig")


def gerar_tabelas_dissertacao(serie, pers, sens, dist, rast, pasta):
    f = serie[serie.recorte == "funcao12"].set_index("ano")
    s = serie[serie.recorte == "see1261"].set_index("ano")

    t6 = pd.DataFrame({
        "Ano": f.index,
        "Função 12 (R$ bi)": [br(v / 1e9) for v in f.vr_empenhado_real],
        "Δ real F12": [pct(v) for v in f.var_real_empenhado],
        "SEE/MG (R$ bi)": [br(v / 1e9) for v in s.vr_empenhado_real],
        "Δ real SEE": [pct(v) for v in s.var_real_empenhado],
        "SEE/F12": [pct(a / b, 1, False) for a, b in zip(s.vr_empenhado, f.vr_empenhado)],
        "Classificação (F12)": f.classificacao.values,
    })
    _salvar(t6, pasta, "tabela06_empenho_real.csv")

    rot = {"funcao12": "Função 12", "see1261": "SEE/MG"}
    t7 = pers.assign(Recorte=pers.recorte.map(rot))[[
        "base", "Recorte", "estagio", "n_pares", "anos", "beta", "erro_padrao_beta", "r2", "p_beta", "beta_log", "r2_log"]]
    t7 = t7.rename(columns={"base": "Base", "estagio": "Estágio", "n_pares": "n", "anos": "Intervalo", "beta": "β",
                            "erro_padrao_beta": "EP(β)", "r2": "R²", "p_beta": "p(β)", "beta_log": "β log", "r2_log": "R² log"})
    for c in ["β", "EP(β)", "R²", "β log", "R² log"]:
        t7[c] = t7[c].map(lambda v: br(v, 3))
    t7["p(β)"] = t7["p(β)"].map(lambda v: "< 0,001" if v < 0.001 else br(v, 3))
    _salvar(t7, pasta, "tabela07_persistencia.csv")

    t8 = sens[sens.recorte == "funcao12"][["limiar", "incrementais", "nao_incrementais", "anos_nao_incrementais"]].copy()
    t8["limiar"] = t8.limiar.map(lambda v: pct(v, 0, False))
    t8.columns = ["Limiar", "Incrementais", "Não incrementais", "Anos não incrementais"]
    _salvar(t8, pasta, "tabela08_sensibilidade_limiares.csv")

    t9 = f.loc[2020:, ["var_real_empenhado", "classificacao"]].reset_index()
    t9["var_real_empenhado"] = t9.var_real_empenhado.map(pct)
    t9.columns = ["Ano", "Variação real do empenho", "Classificação"]
    _salvar(t9, pasta, "tabela09_sequencia_2020_2025.csv")

    t10 = dist.copy()
    for c in ["media", "mediana", "desvio_padrao", "prop_abs_ge_10", "prop_abs_ge_50"]:
        t10[c] = t10[c].map(lambda v: pct(v, 1, False) if c.startswith("prop") else pct(v, 1))
    for c in ["assimetria", "curtose_excedente", "shapiro_w"]:
        t10[c] = t10[c].map(lambda v: br(v, 2))
    t10["shapiro_p"] = t10.shapiro_p.map(lambda v: "< 0,001" if v < 0.001 else br(v, 3))
    _salvar(t10, pasta, "tabela10_distribuicao_subfuncoes.csv")

    t11 = rast[rast.ano.isin([2020, 2021, 2022])].copy()
    t11["ordem"] = t11.groupby("ano").cumcount()
    t11 = t11[t11.ordem < 8]
    t11 = pd.DataFrame({"Ano": t11.ano, "Ação": t11.cd_acao.astype(str) + " – " + t11.nm_acao.str.title(),
                        "Subfunção": t11.nm_subfuncao.str.title(),
                        "Contribuição real (R$ bi)": t11.contribuicao_real.map(lambda v: br(v / 1e9)),
                        "Situação do código": t11.situacao})
    _salvar(t11, pasta, "tabela11_rastreamento_acoes.csv")

    t12 = f[["taxa_empenhado_autorizado", "taxa_liquidado_empenhado", "taxa_pago_liquidado"]].reset_index()
    for c in t12.columns[1:]:
        t12[c] = t12[c].map(lambda v: pct(v, 1, False))
    t12.columns = ["Ano", "Empenhado/autorizado", "Liquidado/empenhado", "Pago/liquidado"]
    _salvar(t12, pasta, "tabela12_taxas_execucao.csv")
