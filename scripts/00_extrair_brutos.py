"""Etapa 0 – extrai os dados brutos das planilhas originais para CSV.

Lê as duas planilhas entregues pelo pesquisador (em ``data/original``) e grava
em ``data/raw`` apenas os dados de entrada, sem nenhum cálculo:

* execucao_detalhada.csv  – empenhado, liquidado e pago (SIAFI-MG/dados abertos)
* creditos_detalhados.csv – créditos iniciais, adicionais e anulações (2020–2025)
* ipca_anual.csv          – variação anual do IPCA (IBGE)
* dotacao_inicial_loa.csv – dotação inicial das LOAs 2015–2025 (base bruta LOA)
* fontes.csv              – proveniência de cada conjunto de dados

Os CSV são o ponto de partida de todo o pipeline. As planilhas originais são
mantidas intactas para auditoria (hash SHA-256 em data/original/SHA256SUMS).
"""
import sys
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from orcamento_mg import config as C  # noqa: E402


def extrair_execucao_e_creditos() -> None:
    ex = pd.read_excel(C.PLANILHA_ANALISE, sheet_name="Execucao_Detalhada")
    ex.to_csv(C.DADOS_BRUTOS / "execucao_detalhada.csv", index=False)
    cr = pd.read_excel(C.PLANILHA_ANALISE, sheet_name="Creditos_Detalhados")
    cr = cr.rename(columns={"ano_particao": "ano"})
    cr.to_csv(C.DADOS_BRUTOS / "creditos_detalhados.csv", index=False)
    print(f"execução: {len(ex)} linhas; créditos: {len(cr)} linhas")


def extrair_ipca() -> None:
    ws = load_workbook(C.PLANILHA_ANALISE, data_only=True)["IPCA"]
    linhas = [r for r in ws.iter_rows(values_only=True) if isinstance(r[0], int)]
    df = pd.DataFrame(
        [(r[0], r[1], r[3]) for r in linhas],
        columns=["ano", "ipca_variacao_anual", "fonte"],
    )
    df.to_csv(C.DADOS_BRUTOS / "ipca_anual.csv", index=False)
    print(f"IPCA: {len(df)} anos")


def extrair_dotacao_loa() -> None:
    wb = load_workbook(C.PLANILHA_LOA, data_only=True)
    registros = []
    # Função 12 – aba 02_Funcoes (2015 e 2017–2025; 2016 sem desagregação por função)
    for r in wb["02_Funcoes"].iter_rows(values_only=True):
        if isinstance(r[0], int) and isinstance(r[1], (int, float)):
            registros.append((r[0], "funcao12", int(r[1]), r[10], "02_Funcoes"))
    # UO 1261 – aba 03_SEE_total (2019–2025)
    for r in wb["03_SEE_total"].iter_rows(values_only=True):
        if isinstance(r[0], int) and isinstance(r[1], (int, float)):
            registros.append((r[0], "see1261", int(r[1]), "Despesa_Acao (UO 1261)", "03_SEE_total"))
    df = pd.DataFrame(registros, columns=["ano", "recorte", "dotacao_inicial", "arquivo_fonte", "aba_origem"])
    df = df.sort_values(["recorte", "ano"])
    df.to_csv(C.DADOS_BRUTOS / "dotacao_inicial_loa.csv", index=False)
    print(f"dotação inicial: {len(df)} registros")


def extrair_fontes() -> None:
    ws = load_workbook(C.PLANILHA_ANALISE, data_only=True)["Fontes"]
    linhas = [r for r in ws.iter_rows(values_only=True)]
    cab = list(linhas[1])
    df = pd.DataFrame([r for r in linhas[2:] if r[0]], columns=cab)
    df.to_csv(C.DADOS_BRUTOS / "fontes.csv", index=False)


if __name__ == "__main__":
    C.DADOS_BRUTOS.mkdir(parents=True, exist_ok=True)
    extrair_execucao_e_creditos()
    extrair_ipca()
    extrair_dotacao_loa()
    extrair_fontes()
