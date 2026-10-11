#!/usr/bin/env python3
"""Tegner plan af tilbygningen sammen med det eksisterende hus i 1:100 (A3 liggende).

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
from nordpil import nordpil
from tegningshoved import tegningshoved

BYGNINGSDREJNING = 1.6   # planen følger bygningerne, som ligger ca. 1,6 grader drejet fra stik nord

HER = Path(__file__).parent
cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))

MAALESTOK = 100
A4 = (420, 297)   # A3 liggende
HUS_BREDDE = cfg["hus_ydermaal"]["bredde"]   # eksisterende hus nord-syd
HUS_LAENGDE = cfg["hus_ydermaal"]["laengde"]
HV = 0.35         # eksisterende ydervæg
B = cfg["tilbygning"]["bredde"]
L = HUS_BREDDE + cfg["tilbygning"]["forbi_husets_sydfacade"]
YV, GV, IV = 0.45, 0.15, 0.10   # ydervæg, væg garage/bolig, indervæg

# Rumdybder nord-syd, fra nord
GARAGE_D = 6.0
MIDT_D = 3.6
ix0, ix1 = YV, B        # indvendig østside ligger i husets vestgavl hele vejen, så bygningen er lige bred indvendigt
gx1 = B                               # langs det eksisterende hus bruges husets vestgavl som væg, så rummet går helt ud til den
iy0, iy1 = YV, L - YV
g_y0 = iy1 - GARAGE_D                 # garagens sydvæg (inderside)
m_y1 = g_y0 - GV                      # midterzonens nordside
m_y0 = m_y1 - MIDT_D
s_y1 = m_y0 - IV                      # soveværelsets nordside
# Midterzone vest -> øst: bad, walk-in og en smal gang (1,1 m) fra stuen til soveværelset
BAD_B, WALK_B = 3.0, 3.25
bad_x1 = ix0 + BAD_B
walk_x0 = bad_x1 + IV
walk_x1 = walk_x0 + WALK_B
gang_x0 = walk_x1 + IV

fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
felt = (20, 48, 380, 230)  # mm
ax = fig.add_axes([felt[0] / A4[0], felt[1] / A4[1], felt[2] / A4[0], felt[3] / A4[1]])
bm, hm = felt[2] * MAALESTOK / 1000, felt[3] * MAALESTOK / 1000
ax.set_xlim(-5.5, -5.5 + bm)
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


# Eksisterende hus mod øst, med rum efter mæglerens vejledende plantegning
hx0, hy0 = B, L - HUS_BREDDE
GRAA = "#8a8a8a"
ax.add_patch(Rectangle((hx0, hy0), HUS_LAENGDE, HUS_BREDDE, fc="#f4f4f4", ec="none", zorder=0))
for x_, y_, w_, h_ in ((hx0, hy0, HUS_LAENGDE, HV), (hx0, L - HV, HUS_LAENGDE, HV), (hx0 + HUS_LAENGDE - HV, hy0, HV, HUS_BREDDE), (hx0, hy0, HV, HUS_BREDDE)):
    ax.add_patch(Rectangle((x_, y_), w_, h_, fc=GRAA, ec="none", zorder=3))
for navn, rx, ry, rw, rh in cfg.get("hus_rum", {}).get("rum", []):
    ax.add_patch(Rectangle((hx0 + HV + rx, hy0 + HV + ry), rw, rh, fc="none", ec=GRAA, lw=1.0, zorder=2))
    ax.text(hx0 + HV + rx + rw / 2, hy0 + HV + ry + rh / 2, f"{navn}\n{rw:.2f} × {rh:.2f}".replace(".", ","), fontsize=6, ha="center", va="center", color="#555555", zorder=2)
um = hx0 + HUS_LAENGDE / 2
for liste, yv in (("hus_sydfacade", hy0), ("hus_nordfacade", L - HV)):
    for ab in cfg.get(liste, {}).get("aabninger", []):
        if ab.get("doer") or ab["z0"] < 0.3:
            aabning(um + ab["u0"], yv, ab["u1"] - ab["u0"], HV)
            ax.plot([um + ab["u0"], um + ab["u1"]], [yv + HV / 2] * 2, color="#1f6fb2" if not ab.get("doer") else "#666666", lw=1.2, zorder=5)
        else:
            vindue(um + ab["u0"], yv, ab["u1"] - ab["u0"], HV)
ax.text(hx0 + HUS_LAENGDE / 2, L + 0.5, f"Eksisterende hus, omkring {HUS_LAENGDE:.1f} × {HUS_BREDDE:.1f} m (BBR 123 m²)".replace(".", ","), fontsize=7.5, ha="center", color="#555555")

# Ydervægge
vaeg(0, 0, B + YV, YV)
vaeg(0, L - YV, B, YV)
vaeg(0, 0, YV, L)
vaeg(B, 0, YV, L - HUS_BREDDE)                 # ny østvæg syd for huset, uden på gavlens linje
ax.annotate("eksisterende vestgavl\nbruges som fælles væg", xy=(B + HV / 2, L - 4.6), xytext=(B - 2.3, L + 1.1), fontsize=6, ha="center", va="center", color="#b36b00",
            arrowprops=dict(arrowstyle="-", lw=0.5, color="#b36b00"), zorder=7)
# Indervægge
vaeg(ix0, g_y0 - GV, gx1 - ix0, GV)            # garage / bolig
vaeg(ix0, m_y0 - IV, ix1 - ix0, IV)            # midterzone / soveværelse
vaeg(bad_x1, m_y0, IV, MIDT_D)                 # bad / walk-in
vaeg(walk_x1, m_y0, IV, MIDT_D)                # walk-in / gang

# Garageporte i nordgavl (2 x 2,7 m)
PORT = 2.7
p1 = ix0 + 0.6
p2 = gx1 - 0.6 - PORT
for px in (p1, p2):
    aabning(px, L - YV, PORT, YV)
    ax.plot([px, px + PORT], [L - YV / 2, L - YV / 2], color="#cc0000", lw=1.5, zorder=5)
    ax.text(px + PORT / 2, L + 0.35, "port 2,7 m", fontsize=6, ha="center", color="#cc0000")

# Biler (SUV 4,9 x 2,0 m)
for px in (p1, p2):
    bx = px + (PORT - 2.0) / 2
    ax.add_patch(Rectangle((bx, iy1 - 0.5 - 4.9), 2.0, 4.9, fc="#f3f3f3", ec="#999999", lw=0.6, ls="--", zorder=2))
    ax.text(bx + 1.0, iy1 - 0.5 - 2.45, "SUV\n4,9 × 2,0", fontsize=6, ha="center", va="center", color="#777777")

# Varmtvandsbeholder med ventilation og varmegenvinding, frit i garagens sydvestlige hjørne (intet teknikrum)
ax.add_patch(Rectangle((ix0 + 0.1, g_y0 + 0.1), 0.9, 0.6, fc="#ffe0a3", ec="#b36b00", lw=0.7, zorder=5))
ax.annotate("Varmtvandsbeholder med\nventilation og varmegenvinding\n(ca. 0,9 × 0,6 m)", xy=(ix0 + 0.4, g_y0 + 0.4), xytext=(-2.9, g_y0 + 1.4),
            fontsize=6, ha="center", va="center", arrowprops=dict(arrowstyle="-", lw=0.5), zorder=7)

# Døre
D = 0.9
# stue (eksisterende hus) -> gang, gennem husets vestgavl; døren åbner ind i stuen, så gangen kan være smal
aabning(B, m_y1 - 0.95, HV, D)
doer(B + HV, m_y1 - 0.95, D, 0)
ax.text(B + 2.0, m_y1 - 0.45, "ny dør\ntil stue", fontsize=5.5, ha="center", va="center", color="#b36b00", zorder=7)
# garage -> bryggers (hvor bryggersets vindue sidder i dag)
bry_y = L - HV - 2.2
aabning(B, bry_y, HV, D)
doer(B + HV, bry_y, D, 0)
ax.text(B - 1.1, bry_y + 0.45, "ny dør til\nbryggers", fontsize=5.5, ha="center", va="center", color="#b36b00", zorder=7)
# gang -> soveværelse
aabning(gang_x0 + 0.1, m_y0 - IV, D, IV)
doer(gang_x0 + 0.1, m_y0 - IV, D, 270)
# soveværelse -> walk-in
aabning(walk_x0 + 1.1, m_y0 - IV, D, IV)
doer(walk_x0 + 1.1, m_y0, D, 0)
# soveværelse -> bad
aabning(ix0 + 1.0, m_y0 - IV, D, IV)
doer(ix0 + 1.0, m_y0, D, 0)

# Vinduer
vindue(2.5, 0, 3.0, YV)                          # soveværelse, terrassedør/vindue mod syd
VB = cfg["vindue_standard"]["bredde"]             # samme vindue som husets små vinduer
vindue(0, 1.0, YV, VB)                           # soveværelse mod vest
vindue(B, 1.6, YV, VB)                           # soveværelse mod øst
vindue(0, m_y0 + 1.3, YV, VB)                    # bad mod vest
ax.text(4.0, -0.35, "terrassedør / vindue 3,0 m mod syd", fontsize=6, ha="center", color="#1f6fb2")

# Rumtekster
g_areal = (gx1 - ix0) * GARAGE_D
gang_areal = (ix1 - gang_x0) * MIDT_D
rum((ix0 + gx1) / 2 + 0.4, g_y0 + 0.45, f"Garage (uopvarmet)  {g_areal:.0f} m²")
rum((ix0 + bad_x1) / 2, m_y0 + MIDT_D / 2 + 0.6, f"Bad/toilet\n{BAD_B * MIDT_D:.1f} m²")
rum((walk_x0 + walk_x1) / 2, m_y0 + MIDT_D / 2 + 0.3, f"Walk-in\n{WALK_B * MIDT_D:.1f} m²")
ax.text((gang_x0 + ix1) / 2, m_y0 + MIDT_D / 2 - 0.3, f"Gang {gang_areal:.1f} m²", fontsize=6.5, ha="center", va="center", rotation=90, zorder=6)
rum((ix0 + ix1) / 2 + 0.6, (iy0 + s_y1) / 2, f"Soveværelse\n{(ix1 - ix0) * (s_y1 - iy0):.1f} m²")
# Seng 1,8 x 2,1 som møbleringsforslag
ax.add_patch(Rectangle((ix0 + 0.1, iy0 + 1.6), 2.1, 1.8, fc="none", ec="#999999", lw=0.6, ls="--", zorder=2))
ax.text(ix0 + 1.15, iy0 + 2.5, "seng", fontsize=6, ha="center", va="center", color="#777777")

# Mål
maal((0, -1.0), (B + YV, -1.0), f"{B + YV:.2f} m udv. / {ix1 - ix0:.2f} m indv.".replace(".", ","), (0, -0.3))
maal((-0.9, 0), (-0.9, L), f"{L:.1f} m".replace(".", ","), (-0.35, -3.0), 90)
maal((B + YV + 0.6, 0), (B + YV + 0.6, L - HUS_BREDDE), f"{L - HUS_BREDDE:.1f} m forbi husets sydfacade".replace(".", ","), (0.35, 0), 90)
maal((ix0, g_y0 + 3.2), (gx1, g_y0 + 3.2), f"{gx1 - ix0:.2f} m indv.".replace(".", ","), (0, 0.25))

# Nordpil
nordpil(fig, 0.93, 0.89, vinkel=BYGNINGSDREJNING)

brutto = B * HUS_BREDDE + (B + YV) * (L - HUS_BREDDE)
opv = (B + YV) * (L - HUS_BREDDE) + B * (g_y0 - GV / 2 - (L - HUS_BREDDE))
fig.text(0.05, 0.125, "Tilbygning og eksisterende hus, plan, Nældevej 42, 9000 Aalborg", fontsize=12, weight="bold")
fig.text(0.05, 0.100, f"Målestok 1:{MAALESTOK} (A3)   ·   Tilbygning {L:.1f} m lang, {ix1 - ix0:.2f} m bred indvendigt, {brutto:.0f} m² brutto, heraf omkring {opv:.0f} m² opvarmet bolig".replace(".", ","), fontsize=8)
fig.text(0.05, 0.075, "FORELØBIG SKITSE. Det eksisterende hus er tegnet efter ejendomsmæglerens vejledende plantegning fra 2024 (ikke målfast) og skal måles op. Vægtykkelser i tilbygningen er antaget:", fontsize=7.5, color="red")
fig.text(0.05, 0.055, "ydervæg 45 cm, væg garage/bolig 15 cm, indervægge 10 cm. Brandadskillelse mellem garage og bolig (herunder døren til bryggerset) er ikke dimensioneret. Bryggersets vindue i vestgavlen forsvinder. Langs huset bruges husets eksisterende vestgavl som fælles væg.", fontsize=7.5, color="red")

tegningshoved(fig, "Hus med tilbygning, plan", "1 : 100 (A3)", "A2.1", x=0.66, y=0.004, b=0.32, h=0.044)
fig.savefig(HER / "tilbygning_plan.pdf")
fig.savefig(HER / "tilbygning_plan.png", dpi=200)
print(f"Tilbygning {L:.1f} m lang, {ix1 - ix0:.2f} m indv. bred, {brutto:.0f} m² brutto; garage {g_areal:.1f} m², sovev. {(ix1 - ix0) * (s_y1 - iy0):.1f} m², bad {BAD_B * MIDT_D:.1f}, walk-in {WALK_B * MIDT_D:.1f}, gang {gang_areal:.1f} ({ix1 - gang_x0:.2f} m bred); opvarmet brutto ca. {opv:.0f} m²")
