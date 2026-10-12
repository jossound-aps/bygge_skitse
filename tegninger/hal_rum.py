#!/usr/bin/env python3
"""Tegner det lukkede, private rum i hallens sydende: plan i 1:50 og et perspektiv set fra hallen.

Kør:  python3 tegninger/hal_rum.py
Giver: tegninger/hal_rum.pdf / .png   (A3 liggende)

Rumkoordinater i meter: X langs rummet fra østvæggen (0) til vestvæggen mod huset, Y fra væggen mod hallen (0)
ind mod sydgavlen, Z op. Indretningen er et forslag; ret listen INVENTAR.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Arc, Polygon, Rectangle
from nordpil import nordpil
from tegningshoved import tegningshoved

BYGNINGSDREJNING = 1.6   # planen følger bygningerne, som ligger ca. 1,6 grader drejet fra stik nord

HER = Path(__file__).parent
h = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))["hal"]

B, RUM = h["bredde"], h["rum_laengde"]
YV, SV = 0.15, 0.15
LX, LY = B - 2 * YV, RUM - YV - SV / 2          # indvendige mål
SIDE, HAELD = 4.0, 30.0
KIP = SIDE + B / 2 * math.tan(math.radians(HAELD))
DOER = (6.70, 0.9)                               # dør fra hallen: start-X og bredde
TOILET = (0.0, LY - 1.8, 1.5, 1.8)               # x, y, bredde, dybde
# (navn, x, y, bredde, dybde, højde, farve). Indretningen er et forslag.
INVENTAR = [
    ("Arbejdsbord", 0.15, 0.0, 2.4, 0.7, 0.9, "#b08d57"),
    ("Lejepresse", 2.7, 0.0, 0.6, 0.6, 1.6, "#6b6e73"),
    ("Værkstedsvogn", 3.45, 0.0, 0.9, 0.5, 0.9, "#b03a2e"),
    ("Reoler: hynder, parasol\nog havegrej", 1.75, LY - 0.6, LX - 1.85, 0.6, 2.2, "#c9a66b"),
    ("Hjulstativ til\nsæsonhjul", 7.65, 0.0, 2.0, 0.5, 1.9, "#8a8f94"),
    ("Cykler og\nhaveredskaber", 4.5, 0.0, 1.6, 0.6, 1.1, "#9fb4a0"),
    ("Havebord og\nhavestole", 5.0, 1.45, 2.0, 1.0, 1.2, "#8c6d4a"),
    ("Grill", 7.25, 1.5, 0.6, 0.6, 1.0, "#333333"),
]

fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))

# ---------------- Plan 1:50 ----------------
MAAL = 50
felt = (30, 183, 360, 108)  # mm: venstre, bund, bredde, højde
ax = fig.add_axes([felt[0] / 420, felt[1] / 297, felt[2] / 420, felt[3] / 297])
bm, hm = felt[2] * MAAL / 1000, felt[3] * MAAL / 1000
ax.set_xlim(LX / 2 - bm / 2, LX / 2 + bm / 2)
ax.set_ylim(LY / 2 - hm / 2, LY / 2 + hm / 2)
ax.invert_xaxis()            # som på halplanen: nord op, vest (mod huset) til venstre
ax.invert_yaxis()
ax.set_aspect("equal")
ax.axis("off")


def dk(tal, dec=1):
    return f"{tal:.{dec}f}".replace(".", ",")


VAEG = "#333333"
ax.add_patch(Rectangle((0, 0), LX, LY, fc="#edf3fb", ec="none", zorder=0))
for x, y, w, hh in ((-YV, -SV, LX + 2 * YV, SV), (-YV, LY, LX + 2 * YV, YV), (-YV, -SV, YV, LY + SV + YV), (LX, -SV, YV, LY + SV + YV)):
    ax.add_patch(Rectangle((x, y), w, hh, fc=VAEG, ec="none", zorder=3))
ax.add_patch(Rectangle((DOER[0], -SV), DOER[1], SV, fc="white", ec="none", zorder=4))
ax.add_patch(Arc((DOER[0], 0), 2 * DOER[1], 2 * DOER[1], theta1=0, theta2=90, color="#666666", lw=0.5, zorder=5))
ax.text(DOER[0] + DOER[1] / 2, -0.45, "dør fra hallen", fontsize=7, ha="center", color="#cc0000")
# toilet
tx, ty, tw, td = TOILET
ax.add_patch(Rectangle((tx + tw, ty), 0.1, td, fc=VAEG, ec="none", zorder=3))
ax.add_patch(Rectangle((tx, ty - 0.1), tw + 0.1, 0.1, fc=VAEG, ec="none", zorder=3))
ax.add_patch(Rectangle((tx + tw, ty + 0.5), 0.1, 0.8, fc="white", ec="none", zorder=4))
ax.add_patch(Rectangle((tx + 0.55, ty + td - 0.65), 0.4, 0.6, fc="white", ec="#555555", lw=0.6, zorder=5))       # wc
ax.add_patch(Rectangle((tx + 0.05, ty + 0.15), 0.45, 0.35, fc="white", ec="#555555", lw=0.6, zorder=5))          # håndvask
ax.text(tx + tw / 2, ty + 0.85, f"Toilet og\nhåndvask\n{dk(tw)} × {dk(td)} m", fontsize=7, ha="center", va="center", zorder=6)
for navn, x, y, w, d, _, farve in INVENTAR:
    ax.add_patch(Rectangle((x, y), w, d, fc=farve, ec="#555555", lw=0.6, ls="--", alpha=0.75, zorder=2))
    ax.text(x + w / 2, y + d / 2, navn.replace("\n", " "), fontsize=6.5, ha="center", va="center", zorder=6)
ax.text(3.0, 1.45, f"Privat rum til opbevaring, med toilet\n{dk(LX)} × {dk(LY, 2)} m = {dk(LX * LY)} m² netto ({B * RUM:.0f} m² brutto)", fontsize=8, ha="center", va="center", zorder=6)


def maal(p, q, tekst, off=(0, 0), rot=0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0), zorder=6)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=7, ha="center", va="center", rotation=rot)


maal((0, LY + 0.55), (LX, LY + 0.55), f"{dk(LX)} m", (0, 0.22))
maal((LX + 0.6, 0), (LX + 0.6, LY), f"{dk(LY, 2)} m", (0.25, 0), 90)
ax.text(LX / 2, LY + 0.25, "sydgavl (ingen åbninger)", fontsize=6.5, ha="center", va="center", color="#555555")
ax.text(LX / 2, -0.22, "væg mod den åbne hal", fontsize=6.5, ha="center", va="center", color="#555555")
nordpil(fig, 0.93, 0.89, vinkel=BYGNINGSDREJNING)
ax.text(LX + 1.7, LY / 2, "mod\nhuset", fontsize=7, ha="center", va="center", color="#555555")
fig.text(0.07, 0.955, "Plan 1:50", fontsize=10, weight="bold")

# ---------------- Perspektiv set fra hallen ----------------
KAM = np.array([LX / 2, -6.5, 3.0])
flader = []


def proj(p):
    p = np.asarray(p, float)
    d = p[..., 1] - KAM[1]
    # X vokser mod vest, så huset ligger til højre, som man ser det, når man står i hallen og ser mod syd
    return np.stack([(p[..., 0] - KAM[0]) / d, (p[..., 2] - KAM[2]) / d], axis=-1)


def nuance(farve, f):
    r, g, b = (int(farve[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


def flade(pts, farve, kant="#333333", lw=0.4, normal=None):
    p = np.array(pts, float)
    c = p.mean(axis=0)
    if normal is None or np.dot(normal, KAM - c) > 0:
        flader.append((float(np.linalg.norm(c - KAM)), p, farve, kant, lw))


def kasse(x0, y0, z0, x1, y1, z1, farve, kant="#333333", lw=0.4):
    for pts, n, f in (
        ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0), 0.9),
        ([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], (-1, 0, 0), 0.72),
        ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0), 0.72),
        ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1), 1.0),
    ):
        flade(pts, nuance(farve, f), kant, lw, n)


ax2 = fig.add_axes([0.03, 0.10, 0.94, 0.50])
ax2.set_aspect("equal")
ax2.axis("off")
PANEL, LOFT, GULV = "#e4e6e7", "#d5d8da", "#c2c0ba"
bag = [
    ([(0, 0, 0), (LX, 0, 0), (LX, LY, 0), (0, LY, 0)], GULV),
    ([(0, 0, 0), (0, LY, 0), (0, LY, SIDE), (0, 0, SIDE)], nuance(PANEL, 0.93)),
    ([(LX, 0, 0), (LX, LY, 0), (LX, LY, SIDE), (LX, 0, SIDE)], nuance(PANEL, 0.93)),
    ([(0, 0, SIDE), (LX / 2, 0, KIP), (LX / 2, LY, KIP), (0, LY, SIDE)], LOFT),
    ([(LX, 0, SIDE), (LX / 2, 0, KIP), (LX / 2, LY, KIP), (LX, LY, SIDE)], nuance(LOFT, 0.95)),
    ([(0, LY, 0), (LX, LY, 0), (LX, LY, SIDE), (LX / 2, LY, KIP), (0, LY, SIDE)], "#eef0f1"),
]
for pts, farve in bag:
    ax2.add_patch(Polygon(proj(pts), closed=True, fc=farve, ec="#888888", lw=0.5, zorder=1))
for z in (1.0, 2.0, 3.0):                                  # panelsamlinger, 1 m paneler
    for l in ([(0, 0, z), (0, LY, z)], [(LX, 0, z), (LX, LY, z)], [(0, LY, z), (LX, LY, z)]):
        q = proj(l)
        ax2.plot(q[:, 0], q[:, 1], color="#b4b8bb", lw=0.4, zorder=1.5)
for s in (0.5, 1.7, 2.9, 4.1, 5.3):                        # åse under taget
    dx, dz = s * math.cos(math.radians(HAELD)), s * math.sin(math.radians(HAELD))
    for x in (dx - YV, LX + YV - dx):
        q = proj([(x, 0, SIDE + dz - 0.06), (x, LY, SIDE + dz - 0.06)])
        ax2.plot(q[:, 0], q[:, 1], color="#c9a66b", lw=2.0, zorder=1.5)
# gavlrammen i stål
t30 = math.tan(math.radians(HAELD))
for sx in (lambda x: x, lambda x: LX - x):
    flade([(sx(0.0), LY - 0.02, 0), (sx(0.26), LY - 0.02, 0), (sx(0.26), LY - 0.02, SIDE - 0.2), (sx(0.0), LY - 0.02, SIDE)], "#1c1d1f", "#000000", 0.5)
    flade([(sx(0.0), LY - 0.02, SIDE), (sx(LX / 2), LY - 0.02, KIP - 0.1), (sx(LX / 2), LY - 0.02, KIP - 0.4), (sx(1.5), LY - 0.02, SIDE + 1.5 * t30 - 0.3), (sx(0.26), LY - 0.02, SIDE - 0.7)],
          "#1c1d1f", "#000000", 0.5)
# toiletrum (lette vægge til 2,4 m) med dør
kasse(tx, ty, 0, tx + tw, LY, 2.4, "#f3f3f1")
flade([(tx + tw + 0.01, ty + 0.5, 0), (tx + tw + 0.01, ty + 1.3, 0), (tx + tw + 0.01, ty + 1.3, 2.05), (tx + tw + 0.01, ty + 0.5, 2.05)], "#8c9399", "#333333", 0.5)
for navn, x, y, w, d, hh, farve in INVENTAR:
    if navn.startswith("Reoler"):                          # reoler vises med hylder
        for z in (0.1, 0.65, 1.2, 1.75, 2.2):
            kasse(x, y, z - 0.04, x + w, y + d, z, farve)
        for xx in np.arange(x, x + w + 0.01, (w) / 6):
            kasse(xx - 0.03, y, 0, xx + 0.03, y + d, hh, nuance(farve, 0.8))
    elif navn.startswith("Hjulstativ"):
        for z in (0.75, 1.55):
            kasse(x, y, z - 0.05, x + w, y + d, z, farve)
            for i in range(4):                             # fire hjul pr. hylde
                cx_ = x + 0.3 + i * (w - 0.6) / 3
                vink = [2 * math.pi * k / 16 for k in range(16)]
                flade([(cx_ + 0.3 * math.cos(a), y + d / 2 - 0.12, z - 0.72 + 0.37 + 0.3 * math.sin(a)) for a in vink], "#2a2a2a", "#111111", 0.3)
                flade([(cx_ + 0.15 * math.cos(a), y + d / 2 - 0.13, z - 0.72 + 0.37 + 0.15 * math.sin(a)) for a in vink], "#9a9da1", "#444444", 0.3)
        for xx in (x, x + w):
            kasse(xx - 0.03, y, 0, xx + 0.03, y + d, hh, nuance(farve, 0.8))
    elif navn.startswith("Arbejdsbord"):
        kasse(x, y, hh - 0.06, x + w, y + d, hh, farve)
        for xx in (x + 0.05, x + w - 0.11):
            kasse(xx, y + 0.05, 0, xx + 0.06, y + d - 0.05, hh - 0.06, nuance(farve, 0.75))
    else:
        kasse(x, y, 0, x + w, y + d, hh, farve)
# person som målestok
kasse(4.3, 2.4, 0, 4.7, 2.65, 1.5, "#6d6d6d", "#444444", 0.3)
kasse(4.4, 2.43, 1.5, 4.6, 2.62, 1.8, "#d8b79a", "#444444", 0.3)
for _, p, farve, kant, lw in sorted(flader, key=lambda f: -f[0]):
    ax2.add_patch(Polygon(proj(p), closed=True, fc=farve, ec=kant, lw=lw, joinstyle="round", zorder=2))


def skilt(tekst, p, dx, dy):
    q = proj(p)
    ax2.annotate(tekst, xy=q, xytext=(q[0] + dx, q[1] + dy), fontsize=7.5, ha="center", va="center", zorder=5,
                 arrowprops=dict(arrowstyle="-", lw=0.5, color="#333333"), bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#1f5fa8", lw=0.9))


skilt("Toilet med håndvask", (tx + tw / 2, ty, 2.4), 0.04, 0.17)
skilt("Reoler langs sydgavlen", (LX / 2 + 2.3, LY - 0.6, 2.2), 0.0, 0.13)
skilt("Hjulstativ til sæsonhjul", (8.65, 0.0, 1.9), 0.14, 0.10)
skilt("Arbejdsbord", (1.35, 0.0, 0.9), -0.10, -0.12)
skilt("Lejepresse", (3.0, 0.0, 1.6), -0.04, 0.13)
skilt("Værkstedsvogn", (3.9, 0.0, 0.9), 0.0, -0.15)
skilt("Havebord og havestole, stablet om vinteren", (6.0, 1.45, 1.2), 0.0, 0.15)
skilt("Grill", (7.55, 1.5, 1.0), 0.07, 0.09)
skilt("Cykler og haveredskaber", (5.3, 0.0, 1.1), 0.03, -0.13)
q = proj((DOER[0] + DOER[1] / 2, 0, 0))
ax2.annotate("dør fra hallen\n(væggen mod hallen er skåret væk)", xy=q, xytext=(q[0], q[1] - 0.10), fontsize=7, ha="center", va="center", color="#cc0000",
             arrowprops=dict(arrowstyle="-", lw=0.5, color="#cc0000"))
q = proj((4.5, 2.4, 1.8))
ax2.text(q[0] + 0.035, q[1] - 0.03, "person\n1,8 m", fontsize=6.5, ha="left", va="center", color="#444444")
ax2.autoscale_view()
x0, x1 = ax2.get_xlim()
y0, y1 = ax2.get_ylim()
ax2.set_xlim(x0 - 0.03, x1 + 0.03)
ax2.set_ylim(y0 - 0.14, y1 + 0.03)
fig.text(0.07, 0.605, "Perspektiv set fra den åbne hal mod syd (huset ligger til højre)", fontsize=10, weight="bold")

import textwrap
fig.text(0.05, 0.090, "Det lukkede rum i hallens sydende, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
_fod = (f"Privat rum til opbevaring med toilet og håndvask til dem, der rider og arbejder med hestene og maskinerne. Indvendigt {dk(LX)} × {dk(LY, 2)} m, sidehøjde {dk(SIDE)} m, kip {dk(KIP)} m. Adgang kun fra hallen. "
        "Her står lejepresse, værkstedsvogn, sæsonhjul og cykler samt havemøbler, grill og andet udeudstyr, som skal ind om vinteren. Indretningen er vejledende. Rummet er uden vinduer og uden egen udgang til det fri. Perspektivet er ikke målfast.")
fig.text(0.05, 0.072, "\n".join(textwrap.wrap(_fod, 118)), fontsize=7, va="top", linespacing=1.35)
tegningshoved(fig, "Hal, det lukkede rum: plan og perspektiv", "1 : 50 (A3)", "A1.6", x=0.62, y=0.012, b=0.36, h=0.06)
fig.savefig(HER / "hal_rum.pdf")
fig.savefig(HER / "hal_rum.png", dpi=160)
print(f"hal_rum.pdf/.png skrevet: {LX:.1f} x {LY:.2f} m = {LX * LY:.1f} m² netto")
