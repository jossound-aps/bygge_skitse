#!/usr/bin/env python3
"""Tegner staldens eksisterende indretning og brug (bilag A3.1), så det fremgår, at alle rum er i brug.

Kør:  python3 tegninger/stald_plan.py
Giver: tegninger/stald_plan.pdf / .png   (A3 liggende, 1:100)

Rummene er målt op efter mæglerens vejledende plan fra salgsopstillingen (9.9.2024), som ikke er målfast.
Koordinater i meter: x fra staldens nordvestlige hjørne mod øst, y mod syd. Brugen står i listen RUM;
tekst i [kantede parenteser] skal oplyses af ejer.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from nordpil import nordpil
from tegningshoved import tegningshoved

BYGNINGSDREJNING = 1.6   # planen følger bygningerne, som ligger ca. 1,6 grader drejet fra stik nord
HER = Path(__file__).parent

L, D = 23.3, 7.46                 # hovedlængens udvendige længde og dybde
FX0, FY1 = 16.55, 15.5            # sydfløjens vestside og sydgavl
GANG_Y = 3.8                      # skillelinje mellem nordlige rum og staldgang
HEST, SADEL, BOLIG, VAAD, SKUR = "#dcebd2", "#f0dfbf", "#d9e2ee", "#e6e6e6", "#eadfd6"


def kasse(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# (nr, navn, polygon, farve, brug)
RUM = [
    ("1", "Hesteboks", kasse(10.57, 0, 13.78, GANG_Y), HEST, "Opstaldning af ejendommens heste"),
    ("2", "Hesteboks", kasse(13.78, 0, 17.0, GANG_Y), HEST, "Opstaldning af ejendommens heste"),
    ("3", "Hesteboks", kasse(17.0, 0, 20.1, GANG_Y), HEST, "Opstaldning af ejendommens heste"),
    ("4", "Hesteboks", kasse(20.1, 0, L, GANG_Y), HEST, "Opstaldning af ejendommens heste"),
    ("5", "Ponyboks", kasse(8.92, 4.84, 12.1, D), HEST, "Opstaldning af ejendommens ponyer"),
    ("6", "Ponyboks", kasse(20.1, 5.1, L, D), HEST, "Opstaldning af ejendommens ponyer"),
    ("7", "Staldgang", [(8.92, GANG_Y), (L, GANG_Y), (L, 5.1), (20.1, 5.1), (20.1, D), (12.1, D), (12.1, 4.84), (8.92, 4.84)], "#eef5e8",
     "Adgang til boksene, strigleplads, foder og udmugning [bekræftes]"),
    ("8", "Løsdrift", kasse(FX0, D, L, FY1), HEST, "Løsdrift med dybstrøelse, hestene går frit ud og ind til foldene"),
    ("9", "Gæsteværelse", [(4.17, 0), (8.92, 0), (8.92, 4.84), (6.76, 4.84), (6.76, GANG_Y), (4.17, GANG_Y)], BOLIG,
     "Gæsteværelse til husstandens private gæster. Ét rum; kun en støttevæg på 1 m ved ydervæggen"),
    ("10", "Sadelrum", kasse(8.92, 0, 10.57, GANG_Y), SADEL, "Sadler, trenser, seletøj og rideudstyr. Tidligere værksted"),
    ("11", "Bad", kasse(6.76, 4.84, 8.92, D), VAAD, "Bad og toilet til stalden"),
    ("12", "Gæsteværelse", [(0, 0), (4.17, 0), (4.17, GANG_Y), (6.76, GANG_Y), (6.76, D), (0, D)], BOLIG,
     "Ejendommens gamle stuehus. Bruges som gæsteværelse til husstandens private gæster"),
    ("13", "Skur", kasse(L, 0, L + 2.8, 8.3), SKUR, "Åbnede wrapballer opbevares her i tørvejr. Ejendommens eneste udhus (byggesag 2020-1967)"),
]


def areal(p):
    return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2


def midte(p):
    return sum(q[0] for q in p) / len(p), sum(q[1] for q in p) / len(p)


def dk(tal, dec=0):
    return f"{tal:.{dec}f}".replace(".", ",")


fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
X0, X1, Y0, Y1 = -1.5, 27.5, -2.5, 17.0                       # udsnit i meter; 1 m = 10 mm på A3 giver 1:100
ax = fig.add_axes([0.03, 0.26, (X1 - X0) * 10 / 420, (Y1 - Y0) * 10 / 297])
ax.set_xlim(X0, X1)
ax.set_ylim(Y1, Y0)
ax.set_aspect("equal")
ax.axis("off")

MIDT = {"7": (16.0, 4.45), "9": (6.6, 2.1), "12": (2.6, 4.6)}   # tekstplacering i rum, der ikke er rektangler
for nr, navn, p, farve, _ in RUM:
    ax.add_patch(Polygon(p, closed=True, fc=farve, ec="black", lw=1.1 if nr != "13" else 0.8, zorder=2))
    mx, my = MIDT.get(nr, midte(p))
    lille = nr in ("10", "11", "13")
    ax.text(mx, my, f"{nr}\n{navn}\nca. {dk(areal(p))} m²", fontsize=6.2 if lille else 7.5, ha="center", va="center", zorder=4,
            rotation=90 if nr in ("10", "13") else 0)
# ydervægge
omrids = [(0, 0), (L, 0), (L, FY1), (FX0, FY1), (FX0, D), (0, D)]
ax.add_patch(Polygon(omrids, closed=True, fc="none", ec="black", lw=2.6, zorder=5))
# støttevæg i gæsteværelset (nr. 9): 1 m ind fra ydervæggen mod nord
ax.plot([7.4, 7.4], [0, 1.0], color="black", lw=1.6, zorder=3)
# lette skillevægge i staldgangen
for x in (15.6, 17.4):
    ax.plot([x, x], [5.3, D], color="#555555", lw=0.8, zorder=3)
# hovedmål
ax.annotate("", (0, -1.0), (L, -1.0), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(L / 2, -1.25, f"ca. {dk(L, 1)} m", fontsize=7, ha="center")
ax.annotate("", (-0.8, 0), (-0.8, D), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(-1.05, D / 2, f"ca. {dk(D, 1)} m", fontsize=7, ha="center", va="center", rotation=90)
ax.annotate("", (FX0 - 0.8, D), (FX0 - 0.8, FY1), arrowprops=dict(arrowstyle="<->", lw=0.6))
ax.text(FX0 - 1.05, (D + FY1) / 2, f"ca. {dk(FY1 - D, 1)} m", fontsize=7, ha="center", va="center", rotation=90)
ax.text(L / 2, -2.1, "Nældevej (nord)", fontsize=7, ha="center", color="#666666")
ax.text(8.0, 11.5, "Gårdsplads\n(stuehuset ligger mod syd)", fontsize=7, ha="center", va="center", color="#666666")
ax.text(L + 3.1, 11.5, "Folde og\nridebane\nmod øst", fontsize=7, va="center", color="#666666")

fig.text(0.03, 0.955, "Stald, BBR-bygning 2: eksisterende indretning og brug", fontsize=15, weight="bold")
fig.text(0.03, 0.93, "Alle rum er i brug: stald, sadelrum og bad til hesteholdet og vestenden med det gamle stuehus til gæsteværelser. Der er ingen ledige rum til maskiner, trailere eller opbevaring.", fontsize=9)

# rumliste
tx, ty, dy = 0.725, 0.90, 0.036
fig.text(tx, ty, "Nr.   Rum, areal og brug", fontsize=8.5, weight="bold")
import textwrap
y = ty - 0.03
for nr, navn, p, farve, brug in RUM:
    linjer = textwrap.wrap(brug, 46)
    fig.patches.append(plt.Rectangle((tx, y - 0.006), 0.012, 0.017, fc=farve, ec="black", lw=0.5, transform=fig.transFigure))
    fig.text(tx + 0.018, y, f"{nr}", fontsize=7.5, weight="bold")
    fig.text(tx + 0.038, y, f"{navn}, ca. {dk(areal(p))} m²", fontsize=7.5, weight="bold")
    fig.text(tx + 0.038, y - 0.016, "\n".join(linjer), fontsize=6.8, va="top", linespacing=1.3)
    y -= dy + 0.013 * (len(linjer) - 1)

grupper = {"Hestehold (bokse, staldgang, løsdrift)": [r for r in RUM if r[0] in "1 2 3 4 5 6 7 8".split()],
           "Sadelrum og bad": [r for r in RUM if r[0] in ("10", "11")],
           "Gæsteværelser": [r for r in RUM if r[0] in ("9", "12")]}
yy = 0.215
fig.text(0.03, yy, "Sammentælling (rumarealer, ca.)", fontsize=8.5, weight="bold")
for i, (g, rr) in enumerate(grupper.items()):
    fig.text(0.03, yy - 0.024 * (i + 1), f"{g}:", fontsize=8)
    fig.text(0.25, yy - 0.024 * (i + 1), f"{dk(sum(areal(r[2]) for r in rr))} m²", fontsize=8, ha="right")
fig.text(0.03, yy - 0.024 * 4.3, "Stalden er registreret med 284 m² i BBR. Forskellen skyldes vægge, og at planen ikke er målfast. Skuret (nr. 13) er ikke en del af stalden.", fontsize=7.5)
fig.text(0.03, 0.075, "Tegnet efter ejendomsmæglerens vejledende plan (ikke målfast). Rumarealer er regnet til vægmidte og er omtrentlige.\n"
                      "Døre, vinduer og porte er ikke vist. Skurets placering og mål er efter situationsplanen.", fontsize=7, color="#444444", linespacing=1.4)

nordpil(fig, 0.685, 0.89, vinkel=BYGNINGSDREJNING)
tegningshoved(fig, "Stald, eksisterende indretning og brug", "1 : 100 (A3)", "A3.1", x=0.62, y=0.012, b=0.36, h=0.06)
fig.savefig(HER / "stald_plan.pdf")
fig.savefig(HER / "stald_plan.png", dpi=120)
print("stald_plan.pdf")
