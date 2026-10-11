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
for x0, y0, x1, y1 in ((7.9, 12.15, 9.85, YN), (4.1, 9.9, 7.7, YN)):                                                     # private felter: trailer 1 og liftplads
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
for dx0 in (6.85, 2.95):                                 # privat rum (vest) og rum til foder, udstyr og værktøj med toilet (øst)
    baggrund.append(([(dx0, YN - 0.01, 0), (dx0 + 0.9, YN - 0.01, 0), (dx0 + 0.9, YN - 0.01, 2.1), (dx0, YN - 0.01, 2.1)], "#8c9399", "#333333", 0.6))

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


# Koordinater som på halplanen (hal_plan.py): x = 0 er østvæggen (til venstre i billedet), y = 0 er portgavlen.
# Maskinerne er forenklede figurer efter ejers fotos (IMG_3005-3010, P_20220430).
GUL, ROED = "#f0b323", "#c8553d"

# Traktor med frontlæsser 4,8 x 2,1 m (drift), i midterbanen lige inden for porten, bagenden mod porten
TR = "#2f7a3b"
hjulpar(3.95, 6.05, 0.6, 2.1, 1.5, 0.45)                  # baghjul
hjulpar(4.05, 5.95, 3.3, 4.2, 0.95, 0.3)                  # forhjul
kasse(4.55, 1.0, 0.7, 5.45, 4.3, 1.55, TR)                # krop og motorhjelm
kasse(4.45, 0.8, 1.55, 5.55, 2.3, 2.75, "#9fb7c4")        # førerhus
kasse(4.4, 0.75, 2.75, 5.6, 2.35, 2.85, TR)               # tag
for x in (4.25, 5.6):                                     # læsserarme
    kasse(x, 2.3, 1.35, x + 0.15, 4.7, 1.55, "#333333")
kasse(4.05, 4.6, 0.15, 5.95, 5.3, 0.85, "#555555")        # skovl
etiket("Traktor med frontlæsser", 5.0, 0.8, 2.85, False)

# Balleflytter til wrapballer 3,0 x 1,9 m (drift): sort A-ramme på to brede hjul, røde spyd bagud
hjulpar(4.05, 5.95, 7.4, 8.1, 0.6, 0.35)
kasse(4.4, 7.7, 0.3, 5.6, 7.8, 0.38, "#1a1a1a")
kasse(4.95, 5.9, 0.3, 5.05, 7.7, 0.38, "#1a1a1a")         # trækstang
kasse(4.95, 7.62, 0.38, 5.05, 7.74, 1.3, "#1a1a1a")       # mast med spil
for x in (4.6, 5.32):
    kasse(x, 7.8, 0.2, x + 0.08, 8.8, 0.28, "#cc2222")
etiket("Balleflytter", 5.0, 7.7, 1.3, False, dy=0.03)

# Halmballe-elevator 8,0 x 0,9 m (drift) langs østvæggen
kasse(0.4, 0.5, 0.45, 1.0, 8.5, 0.62, ROED)
for y in (1.2, 4.5, 7.8):
    kasse(0.45, y, 0, 0.5, y + 0.06, 0.45, "#7a2e1e")
    kasse(0.9, y, 0, 0.95, y + 0.06, 0.45, "#7a2e1e")
etiket("Halmballe-elevator", 0.7, 3.0, 0.62, False, dx=-0.03, dy=0.06)

# To plænetraktorer (drift)
for y0, l_, navn in ((0.6, 2.0, "Plænetraktor"), (6.55, 2.3, "Plænetraktor")):
    hjulpar(1.45, 2.75, y0 + 0.2, y0 + 0.65, 0.45, 0.25)
    hjulpar(1.45, 2.75, y0 + l_ - 0.7, y0 + l_ - 0.2, 0.5, 0.25)
    kasse(1.62, y0 + 0.1, 0.3, 2.58, y0 + l_ - 0.1, 0.75, GUL)
    kasse(1.85, y0 + 0.8, 0.75, 2.35, y0 + 1.3, 1.2, "#222222")
    etiket(navn, 2.1, y0 + 0.9, 1.2, False, dy=0.03)

# Møgtrailer 3,3 x 1,6 m (drift)
hjulpar(1.3, 2.9, 4.9, 5.5, 0.6, 0.2)
kasse(1.45, 4.0, 0.5, 2.75, 6.25, 0.95, "#8a5a44")
kasse(2.05, 3.0, 0.45, 2.15, 4.0, 0.52, "#444444")        # træk
etiket("Møgtrailer", 2.1, 4.0, 0.95, False, dy=0.03)

# Ladtrailer med kapel, 3 aksler, 8,0 x 2,55 m (drift), langs vestvæggen
for y in (5.4, 6.2, 7.0):
    hjulpar(7.25, 9.8, y, y + 0.6, 0.7, 0.22)
kasse(7.37, 2.8, 0.75, 9.68, 9.35, 0.9, GALV)
kasse(7.37, 2.8, 0.9, 9.68, 9.35, 2.9, "#b9bdc2")         # kapel
kasse(8.47, 1.4, 0.6, 8.57, 2.8, 0.7, "#777777")          # træk
etiket("Ladtrailer med kapel (hø, halm, wrap)", 8.5, 2.8, 2.9, False)

