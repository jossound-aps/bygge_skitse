#!/usr/bin/env python3
"""Tegner situationsplan i 1:500 (A4) for Nældevej 42 ud fra data/grundkort.json og situationsplan.json.

Kør:  python3 tegninger/situationsplan.py
Giver: tegninger/situationsplan.pdf / .png          (stregtegning)
       tegninger/situationsplan_luftfoto.pdf / .png (samme, oven på luftfoto)
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

HER = Path(__file__).parent
MAALESTOK = 500
A4 = (210, 297)  # mm
FELT = (10, 32, 190, 255)  # tegnefelt: venstre, bund, bredde, højde i mm
CENTRUM = (-6.0, -20.0)  # midten af tegnefeltet i lokale meter

grund = json.loads((HER / "data/grundkort.json").read_text(encoding="utf-8"))
cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))


def bygning(osm_id):
    return next(b["punkter"] for b in grund["bygninger"] if b["osm_id"] == osm_id)


# Husets akser: u langs husets længste side (mod øst), v vinkelret (mod nord)
hus = bygning(cfg["hus_osm_id"])[:-1]
cx = sum(p[0] for p in hus) / len(hus)
cy = sum(p[1] for p in hus) / len(hus)
kanter = [(hus[i], hus[(i + 1) % len(hus)]) for i in range(len(hus))]
a, b = max(kanter, key=lambda k: math.dist(*k))
ux, uy = b[0] - a[0], b[1] - a[1]
n = math.hypot(ux, uy)
ux, uy = ux / n, uy / n
if ux < 0:
    ux, uy = -ux, -uy
vx, vy = -uy, ux


def xy(u, v):
    return (cx + u * ux + v * vx, cy + u * uy + v * vy)


def rekt(u0, v0, u1, v1):
    return [xy(u0, v0), xy(u1, v0), xy(u1, v1), xy(u0, v1)]


us = [(p[0] - cx) * ux + (p[1] - cy) * uy for p in hus]
vs = [(p[0] - cx) * vx + (p[1] - cy) * vy for p in hus]
tag_l, tag_b = max(us) - min(us), max(vs) - min(vs)
# Husets ydervægge (ejers mål), centreret i tagfladen fra kortdata
hus_l, hus_b = cfg["hus_ydermaal"]["laengde"], cfg["hus_ydermaal"]["bredde"]
hus_u0, hus_u1, hus_v0, hus_v1 = -hus_l / 2, hus_l / 2, -hus_b / 2, hus_b / 2

# Antaget skel, tilbygning og hal i husets akser
skel_u = -tag_l / 2 - cfg["skel"]["afstand_fra_husets_vestgavl"]
tb_b = cfg["tilbygning"]["bredde"]
tb = (hus_u0 - tb_b, hus_v0 - cfg["tilbygning"]["forbi_husets_sydfacade"], hus_u0, hus_v1)
tb_l = tb[3] - tb[1]
h = cfg["hal"]
hal_u0 = skel_u + h["afstand_til_skel"]
hal_u1 = hal_u0 + h["bredde"]
hal_v1 = tb[1] - h["afstand_til_tilbygning"]
hal_v0 = hal_v1 - h["laengde"]
skille_v = hal_v1 - h["rum_laengde"]
rum_m2 = h["bredde"] * h["rum_laengde"]
privat_m2 = rum_m2 + h["privat_i_aaben_hal_m2"]
drift_m2 = h["bredde"] * h["laengde"] - privat_m2


def maal(ax, p, q, tekst, forskyd=(0, 0), farve="black"):
    """Mållinje mellem to punkter med tekst på midten."""
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", color=farve, lw=0.6, shrinkA=0, shrinkB=0), zorder=6)
    mx, my = (p[0] + q[0]) / 2 + forskyd[0], (p[1] + q[1]) / 2 + forskyd[1]
    ax.text(mx, my, tekst, fontsize=6.5, color=farve, ha="center", va="center", zorder=7,
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))


def tegn(luftfoto):
    fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
    ax = fig.add_axes([FELT[0] / A4[0], FELT[1] / A4[1], FELT[2] / A4[0], FELT[3] / A4[1]])
    bm, hm = FELT[2] * MAALESTOK / 1000, FELT[3] * MAALESTOK / 1000
    ax.set_xlim(CENTRUM[0] - bm / 2, CENTRUM[0] + bm / 2)
    ax.set_ylim(CENTRUM[1] - hm / 2, CENTRUM[1] + hm / 2)
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])

    streg = "white" if luftfoto else "black"
    if luftfoto:
        lf = grund["luftfoto"]
        e, dy = lf["extent"], lf.get("forskydning_y", 0.0)
        ax.imshow(plt.imread(HER / "data" / lf["fil"]), extent=[e[0], e[1], e[2] + dy, e[3] + dy], zorder=0)
    else:
        for vej in grund["veje"]:
            ax.plot(*zip(*vej["punkter"]), color="#bbbbbb", lw=6, solid_capstyle="round", zorder=1)
            ax.text(ax.get_xlim()[0] + 12, ax.get_ylim()[1] - 15, vej["navn"], fontsize=7, color="#444444")

    # Eksisterende bygninger
    for b_ in grund["bygninger"]:
        if b_["osm_id"] == cfg["hus_osm_id"]:
            continue
        egen = b_["osm_id"] == cfg["stald_osm_id"]
        ax.add_patch(Polygon(b_["punkter"], closed=True, fc="#9a9a9a" if egen else "#dddddd",
                             ec=streg if luftfoto else "black", lw=0.8, alpha=0.9 if not luftfoto else 0.25, zorder=3))
    ax.add_patch(Polygon(rekt(hus_u0, hus_v0, hus_u1, hus_v1), closed=True, fc="#9a9a9a", ec=streg if luftfoto else "black",
                         lw=0.8, alpha=0.9 if not luftfoto else 0.25, zorder=3))
    ax.text(*xy(0, 0), f"Eksisterende hus\n{hus_l:.1f} × {hus_b:.1f} m = {hus_l * hus_b:.0f} m²", fontsize=6, ha="center", va="center", zorder=7)
    if "skur" in cfg:
        sk = cfg["skur"]["punkter"]
        ax.add_patch(Polygon(sk, closed=True, fc="#9a9a9a", ec=streg if luftfoto else "black", lw=0.8, alpha=0.9 if not luftfoto else 0.25, zorder=3))
        ax.text(sum(p[0] for p in sk) / len(sk), sum(p[1] for p in sk) / len(sk), "Skur", fontsize=6, ha="center", va="center", zorder=7)
    st = bygning(cfg["stald_osm_id"])
    ax.text(sum(p[0] for p in st[:-1]) / (len(st) - 1) + 1, max(p[1] for p in st) - 4, "Hestestald", fontsize=6, ha="center", zorder=7)

    # Antaget skel
    s0, s1 = xy(skel_u, hus_v1 + 45), xy(skel_u, hal_v0 - 30)
    ax.plot([s0[0], s1[0]], [s0[1], s1[1]], color="red", lw=1.0, ls=(0, (6, 3)), zorder=5)
    ax.text(*xy(skel_u - 1.5, hal_v0 - 12), f"ANTAGET skel mod matr.nr. {cfg['skel']['nabo_matrikel']}", fontsize=6.5, color="red",
            rotation=90 + math.degrees(math.atan2(uy, ux)), ha="center", va="center", zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))

    # Jordvarmeslanger (anslået zone)
    jv = cfg.get("jordvarme")
    if jv:
        zone = [xy(skel_u + d, v) for d, v in jv["vestkant"]] + [xy(skel_u + d, v) for d, v in reversed(jv["oestkant"])]
        ax.add_patch(Polygon(zone, closed=True, fc="none" if luftfoto else "#ffe9e9", ec="#d1007a", lw=0.9, ls="--", hatch="xx", alpha=0.9, zorder=2))
        if "oestligste_slange" in jv:
            sl = [xy(skel_u + d, v) for d, v in jv["oestligste_slange"]]
            ax.plot(*zip(*sl), color="#d1007a", lw=1.4, zorder=5)
        ax.text(*xy(skel_u + 20, hal_v0 - 9), "Jordvarme: gravet felt (skraveret)\nog østligste slange (linje), ± 2 m", fontsize=6, color="#d1007a", ha="center", va="center", zorder=7,
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=1))

    # Tilbygning
    ax.add_patch(Polygon(rekt(*tb), closed=True, fc="#ffd27f", ec="#b36b00", lw=1.2, hatch="///", zorder=4))
    ax.text(*xy((tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2), f"Tilbygning\n{tb_b:.1f} × {tb_l:.1f} m\n{tb_b * tb_l:.0f} m²", fontsize=6, ha="center", va="center", zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))

    # Hal med opdeling
    ax.add_patch(Polygon(rekt(hal_u0, skille_v, hal_u1, hal_v1), closed=True, fc="#9fc5e8", ec="#1f4e79", lw=1.2, zorder=4))
    ax.add_patch(Polygon(rekt(hal_u0, hal_v0, hal_u1, skille_v), closed=True, fc="#b6d7a8", ec="#1f4e79", lw=1.2, zorder=4))
    ax.text(*xy((hal_u0 + hal_u1) / 2, (skille_v + hal_v1) / 2), f"Rum {rum_m2:.0f} m²", fontsize=6, ha="center", va="center", zorder=7)
    ax.text(*xy((hal_u0 + hal_u1) / 2, (hal_v0 + skille_v) / 2), f"Åben hal\ndrift ca. {drift_m2:.0f} m²\nprivat ca. {h['privat_i_aaben_hal_m2']:.0f} m²", fontsize=6, ha="center", va="center", zorder=7)
    # Kip
    k0, k1 = xy((hal_u0 + hal_u1) / 2, hal_v0), xy((hal_u0 + hal_u1) / 2, hal_v1)
    ax.plot([k0[0], k1[0]], [k0[1], k1[1]], color="#1f4e79", lw=0.5, ls=":", zorder=5)
    # Åbninger: dør i nordgavl, port i sydgavl (drift), port i østlig langside (privat)
    um = (hal_u0 + hal_u1) / 2
    for (p, q), tekst, off in (
        ((xy(um - 0.5, hal_v1), xy(um + 0.5, hal_v1)), "dør", (0, 1.6)),
        ((xy(um - 2.0, hal_v0), xy(um + 2.0, hal_v0)), "port", (0, -1.8)),
    ):
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#cc0000", lw=2.5, solid_capstyle="butt", zorder=6)
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=5.5, color="#cc0000", ha="center", va="center", zorder=7,
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.6))

    # Mål
    mv = (hal_v0 + skille_v) / 2
    maal(ax, xy(skel_u, mv), xy(hal_u0, mv), f"{h['afstand_til_skel']:.1f} m", (-2.5, 2))
    maal(ax, xy(um, hal_v1), xy(um, tb[1]), f"{h['afstand_til_tilbygning']:.1f} m", (3.2, 0))
    maal(ax, xy(hal_u0, hal_v0 - 3.5), xy(hal_u1, hal_v0 - 3.5), f"{h['bredde']:.1f} m", (0, -1.6))
    maal(ax, xy(hal_u1 + 3, hal_v0), xy(hal_u1 + 3, hal_v1), f"{h['laengde']:.1f} m", (3.2, -7))
    maal(ax, xy(skel_u, hus_v1 + 2), xy(tb[0], hus_v1 + 2), f"{tb[0] - skel_u:.1f} m", (0, 1.6))
    maal(ax, xy(tb[0], tb[1] - 2), xy(tb[2], tb[1] - 2), f"{tb_b:.1f} m", (0, -1.6))
    maal(ax, xy(tb[2] + 2, tb[1]), xy(tb[2] + 2, hus_v0), f"{hus_v0 - tb[1]:.1f} m", (3.0, 0))

    # Nordpil og målestok
    x_n, y_n = ax.get_xlim()[1] - 8, ax.get_ylim()[1] - 16
    ax.annotate("N", xy=(x_n, y_n + 10), xytext=(x_n, y_n), ha="center", va="center", fontsize=9, color=streg,
                arrowprops=dict(arrowstyle="-|>", color=streg, lw=1.2), zorder=8)
    x_s, y_s = ax.get_xlim()[0] + 5, ax.get_ylim()[0] + 4
    for i in range(4):
        ax.add_patch(Polygon([(x_s + 5 * i, y_s), (x_s + 5 * i + 5, y_s), (x_s + 5 * i + 5, y_s + 1), (x_s + 5 * i, y_s + 1)],
                             closed=True, fc="black" if i % 2 == 0 else "white", ec="black", lw=0.5, zorder=8))
    ax.text(x_s, y_s + 2, "0", fontsize=6, ha="center", color=streg, zorder=8)
    ax.text(x_s + 20, y_s + 2, "20 m", fontsize=6, ha="center", color=streg, zorder=8)

    # Tegningshoved
    fig.text(0.05, 0.085, "Situationsplan, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
    fig.text(0.05, 0.065, f"Målestok 1:{MAALESTOK} (A4)   ·   Tilbygning til hus og ny hal {h['laengde']:.0f} × {h['bredde']:.0f} m", fontsize=8)
    fig.text(0.05, 0.045, "FORELØBIG SKITSE. Skel er antaget ud fra luftfoto og er ikke hentet fra matriklen. "
                          "Jordvarmezonen er anslået. Husets mål er ejers oplysning.", fontsize=7.5, color="red")
    fig.text(0.05, 0.028, "Bygningsomrids og vej: © OpenStreetMap-bidragydere (GeoDanmark)."
             + (" Luftfoto: Apple Kort, markør fjernet digitalt, kun arbejdskort." if luftfoto else ""), fontsize=6, color="#555555")

    navn = "situationsplan_luftfoto" if luftfoto else "situationsplan"
    fig.savefig(HER / f"{navn}.pdf")
    fig.savefig(HER / f"{navn}.png", dpi=200)
    plt.close(fig)


for lf in (False, True):
    tegn(lf)

print(f"Hus: {hus_l:.1f} x {hus_b:.1f} m (tagflade i kortdata {tag_l:.1f} x {tag_b:.1f} m)")
print(f"Tilbygning: {tb_b:.1f} x {tb_l:.1f} m = {tb_b * tb_l:.0f} m², {tb[0] - skel_u:.1f} m til antaget skel")
print(f"Hal: {h['laengde']:.0f} x {h['bredde']:.0f} m, rum {rum_m2:.0f} m², privat i alt ca. {privat_m2:.0f} m², drift ca. {drift_m2:.0f} m²")
