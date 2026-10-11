#!/usr/bin/env python3
"""Tekniske tegninger og overslagsberegning for hallen.

Kør:  python3 tegninger/hal_teknisk.py
Giver: tegninger/hal_facader.pdf/.png        (A1.2, 1:100)
       tegninger/hal_snit.pdf/.png           (A1.3, 1:50, med hovedresultater)
       tegninger/hal_konstruktion.pdf/.png   (A1.4, 1:100: ramme- og åseplan samt fundamentsplan)
       docs/hal-statik-overslag.md           (laster, snitkræfter, udnyttelser, åse, fundamenter, afstivning)

Beregningen er et OVERSLAG til dialog med leverandør og rådgiver. Den er ikke en statisk dokumentation.
"""
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon, Rectangle

from nordpil import nordpil
from statik import Ramme, kombiner
from tegningshoved import tegningshoved

HER = Path(__file__).parent
h_cfg = json.loads((HER / "situationsplan.json").read_text(encoding="utf-8"))["hal"]

# ---------------- Forudsætninger ----------------
B, L = h_cfg["bredde"], h_cfg["laengde"]
SIDE, HAELD, SOKKEL = 4.0, 30.0, 0.4          # SIDE og KIP måles fra soklens overkant (= gulv); soklen går 0,4 m over terræn som stuehusets
FORPLADS = (0.0, 4.0)                           # fliserampe foran porten: ingen vandret del, rampens længde
SIDEUDFALD = 2.0                                # rampen falder også ud til siderne over denne bredde
ALFA = math.radians(HAELD)
KIP = SIDE + B / 2 * math.tan(ALFA)
RAMMER_Y = [0.15, 5.0, 10.0, 15.0, L - 0.15]          # fem rammer
A_RAMME = 5.0                                         # belastningsbredde for en mellemramme
G_TAG, G_VAEG = 0.25, 0.15                            # kN/m²: paneler, åse og beslag (uden rammens egenvægt)
SK, MU1, MU_W = 1.0, 0.8, 1.2                         # sne: terrænværdi og formfaktorer (DK NA 2024)
QP = 0.78                                             # kN/m², terrænkategori II, z = 7,3 m over terræn, vb = 24 m/s
FY, E_STAAL, GM0, GM1 = 235e3, 210e6, 1.1, 1.2        # S235; partialkoefficienter efter DK NA (efter hukommelsen)
# IPE: A cm², Iy cm4, Wpl cm³, h mm, b mm, kg/m
IPE = {"IPE 200": (28.5, 1943, 221, 200, 100, 22.4), "IPE 220": (33.4, 2772, 285, 220, 110, 26.2), "IPE 240": (39.1, 3892, 367, 240, 120, 30.7),
       "IPE 270": (45.9, 5790, 484, 270, 135, 36.1), "IPE 300": (53.8, 8356, 628, 300, 150, 42.2), "IPE 330": (62.6, 11770, 804, 330, 160, 49.1),
       "IPE 360": (72.7, 16270, 1019, 360, 170, 57.1)}
STAENGER = ["sv", "tv", "to", "so"]                   # søjle vest, tag vest, tag øst, søjle øst
NORMAL = {"sv": (-1, 0), "tv": (-math.sin(ALFA), math.cos(ALFA)), "to": (math.sin(ALFA), math.cos(ALFA)), "so": (1, 0)}
# vind: (cpe - cpi) pr. stang. W1 = vind fra vest med tryk på taget, W1e = samme fra øst, W2 = fra vest med sug, W3 = vind langs kippen
VIND = {"W1": {"sv": 1.1, "tv": 0.7, "to": 0.3, "so": -0.2}, "W1e": {"sv": -0.2, "tv": 0.3, "to": 0.7, "so": 1.1},
        "W2": {"sv": 0.6, "tv": -0.4, "to": -0.7, "so": -0.7}, "W3": {"sv": -1.0, "tv": -1.0, "to": -1.0, "so": -1.0}}
KOMB = {"K1  1,0 G + 1,5 S(jævn) + 0,45 W(tryk)": {"G": 1.0, "S1": 1.5, "W1": 0.45},
        "K2  1,0 G + 1,5 S(ophobning vest) + 0,45 W(fra øst)": {"G": 1.0, "S2": 1.5, "W1e": 0.45},
        "K3  1,0 G + 1,5 S(omfordelt) + 0,45 W(tryk)": {"G": 1.0, "S3": 1.5, "W1": 0.45},
        "K4  1,0 G + 1,5 W(tryk)": {"G": 1.0, "W1": 1.5},
        "K5  0,9 G + 1,5 W(sug, på tværs)": {"G": 0.9, "W2": 1.5},
        "K6  0,9 G + 1,5 W(sug, langs kip)": {"G": 0.9, "W3": 1.5},
        "K7  1,2 G": {"G": 1.2}}


def dk(v, d=1):
    return f"{v:.{d}f}".replace(".", ",")


