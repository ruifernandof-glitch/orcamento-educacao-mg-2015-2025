"""Pipeline completo: dados brutos → indicadores → tabelas, figuras e memória.

Uso:  python scripts/run_all.py
Pré-requisito: data/raw preenchido (python scripts/00_extrair_brutos.py).
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from orcamento_mg import config as C  # noqa: E402
from orcamento_mg import figuras as Fg  # noqa: E402
from orcamento_mg import indicadores as I  # noqa: E402
from orcamento_mg import memoria  # noqa: E402
from orcamento_mg.dados import fatores_ipca  # noqa: E402
from orcamento_mg.tabelas import gerar_tabelas_dissertacao  # noqa: E402
from orcamento_mg.conferencia import conferir_com_planilha_original  # noqa: E402


def main():
    for d in (C.DADOS_PROCESSADOS, C.TABELAS, C.FIGURAS):
        d.mkdir(parents=True, exist_ok=True)
    P = C.DADOS_PROCESSADOS

    fat = fatores_ipca()
    fat.rename_axis("ano").reset_index().to_csv(P / "fatores_ipca.csv", index=False)

    serie = I.serie_anual(); serie.to_csv(P / "serie_anual.csv", index=False)
    pers = pd.concat([I.persistencia(serie, "real"), I.persistencia(serie, "nominal")], ignore_index=True)
    pers.to_csv(P / "persistencia_regressoes.csv", index=False)
    sens = I.sensibilidade(serie); sens.to_csv(P / "sensibilidade_limiares.csv", index=False)
    painel = I.painel_subfuncoes(); painel.to_csv(P / "painel_subfuncoes.csv", index=False)
    dist = I.tabela_distribuicao(painel); dist.to_csv(P / "distribuicao_subfuncoes.csv", index=False)
    hhi = I.hhi(painel); hhi.to_csv(P / "concentracao_hhi.csv", index=False)
    rast = I.rastreamento_acoes(); rast.to_csv(P / "rastreamento_acoes.csv", index=False)
    I.resumo_quebra_codificacao(rast).to_csv(P / "quebra_codificacao_acoes.csv", index=False)
    print("indicadores: ok")

    Fg.fig_modelo_pesquisa(C.FIGURAS / "figura1_modelo_pesquisa.png")
    Fg.fig_empenho_real(serie, C.FIGURAS / "figura2_empenho_real.png")
    Fg.fig_variacoes(serie, C.FIGURAS / "figura3_variacoes_limiares.png")
    Fg.fig_hhi(hhi, C.FIGURAS / "figura4_hhi.png")
    Fg.fig_histograma(painel, C.FIGURAS / "figura5_histograma_variacoes.png")
    print("figuras: ok")

    gerar_tabelas_dissertacao(serie, pers, sens, dist, rast, C.TABELAS)
    print("tabelas: ok")

    ipca = pd.read_csv(C.DADOS_BRUTOS / "ipca_anual.csv").set_index("ano")["ipca_variacao_anual"]
    memoria.gerar(serie, painel, ipca, C.RAIZ / "outputs" / "memoria_de_calculo.xlsx")
    print("memória de cálculo: ok")

    conf = conferir_com_planilha_original(serie, pers, sens, hhi, painel, rast)
    conf.to_csv(C.RAIZ / "outputs" / "conferencia_planilha_original.csv", index=False)
    print(conf.groupby("situacao").size().to_string())


if __name__ == "__main__":
    main()
