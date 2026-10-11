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
from nordpil import nordpil
from tegningshoved import tegningshoved

BYGNINGSDREJNING = 1.6   # planen følger bygningerne, som ligger ca. 1,6 grader drejet fra stik nord

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
# (navn, type, x, y, bredde øst-vest, længde nord-syd) – egne mål uden friplads, anslået fra ejers fotos IMG_3005-3010 og P_20220430
# Plankoordinater: x = 0 er hallens østvæg og x = B vestvæggen (mod huset), y = 0 er portgavlen, når porten vender mod nord.
# Traktoren står i midten lige inden for porten, så der ikke er et fælles kørselsareal; den køres ud, når noget bagved skal ud.
# Alt til ejendommens drift står mod nord og øst; det private er samlet i sydvest: lift, trailer 1 og det vestlige rum.
DRIFT = [
    ("Traktor med\nfrontlæsser\n4,8 × 2,1 m", "traktor", 3.95, 0.60, 2.1, 4.8),
    ("Balleflytter\n(wrapballer)\n3,0 × 1,9 m", "balleflytter", 4.05, 5.80, 1.9, 3.0),
    ("Halmballe-elevator (transportbånd) 8,0 × 0,9 m", "elevator", 0.25, 0.50, 0.9, 8.0),
    ("Plæne-\ntraktor\n2,0 × 1,3", "klipper", 1.45, 0.60, 1.3, 2.0),
    ("Møgtrailer\n3,3 × 1,6 m", "trailer_rust", 1.30, 3.00, 1.6, 3.3),
    ("Plæne-\ntraktor\n2,3 × 1,2", "klipper", 1.50, 6.55, 1.2, 2.3),
    ("Hestetrailer\n5,0 × 2,1 m", "trailer", 0.40, 10.60, 2.1, 5.0),
    ("Ladtrailer med kapel,\n3 aksler (hø, halm, wrap)\n8,0 × 2,55 m", "kapeltrailer", 7.25, 1.40, 2.55, 8.0),
    ("Redskaber og\nridebaneharve\n2,3 × 1,7 m", "redskab", 8.00, 9.70, 1.7, 2.3),
]
PRIVAT = [
    ("Trailer 1\n3,6 × 1,7 m", "trailer", 8.00, 12.25, 1.7, 3.6),
]
LIFT = (4.10, 9.90, 3.6, 6.0)        # lift/værksted for enden af midterbanen
RUMDEL = 5.0                         # skillevæg i det lukkede rum: øst = foder, udstyr, værktøj og toilet (drift), vest = privat
TOILET = (ix0, iy1 - 1.8, 1.5, 1.8)
# Private zoner i den åbne hal (til arealopgørelsen), inkl. friplads
PRIVATZONER = [
    (7.90, 12.15, ix1 - 7.90, h_y1 - 12.15),   # trailer 1
]

fig = plt.figure(figsize=(A4[0] / 25.4, A4[1] / 25.4))
felt = (15, 42, 180, 245)
ax = fig.add_axes([felt[0] / A4[0], felt[1] / A4[1], felt[2] / A4[0], felt[3] / A4[1]])
bm, hm = felt[2] * MAALESTOK / 1000, felt[3] * MAALESTOK / 1000
VENDT = h.get("port_mod") == "nord"      # porten mod nord: hele planen drejes 180 grader, så nord stadig er op på arket
ax.set_xlim(B / 2 - bm / 2, B / 2 + bm / 2)
ax.set_ylim(L / 2 - hm / 2 - 0.3, L / 2 + hm / 2 - 0.3)
if VENDT:
    ax.invert_xaxis()
    ax.invert_yaxis()
ax.set_aspect("equal")
ax.axis("off")


def vaeg(x, y, w, hh):
    ax.add_patch(Rectangle((x, y), w, hh, fc="#333333", ec="none", zorder=3))


def aabning(x, y, w, hh):
    ax.add_patch(Rectangle((x, y), w, hh, fc="white", ec="none", zorder=4))