def beregn(profil, a=A_RAMME):
    A, I, Wpl, hh, bb, kg = IPE[profil]
    EA, EI = E_STAAL * A * 1e-4, E_STAAL * I * 1e-8
    r = Ramme()
    r.stang("sv", (0, 0), (0, SIDE), EA, EI)
    r.stang("tv", (0, SIDE), (B / 2, KIP), EA, EI)
    r.stang("to", (B / 2, KIP), (B, SIDE), EA, EI)
    r.stang("so", (B, SIDE), (B, 0), EA, EI)
    r.understoet((0, 0))
    r.understoet((B, 0))
    egen = kg * 9.81 / 1000
    lt = {"G": r.last(["tv", "to"], "g", G_TAG * a) + r.last(["sv", "so"], "g", G_VAEG * a) + r.last(STAENGER, "g", egen),
          "S1": r.last(["tv", "to"], "plan", MU1 * SK * a),
          "S2": r.last(["tv"], "plan", MU_W * SK * a),
          "S3": r.last(["tv"], "plan", MU1 * SK * a) + r.last(["to"], "plan", 0.5 * MU1 * SK * a)}
    for navn, c in VIND.items():
        lt[navn] = sum(r.last([s], "normal", c[s] * QP * a, NORMAL) for s in STAENGER)
    res = {k: r.loes(F) for k, F in lt.items()}
    NRd, MRd = A * 1e-4 * FY, Wpl * 1e-6 * FY
    s_len = math.hypot(B / 2, KIP - SIDE)
    c = s_len / SIDE                                    # samme profil i søjle og spær
    beta = math.sqrt(4 + 1.4 * c + 0.02 * c * c)        # knæklængdefaktor for to-charniers ramme (tilnærmet)

    def chi(Lcr):
        lam = math.sqrt(NRd / (math.pi ** 2 * EI / Lcr ** 2))
        phi = 0.5 * (1 + 0.21 * (lam - 0.2) + lam * lam)
        return 1 / (phi + math.sqrt(max(phi * phi - lam * lam, 0)))

    ud = {"profil": profil, "komb": {}, "u_snit": 0, "u_soejle": 0, "u_spaer": 0, "beta": beta, "kg": kg, "h": hh}
    kn_v, kn_o = r.knude(0, 0), r.knude(B, 0)
    for navn, f in KOMB.items():
        k = kombiner([res[x] for x in f], list(f.values()))
        rad = {"M": {}, "N": {}}
        for s in STAENGER:
            N, M = k["snit"][s]["N"], k["snit"][s]["M"]
            rad["M"][s] = float(np.abs(M).max())
            rad["N"][s] = float(N[np.abs(N).argmax()])
            ud["u_snit"] = max(ud["u_snit"], float((np.abs(N) / (NRd / GM0) + np.abs(M) / (MRd / GM0)).max()))
            Nc = max(0.0, float(-N.min()))
            Lcr = beta * SIDE if s in ("sv", "so") else 2 * s_len
            u = Nc / (chi(Lcr) * NRd / GM1) + rad["M"][s] / (MRd / GM1)
            if s in ("sv", "so"):
                ud["u_soejle"] = max(ud["u_soejle"], u)
            else:
                ud["u_spaer"] = max(ud["u_spaer"], u)
        rad["reak"] = (k["reak"][kn_v], k["reak"][kn_o])
        rad["Mhjoerne"] = float(abs(k["snit"]["sv"]["M"][-1]))
        rad["Mkip"] = float(abs(k["snit"]["tv"]["M"][-1]))
        ud["komb"][navn] = rad
    ud["f_kip"] = -float(res["S1"]["u"][3 * r.knude(B / 2, KIP) + 1]) * 1000           # mm, karakteristisk sne
    ud["f_side"] = max(abs(float(res["W1"]["u"][3 * r.knude(0, SIDE)])), abs(float(res["W1"]["u"][3 * r.knude(B, SIDE)]))) * 1000
    ud["ok"] = max(ud["u_snit"], ud["u_soejle"], ud["u_spaer"]) <= 1.0 and ud["f_kip"] <= B * 1000 / 200 and ud["f_side"] <= SIDE * 1000 / 150
    return ud


alle = [beregn(p) for p in IPE]
valgt = next(a for a in alle if a["ok"])
PROFIL, PH = valgt["profil"], valgt["h"] / 1000

# ---------------- Åse (konstruktionstræ C24) ----------------
AASE_S = [0.5, 1.7, 2.9, 4.1, 5.3]                    # placering målt langs spæret fra tagfod
C24 = {"fm": 24.0, "E": 11000.0}
KMOD, GM_TRAE = 0.9, 1.35                             # korttidslast (sne), DK NA (efter hukommelsen)


def aas(b_mm, h_mm, spaend, afstand=1.2):
    q_d = (1.0 * G_TAG + 1.5 * MU_W * SK * math.cos(ALFA)) * afstand * math.cos(ALFA)   # kN/m vinkelret på taget, regningsmæssig
    q_k = MU_W * SK * math.cos(ALFA) * afstand * math.cos(ALFA)                         # karakteristisk sne
    W, I = b_mm * h_mm ** 2 / 6, b_mm * h_mm ** 3 / 12
    sig = q_d * spaend ** 2 / 8 * 1e6 / W
    f = 5 * q_k * (spaend * 1000) ** 4 / (384 * C24["E"] * I)
    return sig / (KMOD * C24["fm"] / GM_TRAE), f, spaend * 1000 / 200


AASE_KAND = [(45, 195), (45, 220), (45, 245), (70, 220), (75, 225), (95, 220), (95, 245)]
aase_tab = {sp: [(b, hh, *aas(b, hh, sp)) for b, hh in AASE_KAND] for sp in (5.0, 4.0)}
AAS = next(((b, hh) for b, hh, u, f, fm in aase_tab[5.0] if u <= 1 and f <= fm), AASE_KAND[-1])

# ---------------- Fundamenter og afstivning ----------------
loeft = max(max(0.0, -rk[1]) for k in valgt["komb"].values() for rk in k["reak"])
tryk = max(max(rk[1] for rk in k["reak"]) for k in valgt["komb"].values())
vandret = max(abs(rk[0]) for k in valgt["komb"].values() for rk in k["reak"])
GAVLAREAL = B * SIDE + B * (KIP - SIDE) / 2
F_GAVL = 1.5 * QP * 1.0 * GAVLAREAL / 2               # regningsmæssig kraft til tagskiven fra én gavl (cpe +0,7 og -0,3)
F_VAEGKRYDS = F_GAVL / 2                              # pr. langside
N_DIAG = F_VAEGKRYDS / math.cos(math.atan(SIDE / 5.0))
LOEFT_KRYDS = F_VAEGKRYDS * SIDE / 5.0
loeft_ialt = loeft + LOEFT_KRYDS
# Gennemgående sokkel (stribefundament) hele vejen rundt, ingen punktfundamenter
SOK_B, SOK_DYBDE = 0.40, 0.90                         # bredde og dybde under terræn; soklen går SOKKEL over terræn
SOK_H = SOK_DYBDE + SOKKEL
sok_vaegt_m = SOK_B * SOK_H * 24                      # kN pr. m sokkel
L_LOEFT = 3.0                                         # sokkellængde, der regnes aktiveret mod løft ved en rammefod (forudsætter armeret sokkel)
fund_vaegt = sok_vaegt_m * L_LOEFT
fund_ok = 0.9 * fund_vaegt >= loeft_ialt
L_TRYK = 0.3 + 2 * SOK_H                              # trykspredning 1:1 gennem soklens højde
tryk_jord = (tryk + sok_vaegt_m * L_TRYK) / (L_TRYK * SOK_B)
FUND = (SOK_B, SOK_B, SOK_DYBDE)                      # bruges af tegningerne

