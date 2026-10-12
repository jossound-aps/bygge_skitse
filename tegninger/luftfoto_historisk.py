#!/usr/bin/env python3
"""Bilag B2: historiske luftfotos af stald og ridebane, 2012-2026 (fra billeder/luftfoto_historisk/).

Kør:  python3 tegninger/luftfoto_historisk.py
Giver: tegninger/luftfoto_historisk.pdf/.png (A3 liggende)
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from tegningshoved import tegningshoved

HER = Path(__file__).parent
MAPPE = HER.parent / "billeder" / "luftfoto_historisk"
M_PR_PX = 0.325                                   # zoomniveau 18 ved 57° nord
BOX = (560, 420, 960, 720)                        # udsnit om stald og ridebane i de 1024 × 1024 px store billeder
BILLEDER = [
    ("esri-optaget-2012-01-15_udgave-2014-02-20.png", "Optaget 15. januar 2012", "Én indhegnet, bar jordbane på ca. 45 × 55 m øst for stalden, med heste"),
    ("esri-udgave-2016-11-16.png", "Esri-udgave 16. november 2016", "Samme areal, græsklædt og slidt af brug"),
    ("esri-udgave-2022-06-08.png", "Esri-udgave 8. juni 2022", "Banen gjort mindre: sandbane mod nord, jordfolde mod syd"),
    ("esri-udgave-2023-04-05.png", "Esri-udgave 5. april 2023", "Sandbane"),
    ("esri-udgave-2024-03-28.png", "Esri-udgave 28. marts 2024", "Sandbane"),
    ("esri-udgave-2025-04-24.png", "Esri-udgave 24. april 2025", "Sandbane"),
    ("esri-udgave-2026-04-30.png", "Esri-udgave 30. april 2026", "Sandbane og jordfolde, som i dag"),
]

fig = plt.figure(figsize=(420 / 25.4, 297 / 25.4))
fig.text(0.03, 0.95, "Historiske luftfotos af stald og ridebane, Nældevej 42, 9000 Aalborg", fontsize=14, weight="bold")
fig.text(0.03, 0.925, "Samme udsnit (ca. 130 × 98 m, nord op) fra syv forskellige luftfotos. Stalden ses til venstre, ridebanen til højre for den. I 2012 var hele arealet én jordbane; den tidligere ejer gjorde den mindre og indrettede den sydlige del som jordfolde til heste med sukkersyge.", fontsize=9)
for i, (fil, titel, note) in enumerate(BILLEDER):
    im = Image.open(MAPPE / fil).crop(BOX)
    r, c = divmod(i, 4)
    ax = fig.add_axes([0.03 + c * 0.24, 0.52 - r * 0.40, 0.225, 0.33])
    ax.imshow(im)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(titel, fontsize=8.5, weight="bold", pad=3)
    ax.text(0.5, -0.05, note, transform=ax.transAxes, fontsize=7.5, ha="center", va="top")
    if i == 0:
        ax.plot([20, 20 + 50 / M_PR_PX], [im.size[1] - 15] * 2, color="white", lw=2.5)
        ax.text(20, im.size[1] - 22, "50 m", color="white", fontsize=7)
fig.text(0.03, 0.09, "Kilde: Esri World Imagery Wayback (livingatlas.arcgis.com/wayback), zoomniveau 18. Optagelsesdatoen 15. januar 2012 er oplyst i Esris metadata for det ældste foto (Denmark_Imagery 2012, 10 cm). "
                     "For de senere udgaver oplyser Esri ikke optagelsesdatoen, så de er angivet med udgavens dato.", fontsize=7, color="#444444")
fig.text(0.03, 0.07, "Kommunens egne ortofotos fra 1995 og frem kan supplere, hvis det ønskes.", fontsize=7, color="#444444")
tegningshoved(fig, "Historiske luftfotos 2012-2026, stald og ridebane", "ca. 1 : 1.000 (A3)", "B2", x=0.62, y=0.012, b=0.36, h=0.06)
fig.savefig(HER / "luftfoto_historisk.pdf")
fig.savefig(HER / "luftfoto_historisk.png", dpi=110)
print("luftfoto_historisk.pdf")
