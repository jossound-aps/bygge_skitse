#!/usr/bin/env python3
"""Tegner plan af hallen i 1:100 (A4): lukket rum i nordenden og én åben hal med driftszone og privat zone.

Kør:  python3 tegninger/hal_plan.py
Giver: tegninger/hal_plan.pdf / .png

Koordinater i meter: x fra vestfacaden (mod skel) mod øst, y fra sydgavlen mod nord.
Maskin- og trailermål er foreløbige og rettes i listerne DRIFT og PRIVAT.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle

HER = Path(__file__).parent
h = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))["hal"]

MAALESTOK = 100
A4 = (210, 297)
B, L = h["bredde"], h["laengde"]
RUM_L = h["rum_laengde"]
YV, SV, IV = 0.15, 0.15, 0.10      # ydervæg (panel + stål), væg mod rum, let indervæg
ix0, ix1, iy0, iy1 = YV, B - YV, YV, L - YV
skil = L - RUM_L                    # væggens midte
h_y1 = skil - SV / 2                # åben hals nordside
r_y0 = skil + SV / 2                # rummets sydside

GROEN, BLAA = "#dcefd3", "#d6e6f7"
# (navn, x, y, bredde øst-vest, længde nord-syd) – egne mål uden friplads
DRIFT = [
    ("Balletrailer\n6,5 × 2,5 m", 0.50, 0.60, 2.5, 6.5),
    ("Traktor med\nfrontlæsser\n4,8 × 2,1 m", 7.25, 0.50, 2.1, 4.8),
    ("Møgvogn\n4,5 × 2,0 m", 7.30, 5.70, 2.0, 4.5),
    ("Redskaber\n2,9 × 1,2 m", 2.10, 7.40, 1.2, 2.9),
]
PRIVAT = [
    ("Trailer 1\n3,6 × 1,7 m", 0.30, 7.40, 1.7, 3.6),
    ("Trailer 2\n3,6 × 1,7 m", 0.30, 11.30, 1.7, 3.6),
    ("Trailer 3\n5,0 × 2,1 m", 7.50, 10.60, 2.1, 5.0),
]
LIFT = (3.40, 9.90, 3.6, 6.0)        # lift/værksted nord-syd for enden af kørebanen
KOERE = (3.35, iy0, 3.3, 9.75)       # kørebane fra sydporten
TOILET = (ix0, iy1 - 1.8, 1.5, 1.8)
# Private zoner i den åbne hal (til arealopgørelsen), inkl. friplads
PRIVATZONER = [
    (ix0, 7.30, 1.95, h_y1 - 7.30),            # trailer 1 og 2
    (7.35, 10.45, ix1 - 7.35, h_y1 - 10.45),   # trailer 3
]

fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
felt = (15, 42, 180, 245)
ax = fig.add_axes([felt[0] / A4[0], felt[1] / A4[1], felt[2] / A4[0], felt[3] / A4[1]])
bm, hm = felt[2] * MAALESTOK / 1000, felt[3] * MAALESTOK / 1000
ax.set_xlim(B / 2 - bm / 2, B / 2 + bm / 2)
ax.set_ylim(L / 2 - hm / 2 - 0.3, L / 2 + hm / 2 - 0.3)
ax.set_aspect("equal")
ax.axis("off")


def vaeg(x, y, w, hh):
    ax.add_patch(Rectangle((x, y), w, hh, fc="#333333", ec="none", zorder=3))


def aabning(x, y, w, hh):
    ax.add_patch(Rectangle((x, y), w, hh, fc="white", ec="none", zorder=4))


def port(p, q, tekst, tx, ty):
    ax.plot([p[0], q[0]], [p[1], q[1]], color="#cc0000", lw=1.8, zorder=5)
    ax.text(tx, ty, tekst, fontsize=6, ha="center", va="center", color="#cc0000")


def ting(navn, x, y, w, hh, fc):
    ax.add_patch(Rectangle((x, y), w, hh, fc=fc, ec="#666666", lw=0.6, ls="--", zorder=2))
    ax.text(x + w / 2, y + hh / 2, navn, fontsize=5.6, ha="center", va="center", color="#222222", zorder=6,
            rotation=90 if hh > 2.2 * w else 0)


def maal(p, q, tekst, off=(0, 0), rot=0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0), zorder=6)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=6.5, ha="center", va="center", rotation=rot)


def dk(tal, dec=1):
    return f"{tal:.{dec}f}".replace(".", ",")


# Gulvflader: hele hallen som drift, derefter de private zoner
ax.add_patch(Rectangle((ix0, iy0), ix1 - ix0, h_y1 - iy0, fc="#f3f9ef", ec="none", zorder=0))
for z in PRIVATZONER:
    ax.add_patch(Rectangle(z[:2], z[2], z[3], fc="#edf4fc", ec="#1f4e79", lw=0.6, ls=":", zorder=1))
ax.add_patch(Rectangle((ix0, r_y0), ix1 - ix0, iy1 - r_y0, fc="#edf4fc", ec="none", zorder=0))

# Vægge
vaeg(0, 0, B, YV)
vaeg(0, L - YV, B, YV)
vaeg(0, 0, YV, L)
vaeg(B - YV, 0, YV, L)
vaeg(ix0, h_y1, ix1 - ix0, SV)

# Åben hal
ax.add_patch(Rectangle(KOERE[:2], KOERE[2], KOERE[3], fc="#ffffff", ec="#aaaaaa", lw=0.5, ls=":", zorder=1))
ax.text(KOERE[0] + KOERE[2] / 2, 4.6, f"Kørebane {dk(KOERE[2])} m bred (fælles adgang)", fontsize=5.8, ha="center", va="center", color="#777777", rotation=90)
for t in DRIFT:
    ting(*t, fc=GROEN)
for t in PRIVAT:
    ting(*t, fc=BLAA)
ax.add_patch(Rectangle(LIFT[:2], LIFT[2], LIFT[3], fc=BLAA, ec="#666666", lw=0.6, ls="--", zorder=2))
ax.text(LIFT[0] + LIFT[2] / 2, LIFT[1] + LIFT[3] / 2, f"Liftplads / værksted\n{dk(LIFT[2])} × {dk(LIFT[3])} m\n(tosøjlet lift\ntil egne biler)", fontsize=5.6, ha="center", va="center", zorder=6)
for sx in (LIFT[0] + 0.2, LIFT[0] + LIFT[2] - 0.4):
    ax.add_patch(Rectangle((sx, LIFT[1] + 3.2), 0.2, 0.3, fc="#b36b00", ec="none", zorder=6))

# Porte og døre
PORT_D = 4.0
aabning(B / 2 - PORT_D / 2, 0, PORT_D, YV)
port((B / 2 - PORT_D / 2, YV / 2), (B / 2 + PORT_D / 2, YV / 2), f"port {dk(PORT_D)} m (eneste port)", B / 2, -0.4)

# Lukket rum i nordenden
vaeg(TOILET[0] + TOILET[2], TOILET[1], IV, TOILET[3])
vaeg(TOILET[0], TOILET[1] - IV, TOILET[2] + IV, IV)
aabning(TOILET[0] + TOILET[2], TOILET[1] + 0.4, IV, 0.8)
ax.text(TOILET[0] + TOILET[2] / 2, TOILET[1] + TOILET[3] / 2, "Toilet\n1,5 × 1,8", fontsize=5.6, ha="center", va="center", zorder=6)
aabning(3.95, L - YV, 0.9, YV)                      # dør mod huset
ax.add_patch(Arc((3.95, L - YV), 1.8, 1.8, theta1=270, theta2=360, color="#666666", lw=0.5, zorder=5))
ax.text(4.4, L + 0.3, "dør mod huset", fontsize=6, ha="center", color="#cc0000")
aabning(2.3, h_y1, 0.9, SV)                         # dør mellem rum og hal
ax.add_patch(Arc((2.3, r_y0), 1.8, 1.8, theta1=0, theta2=90, color="#666666", lw=0.5, zorder=5))
rum_net = (ix1 - ix0) * (iy1 - r_y0)
ax.text(6.3, (r_y0 + iy1) / 2 + 0.3, f"Rum (opbevaring)\n{dk(ix1 - ix0)} × {dk(iy1 - r_y0, 2)} m\n{dk(rum_net)} m² netto, {B * RUM_L:.0f} m² brutto", fontsize=6.5, ha="center", va="center", zorder=6)

# Arealopgørelse
privat_hal = sum(z[2] * z[3] for z in PRIVATZONER) + LIFT[2] * LIFT[3]
privat = B * RUM_L + privat_hal
tx = -1.75
ax.text(tx, 17.9, f"LUKKET RUM\n{B * RUM_L:.0f} m² brutto\n(privat)", fontsize=7, ha="center", va="center", color="#1f4e79", weight="bold")
ax.text(tx, 11.2, f"ÅBEN HAL\n{B * (L - RUM_L):.0f} m² brutto", fontsize=7, ha="center", va="center", weight="bold")
ax.text(tx, 9.4, f"blå felter:\nprivat ca. {privat_hal:.0f} m²", fontsize=6.5, ha="center", va="center", color="#1f4e79")
ax.text(tx, 8.1, f"grønne felter:\ndrift ca. {B * L - privat:.0f} m²", fontsize=6.5, ha="center", va="center", color="#38761d")
ax.text(tx, 5.6, f"I ALT\nprivat ca. {privat:.0f} m²\ndrift ca. {B * L - privat:.0f} m²", fontsize=7, ha="center", va="center", weight="bold")

# Mål
maal((0, -1.1), (B, -1.1), f"{dk(B)} m", (0, -0.3))
maal((B + 2.3, 0), (B + 2.3, skil), f"{dk(L - RUM_L)} m", (0.35, 0), 90)
maal((B + 2.3, skil), (B + 2.3, L), f"{dk(RUM_L)} m", (0.35, 0), 90)
maal((B + 3.2, 0), (B + 3.2, L), f"{dk(L)} m", (0.35, 0), 90)
ax.annotate("N", xy=(tx, L + 0.6), xytext=(tx, L - 0.9), ha="center", va="center", fontsize=9, arrowprops=dict(arrowstyle="-|>", lw=1.2))
ax.text(tx, 0.6, f"skel mod\nmatr.nr. 1cb\n←  {dk(h['afstand_til_skel'])} m", fontsize=6, ha="center", va="center", color="red")

fig.text(0.07, 0.125, "Hal, plan og indretning, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
fig.text(0.07, 0.105, f"Målestok 1:{MAALESTOK} (A4)   ·   Udvendigt {dk(B)} × {dk(L)} m = {B * L:.0f} m²   ·   Sidehøjde 4,0 m, taghældning 30°, kip nord-syd", fontsize=8)
fig.text(0.07, 0.085, "FORELØBIG SKITSE. Stiplede felter viser maskinernes og trailernes egne mål, som er antaget og skal erstattes", fontsize=7, color="red")
fig.text(0.07, 0.070, "med de faktiske. Vægtykkelse 15 cm er antaget. Rammernes søjler er ikke vist.", fontsize=7, color="red")

fig.savefig(HER / "hal_plan.pdf")
fig.savefig(HER / "hal_plan.png", dpi=200)
print(f"Rum {B * RUM_L:.0f} m² brutto ({rum_net:.1f} netto); privat i åben hal ca. {privat_hal:.0f} m²; privat i alt ca. {privat:.0f} m²; drift ca. {B * L - privat:.0f} m²")
