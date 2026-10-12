#!/usr/bin/env python3
"""Tekniske tegninger og overslagsberegning for tilbygningen.

Kør:  python3 tegninger/tilbygning_teknisk.py
Giver: tegninger/hus_facader.pdf/.png         (A2.2, 1:100: hus med tilbygning, fire facader)
       tegninger/tilbygning_snit.pdf/.png     (A2.3, 1:50: snit med gitterspær og hovedresultater)
       docs/tilbygning-statik-overslag.md
       tegninger/tilbygning_beregning.pdf  (samme rapport som PDF, bilag A2.4 i ansøgningen)

Spærtypen følger det eksisterende hus (W-gitterspær i træ, se billeder/IMG_2987-2989).
Beregningen er et OVERSLAG og ikke en statisk dokumentation.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Rectangle

from rapport_pdf import md_til_pdf
from statik import Ramme, kombiner
from tegningshoved import tegningshoved

HER = Path(__file__).parent
cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))
SOK_HUS, SOK_STALD = cfg.get("sokler", {}).get("hus", 0.0), cfg.get("sokler", {}).get("stald", 0.0)
for _k in ("hus_sydfacade", "hus_nordfacade"):      # åbningernes højder står over gulv; gulvet ligger i soklens overkant
    for _ab in cfg.get(_k, {}).get("aabninger", []):
        _ab["z0"], _ab["z1"] = _ab["z0"] + SOK_HUS, _ab["z1"] + SOK_HUS
cfg["vindue_standard"]["brystning"] += SOK_HUS

HL, HB = cfg["hus_ydermaal"]["laengde"], cfg["hus_ydermaal"]["bredde"]
TB = cfg["tilbygning"]["bredde"]
TL = HB + cfg["tilbygning"]["forbi_husets_sydfacade"]
TAGFOD, HAELD = cfg.get("sokler", {}).get("hus_tagfod_over_terraen", 2.5), 25.0     # over terræn, anslået fra fotos; følger det eksisterende hus
ALFA = math.radians(HAELD)
KIP = TAGFOD + HB / 2 * math.tan(ALFA)
VS = cfg["vindue_standard"]
YV = 0.45

# ---------------- Overslag for gitterspær ----------------
SPAN = 8.0                                       # mellem vægmidter i den sydlige del (største spænd)
CC = 1.0                                         # spærafstand, som i det eksisterende hus (anslået fra foto)
G_TOP, G_BUND, Q_LOFT = 0.35, 0.35, 0.5          # kN/m²: tag (bølgeplader, lægter, spær), loft (isolering, beklædning), opbevaring på loft
SK, MU1, MU_W, QP = 1.0, 0.8, 1.2, 0.67          # sne som for hallen; vind q_p i 4,4 m højde, terrænkategori II
C24 = {"fm": 24.0, "fc": 21.0, "ft": 14.5, "E05": 7400.0, "E": 11000.0}
KMOD, GM = 0.9, 1.35
HR = SPAN / 2 * math.tan(ALFA)
KN = {"A": (0, 0), "B": (SPAN, 0), "C": (SPAN / 2, HR), "T1": (SPAN / 4, HR / 2), "T2": (3 * SPAN / 4, HR / 2), "U1": (SPAN / 3, 0), "U2": (2 * SPAN / 3, 0)}
STG = {"o1": ("A", "T1", "top"), "o2": ("T1", "C", "top"), "o3": ("C", "T2", "top"), "o4": ("T2", "B", "top"),
       "u1": ("A", "U1", "bund"), "u2": ("U1", "U2", "bund"), "u3": ("U2", "B", "bund"),
       "d1": ("U1", "T1", "gitter"), "d2": ("U1", "C", "gitter"), "d3": ("U2", "C", "gitter"), "d4": ("U2", "T2", "gitter")}
NORMAL = {"o1": (-math.sin(ALFA), math.cos(ALFA)), "o2": (-math.sin(ALFA), math.cos(ALFA)), "o3": (math.sin(ALFA), math.cos(ALFA)), "o4": (math.sin(ALFA), math.cos(ALFA))}
KOMB = {"K1  1,0 G + 1,5 S(jævn) + 0,75 Q(loft)": {"G": 1.0, "S1": 1.5, "Q": 0.75},
        "K2  1,0 G + 1,5 S(ophobning vest) + 0,75 Q(loft)": {"G": 1.0, "S2": 1.5, "Q": 0.75},
        "K3  0,9 G + 1,5 W(sug)": {"G": 0.9, "W": 1.5}}
KAND = [((45, 120), (45, 95), (45, 70)), ((45, 145), (45, 120), (45, 95)), ((45, 170), (45, 120), (45, 95)), ((45, 195), (45, 145), (45, 95)), ((45, 220), (45, 145), (45, 120))]


def dk(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")


def beregn(dim):
    tv = dict(zip(("top", "bund", "gitter"), dim))
    r = Ramme()
    for navn, (a, b, gr) in STG.items():
        bb, hh = tv[gr]
        A, I = bb * hh * 1e-6, bb * hh ** 3 / 12 * 1e-12
        r.stang(navn, KN[a], KN[b], C24["E"] * 1e3 * A, C24["E"] * 1e3 * I * (1e-4 if gr == "gitter" else 1), n=8)
    r.understoet(KN["A"])
    r.understoet(KN["B"], ux=False)
    top, bund = ["o1", "o2", "o3", "o4"], ["u1", "u2", "u3"]
    lt = {"G": r.last(top, "g", G_TOP * CC) + r.last(bund, "g", G_BUND * CC), "Q": r.last(bund, "g", Q_LOFT * CC),
          "S1": r.last(top, "plan", MU1 * SK * CC), "S2": r.last(["o1", "o2"], "plan", MU_W * SK * CC),
          "W": r.last(top, "normal", -1.0 * QP * CC, NORMAL)}
    res = {k: r.loes(F) for k, F in lt.items()}
    fmd, fcd, ftd = (KMOD * C24[k] / GM for k in ("fm", "fc", "ft"))
    ud = {"dim": dim, "u": {"top": 0, "bund": 0, "gitter": 0}, "N": {}, "komb": {}}
    for kn, f in KOMB.items():
        k = kombiner([res[x] for x in f], list(f.values()))
        ud["komb"][kn] = {"reak": (k["reak"][r.knude(*KN["A"])], k["reak"][r.knude(*KN["B"])]), "N": {}}
        for navn, (a, b, gr) in STG.items():
            bb, hh = tv[gr]
            A, W = bb * hh, bb * hh ** 2 / 6
            N, M = k["snit"][navn]["N"], k["snit"][navn]["M"]
            Nmax = float(N[np.abs(N).argmax()])
            Mmax = float(np.abs(M).max()) if gr != "gitter" else 0.0
            ud["komb"][kn]["N"][navn] = Nmax
            sig_m = Mmax * 1e6 / W
            laengde = math.dist(KN[a], KN[b]) * 1000
            if Nmax < 0:                               # tryk med søjlevirkning
                i = (hh if gr != "gitter" else bb) / math.sqrt(12)      # gitterstænger knækker om den svage akse
                lam_rel = laengde / i / math.pi * math.sqrt(C24["fc"] / C24["E05"])
                kk = 0.5 * (1 + 0.2 * (lam_rel - 0.3) + lam_rel ** 2)
                kc = min(1.0, 1 / (kk + math.sqrt(max(kk * kk - lam_rel ** 2, 1e-9))))
                u = abs(Nmax) * 1e3 / A / (kc * fcd) + sig_m / fmd
            else:
                u = Nmax * 1e3 / A / ftd + sig_m / fmd
            ud["u"][gr] = max(ud["u"][gr], u)
    ud["f"] = -float(res["S1"]["u"][3 * r.knude(SPAN / 2, 0) + 1]) * 1000 if (SPAN / 2, 0) in r.knuder else max(-float(v) for v in res["S1"]["u"][1::3]) * 1000
    ud["ok"] = max(ud["u"].values()) <= 1.0
    return ud


alle = [beregn(d) for d in KAND]
valgt = next((a for a in alle if a["ok"]), alle[-1])
DT, DB, DG = valgt["dim"]
ned = max(max(rk[1] for rk in k["reak"]) for k in valgt["komb"].values())
loeft = max(max(0.0, -rk[1]) for k in valgt["komb"].values() for rk in k["reak"])
G_VAEG = 8.0                                     # kN/m, antaget egenvægt af 2,5 m ydervæg inkl. sokkel
linjelast = ned / CC + 1.0 * G_VAEG
FUND_B = 0.6
k1 = list(valgt["komb"].values())[0]

rap = f"""# Foreløbig overslagsberegning for tilbygningens tagkonstruktion