def port(p, q, tekst, tx, ty):
    ax.plot([p[0], q[0]], [p[1], q[1]], color="#cc0000", lw=1.8, zorder=5)
    ax.text(tx, ty, tekst, fontsize=6, ha="center", va="center", color="#cc0000")


def hjul(x, y, w=0.28, l=0.6, fc="#222222"):
    ax.add_patch(Rectangle((x, y), w, l, fc=fc, ec="none", zorder=2.6))


def ting(navn, type_, x, y, w, hh, fc):
    """Tegner en maskine set oppefra, forenklet efter ejers fotos. Det stiplede felt er maskinens egne mål."""
    ax.add_patch(Rectangle((x, y), w, hh, fc=fc, ec="#666666", lw=0.6, ls="--", zorder=2))
    Z = dict(zorder=2.5)
    if type_ == "traktor":                                  # bagende mod porten, frontlæsser mod syd
        ax.add_patch(Rectangle((x + 0.45, y + 0.3), w - 0.9, 2.9, fc="#3f6f3a", ec="#222222", lw=0.5, **Z))
        ax.add_patch(Rectangle((x + 0.35, y + 0.35), w - 0.7, 1.3, fc="#cfd8dc", ec="#222222", lw=0.5, **Z))      # førerhus
        for hx in (x, x + w - 0.45):
            hjul(hx, y + 0.2, 0.45, 1.5)                    # baghjul
        for hx in (x + 0.15, x + w - 0.45):
            hjul(hx, y + 2.4, 0.30, 0.8)                    # forhjul
        for hx in (x + 0.5, x + w - 0.6):
            ax.add_patch(Rectangle((hx, y + 3.0), 0.1, 1.4, fc="#222222", ec="none", **Z))                        # læsserarme
        ax.add_patch(Rectangle((x + 0.1, y + 4.3), w - 0.2, 0.45, fc="#555555", ec="#222222", lw=0.5, **Z))       # skovl/ballespyd
    elif type_ == "balleflytter":                           # sort A-ramme på to brede hjul, trækstang mod porten, to røde spyd bagud
        hjul(x, y + 1.6, 0.35, 0.7)
        hjul(x + w - 0.35, y + 1.6, 0.35, 0.7)
        ax.plot([x + 0.3, x + w - 0.3], [y + 1.95, y + 1.95], color="#111111", lw=1.6, **Z)
        ax.plot([x + 0.4, x + w / 2, x + w - 0.4], [y + 1.95, y + 0.1, y + 1.95], color="#111111", lw=1.2, **Z)
        for hx in (x + 0.55, x + w - 0.55):
            ax.plot([hx, hx], [y + 1.95, y + hh - 0.05], color="#cc2222", lw=1.6, **Z)
    elif type_ == "elevator":                               # langt rødt transportbånd
        ax.add_patch(Rectangle((x + 0.15, y + 0.1), w - 0.3, hh - 0.2, fc="#c8553d", ec="#7a2e1e", lw=0.5, **Z))
        yy = y + 0.4
        while yy < y + hh - 0.2:
            ax.plot([x + 0.15, x + w - 0.15], [yy, yy], color="#7a2e1e", lw=0.3, zorder=2.6)
            yy += 0.4
    elif type_ == "klipper":                                # gul plænetraktor med sort sæde
        ax.add_patch(Rectangle((x + 0.15, y + 0.15), w - 0.3, hh - 0.3, fc="#f0b323", ec="#222222", lw=0.5, **Z))
        if w > hh:                                          # står på tværs
            ax.add_patch(Rectangle((x + 0.6, y + 0.35), 0.6, hh - 0.7, fc="#222222", ec="none", zorder=2.7))
            for hy in (y + 0.02, y + hh - 0.24):
                hjul(x + 0.25, hy, 0.5, 0.22)
                hjul(x + w - 0.75, hy, 0.5, 0.22)
        else:
            ax.add_patch(Rectangle((x + 0.35, y + 0.6), w - 0.7, 0.6, fc="#222222", ec="none", zorder=2.7))
            for hx in (x + 0.02, x + w - 0.24):
                hjul(hx, y + 0.25, 0.22, 0.5)
                hjul(hx, y + hh - 0.75, 0.22, 0.5)
    elif type_ in ("trailer", "trailer_rust", "kapeltrailer"):
        trk = 1.4 if type_ == "kapeltrailer" else 1.0      # trækstang mod porten
        farve = {"trailer": "#c9ccd1", "trailer_rust": "#8a5a44", "kapeltrailer": "#b9bdc2"}[type_]
        ax.add_patch(Rectangle((x + 0.12, y + trk), w - 0.24, hh - trk - 0.05, fc=farve, ec="#222222", lw=0.6, **Z))
        ax.plot([x + 0.4, x + w / 2, x + w - 0.4], [y + trk, y + 0.05, y + trk], color="#222222", lw=1.0, **Z)
        aksler = (0.50, 0.62, 0.74) if type_ == "kapeltrailer" else (0.6,)
        for fa in aksler:
            for hx in (x, x + w - 0.16):
                hjul(hx, y + trk + (hh - trk) * fa - 0.3, 0.16, 0.6)
        if type_ == "kapeltrailer":                         # kapellets bøjler
            for fa in (0.25, 0.5, 0.75):
                ax.plot([x + 0.12, x + w - 0.12], [y + trk + (hh - trk) * fa] * 2, color="#8e9399", lw=0.4, zorder=2.6)
    elif type_ == "redskab":                                # rød slæbeharve med tænder
        ax.add_patch(Rectangle((x + 0.2, y + 0.3), w - 0.4, 1.0, fc="none", ec="#b03a2e", lw=1.0, **Z))
        for i in range(6):
            ax.plot([x + 0.3 + i * (w - 0.6) / 5] * 2, [y + 0.3, y + 1.3], color="#b03a2e", lw=0.6, **Z)
    ax.text(x + w / 2, y + hh / 2, navn, fontsize=5.0, ha="center", va="center", color="#111111", zorder=6,
            rotation=90 if hh > 2.2 * w else 0, bbox=dict(fc="white", ec="none", alpha=0.72, pad=0.6))