# ---------------- Rapport ----------------
rap = [f"""# Overslagsberegning for hallens bærende konstruktion

Dannet automatisk af `tegninger/hal_teknisk.py` den 10. oktober 2026. Hører til tegningerne A1.2-A1.4.

**Dette er et overslag og ikke en statisk dokumentation.** Det viser størrelsesordener, så I kan tale med stålleverandør og rådgiver på et oplyst grundlag. Den endelige dimensionering skal laves af den, der påtager sig ansvaret for konstruktionen, og kan give andre dimensioner.

## 1. Forudsætninger

| | |
|---|---|
| Geometri | Spændvidde {dk(B)} m, sidehøjde {dk(SIDE)} m og kiphøjde {dk(KIP, 2)} m over soklens overkant (gulv), taghældning {dk(HAELD, 0)}°. Soklen går {dk(SOKKEL)} m over terræn, så kippen er {dk(KIP + SOKKEL, 2)} m over terræn |
| System | To-charniers stålramme (leddelt ved fundament, stive rammehjørner og kip), samme profil i søjler og spær |
| Rammeafstand | {dk(A_RAMME)} m (fem rammer). Beregnet for en mellemramme |
| Stål | S235, f_y = 235 MPa, γ_M0 = {dk(GM0)}, γ_M1 = {dk(GM1)} |
| Konsekvensklasse | CC2, K_FI = 1,0 |
| Egenlast | Tag {dk(G_TAG, 2)} kN/m² (paneler, åse, beslag), vægge {dk(G_VAEG, 2)} kN/m², plus rammens egenvægt |
| Sne | s_k = {dk(SK)} kN/m², C_e = C_t = 1,0. Jævn μ = {dk(MU1)}; omfordelt {dk(MU1)}/{dk(MU1 / 2)}; ophobning på vestlig tagflade μ_w = {dk(MU_W)} (DK NA 5.3.3(4)) |
| Vind | q_p = {dk(QP, 2)} kN/m² (v_b = 24 m/s, terrænkategori II, z = {dk(KIP + SOKKEL)} m) |
| Lastkombinationer | DS/EN 1990 DK NA: ψ0 = 0,3 for vind sammen med dominerende sne; ψ0 = 0 for sne sammen med dominerende vind |

Formfaktorer for vind (udvendig minus indvendig), efter hukommelsen fra DS/EN 1991-1-4 afsnit 7.2:

| Tilfælde | Søjle vest | Tag vest | Tag øst | Søjle øst |
|---|---|---|---|---|
""" + "\n".join(f"| {n} | {dk(c['sv'])} | {dk(c['tv'])} | {dk(c['to'])} | {dk(c['so'])} |" for n, c in VIND.items()) + f"""

W1: vind fra vest med tryk på vindsidens tag og indvendigt sug. W1e: samme fra øst. W2: vind fra vest med sug på taget og indvendigt overtryk. W3: vind langs kippen med sug på hele rammen og indvendigt overtryk. Positiv værdi er tryk ind mod bygningen. Åben port i storm er ikke regnet med.

## 2. Valg af rammeprofil

Krav: udnyttelse højst 1,0, nedbøjning i kip for karakteristisk sne højst L/200 = {dk(B * 1000 / 200, 0)} mm, og vandret udbøjning i tagfod for karakteristisk vind højst h/150 = {dk(SIDE * 1000 / 150, 0)} mm.

| Profil | kg/m | Tværsnit | Søjle (knæk i rammens plan) | Spær | Nedbøjning kip | Udbøjning tagfod | Opfylder |
|---|---|---|---|---|---|---|---|
""" + "\n".join(f"| {a['profil']} | {dk(a['kg'])} | {dk(a['u_snit'], 2)} | {dk(a['u_soejle'], 2)} | {dk(a['u_spaer'], 2)} | {dk(a['f_kip'], 0)} mm | {dk(a['f_side'], 0)} mm | {'ja' if a['ok'] else 'nej'} |" for a in alle) + f"""

**Mindste profil, der opfylder kravene i dette overslag: {PROFIL}.** Stålvægt for fem rammer: ca. {dk(5 * valgt['kg'] * (2 * SIDE + 2 * math.hypot(B / 2, KIP - SIDE)), 0)} kg.

Udnyttelserne er regnet som N/N_Rd + M/M_Rd med plastisk bøjningsmodstand. Søjlens knæklængde i rammens plan er sat til {dk(valgt['beta'], 2)} × søjlehøjden.

**Ikke eftervist:** kipning af spær og søjler, samlinger (rammehjørne, kip, fodplade), knæk ud af rammens plan, lokale forhold ved porten og gavlrammerne. Kipning kræver, at den trykkede inderflange ved rammehjørnet fastholdes, f.eks. med skråstivere fra åsene. Disse forhold kan øge profilet eller kræve udfligning af rammehjørnet, som på referencehallen.

## 3. Snitkræfter og reaktioner for {PROFIL}

| Lastkombination | M rammehjørne | M kip | N søjle | Lodret reaktion vest / øst | Vandret reaktion |
|---|---|---|---|---|---|
""" + "\n".join(f"| {n} | {dk(k['Mhjoerne'])} kNm | {dk(k['Mkip'])} kNm | {dk(k['N']['sv'])} kN | {dk(k['reak'][0][1])} / {dk(k['reak'][1][1])} kN | {dk(max(abs(k['reak'][0][0]), abs(k['reak'][1][0])))} kN |" for n, k in valgt["komb"].items()) + f"""

Normalkraft: træk er positivt. Lodret reaktion: positiv er tryk på fundamentet, negativ er løft.

## 4. Åse

Konstruktionstræ C24, {len(AASE_S)} åse pr. tagflade med ca. 1,2 m afstand langs spæret. Regnet som simpelt understøttede for ophobet sne (μ = {dk(MU_W)}) vinkelret på taget; lasten langs taget forudsættes optaget af tagpanelerne. k_mod = {dk(KMOD)}, γ_M = {dk(GM_TRAE, 2)}.

| Dimension | Spænd 5,0 m: udnyttelse | nedbøjning (krav {dk(5000 / 200, 0)} mm) | Spænd 4,0 m: udnyttelse | nedbøjning (krav {dk(4000 / 200, 0)} mm) |
|---|---|---|---|---|
""" + "\n".join(f"| {b} × {hh} mm | {dk(u5, 2)} | {dk(f5, 0)} mm | {dk(u4, 2)} | {dk(f4, 0)} mm |" for (b, hh, u5, f5, _), (_, _, u4, f4, _) in zip(aase_tab[5.0], aase_tab[4.0])) + f"""

Med 5 m mellem rammerne kræves ca. **{AAS[0]} × {AAS[1]} mm**. Det er kraftige åse; med 4 m rammeafstand (seks rammer) kan de blive mindre. Stålåse (Z- eller C-profiler) er et almindeligt alternativ ved 5 m. Tagpanelets tilladte spændvidde bestemmer den endelige åseafstand.

## 5. Fundamenter

| | |
|---|---|
| Største lodrette tryk fra rammen | {dk(tryk)} kN (regningsmæssigt) |
| Største løft fra rammen | {dk(loeft)} kN |
| Tillæg til løft i afstivede fag (vægkryds) | {dk(LOEFT_KRYDS)} kN |
| Største vandrette kraft i rammefod | {dk(vandret)} kN |
| Fundament | Gennemgående armeret betonsokkel hele vejen rundt, {dk(SOK_B, 2)} m bred, {dk(SOK_DYBDE)} m under terræn og {dk(SOKKEL)} m over. Ingen punktfundamenter |
| Soklens egenvægt | {dk(sok_vaegt_m)} kN/m |
| Kontrol af løft | {dk(L_LOEFT)} m sokkel regnes aktiveret ved hver rammefod: 0,9 × {dk(fund_vaegt)} = {dk(0.9 * fund_vaegt)} kN mod {dk(loeft_ialt)} kN: {'opfyldt' if fund_ok else 'IKKE opfyldt'} |
| Tryk på jorden under en rammefod | ca. {dk(tryk_jord, 0)} kN/m², når lasten spredes over {dk(L_TRYK)} m sokkel. Jordens bæreevne er ikke undersøgt |

Soklens underside ligger i 0,9 m dybde som forudsat frostsikker; for uopvarmede bygninger kan der kræves større dybde. Den vandrette kraft i rammefoden skal optages af fundamentet (jordtryk og friktion) eller af et trækbånd i gulvet mellem modstående fundamenter. Løftet forudsætter, at soklen er armeret i længderetningen, så den kan fordele kræfterne fra rammefoden, og at søjlens fodplade er forankret i soklen. Soklen bærer også vægpanelerne.

## 6. Afstivning i længderetningen

Rammerne er kun stive på tværs. Vind på gavlene føres via et vindgitter i tagfladen til vægkryds i langsiderne.

| | |
|---|---|
| Gavlareal | {dk(GAVLAREAL)} m² |
| Regningsmæssig kraft til tagets vindgitter fra én gavl | {dk(F_GAVL)} kN |
| Kraft pr. langside | {dk(F_VAEGKRYDS)} kN |
| Træk i vægdiagonal (fag 5,0 × 4,0 m) | {dk(N_DIAG)} kN |
| Rundstål Ø16 S235, bæreevne ca. 157 mm² × 235 / 1,1 | {dk(157 * 235 / 1.1 / 1000)} kN: {'tilstrækkeligt' if 157 * 235 / 1.1 / 1000 >= N_DIAG else 'for lidt'} |

Der er tegnet krydsafstivning i ét fag i hver langside og i tagfladen i samme fag. Når vægpanelerne skrues direkte på søjlerne uden rigler, findes der ingen andre dele, der kan overføre kræfterne, så krydsene er nødvendige, medmindre leverandøren dokumenterer panelernes skivevirkning.

## 7. Det skal den projekterende tage stilling til

1. Rammeafstand: 5 m giver kraftige åse og kræver ca. 120 mm vægpanel; 4 m letter begge dele.
2. Kipning og samlinger, som ikke er eftervist her.
3. Om det danske tillæg for sneophobning gælder (åbent terræn 400 m mod øst).
4. Åben eller lukket port i storm.
5. Gavlrammerne: stolper og overligger ved porten (4,0 × 4,0 m) og fastgørelse af gavlpanelerne.
6. Jordbundsforhold og funderingsdybde.
7. Konsekvensklasse (CC2 er forudsat).
"""]
(HER.parent / "docs" / "hal-statik-overslag.md").write_text(rap[0], encoding="utf-8")

