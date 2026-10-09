#!/usr/bin/env python3
"""Tegner rumlige skitser (parallelprojektion) af hus, tilbygning, stald og hal set fra de fire hjørner.

Kør:  python3 tegninger/isometri.py
Giver: tegninger/isometri.pdf / .png              (alle fire på ét A3-ark)
       tegninger/isometri_sydoest.png, _sydvest.png, _nordvest.png, _nordoest.png

Koordinater i husets akser som i situationsplan.py: u mod øst, v mod nord, z op, origo i husets midte.
Højder og taghældninger for de eksisterende bygninger er antaget (se HOEJDER).
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
grund = json.loads((HER / "data/grundkort.json").read_text(encoding="utf-8"))
cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))

HOEJDER = {
    "hus_tagfod": 2.7, "hus_haeldning": 30.0,       # antaget; tilbygningen følger huset
    "stald_tagfod": 2.6, "stald_haeldning": 25.0,   # antaget
    "hal_side": 4.0, "hal_haeldning": 30.0, "hal_sokkel": 0.3,
}
ELEV = math.radians(24)
# kameraets kompasretning set fra grunden (grader fra nord, med uret); drejet lidt mod syd/nord, så gavlene ses
VISNINGER = [("sydøst", "sydoest", 142), ("sydvest", "sydvest", 218), ("nordvest", "nordvest", 322), ("nordøst", "nordoest", 38)]

SORT, SORT_TAG, SOKKEL, PORTFARVE = "#17181a", "#26282b", "#b9b9b4", "#4a4e54"
HUSVAEG, HUSTAG, STALD, STALDTAG = "#ece8df", "#3a3d42", "#c9c9c9", "#8d8f93"
NYVAEG, NYKANT, GLAS = "#f7e3bd", "#b36b00", "#9cc7e8"   # tilbygningens vægge fremhævet


# --- Geometri fra situationsplanens data ---
def bygning(osm_id):
    return next(b["punkter"] for b in grund["bygninger"] if b["osm_id"] == osm_id)


hus = bygning(cfg["hus_osm_id"])[:-1]
cx, cy = sum(p[0] for p in hus) / len(hus), sum(p[1] for p in hus) / len(hus)
a, b = max(((hus[i], hus[(i + 1) % len(hus)]) for i in range(len(hus))), key=lambda k: math.dist(*k))
ux, uy = b[0] - a[0], b[1] - a[1]
n = math.hypot(ux, uy)
ux, uy = (ux / n, uy / n) if ux > 0 else (-ux / n, -uy / n)


def uv(p):
    return ((p[0] - cx) * ux + (p[1] - cy) * uy, -(p[0] - cx) * uy + (p[1] - cy) * ux)


tag_l = max(uv(p)[0] for p in hus) - min(uv(p)[0] for p in hus)
HL, HB = cfg["hus_ydermaal"]["laengde"], cfg["hus_ydermaal"]["bredde"]
TB = cfg["tilbygning"]["bredde"]
tb_v0 = -HB / 2 - cfg["tilbygning"]["forbi_husets_sydfacade"]
h = cfg["hal"]
skel_u = -tag_l / 2 - cfg["skel"]["afstand_fra_husets_vestgavl"]
hal_u0 = skel_u + h["afstand_til_skel"]
hal_u1 = hal_u0 + h["bredde"]
hal_v1 = tb_v0 - h["afstand_til_tilbygning"]
hal_v0 = hal_v1 - h["laengde"]
stald = [uv(p) for p in bygning(cfg["stald_osm_id"])[:-1]]
G = (-29, -57, 13, 31)   # terrænudsnit u0, v0, u1, v1

S, N, W, E = (0, -1, 0), (0, 1, 0), (-1, 0, 0), (1, 0, 0)


def scene():
    """Returnerer alle flader (punkter, udadrettet normal, farver, påsatte åbninger og linjer) samt etiketter."""
    fl = []

    def flade(pts, normal, fyld, kant="#555555", lw=0.5):
        fl.append({"pts": pts, "n": normal, "fyld": fyld, "kant": kant, "lw": lw, "paa": [], "linjer": []})
        return fl[-1]

    def sadeltag(u0, v0, u1, v1, tagfod, haeld, kip_langs, vaeg, tag, sokkel=0.0, kant="#555555", lw=0.5, udelad=""):
        """Bygning med sadeltag; kip_langs 'u' = kip øst-vest, 'v' = kip nord-syd. Returnerer (kiphøjde, vægge)."""
        t, s, c = math.tan(math.radians(haeld)), math.sin(math.radians(haeld)), math.cos(math.radians(haeld))
        z0, v = sokkel, {}
        if kip_langs == "v":
            um, kip = (u0 + u1) / 2, tagfod + (u1 - u0) / 2 * t
            v["S"] = [(u0, v0, z0), (u1, v0, z0), (u1, v0, tagfod), (um, v0, kip), (u0, v0, tagfod)]
            v["N"] = [(u0, v1, z0), (u1, v1, z0), (u1, v1, tagfod), (um, v1, kip), (u0, v1, tagfod)]
            v["W"] = [(u0, v0, z0), (u0, v1, z0), (u0, v1, tagfod), (u0, v0, tagfod)]
            v["E"] = [(u1, v0, z0), (u1, v1, z0), (u1, v1, tagfod), (u1, v0, tagfod)]
            tage = [([(u1, v0, tagfod), (u1, v1, tagfod), (um, v1, kip), (um, v0, kip)], (s, 0, c)),
                    ([(u0, v0, tagfod), (u0, v1, tagfod), (um, v1, kip), (um, v0, kip)], (-s, 0, c))]
        else:
            vm, kip = (v0 + v1) / 2, tagfod + (v1 - v0) / 2 * t
            v["W"] = [(u0, v0, z0), (u0, v1, z0), (u0, v1, tagfod), (u0, vm, kip), (u0, v0, tagfod)]
            v["E"] = [(u1, v0, z0), (u1, v1, z0), (u1, v1, tagfod), (u1, vm, kip), (u1, v0, tagfod)]
            v["S"] = [(u0, v0, z0), (u1, v0, z0), (u1, v0, tagfod), (u0, v0, tagfod)]
            v["N"] = [(u0, v1, z0), (u1, v1, z0), (u1, v1, tagfod), (u0, v1, tagfod)]
            tage = [([(u0, v0, tagfod), (u1, v0, tagfod), (u1, vm, kip), (u0, vm, kip)], (0, -s, c)),
                    ([(u0, v1, tagfod), (u1, v1, tagfod), (u1, vm, kip), (u0, vm, kip)], (0, s, c))]
        ud = {}
        for k, nrm in (("S", S), ("N", N), ("W", W), ("E", E)):
            if k not in udelad:
                ud[k] = flade(v[k], nrm, vaeg, kant, lw)
                if sokkel:
                    a_, b_ = v[k][0], v[k][1]
                    flade([(a_[0], a_[1], 0), (b_[0], b_[1], 0), (b_[0], b_[1], sokkel), (a_[0], a_[1], sokkel)], nrm, SOKKEL, kant, lw)
        for pts, nrm in tage:
            flade(pts, nrm, tag, kant, lw)
        return kip, ud

    # Stald (eksisterende): hovedlænge øst-vest og sydfløj nord-syd
    hoved = [p for p in stald if p[1] > 15]
    floej = [p for p in stald if p[1] <= 15]
    skil_v = min(p[1] for p in hoved)
    sadeltag(min(p[0] for p in hoved), skil_v, max(p[0] for p in hoved), max(p[1] for p in hoved),
             HOEJDER["stald_tagfod"], HOEJDER["stald_haeldning"], "u", STALD, STALDTAG)
    sadeltag(min(p[0] for p in floej), min(p[1] for p in floej), max(p[0] for p in floej), skil_v,
             HOEJDER["stald_tagfod"], HOEJDER["stald_haeldning"], "v", STALD, STALDTAG, udelad="N")

    # Eksisterende hus (kip øst-vest) og tilbygning (fløj med kip nord-syd, samme tagfod, hældning og bredde)
    e = HOEJDER["hus_tagfod"]
    t, s, c = (f(math.radians(HOEJDER["hus_haeldning"])) for f in (math.tan, math.sin, math.cos))
    kip = e + HB / 2 * t
    hu0, hu1, hv0, hv1 = -HL / 2, HL / 2, -HB / 2, HB / 2
    tu0, tu1, tum = hu0 - TB, hu0, hu0 - TB / 2
    flade([(hu0, hv0, 0), (hu1, hv0, 0), (hu1, hv0, e), (hu0, hv0, e)], S, HUSVAEG)
    flade([(hu0, hv1, 0), (hu1, hv1, 0), (hu1, hv1, e), (hu0, hv1, e)], N, HUSVAEG)
    flade([(hu1, hv0, 0), (hu1, hv1, 0), (hu1, hv1, e), (hu1, 0, kip), (hu1, hv0, e)], E, HUSVAEG)
    flade([(hu0, hv0, e), (hu1, hv0, e), (hu1, 0, kip), (tum, 0, kip)], (0, -s, c), HUSTAG)     # løber ind i fløjens tag i en skotrende
    flade([(hu0, hv1, e), (hu1, hv1, e), (hu1, 0, kip), (tum, 0, kip)], (0, s, c), HUSTAG)
    syd = flade([(tu0, tb_v0, 0), (tu1, tb_v0, 0), (tu1, tb_v0, e), (tum, tb_v0, kip), (tu0, tb_v0, e)], S, NYVAEG, NYKANT, 0.8)
    nord = flade([(tu0, hv1, 0), (tu1, hv1, 0), (tu1, hv1, e), (tum, hv1, kip), (tu0, hv1, e)], N, NYVAEG, NYKANT, 0.8)
    vest = flade([(tu0, tb_v0, 0), (tu0, hv1, 0), (tu0, hv1, e), (tu0, tb_v0, e)], W, NYVAEG, NYKANT, 0.8)
    flade([(tu1, tb_v0, 0), (tu1, hv0, 0), (tu1, hv0, e), (tu1, tb_v0, e)], E, NYVAEG, NYKANT, 0.8)
    flade([(tu0, tb_v0, e), (tu0, hv1, e), (tum, hv1, kip), (tum, tb_v0, kip)], (-s, 0, c), HUSTAG, NYKANT, 0.8)
    flade([(tu1, tb_v0, e), (tu1, hv0, e), (tum, 0, kip), (tum, tb_v0, kip)], (s, 0, c), HUSTAG, NYKANT, 0.8)
    flade([(tu1, hv1, e), (tum, hv1, kip), (tum, 0, kip)], (s, 0, c), HUSTAG, NYKANT, 0.8)
    # åbninger som på tilbygning_plan: terrassedør mod syd, to garageporte mod nord, to vinduer mod vest
    syd["paa"].append(([(tu0 + 2.5, tb_v0, 0.05), (tu0 + 5.5, tb_v0, 0.05), (tu0 + 5.5, tb_v0, 2.15), (tu0 + 2.5, tb_v0, 2.15)], GLAS, "#333333"))
    for x in (1.05, 4.25):
        nord["paa"].append(([(tu0 + x, hv1, 0.05), (tu0 + x + 2.7, hv1, 0.05), (tu0 + x + 2.7, hv1, 2.25), (tu0 + x, hv1, 2.25)], "#d9d4c8", "#666666"))
    for y0, bb in ((0.9, 1.2), (5.6, 0.8)):
        vest["paa"].append(([(tu0, tb_v0 + y0, 0.9), (tu0, tb_v0 + y0 + bb, 0.9), (tu0, tb_v0 + y0 + bb, 2.1), (tu0, tb_v0 + y0, 2.1)], GLAS, "#333333"))

    # Hal: sort stål, kip nord-syd, port i sydgavl (ingen dør), dør i nordgavl
    hs, sok = HOEJDER["hal_side"], HOEJDER["hal_sokkel"]
    hkip, hv_ = sadeltag(hal_u0, hal_v0, hal_u1, hal_v1, hs, HOEJDER["hal_haeldning"], "v", SORT, SORT_TAG, sokkel=sok, kant="#8a8a8a")
    hum, PORT = (hal_u0 + hal_u1) / 2, 4.0
    hv_["S"]["paa"].append(([(hum - PORT / 2, hal_v0, 0.05), (hum + PORT / 2, hal_v0, 0.05), (hum + PORT / 2, hal_v0, 4.0), (hum - PORT / 2, hal_v0, 4.0)], PORTFARVE, "#b5b5b5"))
    hv_["N"]["paa"].append(([(hal_u0 + 3.95, hal_v1, 0.05), (hal_u0 + 4.85, hal_v1, 0.05), (hal_u0 + 4.85, hal_v1, 2.15), (hal_u0 + 3.95, hal_v1, 2.15)], PORTFARVE, "#b5b5b5"))
    z = sok + 1.06                                   # vandrette panelsamlinger, 1,06 m dækbredde
    while z < hkip:
        if z < hs:
            hv_["W"]["linjer"].append([(hal_u0, hal_v0, z), (hal_u0, hal_v1, z)])
            hv_["E"]["linjer"].append([(hal_u1, hal_v0, z), (hal_u1, hal_v1, z)])
            d = 0.0
        else:
            d = (z - hs) / math.tan(math.radians(HOEJDER["hal_haeldning"]))
        for k, vv in (("S", hal_v0), ("N", hal_v1)):
            hv_[k]["linjer"].append([(hal_u0 + d, vv, z), (hal_u1 - d, vv, z)])
        z += 1.06
    etiketter = [
        (f"Ny hal {h['laengde']:.0f} × {h['bredde']:.0f} m, sort\nside {hs:.1f} m, kip {hkip:.1f} m".replace(".", ","), (hum, (hal_v0 + hal_v1) / 2, hkip), 7),
        (f"Tilbygning {TB:.0f} × {HB / 2 - tb_v0:.0f} m", (tum, (tb_v0 + hv1) / 2, kip), 9),
        (f"Eksisterende hus {HL:.0f} × {HB:.0f} m", (3, 0, kip), 6),
        ("Hestestald", (-2, (skil_v + max(p[1] for p in hoved)) / 2, 4.5), 6),
    ]
    return fl, etiketter


def tegn(ax, retning):
    th = math.radians(retning)
    fh = np.array([-math.sin(th), -math.cos(th), 0.0])               # vandret synsretning
    F = math.cos(ELEV) * fh + np.array([0, 0, -math.sin(ELEV)])
    R = np.array([fh[1], -fh[0], 0.0])                               # skærm-højre
    U = math.sin(ELEV) * fh + np.array([0, 0, math.cos(ELEV)])       # skærm-op
    P = np.c_[R, U]
    ax.set_aspect("equal")
    ax.axis("off")
    ax.add_patch(Polygon(np.array([(G[0], G[1], 0), (G[2], G[1], 0), (G[2], G[3], 0), (G[0], G[3], 0)], float) @ P, closed=True, fc="#dfe8d6", ec="none", zorder=0))
    sk = np.array([(skel_u, G[1] + 2, 0), (skel_u, G[3] - 2, 0)], float) @ P
    ax.plot(sk[:, 0], sk[:, 1], color="red", lw=0.9, ls=(0, (6, 3)), zorder=1)
    m = np.array([(skel_u - 1.5, hal_v0 + 8, 0)], float) @ P
    d = sk[1] - sk[0]
    rot = math.degrees(math.atan2(d[1], d[0]))
    ax.text(m[0, 0], m[0, 1], "antaget skel", color="red", fontsize=6, rotation=rot if abs(rot) <= 90 else rot - 180, ha="center", va="center", zorder=1)
    np_ = np.array([(G[2] - 4, G[1] + 4, 0), (G[2] - 4, G[1] + 12, 0)], float) @ P
    ax.annotate("N", xy=np_[1], xytext=np_[0], fontsize=8, ha="center", va="center", arrowprops=dict(arrowstyle="-|>", lw=1.0), zorder=1)

    flader, etiketter = scene()
    synlige = [f for f in flader if np.array(f["n"], float) @ F < -1e-9]
    for f in sorted(synlige, key=lambda f: -float((np.array(f["pts"], float) @ F).mean())):
        ax.add_patch(Polygon(np.array(f["pts"], float) @ P, closed=True, fc=f["fyld"], ec=f["kant"], lw=f["lw"], joinstyle="round", zorder=2))
        for l in f["linjer"]:
            q = np.array(l, float) @ P
            ax.plot(q[:, 0], q[:, 1], color="#5a5d61", lw=0.35, zorder=2)
        for pts, fyld, kant in f["paa"]:
            ax.add_patch(Polygon(np.array(pts, float) @ P, closed=True, fc=fyld, ec=kant, lw=0.7, zorder=2))
    for tekst, p, dy in etiketter:
        q = np.array(p, float) @ P
        ax.annotate(tekst, xy=q, xytext=(q[0], q[1] + dy), fontsize=6.5, ha="center", va="center", zorder=5,
                    arrowprops=dict(arrowstyle="-", lw=0.5, color="#444444"), bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#888888", lw=0.5))
    ax.autoscale_view()
    y0, y1 = ax.get_ylim()
    ax.set_ylim(y0 - 1, y1 + 3)


FODNOTE1 = ("FORELØBIGE SKITSER i parallelprojektion, ikke målfaste. Hallens mål er de ønskede. Tagfod og taghældning på hus og tilbygning (2,7 m, 30°) "
            "og stald (2,6 m, 25°) er antaget og skal måles op.")
FODNOTE2 = "Husets farver, vinduer og døre er ikke kendt og er ikke vist. Tilbygningen er fremhævet med gul væg. Skel er antaget ud fra luftfoto."

# Samlet A3-ark med de fire hjørner
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
for i, (navn, _, retning) in enumerate(VISNINGER):
    ax = fig.add_axes([0.02 + 0.49 * (i % 2), 0.53 - 0.44 * (i // 2), 0.47, 0.43])
    tegn(ax, retning)
    ax.set_title(f"Set fra {navn}", fontsize=11, weight="bold", loc="left")
fig.text(0.03, 0.060, "Rumlige skitser fra fire hjørner, Nældevej 42, 9000 Aalborg", fontsize=12, weight="bold")
fig.text(0.03, 0.040, FODNOTE1, fontsize=7.5, color="red")
fig.text(0.03, 0.024, FODNOTE2, fontsize=7.5, color="red")
fig.savefig(HER / "isometri.pdf")
fig.savefig(HER / "isometri.png", dpi=150)
plt.close(fig)

# Ét billede pr. hjørne
for navn, fil, retning in VISNINGER:
    fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4))
    ax = fig.add_axes([0.02, 0.10, 0.96, 0.84])
    tegn(ax, retning)
    fig.text(0.04, 0.070, f"Rumlig skitse set fra {navn}, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
    fig.text(0.04, 0.045, FODNOTE1, fontsize=6.3, color="red")
    fig.text(0.04, 0.025, FODNOTE2, fontsize=6.3, color="red")
    fig.savefig(HER / f"isometri_{fil}.png", dpi=170)
    plt.close(fig)
print("isometri.pdf/.png og fire enkeltbilleder skrevet")