def maal(p, q, tekst, off=(0, 0), rot=0):
    ax.annotate("", xy=q, xytext=p, arrowprops=dict(arrowstyle="<->", lw=0.5, shrinkA=0, shrinkB=0), zorder=6)
    ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], tekst, fontsize=6.5, ha="center", va="center", rotation=rot)


def dk(tal, dec=1):
    return f"{tal:.{dec}f}".replace(".", ",")


# Gulvflader: hele hallen som drift, derefter de private zoner
ax.add_patch(Rectangle((ix0, iy0), ix1 - ix0, h_y1 - iy0, fc="#f3f9ef", ec="none", zorder=0))
for z in PRIVATZONER:
    ax.add_patch(Rectangle(z[:2], z[2], z[3], fc="#edf4fc", ec="#1f4e79", lw=0.6, ls=":", zorder=1))
ax.add_patch(Rectangle((ix0, r_y0), RUMDEL - ix0, iy1 - r_y0, fc="#f3f9ef", ec="none", zorder=0))          # østligt rum: drift
ax.add_patch(Rectangle((RUMDEL, r_y0), ix1 - RUMDEL, iy1 - r_y0, fc="#edf4fc", ec="none", zorder=0))       # vestligt rum: privat

# Vægge
vaeg(0, 0, B, YV)
vaeg(0, L - YV, B, YV)
vaeg(0, 0, YV, L)
vaeg(B - YV, 0, YV, L)
vaeg(ix0, h_y1, ix1 - ix0, SV)
vaeg(RUMDEL - IV / 2, r_y0, IV, iy1 - r_y0)

# Åben hal
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
port((B / 2 - PORT_D / 2, YV / 2), (B / 2 + PORT_D / 2, YV / 2), f"port {dk(PORT_D)} m mod ridebanen" if VENDT else f"port {dk(PORT_D)} m (eneste port)", B / 2, -0.4)

