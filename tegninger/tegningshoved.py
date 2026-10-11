"""Fælles tegningshoved (titelfelt) til alle tegninger, som i kommunens eksempel: byggesag, emne, dato, mål, nummer."""
from matplotlib.patches import Rectangle

BYGGESAG = "Nældevej 42, 9000 Aalborg"
DATO = "11.10.2026"
UDFOERT_AF = "JB"


def tegningshoved(fig, emne, maal, nr, x=0.62, y=0.012, b=0.36, h=0.075, status="LANDZONEANSØGNING"):
    """Tegner titelfeltet med nederste venstre hjørne i (x, y) i figurens koordinater (0-1)."""
    a = fig.add_axes([x, y, b, h], zorder=30)
    a.set_xlim(0, 1)
    a.set_ylim(0, 1)
    a.axis("off")
    a.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec="black", lw=0.8))
    for yy in (1 / 3, 2 / 3):
        a.plot([0, 0.74], [yy, yy], color="black", lw=0.5)
    a.plot([0.74, 0.74], [0, 1], color="black", lw=0.5)
    a.plot([0.47, 0.47], [0, 2 / 3], color="black", lw=0.5)
    fs = 6.2
    a.text(0.015, 5 / 6, f"BYGGESAG:  {BYGGESAG}", fontsize=fs, va="center")
    a.text(0.015, 0.5, f"EMNE:  {emne}", fontsize=fs, va="center")
    a.text(0.485, 0.5, f"DATO:  {DATO}", fontsize=fs, va="center")
    a.text(0.015, 1 / 6, f"UDFØRT AF:  {UDFOERT_AF}", fontsize=fs, va="center")
    a.text(0.485, 1 / 6, f"MÅL:  {maal}", fontsize=fs, va="center")
    a.text(0.87, 0.62, nr, fontsize=11, weight="bold", ha="center", va="center")
    a.text(0.87, 0.22, status, fontsize=4.8, ha="center", va="center", color="#444444")