Nældevej 42, 9000 Aalborg. 11. oktober 2026. Hører til tegningerne A2.2 og A2.3.

**Beregningen er foreløbig.** Den er udført af bygherren som grundlag for landzoneansøgningen og viser, at tilbygningen kan udføres med gitterspær som i det eksisterende hus. Gitterspærene dimensioneres og leveres af en spærfabrik, som udarbejder den endelige beregning og monteringsvejledning til byggeansøgningen.

Beregningen følger DS/EN 1990, DS/EN 1991-1-3 og DS/EN 1991-1-4 med de danske nationale annekser (DK NA 2024 for sne og vind) og DS/EN 1995-1-1. Spæret er regnet som plan gitterkonstruktion (elementmetode), og lastkombinationerne er dannet efter DS/EN 1990 DK NA, ligning 6.10b.

## 1. Det eksisterende hus

Billederne fra loftet (billeder/IMG_2987-2989) viser W-gitterspær i træ: gennemgående spærhoved og spærfod, to trækdiagonaler fra spærfoden op til kippen og to trykstivere ud til midten af spærhovederne. Spærene står med ca. 1 m afstand og bærer lægter og sorte bølgeplader. Loftet er isoleret på spærfoden og bruges til opbevaring. Tilbygningen er forudsat udført på samme måde, så tag og loft kan føres igennem i samme stil.

