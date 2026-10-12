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
import numpy as np
from matplotlib.patches import Circle, Polygon
from nordpil import nordpil
from tegningshoved import tegningshoved

HER = Path(__file__).parent
MAALESTOK = 500
GRUS = "#d6d1c6"
A4 = (210, 297)  # mm
FELT = (10, 32, 190, 255)  # tegnefelt: venstre, bund, bredde, højde i mm
CENTRUM = (22.5, -20.0)  # midten af tegnefeltet i lokale meter

grund = json.loads((HER / "data/grundkort.json").read_text(encoding="utf-8"))
cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))


def bygning(osm_id):
    return next(b["punkter"] for b in grund["bygninger"] if b["osm_id"] == osm_id)


# Husets akser: u langs husets længste side (mod øst), v vinkelret (mod nord)
hus = bygning(cfg["hus_osm_id"])[:-1]
cx = sum(p[0] for p in hus) / len(hus)
cy = sum(p[1] for p in hus) / len(hus)
_st = bygning(cfg["stald_osm_id"])[:-1]            # aksen følger staldens længste side, så alt ligger parallelt med stalden
kanter = [(_st[i], _st[(i + 1) % len(_st)]) for i in range(len(_st))]
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
if "position" in h:
    hal_u0, hal_v1 = h["position"]["u_vest"], h["position"]["v_nord"]
else:
    hal_u0, hal_v1 = skel_u + h["afstand_til_skel"], tb[1] - h["afstand_til_tilbygning"]
hal_u1 = hal_u0 + h["bredde"]
hal_v0 = hal_v1 - h["laengde"]
PORT_NORD = h.get("port_mod") == "nord"


def bue_til_fold(um, pv, retning, kf):
    """Kørevej fra porten i en bue ind i fold 1: (midterlinje, [venstre kant, højre kant]) i u,v-koordinater. retning = +1, når porten vender mod nord."""
    R, s0, b = kf["radius"], kf["lige"], kf["bredde"] / 2
    pts = [(um, pv + retning * t) for t in np.linspace(0, s0, 3)]
    cu, cv = um + R, pv + retning * s0
    pts += [(cu - R * math.cos(a), cv + retning * R * math.sin(a)) for a in np.linspace(0, math.pi, 40)[1:]]
    pts += [(um + 2 * R, pv - retning * t) for t in np.linspace(0, kf["ind_i_fold"], 4)[1:]]
    kanter = ([], [])
    for i, (x, y) in enumerate(pts):
        x0, y0 = pts[max(i - 1, 0)]
        x1, y1 = pts[min(i + 1, len(pts) - 1)]
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / n, dx / n
        kanter[0].append((x + nx * b, y + ny * b))
        kanter[1].append((x - nx * b, y - ny * b))
    return pts, kanter


def afstand_til_linje(p, linje):
    """Korteste afstand fra punkt til en brudt linje (liste af punkter)."""
    bedst = 1e9
    for a_, b_ in zip(linje[:-1], linje[1:]):
        dx, dy = b_[0] - a_[0], b_[1] - a_[1]
        t = max(0.0, min(1.0, ((p[0] - a_[0]) * dx + (p[1] - a_[1]) * dy) / (dx * dx + dy * dy)))
        bedst = min(bedst, math.hypot(p[0] - a_[0] - t * dx, p[1] - a_[1] - t * dy))
    return bedst


SKEL = {s["navn"]: s for s in cfg.get("matrikelskel", {}).get("linjer", [])}
VESTSKEL = SKEL["1cc mod vest (nabo 1cb)"]["punkter"]
INTERNT = SKEL["1rp mod 1cc, vest"]["punkter"]
# det lukkede rum ligger i den ende, der vender væk fra porten
rum_v0, rum_v1 = (hal_v0, hal_v0 + h["rum_laengde"]) if PORT_NORD else (hal_v1 - h["rum_laengde"], hal_v1)
aab_v0, aab_v1 = (rum_v1, hal_v1) if PORT_NORD else (hal_v0, rum_v0)
rum_m2 = h["bredde"] * h["rum_laengde"]
privat_m2 = h.get("privat_rum_m2", rum_m2) + h["privat_i_aaben_hal_m2"]     # privat rum + private felter i den åbne hal
drift_m2 = h["bredde"] * h["laengde"] - privat_m2



