"""Testes de reprodução: garantem que o pipeline gera os números da dissertação.

Rode com:  pytest -q
"""
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from orcamento_mg import config as C  # noqa: E402
from orcamento_mg import indicadores as I  # noqa: E402
from orcamento_mg.conferencia import conferir_com_planilha_original  # noqa: E402
from orcamento_mg.dados import fatores_ipca, filtrar_recorte, ler_execucao  # noqa: E402


@pytest.fixture(scope="module")
def serie():
    return I.serie_anual()


@pytest.fixture(scope="module")
def painel():
    return I.painel_subfuncoes()


def test_recortes_nao_se_somam():
    ex = ler_execucao()
    f12 = filtrar_recorte(ex, "funcao12")
    see = filtrar_recorte(ex, "see1261")
    # A parte SEE da Função 12 deve ser idêntica ao recorte SEE em todos os anos
    a = f12[f12.cd_unidade_orc == 1261].groupby("ano").vr_empenhado.sum()
    b = see.groupby("ano").vr_empenhado.sum()
    assert np.allclose(a, b)


def test_fator_ipca_encadeado():
    f = fatores_ipca()
    assert f[2025] == 1.0
    assert f[2024] == pytest.approx(1.0426)
    assert f[2015] == pytest.approx(1.6478753508, rel=1e-9)


def test_numeros_centrais_da_dissertacao(serie):
    f = serie[serie.recorte == "funcao12"].set_index("ano")
    assert f.loc[2015, "vr_empenhado_real"] / 1e9 == pytest.approx(15.31, abs=0.005)
    assert f.loc[2025, "vr_empenhado_real"] / 1e9 == pytest.approx(21.58, abs=0.005)
    assert f.loc[2020, "var_real_empenhado"] == pytest.approx(-0.1073, abs=5e-5)
    assert f.loc[2021, "var_real_empenhado"] == pytest.approx(0.4334, abs=5e-5)
    assert f.loc[2022, "var_real_empenhado"] == pytest.approx(0.1121, abs=5e-5)
    assert f.loc[2020, "taxa_empenhado_autorizado"] == pytest.approx(0.754, abs=5e-4)
    s = serie[serie.recorte == "see1261"].set_index("ano")
    assert s.loc[2021, "var_real_empenhado"] == pytest.approx(0.4099, abs=5e-5)


def test_persistencia(serie):
    nom = I.persistencia(serie, "nominal").set_index(["recorte", "estagio"])
    real = I.persistencia(serie, "real").set_index(["recorte", "estagio"])
    # A planilha original (nominal) é reproduzida exatamente
    assert nom.loc[("funcao12", "Empenhado"), "beta"] == pytest.approx(1.0087, abs=1e-4)
    assert nom.loc[("funcao12", "Empenhado"), "r2"] == pytest.approx(0.8442, abs=1e-4)
    # Em valores reais (especificação declarada na metodologia) a persistência é menor
    assert real.loc[("funcao12", "Empenhado"), "beta"] == pytest.approx(0.8181, abs=1e-4)
    assert real.loc[("funcao12", "Empenhado"), "r2"] == pytest.approx(0.5824, abs=1e-4)
    assert real.loc[("funcao12", "Empenhado"), "p_beta"] < 0.05


def test_sensibilidade(serie):
    s = I.sensibilidade(serie)
    f = s[s.recorte == "funcao12"].set_index("limiar")["nao_incrementais"]
    assert list(f.values) == [7, 3, 1]


def test_hhi(painel):
    h = I.hhi(painel).set_index("ano")["hhi"]
    assert h[2015] == pytest.approx(0.3752, abs=1e-4)
    assert h[2025] == pytest.approx(0.2208, abs=1e-4)


def test_distribuicao(painel):
    d = I.distribuicao(painel)
    assert d["n"] == 138
    assert d["mediana"] == pytest.approx(-0.0033, abs=1e-4)
    assert d["shapiro_p"] < 0.001


def test_rastreamento_2020_recodificacao_total():
    r = I.rastreamento_acoes()
    a2020 = r[r.ano == 2020]
    assert (a2020.situacao == "comparável").sum() == 0
    a2021 = r[r.ano == 2021].set_index("cd_acao")["contribuicao_real"]
    assert a2021[2065] / 1e9 == pytest.approx(1.859, abs=1e-3)
    assert a2021[4302] / 1e9 == pytest.approx(1.155, abs=1e-3)


def test_conferencia_sem_divergencia_inexplicada(serie, painel):
    conf = conferir_com_planilha_original(serie, pd.concat([I.persistencia(serie, "nominal")]),
                                          I.sensibilidade(serie), I.hhi(painel), painel, I.rastreamento_acoes())
    assert (conf.situacao == "diverge").sum() == 0
    assert (conf.situacao == "confere").sum() >= 480


@pytest.mark.skipif(shutil.which("soffice") is None and shutil.which("libreoffice") is None,
                    reason="LibreOffice não instalado")
def test_memoria_xlsx_recalculada_igual_ao_python(tmp_path):
    from openpyxl import load_workbook
    origem = RAIZ / "outputs" / "memoria_de_calculo.xlsx"
    if not origem.exists():
        pytest.skip("rode scripts/run_all.py antes")
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    subprocess.run([exe, "--headless", "--convert-to", "xlsx", "--outdir", str(tmp_path), str(origem)],
                   check=True, capture_output=True, timeout=180)
    wb = load_workbook(tmp_path / origem.name, data_only=True)
    assert wb["Distribuicao"]["C2"].value == 138
    assert wb["Persistencia"]["F2"].value == pytest.approx(0.8181, abs=1e-4)
    assert wb["HHI"]["B2"].value == pytest.approx(0.3752, abs=1e-4)