## 2. Forudsætninger

| | |
|---|---|
| Spærtype | W-gitterspær, konstruktionstræ C24, samlet med tandplader |
| Spændvidde | {dk(SPAN)} m mellem vægmidter (den sydlige del, hvor tilbygningen har egne vægge i begge sider) |
| Taghældning og spærafstand | {dk(HAELD, 0)}° og {dk(CC)} m, som anslået for det eksisterende hus |
| Egenlast | Tag {dk(G_TOP, 2)} kN/m² (bølgeplader, lægter, spær), loft {dk(G_BUND, 2)} kN/m² (isolering og loftbeklædning) |
| Nyttelast på loft | {dk(Q_LOFT)} kN/m² til let opbevaring (antaget; ψ0 = 0,5 som for kategori A i DS/EN 1990 DK NA) |
| Sne | s_k = {dk(SK)} kN/m² (DK NA); jævn μ_1 = {dk(MU1)} (tabel 5.2); ophobning på vestlig tagflade μ_w = {dk(MU_W)} efter DK NA 5.3.3(4), fordi tilbygningens kip ligger nord-syd og den østlige tagflade vender mod øst. Medtaget på den sikre side |
| Vind | q_p = {dk(QP, 2)} kN/m² i {dk(KIP)} m højde (v_b,0 = 24 m/s, terrænkategori II); sug på hele taget med c_pe = −0,8 (DS/EN 1991-1-4 tabel 7.4a, zone F/G ved 25°, på den sikre side) og c_pi = +0,2, i alt −1,0 |
| Træ | C24 (DS/EN 338): f_m = 24, f_c,0 = 21, f_t,0 = 14,5 MPa, E_0,05 = 7.400 MPa; k_mod = {dk(KMOD)} (korttidslast, anvendelsesklasse 2); γ_M = {dk(GM, 2)} (DS/EN 1995-1-1 DK NA). Søjlereduktion k_c efter DS/EN 1995-1-1, 6.3.2 |

## 3. Dimensioner

Udnyttelse for tryk eller træk kombineret med bøjning. Trykstænger er regnet med søjlevirkning; spærhovedet fastholdes sideværts af lægterne.

| Spærhoved | Spærfod | Gitterstænger | Udnyttelse hoved | fod | gitter | Opfylder |
|---|---|---|---|---|---|---|
""" + "\n".join(f"| {a['dim'][0][0]} × {a['dim'][0][1]} | {a['dim'][1][0]} × {a['dim'][1][1]} | {a['dim'][2][0]} × {a['dim'][2][1]} | {dk(a['u']['top'], 2)} | {dk(a['u']['bund'], 2)} | {dk(a['u']['gitter'], 2)} | {'ja' if a['ok'] else 'nej'} |" for a in alle) + f"""

