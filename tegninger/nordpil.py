"""Fælles nordpil til alle plantegninger: samme udseende og samme sted (øverst til højre), altid pegende op."""
from matplotlib.patches import FancyBboxPatch


def nordpil(fig, x=0.90, y=0.89, hoejde=0.075, vinkel=0.0):
    """Tegner nordpilen med centrum i (x, y) i figurens koordinater (0-1).

    vinkel = hvor mange grader nord er drejet mod uret i forhold til lodret på arket (tegningerne er drejet lidt,
    så vejen ligger vandret, og pilen viser den rigtige nordretning).
    """
    import math
    dx = -0.28 * math.sin(math.radians(vinkel)) * 1.6   # aksen er smallere end den er høj

    bredde = hoejde * fig.get_figheight() / fig.get_figwidth() * 0.62
    a = fig.add_axes([x - bredde / 2, y - hoejde / 2, bredde, hoejde], zorder=20)
    a.set_xlim(0, 1)
    a.set_ylim(0, 1)
    a.axis("off")
    a.add_patch(FancyBboxPatch((0.06, 0.03), 0.88, 0.94, boxstyle="round,pad=0.02", fc="white", ec="#888888", lw=0.6, alpha=0.9))
    a.annotate("", xy=(0.5 + dx, 0.66), xytext=(0.5 - dx, 0.10), arrowprops=dict(arrowstyle="-|>", lw=1.6, color="black", mutation_scale=15))
    a.text(0.5, 0.80, "N", fontsize=11, weight="bold", ha="center", va="center")
