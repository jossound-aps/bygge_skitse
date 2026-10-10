#!/usr/bin/env python3
"""Tegner hallen indefra i perspektiv: stålrammer, åse, vægge, loft og alt det, der står i hallen.

Kør:  python3 tegninger/hal_indvendig.py
Giver: tegninger/hal_indvendig.pdf / .png

Synsvinkel: fra porten og ind i hallen. Portgavlen er skåret væk, så hele rummet ses.
Koordinater som i hal_plan.py: x fra vestvæggen mod øst, y fra sydgavlen mod nord, z op. Mål i meter.
Maskiner, trailere og bil er forenklede figurer med de foreløbige mål fra hal_plan.py.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon

HER = Path(__file__).parent
h = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))["hal"]

B, L = h["bredde"], h["laengde"]
RUM = h["rum_laengde"]
SIDE, HAELD = 4.0, 30.0
KIP = SIDE + B / 2 * math.tan(math.radians(HAELD))
YN = L - RUM                      # væggen ind til det lukkede rum
RAMMER = [0.15, 5.0, 10.0, 15.0]  # stålrammer, ca. 5 m afstand
KAM = np.array([B / 2, -8.0, 3.7])   # øjepunkt: midt for porten, 8 m ude og 3,7 m oppe, så man ser hen over de forreste maskiner

STAAL, AAS, PANEL, LOFT, GULV = "#1c1d1f", "#c9a66b", "#e4e6e7", "#d5d8da", "#b9b7b1"
DRIFT_KANT, PRIVAT_KANT = "#2f7d32", "#1f5fa8"

flader = []     # (afstand, punkter3d, farve, kant, lw)
SPEJL, YOFF = False, 0.0   # genstandene er defineret med huset til venstre; SPEJL vender dem, så vestsiden (mod huset) er til højre


def proj(p):
    p = np.asarray(p, float)
    d = p[..., 1] - KAM[1]
    return np.stack([(p[..., 0] - KAM[0]) / d, (p[..., 2] - KAM[2]) / d], axis=-1)


def flade(pts, farve, kant="#333333", lw=0.4, normal=None, forrest=0.0):
    p = np.array(pts, float)
    if SPEJL:
        p[:, 0] = B - p[:, 0]
        p[:, 1] += YOFF
        normal = None if normal is None else (-normal[0], normal[1], normal[2])
    c = p.mean(axis=0)
    if normal is not None and np.dot(normal, KAM - c) <= 0:
        return
    flader.append((float(np.linalg.norm(c - KAM)) - forrest, p, farve, kant, lw))


def nuance(farve, f):
    r, g, b = (int(farve[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(v * f))) for v in (r, g, b))


def kasse(x0, y0, z0, x1, y1, z1, farve, kant="#333333", lw=0.4):
    """Retvinklet kasse; kun flader, der vender mod øjepunktet, tegnes."""
    for pts, n, f in (
        ([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], (0, -1, 0), 0.88),
        ([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], (0, 1, 0), 0.7),
        ([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], (-1, 0, 0), 0.72),
        ([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], (1, 0, 0), 0.72),
        ([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], (0, 0, 1), 1.0),
        ([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], (0, 0, -1), 0.55),
    ):
        flade(pts, nuance(farve, f), kant, lw, n)


def tag_z(x):
    return SIDE + (B / 2 - abs(x - B / 2)) * math.tan(math.radians(HAELD))


etiketter = []


def etiket(tekst, x, y, z, privat, dx=0.0, dy=0.035):
    etiketter.append((tekst, (B - x, y + YOFF, z) if SPEJL else (x, y, z), privat, -dx if SPEJL else dx, dy))


# ---------------- Rummet: gulv, vægge, loft ----------------
baggrund = []
baggrund.append(([(0, 0, 0), (B, 0, 0), (B, YN, 0), (0, YN, 0)], GULV, "none", 0))
baggrund.append(([(3.35, 0, 0.001), (6.65, 0, 0.001), (6.65, 9.75, 0.001), (3.35, 9.75, 0.001)], "#c6c4be", "none", 0))        # kørebane
for x0, y0, x1, y1 in ((7.9, 8.4, 9.85, YN), (0.15, 10.45, 2.65, YN), (3.0, 9.9, 6.6, YN)):                               # private felter
    baggrund.append(([(x0, y0, 0.002), (x1, y0, 0.002), (x1, y1, 0.002), (x0, y1, 0.002)], "#c3d3e6", "none", 0))
baggrund.append(([(0, 0, 0), (0, YN, 0), (0, YN, SIDE), (0, 0, SIDE)], nuance(PANEL, 0.93), "#888888", 0.5))                  # vestvæg
baggrund.append(([(B, 0, 0), (B, YN, 0), (B, YN, SIDE), (B, 0, SIDE)], nuance(PANEL, 0.93), "#888888", 0.5))                  # østvæg
baggrund.append(([(0, 0, SIDE), (B / 2, 0, KIP), (B / 2, YN, KIP), (0, YN, SIDE)], LOFT, "#888888", 0.5))                    # loft vest
baggrund.append(([(B, 0, SIDE), (B / 2, 0, KIP), (B / 2, YN, KIP), (B, YN, SIDE)], nuance(LOFT, 0.95), "#888888", 0.5))      # loft øst
baggrund.append(([(0, YN, 0), (B, YN, 0), (B, YN, SIDE), (B / 2, YN, KIP), (0, YN, SIDE)], "#eef0f1", "#666666", 0.7))       # væg til rummet

linjer = []     # (punkter3d, farve, lw) tegnes oven på baggrunden
for z in (1.0, 2.0, 3.0):                                # vandrette panelsamlinger: fire paneler à 1 m i højden
    linjer += [([(0, 0, z), (0, YN, z)], "#b4b8bb", 0.4), ([(B, 0, z), (B, YN, z)], "#b4b8bb", 0.4)]
for y in np.arange(1.06, YN, 1.06):                      # tagpanelernes samlinger
    linjer += [([(0, y, SIDE), (B / 2, y, KIP)], "#c2c6c9", 0.3), ([(B, y, SIDE), (B / 2, y, KIP)], "#c2c6c9", 0.3)]
for s in (0.5, 1.7, 2.9, 4.1, 5.3):                      # åse på tværs af rammerne (træ)
    dx, dz = s * math.cos(math.radians(HAELD)), s * math.sin(math.radians(HAELD))
    for x in (dx, B - dx):
        linjer.append(([(x, 0, SIDE + dz - 0.06), (x, YN, SIDE + dz - 0.06)], AAS, 2.2))
# ingen vægrigler: vægpanelerne skrues direkte på rammernes søjler
# dør fra hallen ind til rummet
baggrund.append(([(6.85, YN - 0.01, 0), (7.75, YN - 0.01, 0), (7.75, YN - 0.01, 2.1), (6.85, YN - 0.01, 2.1)], "#8c9399", "#333333", 0.6))

# ---------------- Stålrammer ----------------
PROFIL = 0.30
for yr in RAMMER:
    t = math.tan(math.radians(HAELD))
    for side in (0, 1):
        sx = (lambda x: x) if side == 0 else (lambda x: B - x)
        # søjle
        flade([(sx(0.03), yr, 0), (sx(0.03 + 0.26), yr, 0), (sx(0.03 + 0.26), yr, SIDE - 0.25), (sx(0.03), yr, SIDE - 0.05)], STAAL, "#000000", 0.5)
        # spær fra rammehjørne til kip, med udfligning ved hjørnet
        xa, xb = 0.03, B / 2
        za, zb = SIDE - 0.05, KIP - 0.12
        flade([(sx(xa), yr, za), (sx(xb), yr, zb), (sx(xb), yr, zb - PROFIL), (sx(1.6), yr, za + (1.6 - xa) * t - PROFIL - 0.02), (sx(xa + 0.26), yr, za - 0.75)],
              STAAL, "#000000", 0.5)

# ---------------- Det, der står i hallen ----------------
GUMMI, GALV = "#2a2a2a", "#aeb4b8"


def hjul(x0, x1, yc, zc, r, n=20):
    """Rundt hjul med aksel på tværs (langs x): to sider med fælg og en slidbane."""
    vink = [2 * math.pi * i / n for i in range(n)]
    for x, nx in ((x0, -1), (x1, 1)):
        flade([(x, yc + r * math.cos(a), zc + r * math.sin(a)) for a in vink], nuance(GUMMI, 0.9), "#111111", 0.3, (nx, 0, 0))
        flade([(x, yc + 0.5 * r * math.cos(a), zc + 0.5 * r * math.sin(a)) for a in vink], "#9a9da1", "#444444", 0.3, (nx, 0, 0), forrest=0.02)   # fælg
    for i in range(n):
        a0, a1 = vink[i], vink[(i + 1) % n] if i + 1 < n else 2 * math.pi
        am = (a0 + a1) / 2
        flade([(x0, yc + r * math.cos(a0), zc + r * math.sin(a0)), (x1, yc + r * math.cos(a0), zc + r * math.sin(a0)),
               (x1, yc + r * math.cos(a1), zc + r * math.sin(a1)), (x0, yc + r * math.cos(a1), zc + r * math.sin(a1))],
              nuance(GUMMI, 0.75 + 0.35 * max(0.0, math.sin(am))), "none", 0, (0, math.cos(am), math.sin(am)))


def hjulpar(xv, xo, y0, y1, dia, bredde=0.3):
    for x in (xv, xo - bredde):
        hjul(x, x + bredde, (y0 + y1) / 2, dia / 2, dia / 2)


SPEJL, YOFF = True, 1.1
# Balletrailer 6,5 x 2,5 m (drift), rykket ind, så gangdøren i portgavlen er fri
hjulpar(0.5, 3.0, 3.1, 3.9, 0.9)
hjulpar(0.5, 3.0, 4.0, 4.8, 0.9)
kasse(0.5, 0.6, 0.95, 3.0, 7.1, 1.12, "#7a8a4a")
for y in (0.6, 7.0):                                      # gavlstøtter
    kasse(0.55, y, 1.12, 0.65, y + 0.1, 2.4, "#55622f")
    kasse(2.85, y, 1.12, 2.95, y + 0.1, 2.4, "#55622f")
    kasse(0.55, y, 2.3, 2.95, y + 0.1, 2.4, "#55622f")
    kasse(0.55, y, 1.7, 2.95, y + 0.1, 1.78, "#55622f")
etiket("Balletrailer 6,5 × 2,5 m", 1.75, 0.6, 2.4, False)

YOFF = 0.0
# Traktor med frontlæsser 4,8 x 2,1 m (drift), bagenden mod porten
TR = "#2f7a3b"
hjulpar(7.25, 9.35, 0.6, 2.1, 1.5, 0.45)                  # baghjul
hjulpar(7.35, 9.25, 3.3, 4.2, 0.95, 0.3)                  # forhjul
kasse(7.85, 1.0, 0.7, 8.75, 4.3, 1.55, TR)                # krop og motorhjelm
kasse(7.75, 0.8, 1.55, 8.85, 2.3, 2.75, "#9fb7c4")        # førerhus
kasse(7.7, 0.75, 2.75, 8.9, 2.35, 2.85, TR)               # tag
for x in (7.55, 8.9):                                     # læsserarme
    kasse(x, 2.3, 1.35, x + 0.15, 4.7, 1.55, "#333333")
kasse(7.35, 4.6, 0.15, 9.25, 5.3, 0.85, "#555555")        # skovl
etiket("Traktor med frontlæsser", 8.3, 0.8, 2.85, False)

# Møgvogn 4,5 x 2,0 m (drift)
hjulpar(7.3, 9.3, 7.4, 8.5, 1.0, 0.3)
kasse(7.4, 5.9, 0.75, 9.2, 10.0, 1.7, "#b5651d")
kasse(8.2, 5.7, 0.6, 8.4, 5.9, 0.75, "#444444")           # træk
etiket("Møgvogn", 8.3, 5.9, 1.7, False)

YOFF = 1.1
# Redskaber til frontlæsser 2,9 x 1,2 m (drift)
kasse(2.15, 7.5, 0, 3.25, 8.6, 0.7, "#8a8f94")            # skovl
kasse(2.2, 8.9, 0, 3.2, 9.0, 0.9, "#666a6e")              # pallegafler
kasse(2.3, 9.0, 0, 2.42, 10.2, 0.08, "#666a6e")
kasse(2.98, 9.0, 0, 3.1, 10.2, 0.08, "#666a6e")
etiket("Redskaber", 2.7, 7.5, 0.7, False, dx=0.02)

# Trailer 1 og 2, 3,6 x 1,7 m (privat)
for y0, navn in ((7.4, "Trailer 1"), (11.1, "Trailer 2")):
    hjulpar(0.3, 2.0, y0 + 1.5, y0 + 2.1, 0.6, 0.2)
    kasse(0.5, y0 + 0.9, 0.45, 1.8, y0 + 3.6, 0.55, GALV)
    kasse(0.5, y0 + 0.9, 0.55, 1.8, y0 + 0.95, 0.9, GALV)
    kasse(0.5, y0 + 3.55, 0.55, 1.8, y0 + 3.6, 0.9, GALV)
    kasse(0.5, y0 + 0.9, 0.55, 0.55, y0 + 3.6, 0.9, GALV)
    kasse(1.75, y0 + 0.9, 0.55, 1.8, y0 + 3.6, 0.9, GALV)
    kasse(1.1, y0, 0.4, 1.2, y0 + 0.9, 0.5, "#777777")    # træk
    etiket(navn, 1.15, y0 + 0.9, 0.9, True)

YOFF = 0.0
# Trailer 3, 5,0 x 2,1 m (privat)
hjulpar(7.5, 9.6, 12.6, 13.2, 0.65, 0.22)
hjulpar(7.5, 9.6, 13.3, 13.9, 0.65, 0.22)
kasse(7.75, 11.7, 0.5, 9.35, 15.6, 0.62, GALV)
for x0, x1, y0, y1 in ((7.75, 9.35, 11.7, 11.76), (7.75, 9.35, 15.54, 15.6), (7.75, 7.81, 11.7, 15.6), (9.29, 9.35, 11.7, 15.6)):
    kasse(x0, y0, 0.62, x1, y1, 1.0, GALV)
kasse(8.5, 10.6, 0.45, 8.6, 11.7, 0.55, "#777777")
etiket("Trailer 3", 8.55, 11.7, 1.0, True)

# Tosøjlet lift med bil (privat), for enden af kørebanen
for x in (3.7, 6.5):
    kasse(x, 12.75, 0, x + 0.25, 13.05, 3.8, "#c0392b")
    kasse(x - 0.15, 12.6, 0, x + 0.4, 13.2, 0.04, "#8e2a20")
kasse(3.7, 12.8, 3.7, 6.75, 13.0, 3.8, "#c0392b")          # overligger
for x0, x1 in ((3.95, 4.5), (5.95, 6.5)):                  # løftearme
    kasse(x0, 12.0, 1.72, x1, 12.12, 1.8, "#444444")
    kasse(x0, 13.7, 1.72, x1, 13.82, 1.8, "#444444")
BIL = "#34495e"
kasse(4.3, 10.7, 1.85, 6.15, 15.2, 2.55, BIL)              # karrosseri
kasse(4.45, 11.9, 2.55, 6.0, 14.4, 3.15, "#8fa7b8")        # kabine
for x in (4.25, 5.95):                                     # bilens hjul hænger frit under den løftede bil
    for yc in (11.65, 14.25):
        hjul(x, x + 0.25, yc, 1.75, 0.34)
etiket("Tosøjlet lift med bil", 5.22, 12.9, 3.8, True, dy=0.02)

# Person 1,8 m som målestok
kasse(5.6, 6.0, 0, 6.0, 6.25, 1.5, "#6d6d6d", "#444444", 0.3)
kasse(5.7, 6.03, 1.5, 5.9, 6.22, 1.8, "#d8b79a", "#444444", 0.3)

SPEJL = False
# ---------------- Tegn ----------------
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
ax = fig.add_axes([0.02, 0.11, 0.96, 0.87])
ax.set_aspect("equal")
ax.axis("off")
for pts, farve, kant, lw in baggrund:
    ax.add_patch(Polygon(proj(pts), closed=True, fc=farve, ec=kant, lw=lw, zorder=1))
for pts, farve, lw in linjer:
    q = proj(pts)
    ax.plot(q[:, 0], q[:, 1], color=farve, lw=lw, solid_capstyle="butt", zorder=1.5)
for _, p, farve, kant, lw in sorted(flader, key=lambda f: -f[0]):
    ax.add_patch(Polygon(proj(p), closed=True, fc=farve, ec=kant, lw=lw, joinstyle="round", zorder=2))
for tekst, p, privat, dx, dy in etiketter:
    q = proj(p)
    ax.annotate(tekst, xy=q, xytext=(q[0] + dx, q[1] + dy), fontsize=7.5, ha="center", va="center", zorder=5,
                arrowprops=dict(arrowstyle="-", lw=0.5, color="#333333"),
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec=PRIVAT_KANT if privat else DRIFT_KANT, lw=1.0))
q = proj((7.3, YN, 2.1))
ax.annotate(f"Dør til lukket rum ({B * RUM:.0f} m²)", xy=q, xytext=(q[0] + 0.02, q[1] + 0.045), fontsize=7, ha="center", va="center", zorder=5,
            arrowprops=dict(arrowstyle="-", lw=0.5), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#666666", lw=0.6))
q = proj((4.2, 6.0, 1.8))
ax.text(q[0] + 0.02, q[1] - 0.03, "person\n1,8 m", fontsize=6, ha="left", va="center", color="#444444", zorder=5)
q = proj((0.2, 0.15, SIDE - 1.0))
ax.annotate("Stålramme: søjle og spær\n(rammer pr. ca. 5 m)", xy=q, xytext=(q[0] + 0.10, q[1] + 0.13), fontsize=7, ha="left", va="center", zorder=5,
            arrowprops=dict(arrowstyle="-", lw=0.5), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#666666", lw=0.6))
q = proj((1.48, 3.0, SIDE + 0.85 - 0.06))
ax.annotate("Åse i træ under tagpanelerne", xy=q, xytext=(q[0] + 0.18, q[1] + 0.10), fontsize=7, ha="left", va="center", zorder=5,
            arrowprops=dict(arrowstyle="-", lw=0.5), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#666666", lw=0.6))
q = proj((B, 3.0, 3.3))
ax.annotate("Vægpaneler 1 m høje, fire i højden,\nskruet direkte på søjlerne", xy=q, xytext=(q[0] - 0.30, q[1] + 0.035), fontsize=7, ha="left", va="center", zorder=5,
            arrowprops=dict(arrowstyle="-", lw=0.5), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#666666", lw=0.6))
ax.autoscale_view()
x0, x1 = ax.get_xlim()
ax.set_xlim(x0 - 0.02, x1 + 0.02)

fig.text(0.04, 0.085, "Hallen indefra, set fra porten (nordgavlen mod ridebanen) mod syd, Nældevej 42, 9000 Aalborg", fontsize=12, weight="bold")
fig.text(0.04, 0.062, f"Hal {B:.0f} × {L:.0f} m, sidehøjde {SIDE:.1f} m, kip {KIP:.1f} m, taghældning {HAELD:.0f}°. Grøn ramme om teksten = driftsdel. Blå ramme = privat. Blå gulvfelter = private zoner.".replace(".", ",", 2), fontsize=8)
fig.text(0.04, 0.040, "FORELØBIG SKITSE i perspektiv, ikke målfast. Nordgavlen med porten er skåret væk. Rammeafstand, profiler og åse er antaget efter referencebilledet og skal fastlægges af leverandøren.", fontsize=7.5, color="red")
fig.text(0.04, 0.022, "Maskiner, trailere og bil er forenklede figurer med de foreløbige mål fra halplanen. Lys, el, vinduer og lysplader er ikke vist. Gangdøren sidder i portgavlen til højre for porten (mod huset) og ses derfor ikke.", fontsize=7.5, color="red")
fig.savefig(HER / "hal_indvendig.pdf")
fig.savefig(HER / "hal_indvendig.png", dpi=160)
print("hal_indvendig.pdf/.png skrevet")