**Mindste sæt, der opfylder overslaget: spærhoved {DT[0]} × {DT[1]} mm, spærfod {DB[0]} × {DB[1]} mm, gitterstænger {DG[0]} × {DG[1]} mm.** Samlingerne (tandplader) er ikke regnet og er ofte det, der bestemmer dimensionerne i praksis.

## 4. Stangkræfter og reaktioner pr. spær

| Lastkombination | Spærhoved ved fod | Spærfod | Trykstiver | Trækdiagonal | Lodret reaktion vest / øst |
|---|---|---|---|---|---|
""" + "\n".join(f"| {n} | {dk(k['N']['o1'])} kN | {dk(k['N']['u1'])} kN | {dk(k['N']['d1'])} kN | {dk(k['N']['d2'])} kN | {dk(k['reak'][0][1])} / {dk(k['reak'][1][1])} kN |" for n, k in valgt["komb"].items()) + f"""

Træk er positivt. Negativ lodret reaktion er løft.

## 5. Vægge, fundamenter og forankring

| | |
|---|---|
| Største lodrette last fra spær | {dk(ned)} kN pr. spær, dvs. {dk(ned / CC)} kN/m væg |
| Antaget egenvægt af ydervæg og sokkel | {dk(G_VAEG)} kN/m |
| Linjelast på fundament | ca. {dk(linjelast)} kN/m |
| Stribefundament {dk(FUND_B)} m bredt | ca. {dk(linjelast / FUND_B, 0)} kN/m² på jorden. Jordens bæreevne er ikke undersøgt |
| Største løft fra vind | {dk(loeft)} kN pr. spær. Kræver spærbeslag og forankring af remmen ned i væggen |

## 6. Forhold, der skal løses i projekteringen