def koerevej_linjer(port_xy, retning_xy):
    """Midterlinje og de to kanter for kørevejen: faste punkter fra json og en S-kurve (Bezier) ind til porten."""
    kv = cfg["koerevej"]
    pts = [tuple(p) for p in kv["punkter"]]
    p0, p3 = pts[-1], port_xy
    d0 = (pts[-1][0] - pts[-2][0], pts[-1][1] - pts[-2][1])
    n0 = math.hypot(*d0)
    l = math.dist(p0, p3) * 0.45
    p1 = (p0[0] + d0[0] / n0 * l, p0[1] + d0[1] / n0 * l)
    p2 = (p3[0] - retning_xy[0] * l, p3[1] - retning_xy[1] * l)
    for i in range(1, 25):
        s = i / 24
        pts.append(tuple((1 - s) ** 3 * a + 3 * (1 - s) ** 2 * s * b + 3 * (1 - s) * s ** 2 * c_ + s ** 3 * d
                         for a, b, c_, d in zip(p0, p1, p2, p3)))
    kanter = ([], [])
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]
        n = math.hypot(tx, ty)
        for k, sgn in zip(kanter, (1, -1)):
            k.append((p[0] - sgn * ty / n * kv["bredde"] / 2, p[1] + sgn * tx / n * kv["bredde"] / 2))
    # mindste krumningsradius på midterlinjen (til vurdering af, om en lastbil kan følge den)
    rmin = 1e9
    for a, b, c_ in zip(pts[:-2], pts[1:-1], pts[2:]):
        areal = abs((b[0] - a[0]) * (c_[1] - a[1]) - (c_[0] - a[0]) * (b[1] - a[1])) / 2
        if areal > 1e-9:
            rmin = min(rmin, math.dist(a, b) * math.dist(b, c_) * math.dist(a, c_) / (4 * areal))
    return pts, kanter, rmin


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
        bel = cfg.get("belaegning", {})
        for vej in grund["veje"]:          # grusvej i anslået bredde
            ax.plot(*zip(*vej["punkter"]), color=GRUS, lw=bel.get("vej_bredde", 4.0) * 1000 / MAALESTOK / 25.4 * 72, solid_capstyle="butt", zorder=0.9)
            ax.text(40, vej["punkter"][-1][1] + 0.1, vej["navn"] + " (grusvej)", fontsize=6.5, color="#444444", ha="center", va="center", zorder=7)
        for fl in bel.get("grus", []):
            ax.add_patch(Polygon(fl["punkter"], closed=True, fc=GRUS, ec="none", zorder=0.9))
            ax.text(*fl["label"], fl["navn"], fontsize=6, color="#555555", ha="center", va="center", zorder=7)
        if "parkering" in bel:
            ax.text(*bel["parkering"]["label"], bel["parkering"]["tekst"], fontsize=6, color="#555555", ha="center", va="center", zorder=7)

    # Læbælter og træer (eksisterende)
    lb = cfg.get("laebaelter", {})
    for baelte in lb.get("baelter", []):
        r = baelte["bredde"] / 2
        pts = baelte["linje"]
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            antal = max(1, round(math.hypot(x1 - x0, y1 - y0) / (1.6 * r)))
            for i in range(antal + 1):
                ax.add_patch(Circle((x0 + (x1 - x0) * i / antal, y0 + (y1 - y0) * i / antal), r, fc="none" if luftfoto else "#cfe6c4",
                                    ec="#d8ffd0" if luftfoto else "#4f8a3c", lw=0.5, alpha=0.9, zorder=1.5))
        mx, my = pts[len(pts) // 2] if len(pts) > 2 else ((pts[0][0] + pts[1][0]) / 2, (pts[0][1] + pts[1][1]) / 2)
        lodret = abs(pts[-1][1] - pts[0][1]) > abs(pts[-1][0] - pts[0][0])
        ax.text(mx, my + (30 if lodret else 0), baelte["navn"], fontsize=6, color="#2f6b1f", rotation=90 if lodret else 0, ha="center", va="center", zorder=7,
                bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.8))
    for tr in lb.get("enkelttraeer", []):
        ax.add_patch(Circle((tr["x"], tr["y"]), tr["radius"], fc="none" if luftfoto else "#cfe6c4", ec="#d8ffd0" if luftfoto else "#4f8a3c", lw=0.5, zorder=1.5))

    # Ridebane og hegn (eksisterende)
    if "ridebane" in cfg:
        rb = cfg["ridebane"]["punkter"]
        ax.add_patch(Polygon(rb, closed=True, fc="none" if luftfoto else "#efe6d2", ec=streg if luftfoto else "#8a7a55", lw=0.8, zorder=1))
        ax.text(sum(p[0] for p in rb) / len(rb), sum(p[1] for p in rb) / len(rb), "Ridebane", fontsize=7, ha="center", va="center", color=streg if luftfoto else "#5c5035", zorder=7)
    if "sandfold" in cfg:
        sf = cfg["sandfold"]["punkter"]
        ax.add_patch(Polygon(sf, closed=True, fc="none" if luftfoto else "#f3ecdc", ec="none", zorder=1))
        ax.text(sum(p[0] for p in sf) / len(sf), sum(p[1] for p in sf) / len(sf), "Sand-\nfold", fontsize=5.5, ha="center", va="center", color=streg if luftfoto else "#5c5035", zorder=7)
    for noegle, navn in (("moedding", None), ("mur", "Lav mur")):
        if noegle in cfg:
            md = cfg[noegle]["punkter"]
            ax.plot(*zip(*md), color=streg if luftfoto else "black", lw=1.2, zorder=3)
            if navn:
                ax.text(sum(p[0] for p in md) / len(md), sum(p[1] for p in md) / len(md), navn, fontsize=5.5, ha="center", va="center", color=streg, zorder=7)
    for linje in cfg.get("hegn", {}).get("linjer", []):
        el = linje["type"] == "el"
        ax.plot(*zip(*linje["punkter"]), color="#ffffff" if luftfoto else "#3a2a1a", lw=0.6 if el else 1.0, ls=(0, (4, 2)) if el else "-", marker="o", ms=1.4, zorder=2)
    if "hegn" in cfg and not luftfoto:
        ax.text(20.0, -36, "Elhegn (stiplet)", fontsize=6, color="#3a2a1a", rotation=90, ha="left", va="center", zorder=7)
    for fo in cfg.get("folde", []):
        ax.text(fo["x"], fo["y"], fo["navn"], fontsize=7, color=streg if luftfoto else "#5c5035", ha="center", va="center", zorder=7)
        ax.text(42, 11.0, "Bræddehegn om ridebane og sandfold", fontsize=6, color="#3a2a1a", ha="center", va="center", zorder=7)

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
        sd = cfg["skur"].get("doer")
        if sd:
            xs0, yn = min(p[0] for p in sk) + sd["afstand_fra_stald"], max(p[1] for p in sk)
            ax.plot([xs0, xs0 + sd["bredde"]], [yn, yn], color="#cc0000", lw=2.0, solid_capstyle="butt", zorder=6)
    st = bygning(cfg["stald_osm_id"])
    ax.text(sum(p[0] for p in st[:-1]) / (len(st) - 1) + 1, max(p[1] for p in st) - 4, "Hestestald", fontsize=6, ha="center", zorder=7)

    # Matrikelskel efter matriklen.dk: ydre skel og skel mellem egne matrikler, røde stiplede linjer
    for s in SKEL.values():
        ydre = s["type"] == "ydre"
        ax.plot(*zip(*s["punkter"]), color="red", lw=1.1 if ydre else 0.9, ls=(0, (6, 3)) if ydre else (0, (2, 2)), zorder=6.5)
    for e in cfg["matrikelskel"].get("etiketter", []):
        ax.text(*e["xy"], e["tekst"], fontsize=7.5, color="red", style="italic", weight="bold", ha="center", va="center", zorder=20, bbox=dict(fc="white", ec="red", lw=0.5, alpha=0.95, pad=2))
    ix = lambda y_: INTERNT[0][0] + (INTERNT[1][0] - INTERNT[0][0]) * (y_ - INTERNT[0][1]) / (INTERNT[1][1] - INTERNT[0][1])
    ax.text(ix(-42) + 1.2, -42, "skel mellem egne matrikler 1cc / 1rp", fontsize=5.5, color="red", rotation=-86, ha="center", va="center", zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.75, pad=1))

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
    ov = cfg["tilbygning"].get("oestvaeg_syd", 0.0)      # syd for huset står østvæggen uden på gavlens linje
    tb_omrids = [xy(tb[0], tb[1]), xy(tb[2] + ov, tb[1]), xy(tb[2] + ov, hus_v0), xy(tb[2], hus_v0), xy(tb[2], tb[3]), xy(tb[0], tb[3])]
    tb_areal = tb_b * hus_b + (tb_b + ov) * (hus_v0 - tb[1])
    ax.add_patch(Polygon(tb_omrids, closed=True, fc="#ffd27f", ec="#b36b00", lw=1.2, hatch="///", zorder=4))
    ax.text(*xy((tb[0] + tb[2]) / 2, (tb[1] + tb[3]) / 2), f"Tilbygning\n{tb_b:.1f} × {tb_l:.1f} m\n{tb_areal:.0f} m²", fontsize=6, ha="center", va="center", zorder=7,
            bbox=dict(fc="white", ec="none", alpha=0.8, pad=1))

    # Hal med opdeling
    ax.add_patch(Polygon(rekt(hal_u0, rum_v0, hal_u1, rum_v1), closed=True, fc="#9fc5e8", ec="#1f4e79", lw=1.2, zorder=4))
    ax.add_patch(Polygon(rekt(hal_u0, aab_v0, hal_u1, aab_v1), closed=True, fc="#b6d7a8", ec="#1f4e79", lw=1.2, zorder=4))
    ax.text(*xy((hal_u0 + hal_u1) / 2, (rum_v0 + rum_v1) / 2), f"Rum {rum_m2:.0f} m²", fontsize=6, ha="center", va="center", zorder=7)
    ax.text(*xy((hal_u0 + hal_u1) / 2, (aab_v0 + aab_v1) / 2), f"Hal i alt\ndrift ca. {drift_m2:.0f} m²\nprivat ca. {privat_m2:.0f} m²", fontsize=6, ha="center", va="center", zorder=7)
    # Kip
    k0, k1 = xy((hal_u0 + hal_u1) / 2, hal_v0), xy((hal_u0 + hal_u1) / 2, hal_v1)
    ax.plot([k0[0], k1[0]], [k0[1], k1[1]], color="#1f4e79", lw=0.5, ls=":", zorder=5)
    # Åbninger: dør i nordgavl, port i sydgavl (drift), port i østlig langside (privat)
    um = (hal_u0 + hal_u1) / 2
    for (p, q), tekst, off in (
        ((xy(hal_u0 + 0.6, hal_v1 if PORT_NORD else hal_v0), xy(hal_u0 + 1.5, hal_v1 if PORT_NORD else hal_v0)), "dør", (-2.2, 0.9 if PORT_NORD else -0.9)),
        ((xy(um - 2.0, hal_v1 if PORT_NORD else hal_v0), xy(um + 2.0, hal_v1 if PORT_NORD else hal_v0)), "port", (0, 1.8 if PORT_NORD else -1.8)),
    ):
        ax.plot([p[0], q[0]], [p[1], q[1]], color="#cc0000", lw=2.5, solid_capstyle="butt", zorder=6)
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=5.5, color="#cc0000", ha="center", va="center", zorder=7,
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.6))

    # Gangsti fra hus til hal
    if "gangsti" in cfg:
        gs = [xy(u_, v_) for u_, v_ in cfg["gangsti"]["punkter_uv"]]
        ax.plot(*zip(*gs), color="#fff3a0" if luftfoto else "#c9b98f", lw=cfg["gangsti"]["bredde"] * 1000 / MAALESTOK / 25.4 * 72, solid_capstyle="butt", solid_joinstyle="round", zorder=2.5)
        ax.text(gs[1][0] + 4.0, gs[1][1] + 0.9, "Gangsti", fontsize=5.5, ha="center", va="bottom", color="#fff3a0" if luftfoto else "#6b5f3f", zorder=7)

    # Kørevej for lastbil (kun streger)
    if "koerevej" in cfg:
        pv = hal_v1 if PORT_NORD else hal_v0
        ret = (-vx, -vy) if PORT_NORD else (vx, vy)          # kørselsretning ind ad porten
        _, kanter, rmin = koerevej_linjer(xy(um, pv), ret)
        for k in kanter:
            ax.plot(*zip(*k), color="#ffe24a" if luftfoto else "#444444", lw=0.9, ls=(0, (5, 2)), zorder=5)
        if "koerevej_fold" in cfg:                    # bue fra porten ind i fold 1 (traktor med vogn kan vende uden at komme på ridebanen)
            kf = cfg["koerevej_fold"]
            midt, kb = bue_til_fold(um, pv, 1 if PORT_NORD else -1, kf)
            for k in kb:
                ax.plot(*zip(*[xy(*p) for p in k]), color="#ffe24a" if luftfoto else "#444444", lw=0.9, ls=(0, (5, 2)), zorder=5)
            tx_, ty_ = xy(um + 2 * kf["radius"] + 2.2, pv - 3.5)
            ax.text(tx_, ty_, "Kørevej til\nfold 1 (bue)", fontsize=5.5, ha="left", va="center", color="#ffe24a" if luftfoto else "#444444", zorder=7)
            rb_syd = max(p[1] for p in cfg["ridebane"]["punkter"][-2:])
            print(f"Kørevej til fold: yderkant af buen når v = {max(p[1] for p in kb[0] + kb[1]):.1f} m; ridebanens sydkant ligger ved y ≈ {rb_syd:.1f} m")
        ax.text(kanter[0][1][0] + 2.3, kanter[0][1][1] - 3, "Eksisterende\nkørevej", fontsize=5.5, ha="left", va="center",
                color="#ffe24a" if luftfoto else "#444444", zorder=7)

    # Fliseplads foran hallens port i gulvhøjde, med rampe ned til terræn
    fp = h.get("forplads")
    if fp and PORT_NORD:
        vb, su = hal_v1 + fp["rampe_laengde"], fp["side_udfald"]
        ax.add_patch(Polygon([xy(hal_u0 - su, hal_v1), xy(hal_u0 + h["bredde"] + su, hal_v1), xy(hal_u0 + h["bredde"], vb), xy(hal_u0, vb)], closed=True,
                             fc="none" if luftfoto else "#e3dfd2", ec="#fff3a0" if luftfoto else "#7a7466", lw=0.6, hatch="++", zorder=2.2))
        tx_, ty_ = xy(hal_u0 - su - 0.4, (hal_v1 + vb) / 2)
        ax.text(tx_, ty_ + 1.2, "Fliserampe\n50 × 50", fontsize=5.2, ha="right", va="center", color="#fff3a0" if luftfoto else "#5a5446", zorder=7)

    # Tagvand fra hallen til ridebanens eksisterende omfangsdræn og pumpebrønd
    if "tagvand" in cfg and "ridebane" in cfg:
        bl = "#7fd0ff" if luftfoto else "#1f6fb5"
        rb = cfg["ridebane"]["punkter"]
        (sx0, sy0), (sx1, sy1) = rb[-1], rb[-2]                      # ridebanens sydkant, fra vest mod øst
        for u_ in (hal_u0, hal_u0 + h["bredde"]):
            px, py = xy(u_, hal_v1)
            ax.plot([px, px], [py, sy0 + (sy1 - sy0) * (px - sx0) / (sx1 - sx0)], color=bl, lw=1.0, ls=(0, (2, 1.5)), zorder=6)
        mx_, my_ = xy(hal_u0 + h["bredde"], hal_v1)
        ax.text(mx_ + 0.8, my_ + 1.6, "Tagvand til\nridebanens dræn", fontsize=5.5, color=bl, ha="left", va="center", zorder=7)
        ppx, ppy = cfg["tagvand"]["pumpe"]
        ax.plot([ppx], [ppy], marker="s", ms=4, color=bl, mec="black", mew=0.4, zorder=8)
        ax.text(ppx + 1.2, ppy + 0.3, "Pumpebrønd\n(eksist.)", fontsize=5.5, color=bl, ha="left", va="center", zorder=7)

    # Mål
    if "position" in h:      # afstande til nærmeste bygninger (brandafstand) og til ridebanens hegn
        maal(ax, xy(hus_u1, hal_v1 - 1.5), xy(hal_u0, hal_v1 - 1.5), f"{hal_u0 - hus_u1:.1f} m til huset", (0, -1.6))
        if "skur" in cfg:
            sk_o = max((p[0] - cx) * ux + (p[1] - cy) * uy for p in cfg["skur"]["punkter"])
            sk_s = min((p[0] - cx) * vx + (p[1] - cy) * vy for p in cfg["skur"]["punkter"])
            afst = math.hypot(max(0.0, hal_u0 - sk_o), max(0.0, sk_s - hal_v1))
            maal(ax, xy(sk_o, sk_s), xy(hal_u0, hal_v1), f"{afst:.1f} m til skuret", (-6.5, 0.8))
    else:
        mv = (aab_v0 + aab_v1) / 2
        maal(ax, xy(skel_u, mv), xy(hal_u0, mv), f"{afstand_til_linje(xy(hal_u0, mv), VESTSKEL):.1f} m til skel", (-2.5, 2))
        maal(ax, xy(um, hal_v1), xy(um, tb[1]), f"{h['afstand_til_tilbygning']:.1f} m", (3.2, 0))
    maal(ax, xy(hal_u0, hal_v0 - 3.5), xy(hal_u1, hal_v0 - 3.5), f"{h['bredde']:.1f} m", (0, -1.6))
    maal(ax, xy(hal_u1 + 3, hal_v0), xy(hal_u1 + 3, hal_v1), f"{h['laengde']:.1f} m", (3.2, -7))
    tb_sv = xy(tb[0], tb[1])                         # tilbygningens sydvestlige hjørne er nærmest vestskellet
    vs_x = VESTSKEL[0][0] + (VESTSKEL[1][0] - VESTSKEL[0][0]) * (tb_sv[1] - VESTSKEL[0][1]) / (VESTSKEL[1][1] - VESTSKEL[0][1])
    maal(ax, (vs_x, tb_sv[1]), tb_sv, f"{afstand_til_linje(tb_sv, VESTSKEL):.1f} m til skel", (0, -1.4))
    maal(ax, xy(tb[0], tb[1] - 2), xy(tb[2], tb[1] - 2), f"{tb_b:.1f} m", (0, -1.6))
    maal(ax, xy(tb[2] + 2, tb[1]), xy(tb[2] + 2, hus_v0), f"{hus_v0 - tb[1]:.1f} m", (3.0, 0))

    # Nordpil og målestok
    nordpil(fig, 0.905, 0.925, vinkel=grund.get("drejning_grader", 0.0))
    x_s, y_s = ax.get_xlim()[0] + 5, ax.get_ylim()[0] + 4
    for i in range(4):
        ax.add_patch(Polygon([(x_s + 5 * i, y_s), (x_s + 5 * i + 5, y_s), (x_s + 5 * i + 5, y_s + 1), (x_s + 5 * i, y_s + 1)],
                             closed=True, fc="black" if i % 2 == 0 else "white", ec="black", lw=0.5, zorder=8))
    ax.text(x_s, y_s + 2, "0", fontsize=6, ha="center", color=streg, zorder=8)
    ax.text(x_s + 20, y_s + 2, "20 m", fontsize=6, ha="center", color=streg, zorder=8)

    # Tegningshoved
    fig.text(0.05, 0.085, "Situationsplan, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
    fig.text(0.05, 0.065, f"Målestok 1:{MAALESTOK} (A4)   ·   Tilbygning til hus og ny hal {h['laengde']:.0f} × {h['bredde']:.0f} m", fontsize=8)
    fig.text(0.05, 0.047, "Matrikelskel (rødt) er tegnet efter matriklen.dk, ca. ± 1 m, og er ikke indmålt.", fontsize=7, color="#444444")
    fig.text(0.05, 0.034, "Jordvarmezonen er anslået. Husets mål følger ejendomsmæglerens plan (2024).", fontsize=7, color="#444444")
    fig.text(0.05, 0.016, "Bygningsomrids og vej: © OpenStreetMap-bidragydere (GeoDanmark)."
             + (" Luftfoto: Apple Kort, kun arbejdskort." if luftfoto else ""), fontsize=5.5, color="#555555")
    tegningshoved(fig, "Situationsplan", f"1 : {MAALESTOK} (A4)", "A0.1", x=0.56, y=0.012, b=0.41, h=0.062)

    navn = "situationsplan_luftfoto" if luftfoto else "situationsplan"
    fig.savefig(HER / f"{navn}.pdf")
    fig.savefig(HER / f"{navn}.png", dpi=200)
    plt.close(fig)


for lf in (False, True):
    tegn(lf)

print(f"Hus: {hus_l:.1f} x {hus_b:.1f} m (tagflade i kortdata {tag_l:.1f} x {tag_b:.1f} m)")
print(f"Tilbygning: {tb_b:.1f} x {tb_l:.1f} m = {tb_b * tb_l:.0f} m², {afstand_til_linje(xy(tb[0], tb[1]), VESTSKEL):.1f} m til vestskel (matriklen.dk, +/- 1 m)")
_hj = {"NV": xy(hal_u0, hal_v1), "NØ": xy(hal_u1, hal_v1), "SØ": xy(hal_u1, hal_v0), "SV": xy(hal_u0, hal_v0)}
print("Hal, afstand fra hjørner til skel 1cc/1rp:", {k_: round(afstand_til_linje(p_, INTERNT), 1) for k_, p_ in _hj.items()}, "(skellet går gennem hallen, hvis NV/SV og NØ/SØ ligger på hver sin side)")
if "koerevej" in cfg:
    print(f"Kørevej: mindste radius på midterlinjen {koerevej_linjer(xy((hal_u0 + hal_u1) / 2, hal_v1 if PORT_NORD else hal_v0), (-vx, -vy) if PORT_NORD else (vx, vy))[2]:.1f} m")
print(f"Hal: {h['laengde']:.0f} x {h['bredde']:.0f} m, rum {rum_m2:.0f} m², privat i alt ca. {privat_m2:.0f} m², drift ca. {drift_m2:.0f} m²")
