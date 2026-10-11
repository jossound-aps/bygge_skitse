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
from matplotlib.patches import Circle, Polygon

HER = Path(__file__).parent
grund = json.loads((HER / "data/grundkort.json").read_text(encoding="utf-8"))
cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))
SOK_HUS, SOK_STALD = cfg.get("sokler", {}).get("hus", 0.0), cfg.get("sokler", {}).get("stald", 0.0)
for _k in ("hus_sydfacade", "hus_nordfacade"):      # åbningernes højder står over gulv; gulvet ligger i soklens overkant
    for _ab in cfg.get(_k, {}).get("aabninger", []):
        _ab["z0"], _ab["z1"] = _ab["z0"] + SOK_HUS, _ab["z1"] + SOK_HUS
cfg["vindue_standard"]["brystning"] += SOK_HUS

HOEJDER = {
    "hus_tagfod": cfg.get("sokler", {}).get("hus_tagfod_over_terraen", 2.5), "hus_haeldning": 25.0,       # anslået fra fotos IMG_0985 og IMG_2993; tilbygningen følger huset
    "stald_tagfod": cfg.get("stald", {}).get("tagfod", 2.6), "stald_haeldning": cfg.get("stald", {}).get("haeldning", 25.0),   # anslået fra foto IMG_9768
    "hal_side": 4.4, "hal_haeldning": 30.0, "hal_sokkel": 0.4,      # tagfod over terræn = 0,4 m sokkel + 4,0 m
}
ELEV = math.radians(24)
# kameraets kompasretning set fra grunden (grader fra nord, med uret); drejet lidt mod syd/nord, så gavlene ses
VISNINGER = [("sydøst", "sydoest", 142), ("sydvest", "sydvest", 218), ("nordvest", "nordvest", 322), ("nordøst", "nordoest", 38)]

SORT, SORT_TAG, SOKKEL, PORTFARVE = "#17181a", "#26282b", "#b9b9b4", "#4a4e54"
HUSVAEG, HUSTAG, STALD, STALDTAG = "#f6f6f3", "#232528", "#f1f1ee", "#2b2d31"   # hus og stald: hvide vægge, sort tag (IMG_0985, IMG_9768)
DOER, HEGN, SAND = "#5b4636", "#2a2a2a", "#eadfc6"
NYVAEG, NYKANT, GLAS = "#fbeccb", "#b36b00", "#5f7f99"   # tilbygningens vægge fremhævet


# --- Geometri fra situationsplanens data ---
def bygning(osm_id):
    return next(b["punkter"] for b in grund["bygninger"] if b["osm_id"] == osm_id)


hus = bygning(cfg["hus_osm_id"])[:-1]
cx, cy = sum(p[0] for p in hus) / len(hus), sum(p[1] for p in hus) / len(hus)
_st = bygning(cfg["stald_osm_id"])[:-1]            # aksen følger staldens længste side
a, b = max(((_st[i], _st[(i + 1) % len(_st)]) for i in range(len(_st))), key=lambda k: math.dist(*k))
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
if "position" in h:
    hal_u0, hal_v1 = h["position"]["u_vest"], h["position"]["v_nord"]
else:
    hal_u0, hal_v1 = skel_u + h["afstand_til_skel"], tb_v0 - h["afstand_til_tilbygning"]
hal_u1 = hal_u0 + h["bredde"]
hal_v0 = hal_v1 - h["laengde"]
PORT_NORD = h.get("port_mod") == "nord"
stald = [uv(p) for p in bygning(cfg["stald_osm_id"])[:-1]]
G = (-29, -52, 73, 42)   # terrænudsnit u0, v0, u1, v1

S, N, W, E = (0, -1, 0), (0, 1, 0), (-1, 0, 0), (1, 0, 0)



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