1. **Bæring på husets gavl.** Langs det eksisterende hus skal spærene hvile på husets vestgavl, som i dag kun bærer sig selv. Gavlens og dens fundaments bæreevne skal vurderes, og der skal laves en rem i tagfodshøjde.
2. **Sammenskæringen med husets tag.** Tilbygningens tag skærer ind i husets tag i to skotrender. De yderste spær i huset skal bære skotrenderne og den sne, der kan samle sig der (DK NA anneks G om tagsammenskæringer).
3. **Springet på 45 cm i østvæggen.** Syd for huset står østvæggen 45 cm længere ude end husets gavl. Spærene i den sydlige del bliver derfor længere, eller tagfoden mod øst kommer lidt lavere. Facadetegningerne viser taget symmetrisk og uden dette spring.
4. **Garageportene i nordgavlen** (to åbninger på 2,7 m) kræver overliggere, og gavlen mister en stor del af sin afstivende skive.
5. **Stabilitet:** tagskive, vindkryds i tagfladen og afstivende vægge er ikke regnet.
6. **Jordvarmeslangen** under den vestlige ydervæg og fundamentets dybde.
7. **Brandadskillelse** mellem garage og bolig, også på loftet.
"""
(HER.parent / "docs" / "tilbygning-statik-overslag.md").write_text(rap, encoding="utf-8")
md_til_pdf(rap, HER / "tilbygning_beregning.pdf", "Bilag A2.4: Foreløbig overslagsberegning, tilbygning, Nældevej 42, 9000 Aalborg")

# ================= TEGNINGER =================
HVID, NY, TAG, GLAS, DOER = "#f6f6f3", "#fff3d6", "#232528", "#5f7f99", "#5b4636"


def maal(ax, p, q, tekst, off=(0, 0), rot=0, fs=6.5):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0), zorder=6)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=fs, ha="center", va="center", rotation=rot)


def ark(maalestok):
    fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 420 * maalestok / 1000)
    ax.set_ylim(0, 297 * maalestok / 1000)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# ---------- A2.2 Facader 1:100 ----------
fig, ax = ark(100)
hu0, hu1, hv0, hv1 = -HL / 2, HL / 2, -HB / 2, HB / 2
tu0, tu1, tv0 = hu0 - TB, hu0, hv0 - cfg["tilbygning"]["forbi_husets_sydfacade"]
tum = (tu0 + tu1) / 2


def langvaeg(X, a, b, oy, farve, kant="black"):
    x0, x1 = sorted((X(a), X(b)))
    ax.add_patch(Rectangle((x0, oy), x1 - x0, TAGFOD, fc=farve, ec=kant, lw=0.8, zorder=2))
    ax.add_patch(Rectangle((x0, oy), x1 - x0, SOK_HUS, fc="#b9b9b4", ec="black", lw=0.5, zorder=3.5))
    ax.add_patch(Rectangle((x0 - 0.3, oy + TAGFOD), x1 - x0 + 0.6, KIP - TAGFOD, fc=TAG, ec="black", lw=0.8, zorder=2))


def gavlflade(X, a, b, oy, farve, kant="black"):
    x0, x1 = sorted((X(a), X(b)))
    ax.add_patch(Polygon([(x0, oy), (x1, oy), (x1, oy + TAGFOD), ((x0 + x1) / 2, oy + KIP), (x0, oy + TAGFOD)], closed=True, fc=farve, ec=kant, lw=0.8, zorder=3))
    ax.add_patch(Rectangle((x0, oy), x1 - x0, SOK_HUS, fc="#b9b9b4", ec="black", lw=0.5, zorder=3.5))
    ax.plot([x0 - 0.3, (x0 + x1) / 2, x1 + 0.3], [oy + TAGFOD - 0.14, oy + KIP + 0.03, oy + TAGFOD - 0.14], color=TAG, lw=2.2, zorder=4)


def aabning(X, a, b, oy, z0, z1, doer=False, fag=1, farve=None):
    x0, x1 = sorted((X(a), X(b)))
    ax.add_patch(Rectangle((x0, oy + z0), x1 - x0, z1 - z0, fc=farve or (DOER if doer else GLAS), ec="#111111", lw=0.7, zorder=5))
    for i in range(1, fag):
        ax.plot([x0 + (x1 - x0) * i / fag] * 2, [oy + z0, oy + z1], color="#111111", lw=0.6, zorder=6)


def hoejder(x, oy):
    maal(ax, (x, oy), (x, oy + TAGFOD), dk(TAGFOD), (-0.4, 0), 90)
    maal(ax, (x - 0.9, oy), (x - 0.9, oy + KIP), dk(KIP, 2), (-0.4, 0), 90)


def facade(titel, ox, oy, bredde):
    ax.plot([ox - 1.9, ox + bredde + 0.5], [oy, oy], color="black", lw=0.8, zorder=1)
    ax.text(ox, oy + KIP + 0.9, titel, fontsize=9, weight="bold")


# Nord: set fra nord, øst til venstre
ox, oy = 2.3, 17.5
X = lambda u: ox + (hu1 - u)
facade("Facade mod nord", ox, oy, HL + TB)
langvaeg(X, hu0, hu1, oy, HVID)
gavlflade(X, tu0, tu1, oy, NY, "#b36b00")
for ab in cfg["hus_nordfacade"]["aabninger"]:
    aabning(X, ab["u0"], ab["u1"], oy, ab["z0"], ab["z1"], ab.get("doer", False))
for x in (1.05, 4.25):                           # garageporte i sokkelhøjde; gruset føres op til dem
    aabning(X, tu0 + x, tu0 + x + 2.7, oy, SOK_HUS, SOK_HUS + 2.2, farve="#d9d4c8")
OPK = cfg["tilbygning"].get("garage_opkoersel", {"laengde": 6.0, "side_udfald": 2.0})
ax.add_patch(Polygon([(X(tu1) - 0.01, oy), (X(tu1) - 0.01, oy + SOK_HUS), (X(tu0), oy + SOK_HUS), (X(tu0) + OPK["side_udfald"], oy)], closed=True, fc="#d6d1c6", ec="black", lw=0.5, hatch="..", zorder=4))
ax.text(X(tu0) + OPK["side_udfald"] + 0.2, oy + 0.2, "grus føres op\ntil portene", fontsize=5.5, va="center")
maal(ax, (X(hu1), oy - 0.9), (X(hu0), oy - 0.9), f"eksisterende hus {dk(HL)} m", (0, -0.35))
maal(ax, (X(tu1), oy - 0.9), (X(tu0), oy - 0.9), f"tilbygning {dk(TB)} m", (0, -0.35))
hoejder(ox - 0.8, oy)
# Vest: set fra vest, nord til venstre
ox2 = 26.3
X = lambda v: ox2 + (hv1 - v)
facade("Facade mod vest (tilbygning)", ox2, oy, TL)
langvaeg(X, tv0, hv1, oy, NY, "#b36b00")
ax.text(X(hv1) + 0.2, oy - 0.45, f"nordgavl: grus føres op til garageportene over ca. {OPK['laengde']:.0f} m", fontsize=5.5, ha="left", va="center")
for y in (1.0, 6.1):
    aabning(X, tv0 + y, tv0 + y + VS["bredde"], oy, VS["brystning"], VS["brystning"] + VS["hoejde"])
maal(ax, (X(hv1), oy - 0.9), (X(tv0), oy - 0.9), f"{dk(TL)} m", (0, -0.35))
# Syd: set fra syd, vest til venstre
ox, oy = 2.3, 5.2
X = lambda u: ox + (u - tu0)
facade("Facade mod syd", ox, oy, HL + TB)
langvaeg(X, hu0, hu1, oy, HVID)
gavlflade(X, tu0, tu1, oy, NY, "#b36b00")
for ab in cfg["hus_sydfacade"]["aabninger"]:
    aabning(X, ab["u0"], ab["u1"], oy, ab["z0"], ab["z1"], fag=ab.get("fag", 1))
aabning(X, tu0 + 2.5, tu0 + 5.5, oy, SOK_HUS, SOK_HUS + 2.1, fag=3)
maal(ax, (X(tu0), oy - 0.9), (X(tu1), oy - 0.9), f"tilbygning {dk(TB)} m", (0, -0.35))
maal(ax, (X(hu0), oy - 0.9), (X(hu1), oy - 0.9), f"eksisterende hus {dk(HL)} m", (0, -0.35))
hoejder(ox - 0.8, oy)
# Øst: set fra øst, syd til venstre
X = lambda v: ox2 + (v - tv0)
facade("Facade mod øst", ox2, oy, TL)
langvaeg(X, tv0, hv0, oy, NY, "#b36b00")
aabning(X, tv0 + 1.6, tv0 + 1.6 + VS["bredde"], oy, VS["brystning"], VS["brystning"] + VS["hoejde"])
gavlflade(X, hv0, hv1, oy, HVID)
maal(ax, (X(tv0), oy - 0.9), (X(hv0), oy - 0.9), f"tilbygning {dk(hv0 - tv0)} m", (0, -0.35))
maal(ax, (X(hv0), oy - 0.9), (X(hv1), oy - 0.9), f"hus {dk(HB)} m", (0, -0.35))
ax.text(1.5, 28.2, "Hus med tilbygning, facader", fontsize=13, weight="bold")
ax.text(1.5, 27.4, "Tilbygningen (gul) udføres i samme stil som huset: hvide vægge, sort bølgepladetag, sorte vinduer i husets standardmål. På tegningen er den fremhævet med gul væg. Grå sokkel ca. 0,4 m som på huset. Højder i meter over terræn.", fontsize=7.5)
ax.text(1.5, 1.8, "Husets højder (tagfod 2,8 m over terræn, sokkel 0,4 m, 25°) og åbninger er anslået fra fotos og ejendomsmæglerens plan og måles op før byggeansøgningen.", fontsize=7, color="#444444")
ax.text(1.5, 1.2, "Stald og skur er ikke vist. Springet på 45 cm i tilbygningens østvæg er ikke vist.", fontsize=7, color="#444444")
tegningshoved(fig, "Hus med tilbygning, facader", "1 : 100 (A3)", "A2.2")
fig.savefig(HER / "hus_facader.pdf")
fig.savefig(HER / "hus_facader.png", dpi=130)
plt.close(fig)

# ---------- A2.3 Snit 1:50 ----------
fig, ax = ark(50)
OX, OY = 2.6, 4.6
BT = SPAN + YV                                   # udvendig bredde i snittet
P = lambda x, z: (OX + x, OY + z)
ax.plot([OX - 1.2, OX + BT + 1.2], [OY, OY], color="black", lw=0.9)
for x in (0, BT - YV):                           # ydervægge og stribefundamenter
    ax.add_patch(Rectangle(P(x, 0), YV, TAGFOD, fc="#e9e4da", ec="black", lw=0.7, hatch="//", zorder=3))
    ax.add_patch(Rectangle(P(x, 0), YV, SOK_HUS, fc="#b9b9b4", ec="black", lw=0.7, zorder=3.2))
    ax.add_patch(Rectangle(P(x + YV / 2 - FUND_B / 2, -0.9), FUND_B, 0.9, fc="#d9d9d9", ec="black", lw=0.6, hatch="...", zorder=2))
ax.add_patch(Rectangle(P(YV, SOK_HUS - 0.12), BT - 2 * YV, 0.12, fc="#cfcfcf", ec="black", lw=0.5))
ax.add_patch(Rectangle(P(YV, SOK_HUS - 0.56), BT - 2 * YV, 0.44, fc="#f6e7a8", ec="#888888", lw=0.3, hatch="xx"))      # 2 x 220 mm isolering (ejers valg)
ax.add_patch(Rectangle(P(YV, SOK_HUS - 0.76), BT - 2 * YV, 0.20, fc="#efe7d3", ec="#888888", lw=0.3, hatch="oo"))
sx0 = YV / 2                                     # spærets understøtning i vægmidte
S_ = lambda k: P(sx0 + KN[k][0], TAGFOD + KN[k][1])
ax.add_patch(Rectangle(P(YV, TAGFOD), BT - 2 * YV, 0.40, fc="#f6e7a8", ec="#888888", lw=0.3, hatch="xx", zorder=1))     # loftisolering
for navn, (a, b, gr) in STG.items():
    bb, hh = dict(zip(("top", "bund", "gitter"), valgt["dim"]))[gr]
    (x0, z0), (x1, z1) = S_(a), S_(b)
    Ls = math.hypot(x1 - x0, z1 - z0)
    nx, nz = -(z1 - z0) / Ls * hh / 2000, (x1 - x0) / Ls * hh / 2000
    ax.add_patch(Polygon([(x0 + nx, z0 + nz), (x1 + nx, z1 + nz), (x1 - nx, z1 - nz), (x0 - nx, z0 - nz)], closed=True, fc="#c9a66b", ec="#5a4520", lw=0.5, zorder=5))
    N = k1["N"][navn]
    ax.text((x0 + x1) / 2 + nx * 4, (z0 + z1) / 2 + nz * 4 + (0.0 if gr != "bund" else -0.02), f"{dk(N)}", fontsize=6, color="#b03030" if N < 0 else "#1f5fa8", ha="center", va="center", zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.4))
t = math.tan(ALFA)
for sgn in (1, -1):                              # tagdækning
    xa, xb = (sx0 - 0.45, sx0 + SPAN / 2) if sgn == 1 else (sx0 + SPAN + 0.45, sx0 + SPAN / 2)
    za = TAGFOD - 0.45 * t + DT[1] / 2000 / math.cos(ALFA) + 0.05
    zb = TAGFOD + HR + DT[1] / 2000 / math.cos(ALFA) + 0.05
    ax.plot([OX + xa, OX + xb], [OY + za, OY + zb], color=TAG, lw=3.0, zorder=6, solid_capstyle="butt")
ax.text(*P(BT / 2, 1.25), "Soveværelse", fontsize=9, ha="center", va="center", color="#555555")
maal(ax, P(0, -1.5), P(BT, -1.5), f"{dk(BT, 2)} m udvendigt", (0, -0.2), fs=7)
maal(ax, P(sx0, TAGFOD + HR + 0.9), P(sx0 + SPAN, TAGFOD + HR + 0.9), f"spærspænd {dk(SPAN)} m", (0, 0.2), fs=7)
maal(ax, P(-0.8, 0), P(-0.8, TAGFOD), f"{dk(TAGFOD)} m", (-0.25, 0), 90, fs=7)
maal(ax, P(BT + 0.8, 0), P(BT + 0.8, TAGFOD + HR), f"{dk(TAGFOD + HR, 2)} m", (0.25, 0), 90, fs=7)


def note(tekst, xz, txz):
    ax.annotate(tekst, xy=P(*xz), xytext=P(*txz), fontsize=6.5, ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.4), zorder=8,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#888888", lw=0.4))


note(f"W-gitterspær C24 pr. {dk(CC)} m:\nhoved {DT[0]}×{DT[1]}, fod {DB[0]}×{DB[1]},\ngitter {DG[0]}×{DG[1]} mm", (sx0 + 1.2, TAGFOD + 0.62), (-2.2, TAGFOD + 2.3))
note("Sorte bølgeplader på lægter,\nsom eksisterende", (sx0 + SPAN - 1.4, TAGFOD + 0.75), (BT - 1.2, TAGFOD + 2.3))
note("Loftisolering på spærfoden", (BT - 2.2, TAGFOD + 0.2), (BT + 0.4, TAGFOD + 0.9))
note("Ydervæg 45 cm,\nsom eksisterende facade", (0.25, 0.7), (-2.4, 0.45))
note("Terrændæk: beton 120 mm,\nisolering 2 × 220 mm,\nkapillarbrydende lag. Gulv i soklens\noverkant, ca. 0,4 m over terræn", (2.5, SOK_HUS - 0.35), (1.2, -1.15))
note(f"Stribefundament {dk(FUND_B)} × 0,9 m", (BT - 0.2, -0.6), (BT + 0.3, -0.9))
ax.text(OX, OY + TAGFOD + HR + 1.8, "Snit B-B gennem soveværelset (set mod nord)", fontsize=10, weight="bold")
ax.text(OX, OY + TAGFOD + HR + 1.35, "Tal på stængerne: normalkraft i kN for sne på hele taget (K1). Rød = tryk, blå = træk.", fontsize=7)
bx, by = 14.4, 12.6
linjer = [("OVERSLAGSBEREGNING, hovedresultater", True),
          (f"Spær: W-gitterspær C24, spænd {dk(SPAN)} m, afstand {dk(CC)} m", False),
          (f"Sne: s_k = {dk(SK)} kN/m², μ = {dk(MU1)} og {dk(MU_W)} (ophobning vest)", False),
          (f"Egenlast tag {dk(G_TOP, 2)} og loft {dk(G_BUND, 2)} kN/m², opbevaring {dk(Q_LOFT)} kN/m²", False), ("", False),
          (f"Udnyttelse spærhoved: {dk(valgt['u']['top'], 2)}", False), (f"Udnyttelse spærfod: {dk(valgt['u']['bund'], 2)}", False),
          (f"Udnyttelse gitterstænger: {dk(valgt['u']['gitter'], 2)}", False), ("", False),
          (f"Lodret last pr. spær: {dk(ned)} kN ({dk(ned / CC)} kN/m væg)", False), (f"Løft fra vind pr. spær: {dk(loeft)} kN", False),
          (f"Linjelast på fundament: ca. {dk(linjelast)} kN/m", False), ("", False),
          ("Ikke eftervist: tandpladesamlinger, bæring på husets", False), ("gavl, skotrender, stabilitet, jordens bæreevne.", False),
          ("Se bilag A2.4.", False)]
ax.add_patch(Rectangle((bx - 0.2, by - 0.33 * len(linjer) - 0.1), 6.5, 0.33 * len(linjer) + 0.45, fc="#fbfbf7", ec="#888888", lw=0.6))
for i, (tx, fed) in enumerate(linjer):
    ax.text(bx, by - 0.33 * i, tx, fontsize=6.8, weight="bold" if fed else "normal", va="center")
ax.text(1.0, 0.75, "Overslagsberegning. Spær dimensioneres og leveres af spærfabrik. Vægopbygning, gulv og fundament er principielle og fastlægges i byggeansøgningen.", fontsize=7, color="#444444")
tegningshoved(fig, "Tilbygning, snit B-B og overslag", "1 : 50 (A3)", "A2.3")
fig.savefig(HER / "tilbygning_snit.pdf")
fig.savefig(HER / "tilbygning_snit.png", dpi=130)
plt.close(fig)
print(f"Spær: hoved {DT}, fod {DB}, gitter {DG}; udnyttelse {valgt['u']}; ned {ned:.1f} kN, løft {loeft:.1f} kN; ok={valgt['ok']}")
