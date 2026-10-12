"""Lægger en beregningsrapport skrevet i enkel markdown ud på A4-sider som PDF (til bilag i ansøgningen).

Understøtter: overskrifter (#, ##), afsnit, punktlister (-, 1.), tabeller med | og fed tekst markeret med **.
"""
import re
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

X0, X1 = 0.08, 0.92
TEGN_PR_BREDDE = {8.3: 128, 7.0: 152}     # omtrentligt antal tegn pr. hel sidebredde ved skriftstørrelsen


def _ren(s):
    return s.replace("**", "").replace("`", "").strip()


def md_til_pdf(md, pdf_sti, fod):
    linjer = md.splitlines()
    figs, st = [], {"fig": None, "y": 0.0, "nr": 0}

    def ny():
        fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4))
        st.update(fig=fig, y=0.945, nr=st["nr"] + 1)
        fig.text(X0, 0.03, fod, fontsize=7, color="#666666")
        fig.text(X1, 0.03, f"Side {st['nr']}", fontsize=7, ha="right", color="#666666")
        figs.append(fig)

    def plads(h):
        if st["fig"] is None or st["y"] - h < 0.06:
            ny()

    def tekst(s, fs, x=X0, bredde=None, fed=False, luft=0.006):
        bredde = bredde or int(TEGN_PR_BREDDE[8.3] * (X1 - x))
        ls = textwrap.wrap(s, bredde) or [""]
        lh = 0.0142 * fs / 8.3
        plads(len(ls) * lh + luft)
        st["fig"].text(x, st["y"], "\n".join(ls), fontsize=fs, va="top", linespacing=1.38, weight="bold" if fed else "normal")
        st["y"] -= len(ls) * lh + luft

    def tabel(raekker):
        raekker = [[_ren(c) for c in r.strip().strip("|").split("|")] for r in raekker if not re.match(r"^\s*\|?\s*-{3,}", r)]
        n = max(len(r) for r in raekker)
        raekker = [r + [""] * (n - len(r)) for r in raekker]
        br = [max(12, max(len(r[i]) for r in raekker)) for i in range(n)]
        tot = sum(min(b, 60) for b in br)
        andele = [min(b, 60) / tot for b in br]
        fs, lh = 7.0, 0.0142 * 7.0 / 8.3
        tegn = TEGN_PR_BREDDE[7.0] * (X1 - X0)
        for ri, r in enumerate(raekker):
            celler = [textwrap.wrap(c, max(4, int(a * tegn) - 1)) or [""] for c, a in zip(r, andele)]
            hoejde = max(len(c) for c in celler) * lh + 0.005
            plads(hoejde)
            x = X0
            for c, a in zip(celler, andele):
                st["fig"].text(x, st["y"], "\n".join(c), fontsize=fs, va="top", linespacing=1.3, weight="bold" if ri == 0 else "normal")
                x += a * (X1 - X0)
            st["fig"].add_artist(plt.Line2D([X0, X1], [st["y"] - hoejde + 0.003] * 2, color="#cccccc", lw=0.4))
            st["y"] -= hoejde
        st["y"] -= 0.008

    ny()
    i, afsnit = 0, []

    def flush():
        if afsnit:
            tekst(_ren(" ".join(afsnit)), 8.3)
            afsnit.clear()

    while i < len(linjer):
        l = linjer[i]
        if l.startswith("|"):
            flush()
            j = i
            while j < len(linjer) and linjer[j].startswith("|"):
                j += 1
            tabel(linjer[i:j])
            i = j
            continue
        if l.startswith("# "):
            flush()
            if st["y"] < 0.93:
                ny()
            tekst(_ren(l[2:]), 13, fed=True, luft=0.012)
        elif l.startswith("## "):
            flush()
            st["y"] -= 0.006
            tekst(_ren(l[3:]), 10.5, fed=True, luft=0.008)
        elif re.match(r"^\s*(-|\d+\.)\s", l):
            flush()
            m = re.match(r"^\s*(-|\d+\.)\s+(.*)", l)
            mark = "•" if m.group(1) == "-" else m.group(1)
            plads(0.0142)
            st["fig"].text(X0 + 0.005, st["y"], mark, fontsize=8.3, va="top")
            tekst(_ren(m.group(2)), 8.3, x=X0 + 0.025, luft=0.005)
        elif l.strip() == "":
            flush()
        else:
            afsnit.append(l.strip())
        i += 1
    flush()
    with PdfPages(pdf_sti) as pdf:
        for f in figs:
            pdf.savefig(f)
            plt.close(f)
    return len(figs)