# ================= TEGNINGER =================
VAEG, TAG, SOKKELF, PORTF = "#2a2c2f", "#1f2023", "#b9b9b4", "#565a60"


def maal(ax, p, q, tekst, off=(0, 0), rot=0, fs=6.5):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0), zorder=6)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=fs, ha="center", va="center", rotation=rot)


def ark(maalestok, format_mm=(420, 297)):
    """Ét ark, hvor 1 enhed = 1 meter i den givne målestok."""
    fig = plt.figure(figsize=(format_mm[0] / 25.4, format_mm[1] / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, format_mm[0] * maalestok / 1000)
    ax.set_ylim(0, format_mm[1] * maalestok / 1000)
    ax.set_aspect("equal")
    ax.axis("off")
    return fig, ax


# ---------- A1.2 Facader 1:100 ----------
fig, ax = ark(100)


def gavl(ox, oy, titel, port, doer_hoejre):
    ty, oy = oy, oy + SOKKEL                         # ty = terræn, oy = soklens overkant og gulv
    ax.plot([ox - 2, ox + B + 2], [ty, ty], color="black", lw=0.8)
    ax.add_patch(Polygon([(ox, oy), (ox + B, oy), (ox + B, oy + SIDE), (ox + B / 2, oy + KIP), (ox, oy + SIDE)], closed=True, fc=VAEG, ec="black", lw=0.8))
    ax.add_patch(Rectangle((ox, ty), B, SOKKEL, fc=SOKKELF, ec="black", lw=0.5))
    if port:                                         # fliseplads foran port og dør, i gulvhøjde
        ax.add_patch(Polygon([(ox - SIDEUDFALD, ty), (ox, oy), (ox + B, oy), (ox + B + SIDEUDFALD, ty)], closed=True, fc="#d8d4c8", ec="black", lw=0.5, hatch="||"))
        ax.text(ox + B + SIDEUDFALD + 0.2, ty + 0.25, "fliserampe, falder\nfrem og til siderne", fontsize=5.5, va="center")
    z = 1.0
    while z < KIP:
        d = 0 if z <= SIDE else (z - SIDE) / math.tan(ALFA)
        ax.plot([ox + d, ox + B - d], [oy + z, oy + z], color="#6a6d72", lw=0.3)
        z += 1.0
    if port:
        ax.add_patch(Rectangle((ox + B / 2 - 2, oy + 0.03), 4.0, 4.0, fc=PORTF, ec="#cfcfcf", lw=0.8))
        for zz in np.arange(0.5, 4.0, 0.5):
            ax.plot([ox + B / 2 - 2, ox + B / 2 + 2], [oy + zz, oy + zz], color="#8c8f94", lw=0.3)
        x0 = ox + B - 1.5 if doer_hoejre else ox + 0.6
        ax.add_patch(Rectangle((x0, oy + 0.03), 0.9, 2.1, fc=PORTF, ec="#cfcfcf", lw=0.8))
        maal(ax, (ox + B / 2 - 2, ty - 0.7), (ox + B / 2 + 2, ty - 0.7), "port 4,0", (0, -0.35))
    maal(ax, (ox, ty - 1.6), (ox + B, ty - 1.6), f"{dk(B)} m", (0, -0.35))
    maal(ax, (ox - 0.9, ty), (ox - 0.9, oy + SIDE), dk(SIDE + SOKKEL), (-0.45, 0), 90)
    maal(ax, (ox - 1.9, ty), (ox - 1.9, oy + KIP), dk(KIP + SOKKEL, 2), (-0.45, 0), 90)
    ax.text(ox, oy + KIP + 0.9, titel, fontsize=9, weight="bold")


def langside(ox, oy, titel, nord_hoejre):
    ty, oy = oy, oy + SOKKEL                         # ty = terræn, oy = soklens overkant og gulv
    ax.plot([ox - 2, ox + L + 2 + (5 if nord_hoejre else 0)], [ty, ty], color="black", lw=0.8)
    ax.add_patch(Rectangle((ox, oy), L, SIDE, fc=VAEG, ec="black", lw=0.8))
    ax.add_patch(Rectangle((ox, ty), L, SOKKEL, fc=SOKKELF, ec="black", lw=0.5))
    x0, r = (ox + L, 1) if nord_hoejre else (ox, -1)   # fliseplads og rampe foran nordgavlen
    ax.add_patch(Polygon([(x0, ty), (x0, oy), (x0 + r * FORPLADS[0], oy), (x0 + r * sum(FORPLADS), ty)], closed=True, fc="#d8d4c8", ec="black", lw=0.5))
    ax.text(x0 + r * 0.2, ty - 0.45, "fliserampe fra port til kørevej", fontsize=5.5, ha="left" if nord_hoejre else "right", va="center")
    ax.add_patch(Rectangle((ox - 0.15, oy + SIDE), L + 0.3, KIP - SIDE, fc=TAG, ec="black", lw=0.8))
    for z in (1.0, 2.0, 3.0):
        ax.plot([ox, ox + L], [oy + z, oy + z], color="#6a6d72", lw=0.3)
    for x in np.arange(1.0, L, 1.0):
        ax.plot([ox + x, ox + x], [oy + SIDE, oy + KIP], color="#4a4d52", lw=0.25)
    maal(ax, (ox, ty - 1.0), (ox + L, ty - 1.0), f"{dk(L)} m", (0, -0.35))
    mx_ = ox - 1.0 if nord_hoejre else ox + L + 1.0   # højdemål i den ende, hvor fliseplads og rampe ikke ligger
    r_ = -1 if nord_hoejre else 1
    maal(ax, (mx_, ty), (mx_, oy + SIDE), dk(SIDE + SOKKEL), (0.45 * r_, 0), 90)
    maal(ax, (mx_ + r_, ty), (mx_ + r_, oy + KIP), dk(KIP + SOKKEL, 2), (0.45 * r_, 0), 90)
    ax.text(ox, oy + KIP + 0.9, titel, fontsize=9, weight="bold")


gavl(4.0, 17.0, "Facade mod nord (port og dør mod ridebanen)", True, True)       # set fra nord er vest til højre
langside(17.5, 17.0, "Facade mod øst", True)             # set fra øst er nord til højre
gavl(4.0, 5.0, "Facade mod syd (ingen åbninger)", False, False)
langside(17.5, 5.0, "Facade mod vest", False)
ax.text(1.5, 28.2, "Ny hal, facader", fontsize=13, weight="bold")
ax.text(1.5, 27.4, f"Vægge: sorte, matte sandwichpaneler, vandrette, 1 m høje. Tag: sorte sandwichpaneler, {dk(HAELD, 0)}°. Sokkel: beton {dk(SOKKEL)} m over terræn; gulv i soklens overkant. Sidehøjde {dk(SIDE)} m over sokkel. Højder i meter over terræn.", fontsize=7.5)
ax.text(1.5, 1.4, "Terræn er forudsat vandret. Panelernes dækbredde (FALK 1060 WB er 1,06 m) og portens endelige højde fastlægges i byggeansøgningen.", fontsize=7, color="#444444")
tegningshoved(fig, "Ny hal, facader", "1 : 100 (A3)", "A1.2")
fig.savefig(HER / "hal_facader.pdf")
fig.savefig(HER / "hal_facader.png", dpi=130)
plt.close(fig)

# ---------- A1.3 Snit 1:50 med hovedresultater ----------
fig, ax = ark(50)
OX, OY = 2.2, 4.3
P = lambda x, z: (OX + x, OY + z)
for xa, xb in ((OX - 1.3, OX), (OX + B, OX + B + 1.3)):        # terræn uden for hallen, SOKKEL under gulv
    ax.plot([xa, xb], [OY - SOKKEL, OY - SOKKEL], color="black", lw=0.9)
ax.text(OX - 1.25, OY - SOKKEL + 0.1, "terræn", fontsize=5.5)
# fundamenter, sokkel og gulv
ax.add_patch(Rectangle((OX + 0.37, OY - 0.12), B - 0.74, 0.12, fc="#cfcfcf", ec="black", lw=0.5))
ax.add_patch(Rectangle((OX + 0.37, OY - 0.32), B - 0.74, 0.20, fc="#efe7d3", ec="#888888", lw=0.3, hatch="oo"))
ax.text(OX + B / 2, OY - 0.06, "betongulv 120 mm", fontsize=5.5, ha="center", va="center")
ax.text(OX + B / 2, OY - 0.22, "kapillarbrydende lag", fontsize=5.5, ha="center", va="center")
# ramme: søjler og spær med udfligning
t = math.tan(ALFA)
for sx in (lambda x: x, lambda x: B - x):
    ax.add_patch(Polygon([P(sx(0.15), 0), P(sx(0.15 + PH), 0), P(sx(0.15 + PH), SIDE - 0.55), P(sx(0.15), SIDE - 0.1)], closed=True, fc="#1c1d1f", ec="black", lw=0.6, zorder=4))
    ov = lambda x: SIDE - 0.1 + (x - 0.15) * t                    # spærets overside
    ax.add_patch(Polygon([P(sx(0.15), ov(0.15)), P(sx(B / 2), ov(B / 2)), P(sx(B / 2), ov(B / 2) - PH / math.cos(ALFA)), P(sx(1.6), ov(1.6) - PH / math.cos(ALFA) - 0.05), P(sx(0.15 + PH), SIDE - 0.9)],
                         closed=True, fc="#1c1d1f", ec="black", lw=0.6, zorder=4))
    # åse og tagpanel
    for s in AASE_S:
        x, z = 0.15 + s * math.cos(ALFA), SIDE - 0.1 + s * math.sin(ALFA)
        hj = [(0, 0), (AAS[0] / 1000, 0), (AAS[0] / 1000, AAS[1] / 1000), (0, AAS[1] / 1000)]
        rot = [(x + a * math.cos(ALFA) - b * math.sin(ALFA), z + a * math.sin(ALFA) + b * math.cos(ALFA)) for a, b in hj]
        ax.add_patch(Polygon([P(sx(px), pz) for px, pz in rot], closed=True, fc="#c9a66b", ec="#5a4520", lw=0.4, zorder=5))
    top = AAS[1] / 1000 / math.cos(ALFA)
    ax.add_patch(Polygon([P(sx(-0.25), SIDE - 0.33 + top), P(sx(B / 2), ov(B / 2) + top), P(sx(B / 2), ov(B / 2) + top + 0.115), P(sx(-0.25), SIDE - 0.33 + top + 0.115)],
                         closed=True, fc="#e4e6e7", ec="black", lw=0.5, zorder=3))
    # vægpanel og sokkel
    ax.add_patch(Rectangle(P(min(sx(0.0), sx(0.12)), 0)[0:2], 0.12, SIDE + 0.15, fc="#e4e6e7", ec="black", lw=0.5, zorder=3))
    ax.add_patch(Rectangle(P(min(sx(-0.03), sx(-0.03 + SOK_B)), -SOK_H), SOK_B, SOK_H, fc="#d9d9d9", ec="black", lw=0.6, hatch="...", zorder=2))
maal(ax, P(0, -1.5), P(B, -1.5), f"{dk(B)} m", (0, -0.2), fs=7)
maal(ax, P(-0.9, 0), P(-0.9, SIDE), f"{dk(SIDE)} m over gulv", (-0.25, 0), 90, fs=7)
maal(ax, P(B + 0.9, -SOKKEL), P(B + 0.9, KIP), f"{dk(KIP + SOKKEL, 2)} m over terræn", (0.25, 0), 90, fs=7)
maal(ax, P(-0.9, -SOK_H), P(-0.9, -SOKKEL), dk(SOK_DYBDE), (-0.25, 0), 90, fs=6)
maal(ax, P(-0.9, -SOKKEL), P(-0.9, 0), dk(SOKKEL), (-0.25, 0), 90, fs=6)


def note(tekst, xz, txz):
    ax.annotate(tekst, xy=P(*xz), xytext=P(*txz), fontsize=6.5, ha="left", va="center", arrowprops=dict(arrowstyle="-", lw=0.4), zorder=7,
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="#888888", lw=0.4))