# Lukket rum i nordenden
vaeg(TOILET[0] + TOILET[2], TOILET[1], IV, TOILET[3])
vaeg(TOILET[0], TOILET[1] - IV, TOILET[2] + IV, IV)
aabning(TOILET[0] + TOILET[2], TOILET[1] + 0.4, IV, 0.8)
ax.text(TOILET[0] + TOILET[2] / 2, TOILET[1] + TOILET[3] / 2, "Toilet og\nhåndvask\n1,5 × 1,8", fontsize=5.2, ha="center", va="center", zorder=6)
aabning(2.95, h_y1, 0.9, SV)                        # dør mellem hal og det østlige rum
ax.add_patch(Arc((2.95, r_y0), 1.8, 1.8, theta1=0, theta2=90, color="#666666", lw=0.5, zorder=5))
aabning(8.5, 0, 0.9, YV)                            # gangdør i portgavlen, i siden mod huset
ax.add_patch(Arc((9.4, YV), 1.8, 1.8, theta1=90, theta2=180, color="#666666", lw=0.5, zorder=5))
ax.text(8.95, -0.4, "dør", fontsize=6, ha="center", color="#cc0000")
aabning(6.85, h_y1, 0.9, SV)                        # dør mellem rum og hal
ax.add_patch(Arc((6.85, r_y0), 1.8, 1.8, theta1=0, theta2=90, color="#666666", lw=0.5, zorder=5))
rum_net = (ix1 - ix0) * (iy1 - r_y0)
RUM_DRIFT, RUM_PRIVAT = RUMDEL * RUM_L, (B - RUMDEL) * RUM_L          # bruttoarealer
ax.text((RUMDEL + ix1) / 2 + 0.3, (r_y0 + iy1) / 2 - 0.3, f"Privat rum\n(opbevaring)\n{RUM_PRIVAT:.0f} m² brutto", fontsize=6.5, ha="center", va="center", zorder=6)
ax.text(3.4, (r_y0 + iy1) / 2 + 0.5, f"Foder, hesteudstyr\nog værktøj til maskinerne\n{RUM_DRIFT:.0f} m² brutto med toilet", fontsize=6.0, ha="center", va="center", zorder=6)

# Arealopgørelse
privat_hal = sum(z[2] * z[3] for z in PRIVATZONER) + LIFT[2] * LIFT[3]
privat = RUM_PRIVAT + privat_hal
tx = -1.75
ax.text(tx, 17.9, f"LUKKEDE RUM\n{RUM_DRIFT:.0f} m² drift\n{RUM_PRIVAT:.0f} m² privat", fontsize=7, ha="center", va="center", color="#1f4e79", weight="bold")
ax.text(tx, 11.2, f"ÅBEN HAL\n{B * (L - RUM_L):.0f} m² brutto", fontsize=7, ha="center", va="center", weight="bold")
ax.text(tx, 9.4, f"blå felter:\nprivat ca. {privat_hal:.0f} m²", fontsize=6.5, ha="center", va="center", color="#1f4e79")
ax.text(tx, 8.1, f"grønne felter:\ndrift ca. {B * L - privat:.0f} m²", fontsize=6.5, ha="center", va="center", color="#38761d")
ax.text(tx, 5.6, f"I ALT\nprivat ca. {privat:.0f} m²\ndrift ca. {B * L - privat:.0f} m²", fontsize=7, ha="center", va="center", weight="bold")

# Mål
maal((0, -1.1), (B, -1.1), f"{dk(B)} m", (0, -0.3))
maal((B + 2.3, 0), (B + 2.3, skil), f"{dk(L - RUM_L)} m", (0.35, 0), 90)
maal((B + 2.3, skil), (B + 2.3, L), f"{dk(RUM_L)} m", (0.35, 0), 90)
maal((B + 3.2, 0), (B + 3.2, L), f"{dk(L)} m", (0.35, 0), 90)
nordpil(fig, 0.905, 0.925, vinkel=BYGNINGSDREJNING)
if not VENDT:
    ax.text(tx, 0.6, "", fontsize=6, ha="center", va="center", color="red")

