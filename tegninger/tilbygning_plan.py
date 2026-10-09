#!/usr/bin/env python3
"""Tegner plan af tilbygningen i 1:100 (A4).

Kør:  python3 tegninger/tilbygning_plan.py
Giver: tegninger/tilbygning_plan.pdf / .png

Koordinater i meter: x fra tilbygningens vestfacade mod øst, y fra sydgavlen mod nord.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Rectangle

HER = Path(__file__).parent
cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))

MAALESTOK = 100
A4 = (210, 297)
HUS_BREDDE = cfg["hus_ydermaal"]["bredde"]   # eksisterende hus nord-syd
B = cfg["tilbygning"]["bredde"]
L = HUS_BREDDE + cfg["tilbygning"]["forbi_husets_sydfacade"]
YV, GV, IV = 0.45, 0.15, 0.10   # ydervæg, væg garage/bolig, indervæg

# Rumdybder nord-syd, fra nord
GARAGE_D = 6.2
MIDT_D = 3.6
ix0, ix1 = YV, B - YV
iy0, iy1 = YV, L - YV
g_y0 = iy1 - GARAGE_D                 # garagens sydvæg (inderside)
m_y1 = g_y0 - GV                      # midterzonens nordside
m_y0 = m_y1 - MIDT_D
s_y1 = m_y0 - IV                      # soveværelsets nordside
# Midterzone vest -> øst: bad, walk-in, gang
BAD_B, WALK_B = 2.5, 2.4
bad_x1 = ix0 + BAD_B
walk_x0 = bad_x1 + IV
walk_x1 = walk_x0 + WALK_B
gang_x0 = walk_x1 + IV

fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
felt = (15, 40, 180, 240)  # mm
ax = fig.add_axes([felt[0] / A4[0], felt[1] / A4[1], felt[2] / A4[0], felt[3] / A4[1]])
bm, hm = felt[2] * MAALESTOK / 1000, felt[3] * MAALESTOK / 1000
ax.set_xlim(B / 2 - bm / 2 + 1.5, B / 2 + bm / 2 + 1.5)
ax.set_ylim(L / 2 - hm / 2, L / 2 + hm / 2)
ax.set_aspect("equal")
ax.axis("off")

VAEG = "#333333"


def vaeg(x, y, w, h):
    ax.add_patch(Rectangle((x, y), w, h, fc=VAEG, ec="none", zorder=3))


def aabning(x, y, w, h, farve="white"):
    ax.add_patch(Rectangle((x, y), w, h, fc=farve, ec="none", zorder=4))


def doer(hx, hy, bredde, start):
    """Dør med slagbue: hængsel i (hx, hy), start = vinkel for lukket dørblad."""
    ax.add_patch(Arc((hx, hy), 2 * bredde, 2 * bredde, angle=0, theta1=start, theta2=start + 90, color="#666666", lw=0.5, zorder=5))


def vindue(x, y, w, h):
    aabning(x, y, w, h)
    ax.add_patch(Rectangle((x, y), w, h, fc="#bfe3ff", ec="#1f6fb2", lw=0.8, zorder=5))


def rum(x, y, tekst):
    ax.text(x, y, tekst, fontsize=7, ha="center", va="center", zorder=6)


def maal(p, q, tekst, off=(0, 0), rot=0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0), zorder=6)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=6.5, ha="center", va="center", rotation=rot)


# Eksisterende hus mod øst (vist som udsnit)
ax.add_patch(Rectangle((B, L - HUS_BREDDE), 4.5, HUS_BREDDE, fc="#eeeeee", ec="#888888", lw=0.8, hatch="..", zorder=1))
ax.text(B + 2.3, L - HUS_BREDDE / 2, "Eksisterende\nhus", fontsize=7, ha="center", va="center", color="#555555", zorder=2)

# Ydervægge
vaeg(0, 0, B, YV)
vaeg(0, L - YV, B, YV)
vaeg(0, 0, YV, L)
vaeg(B - YV, 0, YV, L)
# Indervægge
vaeg(ix0, g_y0 - GV, ix1 - ix0, GV)            # garage / bolig
vaeg(ix0, m_y0 - IV, ix1 - ix0, IV)            # midterzone / soveværelse
vaeg(bad_x1, m_y0, IV, MIDT_D)                 # bad / walk-in
vaeg(walk_x1, m_y0, IV, MIDT_D)                # walk-in / gang

# Garageporte i nordgavl (2 x 2,7 m)
PORT = 2.7
p1 = ix0 + 0.6
p2 = ix1 - 0.6 - PORT
for px in (p1, p2):
    aabning(px, L - YV, PORT, YV)
    ax.plot([px, px + PORT], [L - YV / 2, L - YV / 2], color="#cc0000", lw=1.5, zorder=5)
    ax.text(px + PORT / 2, L + 0.35, "port 2,7 m", fontsize=6, ha="center", color="#cc0000")

# Biler (SUV 4,9 x 2,0 m)
for px in (p1, p2):
    bx = px + (PORT - 2.0) / 2
    ax.add_patch(Rectangle((bx, iy1 - 0.5 - 4.9), 2.0, 4.9, fc="#f3f3f3", ec="#999999", lw=0.6, ls="--", zorder=2))
    ax.text(bx + 1.0, iy1 - 0.5 - 2.45, "SUV\n4,9 × 2,0", fontsize=6, ha="center", va="center", color="#777777")

# Teknikrum i garagens sydvestlige hjørne, op mod badet
T_B, T_D = 0.85, 1.25
vaeg(ix0, g_y0 + T_D, T_B + IV, IV)
vaeg(ix0 + T_B, g_y0, IV, T_D)
aabning(ix0 + T_B, g_y0 + 0.15, IV, 0.7)
ax.add_patch(Rectangle((ix0 + 0.1, g_y0 + 0.1), 0.6, 0.9, fc="#ffe0a3", ec="#b36b00", lw=0.7, zorder=5))
ax.annotate("Teknik: varmtvandsbeholder\nmed ventilation og\nvarmegenvinding\n(ca. 0,9 × 0,6 m)", xy=(ix0 + 0.4, g_y0 + 0.55), xytext=(-2.6, g_y0 + 1.6),
            fontsize=6, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.5), zorder=7)

# Døre
D = 0.9
# garage -> gang
aabning(gang_x0 + 0.5, g_y0 - GV, D, GV)
doer(gang_x0 + 0.5, g_y0 - GV, D, 270)
# gang -> eksisterende hus (i østvæggen)
aabning(B - YV, m_y1 - 1.0, YV, D)
doer(B - YV, m_y1 - 1.0, D, 90)
# gang -> soveværelse
aabning(gang_x0 + 0.5, m_y0 - IV, D, IV)
doer(gang_x0 + 0.5, m_y0 - IV, D, 270)
# soveværelse -> walk-in
aabning(walk_x0 + 0.75, m_y0 - IV, D, IV)
doer(walk_x0 + 0.75, m_y0, D, 0)
# soveværelse -> bad
aabning(ix0 + 0.8, m_y0 - IV, D, IV)
doer(ix0 + 0.8, m_y0, D, 0)

# Vinduer
vindue(2.5, 0, 3.0, YV)                          # soveværelse, terrassedør/vindue mod syd
vindue(0, 0.9, YV, 1.2)                          # soveværelse mod vest
vindue(0, m_y0 + 1.4, YV, 0.8)                   # bad mod vest
ax.text(4.0, -0.35, "terrassedør / vindue 3,0 m mod syd", fontsize=6, ha="center", color="#1f6fb2")

# Rumtekster
g_areal = (ix1 - ix0) * GARAGE_D - (T_B + IV) * (T_D + IV)
rum((ix0 + ix1) / 2 + 0.6, g_y0 + 0.45, f"Garage (uopvarmet)  {g_areal:.0f} m²")
rum((ix0 + bad_x1) / 2, m_y0 + MIDT_D / 2 + 0.6, f"Bad/toilet\n{BAD_B * MIDT_D:.1f} m²")
rum((walk_x0 + walk_x1) / 2, m_y0 + MIDT_D / 2, f"Walk-in\n{WALK_B * MIDT_D:.1f} m²")
rum((gang_x0 + ix1) / 2, m_y0 + MIDT_D / 2 - 0.5, f"Gang\n{(ix1 - gang_x0) * MIDT_D:.1f} m²")
rum((ix0 + ix1) / 2, (iy0 + s_y1) / 2, f"Soveværelse\n{(ix1 - ix0) * (s_y1 - iy0):.1f} m²")
# Seng 1,8 x 2,1 som møbleringsforslag
ax.add_patch(Rectangle((ix0 + 0.1, iy0 + 1.6), 2.1, 1.8, fc="none", ec="#999999", lw=0.6, ls="--", zorder=2))
ax.text(ix0 + 1.15, iy0 + 2.5, "seng", fontsize=6, ha="center", va="center", color="#777777")

# Mål
maal((0, -1.0), (B, -1.0), f"{B:.1f} m".replace(".", ","), (0, -0.3))
maal((-0.9, 0), (-0.9, L), f"{L:.1f} m".replace(".", ","), (-0.35, -3.0), 90)
maal((B + 0.6, 0), (B + 0.6, L - HUS_BREDDE), f"{L - HUS_BREDDE:.1f} m forbi husets sydfacade".replace(".", ","), (0.35, 0), 90)
maal((ix0, g_y0 + 3.2), (ix1, g_y0 + 3.2), f"{ix1 - ix0:.2f} m indv.".replace(".", ","), (0, 0.25))

# Nordpil
ax.annotate("N", xy=(B + 4.0, 3.0), xytext=(B + 4.0, 1.2), ha="center", va="center", fontsize=9, arrowprops=dict(arrowstyle="-|>", lw=1.2))

opv = B * (g_y0 - GV / 2)
fig.text(0.07, 0.115, "Tilbygning, plan, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
fig.text(0.07, 0.095, f"Målestok 1:{MAALESTOK} (A4)   ·   Udvendigt {B:.1f} × {L:.1f} m = {B * L:.0f} m² brutto, heraf omkring {opv:.0f} m² opvarmet bolig".replace(".", ","), fontsize=8)
fig.text(0.07, 0.075, "FORELØBIG SKITSE. Husets bredde på 8 m er ejers oplysning og skal måles op. Vægtykkelser er antaget:", fontsize=7, color="red")
fig.text(0.07, 0.060, "ydervæg 45 cm, væg garage/bolig 15 cm, indervægge 10 cm. Brandadskillelse mellem garage og bolig er ikke dimensioneret.", fontsize=7, color="red")

fig.savefig(HER / "tilbygning_plan.pdf")
fig.savefig(HER / "tilbygning_plan.png", dpi=200)
print(f"Tilbygning {B} x {L:.1f} m = {B * L:.0f} m²; garage {g_areal:.1f} m², sovev. {(ix1 - ix0) * (s_y1 - iy0):.1f} m², bad {BAD_B * MIDT_D:.1f}, walk-in {WALK_B * MIDT_D:.1f}, gang {(ix1 - gang_x0) * MIDT_D:.1f}; opvarmet brutto ca. {opv:.0f} m²")
