"""Gera a memória de cálculo em planilha, com fórmulas vivas.

Cada valor derivado é uma fórmula do Excel/LibreOffice que referencia as
células de entrada. Quem abrir o arquivo vê como cada número foi obtido e pode
alterar um parâmetro (p. ex., o limiar) e ver o efeito. Os valores de entrada
(somas anuais e por subfunção) vêm de ``data/processed`` e estão marcados em
azul; tudo o que está em preto é fórmula.
"""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from . import config as C

AZUL = Font(color="1F4E9E")
NEGRITO = Font(bold=True)
CAB = PatternFill("solid", fgColor="E8F0FB")
PARAM = PatternFill("solid", fgColor="FFF4CC")
FINO = Border(bottom=Side(style="thin", color="999999"))
MOEDA = '#,##0.00'
PCT = '0.00%'


def _cab(ws, linha, nomes):
    for j, n in enumerate(nomes, 1):
        c = ws.cell(linha, j, n); c.font = NEGRITO; c.fill = CAB; c.border = FINO
        c.alignment = Alignment(wrap_text=True, vertical="center")


def _larguras(ws, larg):
    for j, w in enumerate(larg, 1):
        ws.column_dimensions[get_column_letter(j)].width = w


def gerar(serie, painel, ipca, destino):
    wb = Workbook()

    # ------------------------------------------------------------ LEIA-ME
    ws = wb.active; ws.title = "LEIA-ME"
    texto = [
        ("Memória de cálculo – Orçamento da Educação de Minas Gerais, 2015–2025", True),
        ("Gerada por scripts/run_all.py a partir de data/raw. Não edite à mão: rode o pipeline novamente.", False),
        ("", False),
        ("Convenção: azul = dado de entrada (soma dos registros brutos); preto = fórmula; amarelo = parâmetro editável.", False),
        ("Abas: Parametros · IPCA · Serie_F12 · Serie_SEE · Persistencia · Sensibilidade · Subfuncoes · Distribuicao · HHI", False),
        ("Todas as fórmulas estão documentadas em docs/memoria_de_calculo.md, com o exemplo numérico de cada indicador.", False),
    ]
    for i, (t, b) in enumerate(texto, 1):
        ws.cell(i, 1, t).font = Font(bold=b, size=13 if b else 11)
    ws.column_dimensions["A"].width = 120

    # ------------------------------------------------------------ Parâmetros
    wp = wb.create_sheet("Parametros")
    _cab(wp, 1, ["Parâmetro", "Valor", "Uso"])
    params = [("Limiar incremental", C.LIMIAR_INCREMENTAL, "|Δ| ≤ limiar → incremental"),
              ("Limiar de pontuação", C.LIMIAR_PONTUACAO, "|Δ| ≥ limiar → pontuação candidata"),
              ("Limiar de sensibilidade 1", C.LIMIARES_SENSIBILIDADE[0], "Aba Sensibilidade"),
              ("Limiar de sensibilidade 2", C.LIMIARES_SENSIBILIDADE[1], "Aba Sensibilidade"),
              ("Limiar de sensibilidade 3", C.LIMIARES_SENSIBILIDADE[2], "Aba Sensibilidade"),
              ("Piso da base anterior (R$)", C.PISO_BASE_SUBFUNCAO, "Aba Distribuicao")]
    for i, (n, v, u) in enumerate(params, 2):
        wp.cell(i, 1, n); c = wp.cell(i, 2, v); c.fill = PARAM
        c.number_format = PCT if v < 1 else MOEDA; wp.cell(i, 3, u)
    _larguras(wp, [30, 18, 45])
    P_INC, P_PONT, P_PISO = "Parametros!$B$2", "Parametros!$B$3", "Parametros!$B$7"

    # ------------------------------------------------------------ IPCA
    wi = wb.create_sheet("IPCA")
    _cab(wi, 1, ["Ano", "IPCA no ano", "Fator p/ dez./2025", "Fórmula do fator"])
    anos = list(ipca.index)
    n = len(anos)
    for i, a in enumerate(anos, 2):
        wi.cell(i, 1, a); c = wi.cell(i, 2, float(ipca[a])); c.font = AZUL; c.number_format = PCT
        if a == C.ANO_BASE_DEFLACAO:
            wi.cell(i, 3, 1); wi.cell(i, 4, "ano-base: fator = 1")
        else:
            wi.cell(i, 3, f"=C{i + 1}*(1+B{i + 1})"); wi.cell(i, 4, "fator(t) = fator(t+1) × (1 + IPCA(t+1))")
        wi.cell(i, 3).number_format = "0.000000"
    _larguras(wi, [8, 14, 18, 42])
    FATOR = f"IPCA!$A$2:$C${n + 1}"

    # ------------------------------------------------------------ Séries
    def aba_serie(nome, recorte):
        w = wb.create_sheet(nome)
        cols = ["Ano", "Dotação inicial", "Crédito autorizado", "Empenhado", "Liquidado", "Pago", "Fator IPCA",
                "Dotação real", "Autorizado real", "Empenhado real", "Liquidado real", "Pago real",
                "Δ empenho nominal", "Δ empenho real", "Classificação", "Empenhado/autorizado",
                "Liquidado/empenhado", "Pago/liquidado"]
        _cab(w, 1, cols)
        d = serie[serie.recorte == recorte].reset_index(drop=True)
        for i, r in d.iterrows():
            L = i + 2
            w.cell(L, 1, int(r.ano))
            for j, col in enumerate(["dotacao_inicial", "vr_credito_autorizado", "vr_empenhado", "vr_liquidado", "vr_pago"], 2):
                v = r[col]
                if v == v:  # não-NaN
                    c = w.cell(L, j, float(v)); c.font = AZUL; c.number_format = MOEDA
            w.cell(L, 7, f"=VLOOKUP(A{L},{FATOR},3,0)").number_format = "0.000000"
            for j, src in zip(range(8, 13), "BCDEF"):
                w.cell(L, j, f'=IF({src}{L}="","",{src}{L}*$G{L})').number_format = MOEDA
            if i > 0:
                w.cell(L, 13, f"=D{L}/D{L - 1}-1").number_format = PCT
                w.cell(L, 14, f"=J{L}/J{L - 1}-1").number_format = PCT
                w.cell(L, 15, f'=IF(ABS(N{L})<={P_INC},"Incremental/estável",IF(ABS(N{L})<{P_PONT},"Mudança moderada","Pontuação candidata"))')
            w.cell(L, 16, f'=IF(C{L}="","",D{L}/C{L})').number_format = PCT
            w.cell(L, 17, f"=E{L}/D{L}").number_format = PCT
            w.cell(L, 18, f"=F{L}/E{L}").number_format = PCT
        _larguras(w, [7] + [17] * 5 + [10] + [17] * 5 + [12, 12, 22, 14, 14, 14])
        w.freeze_panes = "B2"
        return w, len(d)

    aba_serie("Serie_F12", "funcao12")
    aba_serie("Serie_SEE", "see1261")

    # ------------------------------------------------------------ Persistência
    wr = wb.create_sheet("Persistencia")
    _cab(wr, 1, ["Recorte", "Estágio", "Base", "n", "α (INTERCEPT)", "β (SLOPE)", "R² (RSQ)", "Intervalo"])
    linha = 2
    estagios = [("Empenhado", "D", "J"), ("Liquidado", "E", "K"), ("Pago", "F", "L")]
    for aba, rot in (("Serie_F12", "Função 12"), ("Serie_SEE", "SEE/MG")):
        for est, cn, cr in estagios:
            for base, col in (("real", cr), ("nominal", cn)):
                y = f"{aba}!{col}3:{col}12"; x = f"{aba}!{col}2:{col}11"
                wr.cell(linha, 1, rot); wr.cell(linha, 2, est); wr.cell(linha, 3, base); wr.cell(linha, 4, 10)
                wr.cell(linha, 5, f"=INTERCEPT({y},{x})").number_format = MOEDA
                wr.cell(linha, 6, f"=SLOPE({y},{x})").number_format = "0.0000"
                wr.cell(linha, 7, f"=RSQ({y},{x})").number_format = "0.0000"
                wr.cell(linha, 8, "2015→2016 … 2024→2025")
                linha += 1
    wr.cell(linha + 1, 1, "Y = valor do exercício t (linhas 3–12); X = valor de t−1 (linhas 2–11). "
            "A base 'real' é a especificação da metodologia; a 'nominal' reproduz a planilha original.")
    _larguras(wr, [12, 12, 9, 5, 20, 12, 12, 24])

    # ------------------------------------------------------------ Sensibilidade
    wsn = wb.create_sheet("Sensibilidade")
    _cab(wsn, 1, ["Recorte", "Limiar", "Variações", "Incrementais (|Δ| ≤ limiar)", "Não incrementais", "Proporção não incremental"])
    linha = 2
    for aba, rot in (("Serie_F12", "Função 12"), ("Serie_SEE", "SEE/MG")):
        for k in range(3):
            rng = f"{aba}!N3:N12"
            wsn.cell(linha, 1, rot); wsn.cell(linha, 2, f"=Parametros!B{4 + k}").number_format = PCT
            wsn.cell(linha, 3, f"=COUNT({rng})")
            wsn.cell(linha, 4, f'=COUNTIFS({rng},"<="&B{linha},{rng},">="&-B{linha})')
            wsn.cell(linha, 5, f"=C{linha}-D{linha}")
            wsn.cell(linha, 6, f"=E{linha}/C{linha}").number_format = PCT
            linha += 1
    _larguras(wsn, [12, 10, 11, 26, 18, 24])

    # ------------------------------------------------------------ Subfunções e distribuição
    wsf = wb.create_sheet("Subfuncoes")
    _cab(wsf, 1, ["Ano", "Cód.", "Subfunção", "Empenhado nominal", "Fator IPCA", "Empenhado real",
                  "Real no ano anterior", "Variação real", "Entra na distribuição?", "Participação", "Participação²", "Chave ano|subfunção"])
    p = painel.reset_index(drop=True)
    total_rows = len(p) + 1
    for i, r in p.iterrows():
        L = i + 2
        wsf.cell(L, 1, int(r.ano)); wsf.cell(L, 2, int(r.cd_subfuncao)); wsf.cell(L, 3, r.nm_subfuncao)
        c = wsf.cell(L, 4, float(r.vr_empenhado)); c.font = AZUL; c.number_format = MOEDA
        wsf.cell(L, 5, f"=VLOOKUP(A{L},{FATOR},3,0)").number_format = "0.000000"
        wsf.cell(L, 6, f"=D{L}*E{L}").number_format = MOEDA
        wsf.cell(L, 12, f'=A{L}&"|"&B{L}')
        wsf.cell(L, 7, f'=IFERROR(INDEX($F$2:$F${total_rows},MATCH((A{L}-1)&"|"&B{L},$L$2:$L${total_rows},0)),"")').number_format = MOEDA
        wsf.cell(L, 8, f'=IF(G{L}="","",F{L}/G{L}-1)').number_format = PCT
        wsf.cell(L, 9, f'=IF(G{L}="","não",IF(G{L}>={P_PISO},"sim","não"))')
        wsf.cell(L, 10, f"=D{L}/SUMIF($A$2:$A${total_rows},A{L},$D$2:$D${total_rows})").number_format = "0.0000"
        wsf.cell(L, 11, f"=J{L}^2").number_format = "0.000000"
    _larguras(wsf, [7, 6, 40, 18, 10, 18, 18, 13, 12, 12, 13, 14]); wsf.freeze_panes = "D2"

    wd = wb.create_sheet("Distribuicao")
    rng_v, rng_ok = f"Subfuncoes!$H$2:$H${total_rows}", f"Subfuncoes!$I$2:$I${total_rows}"
    _cab(wd, 1, ["Estatística", "Fórmula", "Valor"])
    # coluna auxiliar com as variações que entram (para MEDIAN/SKEW/KURT)
    wd.cell(1, 6, "Variações incluídas").font = NEGRITO
    for i in range(2, total_rows + 1):
        wd.cell(i, 6, f'=IF(Subfuncoes!I{i}="sim",Subfuncoes!H{i},"")').number_format = PCT
    aux = f"$F$2:$F${total_rows}"
    stats_ = [("n", f'=COUNTIF({rng_ok},"sim")', "0"),
              ("Média", f"=AVERAGE({aux})", PCT), ("Mediana", f"=MEDIAN({aux})", PCT),
              ("Desvio-padrão", f"=STDEV({aux})", PCT), ("Assimetria", f"=SKEW({aux})", "0.000"),
              ("Curtose excedente", f"=KURT({aux})", "0.000"),
              ("Proporção |Δ| ≥ 10%", f'=(COUNTIF({aux},">=0.1")+COUNTIF({aux},"<=-0.1"))/B2', PCT),
              ("Proporção |Δ| ≥ 50%", f'=(COUNTIF({aux},">=0.5")+COUNTIF({aux},"<=-0.5"))/B2', PCT)]
    for i, (nome, f, fmt) in enumerate(stats_, 2):
        wd.cell(i, 1, nome); wd.cell(i, 2, f[1:].replace("/B2", "/C2")); c = wd.cell(i, 3, f); c.number_format = fmt
    # B2 referenced by proportions -> point to C2
    for i in (8, 9):
        wd.cell(i, 3).value = wd.cell(i, 3).value.replace("/B2", "/C2")
    wd.cell(11, 1, "Shapiro–Wilk não tem fórmula nativa na planilha: valor calculado em Python (data/processed/distribuicao_subfuncoes.csv).")
    _larguras(wd, [24, 70, 14, 2, 2, 16])

    # ------------------------------------------------------------ HHI
    wh = wb.create_sheet("HHI")
    _cab(wh, 1, ["Ano", "HHI = Σ participação²", "Subfunções com empenho"])
    for i, a in enumerate(range(C.ANO_INICIAL, C.ANO_FINAL + 1), 2):
        wh.cell(i, 1, a)
        wh.cell(i, 2, f"=SUMIF(Subfuncoes!$A$2:$A${total_rows},A{i},Subfuncoes!$K$2:$K${total_rows})").number_format = "0.0000"
        wh.cell(i, 3, f'=COUNTIFS(Subfuncoes!$A$2:$A${total_rows},A{i},Subfuncoes!$D$2:$D${total_rows},">0")')
    _larguras(wh, [8, 22, 22])

    wb.save(destino)