fig.text(0.07, 0.125, "Hal, plan og indretning, Nældevej 42, 9000 Aalborg", fontsize=11, weight="bold")
fig.text(0.07, 0.105, f"Målestok 1:{MAALESTOK} (A4)   ·   Udvendigt {dk(B)} × {dk(L)} m = {B * L:.0f} m²   ·   Sidehøjde 4,0 m over sokkel, taghældning 30°, kip nord-syd", fontsize=7.5)
fig.text(0.07, 0.085, "Maskiner og trailere er tegnet efter fotos af de faktiske maskiner; målene i de stiplede felter er anslået og kan afvige lidt.", fontsize=7, color="#444444")
fig.text(0.07, 0.070, "Grønne felter: ejendommens drift og hestehold. Blå felter: privat (lift, trailer 1 og det vestlige rum). Rammernes søjler er ikke vist.", fontsize=7, color="#444444")

tegningshoved(fig, "Ny hal, plan og indretning", "1 : 100 (A4)", "A1.1", x=0.56, y=0.010, b=0.41, h=0.052)
fig.savefig(HER / "hal_plan.png", dpi=200)

# ---------------- Side 2: begrundelse for hallen ----------------
import textwrap
from matplotlib.backends.backend_pdf import PdfPages

drift = B * L - privat
BEGRUNDELSE = [
    ("Hvad der søges om", [
        f"Én hal på {B * L:.0f} m² (20 × 10 m) med to anvendelser, som fremgår af plantegningen på side 1. Der søges landzonetilladelse til hele hallen efter planlovens § 35, stk. 1.",
        f"Ca. {drift:.0f} m² til ejendommens drift og hestehold: maskiner, trailere og et rum på {RUM_DRIFT:.0f} m² til foder, hesteudstyr og værktøj med toilet og håndvask (grønne felter).",
        f"Ca. {privat:.0f} m² privat: et rum på {RUM_PRIVAT:.0f} m², en liftplads og plads til en trailer, samlet i hallens sydvestlige hjørne (blå felter).",
    ]),
    ("Maskinerne har hver sin opgave i driften", [
        "Ejendommen er på ca. 3,9 ha med stald på 284 m² (fire hestebokse, to ponybokse og løsdrift), ridebane og folde. Hesteholdet er privat.",
        "Traktor med frontlæsser til baller og udmugning, ladtrailer med kapel til hjemtransport af hø, halm og wrap, hestetrailer, balleflytter til at køre wrapballer ud til hestene, "
        "halmballe-elevator til at lægge halm og hø på lager, møgtrailer til kørsel af gødning til møddingen, to plænetraktorer til folde, ridebanens kanter og ejendommens arealer, og slæbeharve til ridebanen.",
        f"Rummet på {RUM_DRIFT:.0f} m² rummer foder (ca. 25 rundballer om året), hesteudstyr og værktøj til maskinerne. Toilettet med håndvask er til dem, der arbejder i hallen, i stalden og på ridebanen, "
        "så man kan vaske hænder og gå på toilettet i arbejdstøj uden at gå gennem boligen. Der er hverken bad, køkken eller opholdsrum.",
        "Stalden kan ikke bruges til maskinerne: boksene, løsdriften og sadelrummet er i brug til hestene (bilag A3.1), ingen bygning har en port, en traktor kan køre ind ad, "
        "og maskiner og brændstof bør ikke stå sammen med dyr, hø og halm. Maskiner og trailere står i dag udendørs.",
    ]),
    ("Størrelsen svarer til kommunens praksis", [
        "Aalborg Kommune har godkendt samme opdeling i sag S2025-10959 (Duedal 93, 21. maj 2026): en uopvarmet hal på 150,7 m² til maskiner til vedligehold af en ejendom på 1,65 ha uden erhvervsmæssig landbrugsdrift, "
        "og samtidig en garage på 50 m² ved siden af, med afgørende vægt på, at der ikke var andre udhuse, og at behovet var dokumenteret.",
        "I sag S2025-326 (Nørholmsvej 149, 16. juni 2025) godkendte kommunen et udhus på 148 m² til maskiner og værksted på en ejendom på 2,5 ha med privat hobbyhestehold, og i sag S2022-171976 (Nibevej 384, 13. februar 2023) "
        "en lade på 98 m² til traktor, hø og halm på 1,87 ha med tre heste. Begge steder lagde kommunen vægt på, at heste er hjemmehørende i landzonen.",
        f"Den private del på ca. {privat:.0f} m² svarer til den garage eller det udhus på op til 50 m², der kan opføres ved et enfamiliehus i landzone uden tilladelse (§ 36, stk. 1, nr. 8).",
        "Ejendommens eneste udhus er et skur på ca. 23 m². Ved at samle alt under ét tag undgås to fritliggende bygninger, som kommunen lagde afgørende vægt på i sag S2023-4703 (Nørholmsvej 222, 20. april 2023).",
    ]),
    ("Placering og udformning", [
        "Hallen ligger samlet med ejendommens øvrige bygninger, 11,3 m fra stuehuset og 11,4 m fra skuret ved stalden, og nås ad den eksisterende kørevej.",
        "Den er skærmet af læbæltet mod vest og skovbrynet mod øst, og fra Nældevej og fjorden ligger den bag stald, ridebane og læbælte.",
        "Kiphøjden er 7,3 m over terræn, under bygningsreglementets 8,5 m. Facader og tag udføres i sorte, matte, ikke-reflekterende paneler som de sorte tage på stuehus og stald.",
        "Port og dør vender mod ejendommens egne arealer. Der er ingen åbninger mod naboer, og naboerne har skriftligt erklæret, at de ikke har indvendinger (bilag B2).",
    ]),
    ("Vilkår, vi kan acceptere", [
        "At hallen ikke bruges til erhverv, beboelse eller overnatning. Intet udendørs oplag af maskiner, trailere og redskaber. Mørke, ikke-reflekterende farver. Afskærmende beplantning af hjemmehørende arter syd for hallen i mindst 3 m højde.",
    ]),
]