note(f"Stålramme {PROFIL}, S235\nstive hjørner med udfligning", (1.2, SIDE + 0.45), (2.3, 2.6))
note(f"Åse C24 {AAS[0]} × {AAS[1]} mm\npr. ca. 1,2 m", (B / 2 + 1.9, KIP - 1.05), (5.6, 3.6))
note("Tagpanel, sort (sandwich)", (B / 2 + 3.0, KIP - 1.35), (6.8, 6.6))
note("Vægpanel 1 m, sort,\nskruet på søjlerne", (B - 0.06, 2.0), (6.6, 1.6))
note(f"Gennemgående sokkel hele vejen rundt,\narmeret beton {dk(SOK_B, 2)} × {dk(SOK_H)} m,\noverkant {dk(SOKKEL)} m over terræn = gulv", (0.15, -0.5), (1.5, -1.0))
ax.text(OX, OY + KIP + 1.0, "Snit A-A gennem en mellemramme (set mod nord)", fontsize=10, weight="bold")
# resultatboks
bx, by = 14.2, 12.6
k1 = valgt["komb"]
linjer = [
    ("OVERSLAGSBEREGNING, hovedresultater", True),
    (f"Ramme: {PROFIL} S235, rammeafstand {dk(A_RAMME)} m", False),
    (f"Sne: s_k = {dk(SK)} kN/m², μ = {dk(MU1)} (jævn) og {dk(MU_W)} (ophobning vest)", False),
    (f"Vind: q_p = {dk(QP, 2)} kN/m²", False),
    ("", False),
    (f"Største moment i rammehjørne: {dk(max(k['Mhjoerne'] for k in k1.values()))} kNm", False),
    (f"Største moment i kip: {dk(max(k['Mkip'] for k in k1.values()))} kNm", False),
    (f"Udnyttelse tværsnit / søjle / spær: {dk(valgt['u_snit'], 2)} / {dk(valgt['u_soejle'], 2)} / {dk(valgt['u_spaer'], 2)}", False),
    (f"Nedbøjning kip (sne): {dk(valgt['f_kip'], 0)} mm (krav {dk(B * 5, 0)} mm)", False),
    (f"Udbøjning tagfod (vind): {dk(valgt['f_side'], 0)} mm (krav {dk(SIDE * 1000 / 150, 0)} mm)", False),
    ("", False),
    (f"Fundament: gennemgående sokkel {dk(SOK_B, 2)} × {dk(SOK_H)} m", False),
    (f"Reaktioner pr. rammefod (regningsmæssige):", False),
    (f"  tryk {dk(tryk)} kN, løft {dk(loeft)} kN, vandret {dk(vandret)} kN", False),
    (f"Åse: C24 {AAS[0]} × {AAS[1]} mm ved 5 m spænd", False),
    (f"Vægkryds: træk {dk(N_DIAG)} kN i diagonal", False),
    ("", False),
    ("Ikke eftervist: kipning, samlinger, gavlrammer, port,", False),
    ("jordens bæreevne. Se docs/hal-statik-overslag.md.", False),
]
ax.add_patch(Rectangle((bx - 0.2, by - 0.33 * len(linjer) - 0.1), 6.6, 0.33 * len(linjer) + 0.45, fc="#fbfbf7", ec="#888888", lw=0.6))
for i, (tx, fed) in enumerate(linjer):
    ax.text(bx, by - 0.33 * i, tx, fontsize=6.8, weight="bold" if fed else "normal", va="center")