# Redskaber og ridebaneharve (drift)
kasse(8.2, 10.0, 0, 9.5, 11.0, 0.25, "#b03a2e")
etiket("Ridebaneharve", 8.85, 10.0, 0.25, False, dy=0.03)

# Trailer 1, 3,6 x 1,7 m (privat), sydvest
y0 = 12.25
hjulpar(8.0, 9.7, y0 + 1.9, y0 + 2.5, 0.6, 0.2)
kasse(8.2, y0 + 0.9, 0.45, 9.5, y0 + 3.6, 0.55, GALV)
for x0, x1, ya, yb in ((8.2, 9.5, y0 + 0.9, y0 + 0.95), (8.2, 9.5, y0 + 3.55, y0 + 3.6), (8.2, 8.25, y0 + 0.9, y0 + 3.6), (9.45, 9.5, y0 + 0.9, y0 + 3.6)):
    kasse(x0, ya, 0.55, x1, yb, 0.9, GALV)
kasse(8.8, y0, 0.4, 8.9, y0 + 0.9, 0.5, "#777777")        # træk
etiket("Trailer 1", 8.85, y0 + 0.9, 0.9, True)

# Hestetrailer 5,0 x 2,1 m (drift), sydøst
hjulpar(0.4, 2.5, 13.2, 13.8, 0.65, 0.22)
hjulpar(0.4, 2.5, 13.9, 14.5, 0.65, 0.22)
kasse(0.6, 11.6, 0.5, 2.3, 15.55, 2.6, "#d5d8db")
kasse(1.4, 10.6, 0.45, 1.5, 11.6, 0.55, "#777777")
etiket("Hestetrailer", 1.45, 11.6, 2.6, False)

# Tosøjlet lift med bil (privat), for enden af midterbanen
for x in (4.2, 7.25):
    kasse(x, 12.75, 0, x + 0.25, 13.05, 3.8, "#c0392b")
    kasse(x - 0.15, 12.6, 0, x + 0.4, 13.2, 0.04, "#8e2a20")
kasse(4.2, 12.8, 3.7, 7.5, 13.0, 3.8, "#c0392b")           # overligger
for x0, x1 in ((4.45, 5.0), (6.7, 7.25)):                  # løftearme
    kasse(x0, 12.0, 1.72, x1, 12.12, 1.8, "#444444")
    kasse(x0, 13.7, 1.72, x1, 13.82, 1.8, "#444444")
BIL = "#34495e"
kasse(4.93, 10.7, 1.85, 6.78, 15.2, 2.55, BIL)             # karrosseri
kasse(5.08, 11.9, 2.55, 6.63, 14.4, 3.15, "#8fa7b8")       # kabine
for x in (4.88, 6.58):                                     # bilens hjul hænger frit under den løftede bil
    for yc in (11.65, 14.25):
        hjul(x, x + 0.25, yc, 1.75, 0.34)
etiket("Tosøjlet lift med bil", 5.85, 12.9, 3.8, True, dy=0.02)

# Person 1,8 m som målestok
kasse(6.45, 6.0, 0, 6.85, 6.25, 1.5, "#6d6d6d", "#444444", 0.3)
kasse(6.55, 6.03, 1.5, 6.75, 6.22, 1.8, "#d8b79a", "#444444", 0.3)

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
q = proj((5.4, YN, 2.1))
ax.annotate("Døre til de to lukkede rum:\nfoder, udstyr og værktøj med toilet (venstre), privat rum (højre)", xy=q, xytext=(q[0] + 0.02, q[1] + 0.045), fontsize=7, ha="center", va="center", zorder=5,
            arrowprops=dict(arrowstyle="-", lw=0.5), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#666666", lw=0.6))
q = proj((6.85, 6.0, 1.8))
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
fig.text(0.04, 0.062, f"Hal {B:.0f} × {L:.0f} m, sidehøjde {SIDE:.1f} m, kip {KIP:.1f} m, taghældning {HAELD:.0f}°. Grøn ramme om teksten = ejendommens drift. Blå ramme = privat. Blå gulvfelter = private zoner.".replace(".", ",", 2), fontsize=8)
fig.text(0.04, 0.040, "Perspektiv, ikke målfast. Nordgavlen med porten er skåret væk. Rammeafstand, profiler og åse er vejledende og fastlægges af leverandøren.", fontsize=7.5, color="#444444")
fig.text(0.04, 0.022, "Maskiner, trailere og bil er forenklede figurer efter ejers fotos med de anslåede mål fra halplanen. Lys, el, vinduer og lysplader er ikke vist. Gangdøren sidder i portgavlen til højre for porten (mod huset) og ses derfor ikke.", fontsize=7.5, color="#444444")
fig.savefig(HER / "hal_indvendig.pdf")
fig.savefig(HER / "hal_indvendig.png", dpi=160)
print("hal_indvendig.pdf/.png skrevet")