def scene():
    """Returnerer alle flader (punkter, udadrettet normal, farver, påsatte åbninger og linjer) samt etiketter."""
    fl = []

    def flade(pts, normal, fyld, kant="#555555", lw=0.5):
        fl.append({"pts": pts, "n": normal, "fyld": fyld, "kant": kant, "lw": lw, "paa": [], "linjer": []})
        return fl[-1]

    def sokkelbaand(f, hoejde):
        """Grå sokkel nederst på en vægflade; lægges først, så døre og porte tegnes oven på."""
        if hoejde and f is not None:
            a_, b_ = f["pts"][0], f["pts"][1]
            f["paa"].insert(0, ([(a_[0], a_[1], 0), (b_[0], b_[1], 0), (b_[0], b_[1], hoejde), (a_[0], a_[1], hoejde)], SOKKEL, "#777777"))

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
    _, sv_h = sadeltag(min(p[0] for p in hoved), skil_v, max(p[0] for p in hoved), max(p[1] for p in hoved),
                       HOEJDER["stald_tagfod"], HOEJDER["stald_haeldning"], "u", STALD, STALDTAG)
    tag_syd = fl[-2]                                   # hovedlængens sydlige tagflade; skæres ud, hvor fløjens tag går ind
    _, sv_f = sadeltag(min(p[0] for p in floej), min(p[1] for p in floej), max(p[0] for p in floej), skil_v,
                       HOEJDER["stald_tagfod"], HOEJDER["stald_haeldning"], "v", STALD, STALDTAG, udelad="N")
    for f_ in list(sv_h.values()) + list(sv_f.values()):
        sokkelbaand(f_, SOK_STALD)
    tag_floej_oest, tag_floej_vest = fl[-2], fl[-1]     # fløjens tagflader; forlænges ind i hovedlængens tag uden mellemstreg
    # fløjens tag føres ind i hovedlængens sydlige tagflade (skotrender), så L-formens tage hænger sammen
    st_e = HOEJDER["stald_tagfod"]
    st_t, st_s, st_c = (f(math.radians(HOEJDER["stald_haeldning"])) for f in (math.tan, math.sin, math.cos))
    fw0, fw1 = min(p[0] for p in floej), max(p[0] for p in floej)
    fum, fkip = (fw0 + fw1) / 2, st_e + (fw1 - fw0) / 2 * st_t
    moede = (fum, skil_v + (fw1 - fw0) / 2, fkip)          # her møder fløjens kip hovedlængens tagflade
    hw0, hw1, hvm = min(p[0] for p in hoved), max(p[0] for p in hoved), (skil_v + max(p[1] for p in hoved)) / 2
    hkip_st = st_e + (hvm - skil_v) * st_t
    tag_syd["pts"] = [(hw0, skil_v, st_e), (fw0, skil_v, st_e), moede, (fw1, skil_v, st_e), (hw1, skil_v, st_e), (hw1, hvm, hkip_st), (hw0, hvm, hkip_st)]
    fv_syd = min(p[1] for p in floej)
    tag_floej_vest["pts"] = [(fw0, fv_syd, st_e), (fw0, skil_v, st_e), moede, (fum, fv_syd, fkip)]
    tag_floej_oest["pts"] = [(fw1, fv_syd, st_e), (fw1, skil_v, st_e), moede, (fum, fv_syd, fkip)]

    # staldens åbninger: brøkdele af facadelængden (se situationsplan.json)
    hu_w, hu_e, hv_n = min(p[0] for p in hoved), max(p[0] for p in hoved), max(p[1] for p in hoved)
    fu_w, fu_e, fv_s = min(p[0] for p in floej), max(p[0] for p in floej), min(p[1] for p in floej)
    st = cfg.get("stald", {})
    for liste, vaeg, punkt in (
        ("nord", sv_h["N"], lambda f, z: (hu_w + f * (hu_e - hu_w), hv_n, z)),
        ("syd", sv_h["S"], lambda f, z: (hu_w + f * (hu_e - hu_w), skil_v, z)),
        ("oestgavl", sv_h["E"], lambda f, z: (hu_e, hv_n - f * (hv_n - skil_v), z)),
        ("floej_vest", sv_f["W"], lambda f, z: (fu_w, skil_v - f * (skil_v - fv_s), z)),
        ("floej_oest", sv_f["E"], lambda f, z: (fu_e, skil_v - f * (skil_v - fv_s), z)),
    ):
        for ab in st.get(liste, []):
            if liste == "syd" and hu_w + ab["f0"] * (hu_e - hu_w) > fu_w:      # dækket af sydfløjen
                continue
            vaeg["paa"].append(([punkt(ab["f0"], ab["z0"]), punkt(ab["f1"], ab["z0"]), punkt(ab["f1"], ab["z1"]), punkt(ab["f0"], ab["z1"])],
                                DOER if ab.get("doer") else GLAS, "#111111"))
    # møddingsplads: lave hvide mure
    for noegle, farve in (("moedding", "#b9b4a8"), ("mur", STALD)):
        if noegle in cfg:
            mp = [uv(p) for p in cfg[noegle]["punkter"]]
            for (a0, b0), (a1, b1) in zip(mp[:-1], mp[1:]):
                flade([(a0, b0, 0), (a1, b1, 0), (a1, b1, cfg[noegle]["hoejde"]), (a0, b0, cfg[noegle]["hoejde"])], None, farve, "#555555", 0.5)

    # Læbælter og træer (eksisterende): stamme og rund krone, kun inden for terrænudsnittet
    lb = cfg.get("laebaelter", {})
    traeer = [(*uv((tr["x"], tr["y"])), tr["radius"], tr["hoejde"]) for tr in lb.get("enkelttraeer", [])]
    for baelte in lb.get("baelter", []):
        r, pts = baelte["bredde"] / 2, [uv(p) for p in baelte["linje"]]
        for (a0, b0), (a1, b1) in zip(pts[:-1], pts[1:]):
            antal = max(1, round(math.hypot(a1 - a0, b1 - b0) / (1.8 * r)))
            for i in range(antal + 1):
                traeer.append((a0 + (a1 - a0) * i / antal, b0 + (b1 - b0) * i / antal, r, baelte["hoejde"]))
    for i, (tu, tv, r, hh) in enumerate(traeer):
        if G[0] + r <= tu <= G[2] - r and G[1] + r <= tv <= G[3] - r:
            fl.append({"pts": [(tu, tv, hh / 2)], "n": None, "trae": (tu, tv, r, hh, i), "paa": [], "linjer": []})

    # Hegn (eksisterende): stolper og to rækker brædder
    for linje in cfg.get("hegn", {}).get("linjer", []):
        el = linje["type"] == "el"
        pkt_ = [uv(p) for p in linje["punkter"]]
        for (a0, b0), (a1, b1) in zip(pkt_[:-1], pkt_[1:]):
            antal = max(1, round(math.hypot(a1 - a0, b1 - b0) / (4.0 if el else 3.0)))
            for i in range(antal):
                q0 = (a0 + (a1 - a0) * i / antal, b0 + (b1 - b0) * i / antal)
                q1 = (a0 + (a1 - a0) * (i + 1) / antal, b0 + (b1 - b0) * (i + 1) / antal)
                if el:        # elhegn: stolper og én tråd
                    f = flade([(q0[0], q0[1], 0), (q1[0], q1[1], 0), (q1[0], q1[1], 1.3), (q0[0], q0[1], 1.3)], None, "none", "none", 0)
                    f["linjer"] += [[(q0[0], q0[1], 0), (q0[0], q0[1], 1.3)], [(q1[0], q1[1], 0), (q1[0], q1[1], 1.3)], [(q0[0], q0[1], 1.1), (q1[0], q1[1], 1.1)]]
                    f["tynd"] = True
                else:         # bræddehegn: stolper og to rækker brædder
                    f = flade([(q0[0], q0[1], 0), (q1[0], q1[1], 0), (q1[0], q1[1], 1.2), (q0[0], q0[1], 1.2)], None, "none", HEGN, 0.6)
                    f["linjer"].append([(q0[0], q0[1], 0.65), (q1[0], q1[1], 0.65)])

    # Skur øst for staldens sydfløj (eksisterende, vist som kasse med fladt tag; højde antaget)
    if "skur" in cfg:
        sp = [uv(p) for p in cfg["skur"]["punkter"]]
        su0, su1 = min(p[0] for p in sp), max(p[0] for p in sp)
        sv0, sv1 = min(p[1] for p in sp), max(p[1] for p in sp)
        sh = cfg["skur"]["hoejde"]
        for pts, nrm in (([(su0, sv0, 0), (su1, sv0, 0), (su1, sv0, sh), (su0, sv0, sh)], S), ([(su0, sv1, 0), (su1, sv1, 0), (su1, sv1, sh), (su0, sv1, sh)], N),
                         ([(su0, sv0, 0), (su0, sv1, 0), (su0, sv1, sh), (su0, sv0, sh)], W), ([(su1, sv0, 0), (su1, sv1, 0), (su1, sv1, sh), (su1, sv0, sh)], E)):
            f_ = flade(pts, nrm, STALD)
            sd = cfg["skur"].get("doer")
            if sd and nrm == N and sd["side"] == "nord":          # dør i nordsiden, op mod stalden
                d0 = su0 + sd["afstand_fra_stald"]
                f_["paa"].append(([(d0, sv1, 0.05), (d0 + sd["bredde"], sv1, 0.05), (d0 + sd["bredde"], sv1, sd["hoejde"]), (d0, sv1, sd["hoejde"])], DOER, "#111111"))
        flade([(su0, sv0, sh), (su1, sv0, sh), (su1, sv1, sh), (su0, sv1, sh)], (0, 0, 1), "#3a3c40")

    # Eksisterende hus (kip øst-vest) og tilbygning (fløj med kip nord-syd, samme tagfod, hældning og bredde)
    e = HOEJDER["hus_tagfod"]
    t, s, c = (f(math.radians(HOEJDER["hus_haeldning"])) for f in (math.tan, math.sin, math.cos))
    kip = e + HB / 2 * t
    hu0, hu1, hv0, hv1 = -HL / 2, HL / 2, -HB / 2, HB / 2
    tu0, tu1, tum = hu0 - TB, hu0, hu0 - TB / 2
    hus_syd = flade([(hu0, hv0, 0), (hu1, hv0, 0), (hu1, hv0, e), (hu0, hv0, e)], S, HUSVAEG)
    for ab in cfg.get("hus_sydfacade", {}).get("aabninger", []):        # eksisterende vinduer og glasparti, sorte rammer
        hus_syd["paa"].append(([(ab["u0"], hv0, ab["z0"]), (ab["u1"], hv0, ab["z0"]), (ab["u1"], hv0, ab["z1"]), (ab["u0"], hv0, ab["z1"])], GLAS, "#111111"))
        for i in range(1, ab.get("fag", 1)):
            uu = ab["u0"] + (ab["u1"] - ab["u0"]) * i / ab["fag"]
            hus_syd["paa"].append(([(uu, hv0, ab["z0"]), (uu, hv0, ab["z1"])], "none", "#111111"))
    hus_nord = flade([(hu0, hv1, 0), (hu1, hv1, 0), (hu1, hv1, e), (hu0, hv1, e)], N, HUSVAEG)
    for ab in cfg.get("hus_nordfacade", {}).get("aabninger", []):
        hus_nord["paa"].append(([(ab["u0"], hv1, ab["z0"]), (ab["u1"], hv1, ab["z0"]), (ab["u1"], hv1, ab["z1"]), (ab["u0"], hv1, ab["z1"])], DOER if ab.get("doer") else GLAS, "#111111"))
    hus_oest = flade([(hu1, hv0, 0), (hu1, hv1, 0), (hu1, hv1, e), (hu1, 0, kip), (hu1, hv0, e)], E, HUSVAEG)
    flade([(hu0, hv0, e), (hu1, hv0, e), (hu1, 0, kip), (tum, 0, kip)], (0, -s, c), HUSTAG)     # løber ind i fløjens tag i en skotrende
    flade([(hu0, hv1, e), (hu1, hv1, e), (hu1, 0, kip), (tum, 0, kip)], (0, s, c), HUSTAG)
    syd = flade([(tu0, tb_v0, 0), (tu1, tb_v0, 0), (tu1, tb_v0, e), (tum, tb_v0, kip), (tu0, tb_v0, e)], S, NYVAEG, NYKANT, 0.8)
    nord = flade([(tu0, hv1, 0), (tu1, hv1, 0), (tu1, hv1, e), (tum, hv1, kip), (tu0, hv1, e)], N, NYVAEG, NYKANT, 0.8)
    vest = flade([(tu0, tb_v0, 0), (tu0, hv1, 0), (tu0, hv1, e), (tu0, tb_v0, e)], W, NYVAEG, NYKANT, 0.8)
    oest = flade([(tu1, tb_v0, 0), (tu1, hv0, 0), (tu1, hv0, e), (tu1, tb_v0, e)], E, NYVAEG, NYKANT, 0.8)
    for f_ in (hus_syd, hus_nord, hus_oest, syd, nord, vest, oest):
        sokkelbaand(f_, SOK_HUS)
    vs = cfg["vindue_standard"]
    vz0, vz1, vb = vs["brystning"], vs["brystning"] + vs["hoejde"], vs["bredde"]
    oest["paa"].append(([(tu1, tb_v0 + 1.6, vz0), (tu1, tb_v0 + 1.6 + vb, vz0), (tu1, tb_v0 + 1.6 + vb, vz1), (tu1, tb_v0 + 1.6, vz1)], GLAS, "#111111"))   # soveværelsesvindue mod øst
    flade([(tu0, tb_v0, e), (tu0, hv1, e), (tum, hv1, kip), (tum, tb_v0, kip)], (-s, 0, c), HUSTAG, NYKANT, 0.8)
    flade([(tu1, tb_v0, e), (tu1, hv0, e), (tum, 0, kip), (tum, tb_v0, kip)], (s, 0, c), HUSTAG, NYKANT, 0.8)
    flade([(tu1, hv1, e), (tum, hv1, kip), (tum, 0, kip)], (s, 0, c), HUSTAG, NYKANT, 0.8)
    # åbninger som på tilbygning_plan: terrassedør mod syd, to garageporte mod nord, to vinduer mod vest
    syd["paa"].append(([(tu0 + 2.5, tb_v0, SOK_HUS), (tu0 + 5.5, tb_v0, SOK_HUS), (tu0 + 5.5, tb_v0, SOK_HUS + 2.1), (tu0 + 2.5, tb_v0, SOK_HUS + 2.1)], GLAS, "#111111"))
    for x in (1.05, 4.25):                           # garageporte i sokkelhøjde
        nord["paa"].append(([(tu0 + x, hv1, SOK_HUS), (tu0 + x + 2.7, hv1, SOK_HUS), (tu0 + x + 2.7, hv1, SOK_HUS + 2.2), (tu0 + x, hv1, SOK_HUS + 2.2)], "#d9d4c8", "#666666"))
    opk = cfg["tilbygning"].get("garage_opkoersel")  # gruset føres langsomt op til portene
    if opk and SOK_HUS:
        vb_ = hv1 + opk["laengde"]
        flade([(tu0, hv1, SOK_HUS), (tu1, hv1, SOK_HUS), (tu1, vb_, 0.02), (tu0, vb_, 0.02)], (0, 0, 1), "#d6d1c6", "#a8a296")
        flade([(tu0, hv1, SOK_HUS), (tu0 - opk["side_udfald"], hv1, 0.02), (tu0, vb_, 0.02)], (0, 0, 1), "#cdc8bc", "#a8a296")
        flade([(tu1, hv1, SOK_HUS), (tu1, hv1 + 0.01, 0.02), (tu1, vb_, 0.02)], (1, 0, 0), "#c4bfb3", "#a8a296")
    for y0 in (1.0, 5.7):          # soveværelse og bad mod vest
        vest["paa"].append(([(tu0, tb_v0 + y0, vz0), (tu0, tb_v0 + y0 + vb, vz0), (tu0, tb_v0 + y0 + vb, vz1), (tu0, tb_v0 + y0, vz1)], GLAS, "#111111"))

    # Hal: sort stål, kip nord-syd, port i sydgavl (ingen dør), dør i nordgavl
    hs, sok = HOEJDER["hal_side"], HOEJDER["hal_sokkel"]
    hkip, hv_ = sadeltag(hal_u0, hal_v0, hal_u1, hal_v1, hs, HOEJDER["hal_haeldning"], "v", SORT, SORT_TAG, sokkel=sok, kant="#8a8a8a")
    hum, PORT = (hal_u0 + hal_u1) / 2, 4.0
    pg, pv, dg, dv = ("N", hal_v1, "S", hal_v0) if PORT_NORD else ("S", hal_v0, "N", hal_v1)       # portgavl og dørgavl
    du = hal_u0 + 0.6                                  # gangdør i portgavlen, i siden mod huset
    dg, dv = pg, pv
    hv_[pg]["paa"].append(([(hum - PORT / 2, pv, sok), (hum + PORT / 2, pv, sok), (hum + PORT / 2, pv, sok + 4.0), (hum - PORT / 2, pv, sok + 4.0)], PORTFARVE, "#b5b5b5"))
    hv_[dg]["paa"].append(([(du, dv, sok), (du + 0.9, dv, sok), (du + 0.9, dv, sok + 2.15), (du, dv, sok + 2.15)], PORTFARVE, "#b5b5b5"))
    fp = h.get("forplads")                           # fliseplads i gulvhøjde foran portgavlen, med rampe ned til terræn
    if fp:
        r_ = 1 if pg == "N" else -1
        vb, su = pv + r_ * fp["rampe_laengde"], fp["side_udfald"]
        flade([(hal_u0, pv, sok), (hal_u1, pv, sok), (hal_u1, vb, 0.02), (hal_u0, vb, 0.02)], (0, 0, 1), "#d8d4c8", "#8a8a8a")
        for u_, s_ in ((hal_u0, -1), (hal_u1, 1)):      # rampen falder ud til siderne
            flade([(u_, pv, sok), (u_ + s_ * su, pv, 0.02), (u_, vb, 0.02)], (0, 0, 1), "#cdc8ba", "#8a8a8a")
    z = sok + 1.0                                    # vandrette panelsamlinger: paneler à 1 m, fire i højden på siderne
    while z < hkip:
        if z < hs:
            hv_["W"]["linjer"].append([(hal_u0, hal_v0, z), (hal_u0, hal_v1, z)])
            hv_["E"]["linjer"].append([(hal_u1, hal_v0, z), (hal_u1, hal_v1, z)])
            d = 0.0
        else:
            d = (z - hs) / math.tan(math.radians(HOEJDER["hal_haeldning"]))
        for k, vv in (("S", hal_v0), ("N", hal_v1)):
            hv_[k]["linjer"].append([(hal_u0 + d, vv, z), (hal_u1 - d, vv, z)])
        z += 1.0
    etiketter = [
        (f"Ny hal {h['laengde']:.0f} × {h['bredde']:.0f} m, sort\nside {hs:.1f} m, kip {hkip:.1f} m".replace(".", ","), (hum, (hal_v0 + hal_v1) / 2, hkip), 7),
        (f"Tilbygning {TB:.0f} × {HB / 2 - tb_v0:.0f} m", (tum, (tb_v0 + hv1) / 2, kip), 9),
        (f"Eksisterende hus {HL:.0f} × {HB:.0f} m", (3, 0, kip), 6),
        ("Hestestald", (-2, (skil_v + max(p[1] for p in hoved)) / 2, 4.5), 6),
        ("Skur", ((su0 + su1) / 2, (sv0 + sv1) / 2, sh), 4),
        ("Mødding", (*uv((57.7, 6.1)), 1.5), 4),
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
    bel = cfg.get("belaegning", {})
    for vej in grund["veje"]:              # grusvej, klippet til terrænudsnittet
        (xa, ya), (xb, yb) = vej["punkter"][-1], vej["punkter"][-2]
        kant = []
        for uu in (G[0], G[2]):
            # vejen er næsten parallel med u-aksen; find punktet på midterlinjen ud for uu
            s = (uu - uv((xa, ya))[0]) / (uv((xb, yb))[0] - uv((xa, ya))[0])
            kant.append(uv((xa + s * (xb - xa), ya + s * (yb - ya))))
        hb = bel.get("vej_bredde", 4.0) / 2
        q = np.array([(kant[0][0], kant[0][1] - hb, 0), (kant[1][0], kant[1][1] - hb, 0), (kant[1][0], min(kant[1][1] + hb, G[3]), 0), (kant[0][0], min(kant[0][1] + hb, G[3]), 0)], float) @ P
        ax.add_patch(Polygon(q, closed=True, fc="#d6d1c6", ec="none", zorder=0.4))
    for fl_ in bel.get("grus", []):
        q = np.array([(*uv(p_), 0) for p_ in fl_["punkter"]], float) @ P
        ax.add_patch(Polygon(q, closed=True, fc="#d6d1c6", ec="none", zorder=0.4))
    if "ridebane" in cfg:
        rb = np.array([(*uv(p), 0) for p in cfg["ridebane"]["punkter"]], float) @ P
        ax.add_patch(Polygon(rb, closed=True, fc=SAND, ec="#b3a67f", lw=0.5, zorder=0.5))
        ax.text(rb[:, 0].mean(), rb[:, 1].mean(), "Ridebane", fontsize=6.5, color="#6b5f3f", ha="center", va="center", zorder=0.6)
    if "sandfold" in cfg:
        sf = np.array([(*uv(p), 0) for p in cfg["sandfold"]["punkter"]], float) @ P
        ax.add_patch(Polygon(sf, closed=True, fc="#efe7d3", ec="none", zorder=0.5))
    if "gangsti" in cfg:
        q = np.array([(u_, v_, 0) for u_, v_ in cfg["gangsti"]["punkter_uv"]], float) @ P
        ax.plot(q[:, 0], q[:, 1], color="#c9b98f", lw=2.2, solid_capstyle="butt", zorder=0.8)
    if "koerevej" in cfg:
        pu, pvv = (hal_u0 + hal_u1) / 2, hal_v1 if PORT_NORD else hal_v0
        port_xy = (cx + pu * ux - pvv * uy, cy + pu * uy + pvv * ux)
        ret = (uy, -ux) if PORT_NORD else (-uy, ux)
        for k in koerevej_linjer(port_xy, ret)[1]:
            q = np.array([(*uv(p_), 0) for p_ in k], float) @ P
            ax.plot(q[:, 0], q[:, 1], color="#555555", lw=0.8, ls=(0, (5, 2)), zorder=0.8)
    def klip(a_, b_):                                # klipper et linjestykke til terrænudsnittet G (i u, v)
        t0, t1, du, dv = 0.0, 1.0, b_[0] - a_[0], b_[1] - a_[1]
        for p_, q_ in ((-du, a_[0] - G[0]), (du, G[2] - a_[0]), (-dv, a_[1] - G[1]), (dv, G[3] - a_[1])):
            if p_ == 0:
                if q_ < 0:
                    return None
            else:
                r_ = q_ / p_
                if p_ < 0:
                    t0 = max(t0, r_)
                else:
                    t1 = min(t1, r_)
        return None if t0 > t1 else ((a_[0] + t0 * du, a_[1] + t0 * dv), (a_[0] + t1 * du, a_[1] + t1 * dv))

    for s in cfg.get("matrikelskel", {}).get("linjer", []):      # matrikelskel efter matriklen.dk, røde stiplede linjer
        pts = [uv(p_) for p_ in s["punkter"]]
        for a_, b_ in zip(pts[:-1], pts[1:]):
            kl = klip(a_, b_)
            if kl:
                sk = np.array([(*kl[0], 0.03), (*kl[1], 0.03)], float) @ P
                ax.plot(sk[:, 0], sk[:, 1], color="red", lw=0.9, ls=(0, (6, 3)) if s["type"] == "ydre" else (0, (2, 2)), zorder=1)
    for e in cfg.get("matrikelskel", {}).get("etiketter", []):
        eu, ev = uv(e["xy"])
        if G[0] < eu < G[2] and G[1] < ev < G[3]:
            m = np.array([(eu, ev, 0)], float) @ P
            ax.text(m[0, 0], m[0, 1], e["tekst"], color="red", fontsize=7, style="italic", weight="bold", ha="center", va="center", zorder=50, bbox=dict(fc="white", ec="red", lw=0.5, alpha=0.95, pad=2))
    np_ = np.array([(G[2] - 4, G[1] + 4, 0), (G[2] - 4, G[1] + 12, 0)], float) @ P
    ax.annotate("N", xy=np_[1], xytext=np_[0], fontsize=8, ha="center", va="center", arrowprops=dict(arrowstyle="-|>", lw=1.0), zorder=1)

    flader, etiketter = scene()
    synlige = [f for f in flader if f["n"] is None or np.array(f["n"], float) @ F < -1e-9]
    for f in sorted(synlige, key=lambda f: -float((np.array(f["pts"], float) @ F).mean())):
        if "trae" in f:
            tu, tv, r, hh, i = f["trae"]
            fod, top = np.array([tu, tv, 0.0]) @ P, np.array([tu, tv, max(hh - r, r)]) @ P
            ax.plot([fod[0], top[0]], [fod[1], top[1]], color="#6b4f2a", lw=0.8, zorder=2)
            ax.add_patch(Circle(top, r, fc=("#7fae6a", "#6f9f5c", "#8ab874")[i % 3], ec="#4f7a3f", lw=0.4, alpha=0.6, zorder=2))
            continue
        ax.add_patch(Polygon(np.array(f["pts"], float) @ P, closed=True, fc=f["fyld"], ec=f["kant"], lw=f["lw"], joinstyle="round", zorder=2))
        for l in f["linjer"]:
            q = np.array(l, float) @ P
            ax.plot(q[:, 0], q[:, 1], color=HEGN if f["n"] is None else "#5a5d61", lw=(0.35 if f.get("tynd") else 0.6) if f["n"] is None else 0.35, zorder=2)
        for pts, fyld, kant in f["paa"]:
            ax.add_patch(Polygon(np.array(pts, float) @ P, closed=True, fc=fyld, ec=kant, lw=0.7, zorder=2))
    # tekstskilte lægges i to rækker oven over hele motivet, så de ikke dækker bygninger; tynde henvisningsstreger peger ned
    ax.autoscale_view()
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    maal_ = sorted(((np.array(p, float) @ P, tekst) for tekst, p, _ in etiketter), key=lambda m: m[0][0])
    n = len(maal_)
    for i, (q, tekst) in enumerate(maal_):
        lx = x0 + (x1 - x0) * (0.08 + 0.84 * i / max(n - 1, 1))
        ly = y1 + 3.0 + 4.5 * (i % 2)
        ax.annotate(tekst, xy=q, xytext=(lx, ly), fontsize=6.5, ha="center", va="center", zorder=5,
                    arrowprops=dict(arrowstyle="-", lw=0.4, color="#666666", shrinkB=0), bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#888888", lw=0.5))
        ax.plot([q[0]], [q[1]], marker="o", ms=2.2, color="#444444", zorder=5)
    ax.set_ylim(y0 - 1, y1 + 11)


FODNOTE1 = ("Rumlige skitser i parallelprojektion, ikke målfaste. Hallens mål er de ansøgte. Tagfod og taghældning på hus og tilbygning (2,8 m, 25°) "
            "og stald (2,6 m, 38°) samt skurets højde er anslået fra fotos.")
FODNOTE2 = "Farver og åbninger i hus og stald følger ejendomsmæglerens plantegning (2024) og fotos. Ridebane, hegn, grusarealer og læbælter er tegnet efter luftfoto. Tilbygningen er fremhævet med gul væg; den udføres hvid som huset."

# Samlet A3-ark med de fire hjørner
fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
for i, (navn, _, retning) in enumerate(VISNINGER):
    ax = fig.add_axes([0.02 + 0.49 * (i % 2), 0.53 - 0.44 * (i // 2), 0.47, 0.43])
    tegn(ax, retning)
    ax.set_title(f"Set fra {navn}", fontsize=11, weight="bold", loc="left")
fig.text(0.03, 0.060, "Rumlige skitser fra fire hjørner, Nældevej 42, 9000 Aalborg", fontsize=12, weight="bold")
fig.text(0.03, 0.040, FODNOTE1, fontsize=7.5, color="#444444")
fig.text(0.03, 0.024, FODNOTE2, fontsize=7.5, color="#444444")
fig.savefig(HER / "isometri.pdf")
fig.savefig(HER / "isometri.png", dpi=150)
plt.close(fig)

# Ét billede pr. hjørne
for navn, fil, retning in VISNINGER:
    fig = plt.figure(figsize=(297 / 25.4, 210 / 25.4))
    ax = fig.add_axes([0.02, 0.10, 0.96, 0.84])
    tegn(ax, retning)
    fig.text(0.04, 0.070, f"Rumlig skitse set fra {navn}, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
    fig.text(0.04, 0.045, FODNOTE1, fontsize=6.3, color="#444444")
    fig.text(0.04, 0.025, FODNOTE2, fontsize=6.3, color="#444444")
    fig.savefig(HER / f"isometri_{fil}.png", dpi=170)
    plt.close(fig)
print("isometri.pdf/.png og fire enkeltbilleder skrevet")
