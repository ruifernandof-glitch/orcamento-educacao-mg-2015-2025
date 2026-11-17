"""Figuras da dissertação (PNG, 300 dpi, fonte serifada compatível com Times)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.ticker as mticker  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

from . import config as C  # noqa: E402

AZUL, LARANJA, CINZA = "#2a78d6", "#eb6834", "#8a8a8a"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["Times New Roman", "Liberation Serif", "DejaVu Serif"], "font.size": 11,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#555",
    "axes.grid": True, "grid.color": "#e3e3e3", "grid.linewidth": 0.6, "axes.unicode_minus": True,
})


def _br(x, casas=2):
    return f"{x:.{casas}f}".replace(".", ",").replace("-", "−")


def fig_modelo_pesquisa(destino):
    fig, ax = plt.subplots(figsize=(6.3, 4.1), dpi=300)
    ax.axis("off"); ax.set_xlim(0, 10); ax.set_ylim(0.85, 6.5)

    def caixa(x, y, w, h, txt, fc="#ffffff", ec="#333", negrito=False, fs=7.4):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=fc, ec=ec, lw=0.9))
        ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=fs,
                fontweight="bold" if negrito else "normal")

    cab = [(0.0, "Teorias"), (2.55, "Proposições"), (5.1, "Indicadores"), (7.65, "Conclusão permitida")]
    for x, t in cab:
        caixa(x, 5.95, 2.35, 0.5, t, fc="#e8f0fb", ec=AZUL, negrito=True, fs=8.8)
    linhas = [
        ("Incrementalismo\n(Lindblom; Wildavsky)", "Dependência da base\ne ajustes marginais",
         "β e R² (Y em t sobre t−1);\nlimiares de 5%, 10% e 15%", "Persistência compatível\ncom incrementalismo"),
        ("Equilíbrio pontuado\n(Baumgartner; Jones)", "Mudanças desproporcionais\ne caudas pesadas",
         "|Δ| ≥ 10%; assimetria,\ncurtose, Shapiro–Wilk", "Pontuações candidatas;\ncompatibilidade com PET"),
        ("Atenção e agenda\n(equilíbrio pontuado)", "Recomposição interna\ndo gasto",
         "HHI por subfunção;\ncontribuição por ação", "Mudança composicional\ndescritiva"),
        ("Atrito institucional;\nveto players", "Conversão da autorização\nem execução",
         "Empenhado/autorizado;\nliquidado; pago", "Indício de atrito\n(requer triangulação)"),
    ]
    y = 4.75
    for linha in linhas:
        for k, (x, _) in enumerate(cab):
            caixa(x, y, 2.35, 0.95, linha[k])
            if k < 3:
                ax.annotate("", xy=(x + 2.55, y + 0.475), xytext=(x + 2.35, y + 0.475),
                            arrowprops=dict(arrowstyle="-|>", color="#444", lw=0.9))
        y -= 1.12
    ax.text(5, 1.0, "Robustez: Função 12 × UO 1261 – SEE/MG; valores reais (IPCA, dez./2025)",
            ha="center", fontsize=8.5, style="italic", color="#333")
    fig.savefig(destino, bbox_inches="tight"); plt.close(fig)


def fig_empenho_real(serie, destino):
    fig, ax = plt.subplots(figsize=(6.3, 3.3), dpi=300)
    f = serie[serie.recorte == "funcao12"]; s = serie[serie.recorte == "see1261"]
    ax.plot(f.ano, f.vr_empenhado_real / 1e9, color=AZUL, lw=2, marker="o", ms=5, label=C.RECORTES["funcao12"])
    ax.plot(s.ano, s.vr_empenhado_real / 1e9, color=LARANJA, lw=2, marker="s", ms=5, ls="--", label=C.RECORTES["see1261"])
    ax.axvspan(2019.5, 2022.5, color="#f1f1f1", zorder=0)
    ax.text(2021, 22.6, "2020–2022", ha="center", fontsize=9, color="#555")
    ax.set_ylabel("R$ bilhões (dez./2025)"); ax.set_xticks(f.ano); ax.set_ylim(10, 23.5); ax.set_xlim(2014.6, 2025.6)
    for ano, dy in ((2015, 8), (2025, 6)):
        v = float(f.loc[f.ano == ano, "vr_empenhado_real"].iloc[0]) / 1e9
        ax.annotate(_br(v), (ano, v), xytext=(0, dy), textcoords="offset points", fontsize=9, ha="center")
    ax.legend(frameon=False, loc="upper left", fontsize=9.5)
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)


def fig_variacoes(serie, destino):
    f = serie[(serie.recorte == "funcao12") & serie.var_real_empenhado.notna()]
    fig, ax = plt.subplots(figsize=(6.3, 3.3), dpi=300)
    cores = [LARANJA if abs(v) >= C.LIMIAR_PONTUACAO else AZUL for v in f.var_real_empenhado]
    ax.bar(f.ano, f.var_real_empenhado * 100, color=cores, width=0.62, zorder=3)
    for lim, est in zip(C.LIMIARES_SENSIBILIDADE, (":", "--", "-.")):
        for sinal in (1, -1):
            ax.axhline(sinal * lim * 100, color=CINZA, lw=0.9, ls=est, zorder=2)
        ax.text(2025.55, lim * 100, f"{int(lim * 100)}%", va="center", fontsize=8.5, color="#555")
    ax.axhline(0, color="#333", lw=0.8, zorder=4)
    for x, v in zip(f.ano, f.var_real_empenhado):
        rot = (f"{v * 100:+.2f}" if abs(v) < 0.01 else f"{v * 100:+.1f}").replace(".", ",").replace("-", "−")
        ax.text(x, v * 100 + (1.4 if v >= 0 else -1.4), rot, ha="center", va="bottom" if v >= 0 else "top", fontsize=8.5)
    ax.set_xticks(f.ano); ax.set_ylabel("Variação real do empenho (%)"); ax.set_ylim(-17, 50); ax.set_xlim(2015.4, 2026)
    ax.legend(handles=[Patch(color=AZUL, label="|Δ| < 10%"), Patch(color=LARANJA, label="|Δ| ≥ 10% (pontuação candidata)")],
              frameon=False, fontsize=9, loc="upper left")
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)


def fig_hhi(hhi, destino):
    fig, ax = plt.subplots(figsize=(6.3, 3.0), dpi=300)
    ax.plot(hhi.ano, hhi.hhi, color=AZUL, lw=2, marker="o", ms=5)
    for a, h in zip(hhi.ano, hhi.hhi):
        ax.text(a, h + 0.006, _br(h, 3), ha="center", fontsize=8.3)
    ax.set_xticks(hhi.ano); ax.set_ylabel("HHI (0 a 1)"); ax.set_ylim(0.18, 0.40)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: _br(x)))
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)


def fig_histograma(painel, destino):
    v = painel.loc[painel.na_distribuicao, "var_real"].dropna()
    lv = np.log1p(v)
    fig, ax = plt.subplots(figsize=(6.3, 3.0), dpi=300)
    ax.hist(lv, bins=np.arange(-2.5, 4.51, 0.25), color=AZUL, edgecolor="white", linewidth=1.5, zorder=3)
    ax.axvline(0, color="#333", lw=0.8)
    for lim in (np.log(0.9), np.log(1.1)):
        ax.axvline(lim, color=CINZA, lw=0.9, ls="--")
    ax.set_xlabel("ln(1 + variação real) por subfunção e ano"); ax.set_ylabel("Frequência")
    ax.text(0.98, 0.92, f"n = {len(v)}", transform=ax.transAxes, ha="right", fontsize=9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: _br(x, 1)))
    fig.tight_layout(); fig.savefig(destino); plt.close(fig)