fig2 = plt.figure(figsize=(210 / 25.4, 297 / 25.4))
fig2.text(0.08, 0.945, "Begrundelse for ny hal, Nældevej 42, 9000 Aalborg", fontsize=13, weight="bold")
fig2.text(0.08, 0.925, "Kort begrundelse til plantegningen på side 1. Den fulde begrundelse står i ansøgningens afsnit A2.", fontsize=8)
y = 0.895
for overskrift, punkter in BEGRUNDELSE:
    fig2.text(0.08, y, overskrift, fontsize=10, weight="bold")
    y -= 0.019
    for nr, punkt in enumerate(punkter, 1):
        linjer = textwrap.wrap(punkt, 112)
        fig2.text(0.085, y, f"{nr}.", fontsize=8.2, va="top")
        fig2.text(0.105, y, "\n".join(linjer), fontsize=8.2, va="top", linespacing=1.35)
        y -= 0.0133 * len(linjer) + 0.006
    y -= 0.012
fig2.text(0.08, 0.035, "Maskinernes og trailernes mål på side 1 er anslået fra fotos og kan afvige lidt fra de faktiske.", fontsize=7.5, color="#444444")

with PdfPages(HER / "hal_plan.pdf") as pdf:
    pdf.savefig(fig)
    pdf.savefig(fig2)
fig2.savefig(HER / "hal_plan_begrundelse.png", dpi=170)
print(f"Rum {B * RUM_L:.0f} m² brutto ({rum_net:.1f} netto); privat i åben hal ca. {privat_hal:.0f} m²; privat i alt ca. {privat:.0f} m²; drift ca. {B * L - privat:.0f} m²")