# momentkurve for den værste snekombination
navn_k = "K2  1,0 G + 1,5 S(ophobning vest) + 0,45 W(fra øst)"
A_, I_ = IPE[PROFIL][0], IPE[PROFIL][1]
rr = Ramme()
pts = {"sv": ((0, 0), (0, SIDE)), "tv": ((0, SIDE), (B / 2, KIP)), "to": ((B / 2, KIP), (B, SIDE)), "so": ((B, SIDE), (B, 0))}
for s, (p0, p1) in pts.items():
    rr.stang(s, p0, p1, E_STAAL * A_ * 1e-4, E_STAAL * I_ * 1e-8)
rr.understoet((0, 0))
rr.understoet((B, 0))
Fk = (rr.last(["tv", "to"], "g", G_TAG * A_RAMME) + rr.last(["sv", "so"], "g", G_VAEG * A_RAMME) + rr.last(STAENGER, "g", IPE[PROFIL][5] * 9.81 / 1000)
      + 1.5 * rr.last(["tv"], "plan", MU_W * SK * A_RAMME) + 0.45 * sum(rr.last([s], "normal", VIND["W1e"][s] * QP * A_RAMME, NORMAL) for s in STAENGER))
rk = rr.loes(Fk)
mx, mz, sk_ = 14.6, 1.6, 0.42            # lille figur: skala 0,42
Mmax = max(abs(rk["snit"][s]["M"]).max() for s in STAENGER)
for s, (p0, p1) in pts.items():
    M = rk["snit"][s]["M"]
    n = len(M) // 2
    xs = [p0[0] + (p1[0] - p0[0]) * (i // 2 + i % 2) / n for i in range(2 * n)]
    zs = [p0[1] + (p1[1] - p0[1]) * (i // 2 + i % 2) / n for i in range(2 * n)]
    Ls = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
    nx, nz = -(p1[1] - p0[1]) / Ls, (p1[0] - p0[0]) / Ls
    poly = [(mx + x * sk_, mz + z * sk_) for x, z in zip(xs, zs)] + [(mx + (x + nx * m / Mmax * 1.6) * sk_, mz + (z + nz * m / Mmax * 1.6) * sk_) for x, z, m in reversed(list(zip(xs, zs, M)))]
    ax.add_patch(Polygon(poly, closed=True, fc="#f2c9c9", ec="#b03030", lw=0.5))
    ax.plot([mx + p0[0] * sk_, mx + p1[0] * sk_], [mz + p0[1] * sk_, mz + p1[1] * sk_], color="black", lw=1.2)
ax.text(mx, mz + KIP * sk_ + 0.75, f"Momentkurve, {navn_k.split('  ')[0]} (sneophobning på vestlig tagflade)\nstørste moment {dk(Mmax)} kNm", fontsize=6.8, va="center")
ax.text(1.0, 0.75, "Overslagsberegning. Profiler, åse og fundamenter er vejledende og fastlægges af den projekterende i byggeansøgningen.", fontsize=7, color="#444444")
tegningshoved(fig, "Ny hal, snit A-A og overslag", "1 : 50 (A3)", "A1.3")
fig.savefig(HER / "hal_snit.pdf")
fig.savefig(HER / "hal_snit.png", dpi=130)
plt.close(fig)

# ---------- A1.4 Ramme- og åseplan samt fundamentsplan 1:100 ----------
fig, ax = ark(100)
PORT_NORD = h_cfg.get("port_mod") == "nord"


def plan(ox, oy, titel, fundament):
    Q = lambda x, y: (ox + x, oy + y)
    ax.add_patch(Rectangle(Q(0, 0), B, L, fc="#fafafa", ec="black", lw=1.0))
    ax.text(ox, oy + L + 1.3, titel, fontsize=9, weight="bold")
    yport = L if PORT_NORD else 0
    ax.plot([ox + B / 2 - 2, ox + B / 2 + 2], [oy + yport, oy + yport], color="#cc0000", lw=2.5, solid_capstyle="butt", zorder=6)
    ax.text(ox + B / 2, oy + yport + (0.5 if PORT_NORD else -0.5), "port", fontsize=6, color="#cc0000", ha="center", va="center")
    for i, y in enumerate(RAMMER_Y, 1):
        if fundament:
            for x in (0.15, B - 0.15):          # rammefod med fodplade på soklen
                ax.add_patch(Rectangle(Q(x - 0.15, y - 0.15), 0.3, 0.3, fc="#1c1d1f", ec="black", lw=0.5, zorder=4))
        else:
            ax.plot([ox, ox + B], [oy + y, oy + y], color="#1c1d1f", lw=2.2, zorder=4)
        ax.text(ox + B + 0.6, oy + y, f"R{i}", fontsize=7, va="center", ha="left")
    if fundament:
        for x_, y_, w_, h_ in ((0, 0, B, SOK_B), (0, L - SOK_B, B, SOK_B), (0, 0, SOK_B, L), (B - SOK_B, 0, SOK_B, L)):      # gennemgående sokkel
            ax.add_patch(Rectangle(Q(x_, y_), w_, h_, fc="#d9d9d9", ec="black", lw=0.5, hatch="...", zorder=2))
        ax.add_patch(Rectangle(Q(SOK_B, SOK_B), B - 2 * SOK_B, L - 2 * SOK_B, fc="#eeeeee", ec="#888888", lw=0.4, ls="--", zorder=1))
        ax.text(ox + B / 2, oy + L / 2, "betongulv 120 mm\npå kapillarbrydende lag", fontsize=6.5, ha="center", va="center")
        ax.text(ox + B / 2, oy + 2.2, f"gennemgående sokkel\n{dk(SOK_B, 2)} × {dk(SOK_H)} m hele vejen rundt,\nogså under porten", fontsize=6, ha="center", va="center")
        for x in (B / 2 - 2, B / 2 + 2):          # portstolper på soklen
            ax.add_patch(Rectangle(Q(x - 0.1, yport - (SOK_B if PORT_NORD else 0) + SOK_B / 2 - 0.1), 0.2, 0.2, fc="#1c1d1f", ec="black", zorder=4))
    else:
        for s in AASE_S:                          # åse
            for x in (0.15 + s * math.cos(ALFA), B - 0.15 - s * math.cos(ALFA)):
                ax.plot([ox + x, ox + x], [oy, oy + L], color="#b08d57", lw=1.0, zorder=3)
        ax.plot([ox + B / 2, ox + B / 2], [oy, oy + L], color="#555555", lw=0.6, ls="-.", zorder=3)
        ax.text(ox + B / 2 + 0.15, oy + L / 2, "kip", fontsize=6, rotation=90, va="center")
        y0, y1 = RAMMER_Y[1], RAMMER_Y[2]         # afstivet fag: vindgitter i taget og vægkryds
        for xa, xb in ((0, B / 2), (B / 2, B)):
            ax.plot([ox + xa, ox + xb], [oy + y0, oy + y1], color="#1f5fa8", lw=0.9, zorder=5)
            ax.plot([ox + xa, ox + xb], [oy + y1, oy + y0], color="#1f5fa8", lw=0.9, zorder=5)
        for x in (-0.45, B + 0.45):
            ax.plot([ox + x, ox + x], [oy + y0, oy + y1], color="#1f5fa8", lw=3.0, zorder=5)
        ax.text(ox - 0.9, oy + (y0 + y1) / 2, "vægkryds", fontsize=6, color="#1f5fa8", rotation=90, ha="center", va="center")
        ax.text(ox + B / 4, oy + (y0 + y1) / 2 + 1.6, "vindgitter\ni tagfladen", fontsize=6, color="#1f5fa8", ha="center", va="center",
                bbox=dict(fc="white", ec="none", alpha=0.8, pad=0.5))
        for x in (B / 2 - 2, B / 2 + 2):          # portstolper
            ax.add_patch(Rectangle(Q(x - 0.1, yport - 0.1), 0.2, 0.2, fc="#1c1d1f", ec="black", zorder=6))
    maal(ax, Q(0, -1.3), Q(B, -1.3), f"{dk(B)}", (0, -0.35))
    for ya, yb in zip(RAMMER_Y[:-1], RAMMER_Y[1:]):
        maal(ax, Q(-1.6, ya), Q(-1.6, yb), dk(yb - ya, 2), (-0.4, 0), 90, fs=6)
    maal(ax, Q(-2.7, 0), Q(-2.7, L), f"{dk(L)}", (-0.4, 0), 90)


plan(5.5, 4.9, "Ramme- og åseplan", False)
plan(22.0, 4.9, "Fundamentsplan", True)
tx = 34.3
tekst = [("Konstruktionsdele (overslag)", True), (f"Rammer R1-R5: {PROFIL}, S235", False), ("  to-charniers, stive hjørner", False),
         (f"Åse: C24 {AAS[0]} × {AAS[1]} mm,", False), (f"  {len(AASE_S)} pr. tagflade", False), ("Vindgitter og vægkryds:", False), ("  rundstål Ø16 i fag R2-R3", False),
         ("Portstolper og overligger:", False), ("  ikke dimensioneret", False), ("Gennemgående sokkel:", False), (f"  {dk(SOK_B, 2)} × {dk(SOK_H)} m, armeret", False),
         ("  ingen punktfundamenter", False), ("", False), ("Gavlrammerne R1 og R5 har", False), ("halv belastningsbredde, men", False), ("bærer gavlpaneler og port.", False)]
ax.add_patch(Rectangle((tx - 0.3, 24.6 - 0.62 * len(tekst)), 7.2, 0.62 * len(tekst) + 0.7, fc="#fbfbf7", ec="#888888", lw=0.6))
for i, (s, fed) in enumerate(tekst):
    ax.text(tx, 24.6 - 0.62 * i, s, fontsize=7, weight="bold" if fed else "normal", va="center")
ax.text(1.5, 28.2, "Ny hal, konstruktionsplaner", fontsize=13, weight="bold")
ax.text(1.5, 1.4, "Vejledende dimensioner fra overslagsberegningen. Rammeafstand, afstivning og fundamenter fastlægges af den projekterende i byggeansøgningen.", fontsize=7, color="#444444")
nordpil(fig, 0.955, 0.905, vinkel=1.6)
tegningshoved(fig, "Ny hal, ramme-, åse- og fundamentsplan", "1 : 100 (A3)", "A1.4")
fig.savefig(HER / "hal_konstruktion.pdf")
fig.savefig(HER / "hal_konstruktion.png", dpi=130)
plt.close(fig)

print(f"Valgt ramme: {PROFIL} (tværsnit {valgt['u_snit']:.2f}, søjle {valgt['u_soejle']:.2f}, spær {valgt['u_spaer']:.2f}, kip {valgt['f_kip']:.0f} mm, tagfod {valgt['f_side']:.0f} mm)")
print(f"Åse {AAS[0]}x{AAS[1]}; tryk {tryk:.1f} kN, løft {loeft:.1f} + {LOEFT_KRYDS:.1f} kN, vandret {vandret:.1f} kN; fundament ok: {fund_ok}")
