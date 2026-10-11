"""Lille plan rammeberegner (bjælkeelementer med normalkraft) til overslagsberegninger.

Bruges af hal_teknisk.py og tilbygning_teknisk.py. Enheder: kN, m, kNm. Laster lægges som knudelaster på fint
inddelte stænger. Dette er et overslagsværktøj og ikke en statisk dokumentation.
"""
import math

import numpy as np


class Ramme:
    def __init__(self):
        self.knuder, self.elem, self.staenger, self.fast = [], [], {}, {}

    def knude(self, x, y):
        for i, (a, b) in enumerate(self.knuder):
            if abs(a - x) < 1e-9 and abs(b - y) < 1e-9:
                return i
        self.knuder.append((x, y))
        return len(self.knuder) - 1

    def stang(self, navn, p0, p1, EA, EI, n=16):
        """Tilføjer en stang inddelt i n elementer. Lille EI giver en stang, der i praksis er leddelt i enderne."""
        ids, forrige = [], self.knude(*p0)
        for k in range(1, n + 1):
            p = (p0[0] + (p1[0] - p0[0]) * k / n, p0[1] + (p1[1] - p0[1]) * k / n)
            ny = self.knude(*p)
            self.elem.append((forrige, ny, EA, EI))
            ids.append(len(self.elem) - 1)
            forrige = ny
        self.staenger[navn] = ids
        return ids

    def understoet(self, p, ux=True, uy=True, rz=False):
        self.fast[self.knude(*p)] = (ux, uy, rz)

    def _k(self, e):
        i, j, EA, EI = self.elem[e]
        (x0, y0), (x1, y1) = self.knuder[i], self.knuder[j]
        L = math.hypot(x1 - x0, y1 - y0)
        c, s = (x1 - x0) / L, (y1 - y0) / L
        a, b = EA / L, EI / L ** 3
        k = np.array([[a, 0, 0, -a, 0, 0],
                      [0, 12 * b, 6 * b * L, 0, -12 * b, 6 * b * L],
                      [0, 6 * b * L, 4 * b * L * L, 0, -6 * b * L, 2 * b * L * L],
                      [-a, 0, 0, a, 0, 0],
                      [0, -12 * b, -6 * b * L, 0, 12 * b, -6 * b * L],
                      [0, 6 * b * L, 2 * b * L * L, 0, -6 * b * L, 4 * b * L * L]])
        T = np.zeros((6, 6))
        for o in (0, 3):
            T[o:o + 3, o:o + 3] = [[c, s, 0], [-s, c, 0], [0, 0, 1]]
        return k, T, L

    def last(self, staenger, type_, w, normal=None):
        """Returnerer lastvektor. type_: 'g' = lodret pr. m stang, 'plan' = lodret pr. m vandret projektion,
        'normal' = tryk pr. m stang vinkelret på stangen (positiv = ind mod bygningen, modsat udadrettet normal)."""
        F = np.zeros(3 * len(self.knuder))
        for navn in staenger:
            for e in self.staenger[navn]:
                i, j = self.elem[e][0], self.elem[e][1]
                (x0, y0), (x1, y1) = self.knuder[i], self.knuder[j]
                L = math.hypot(x1 - x0, y1 - y0)
                if type_ == "g":
                    fx, fy = 0.0, -w * L / 2
                elif type_ == "plan":
                    fx, fy = 0.0, -w * abs(x1 - x0) / 2
                else:
                    fx, fy = -w * normal[navn][0] * L / 2, -w * normal[navn][1] * L / 2
                for kn in (i, j):
                    F[3 * kn] += fx
                    F[3 * kn + 1] += fy
        return F

    def loes(self, F):
        n = 3 * len(self.knuder)
        K = np.zeros((n, n))
        for e in range(len(self.elem)):
            k, T, _ = self._k(e)
            i, j = self.elem[e][0], self.elem[e][1]
            dof = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
            K[np.ix_(dof, dof)] += T.T @ k @ T
        laast = [3 * kn + d for kn, f in self.fast.items() for d in range(3) if f[d]]
        fri = [d for d in range(n) if d not in laast]
        u = np.zeros(n)
        u[fri] = np.linalg.solve(K[np.ix_(fri, fri)], F[fri])
        R = K @ u - F
        res = {"u": u, "reak": {kn: (R[3 * kn], R[3 * kn + 1]) for kn in self.fast}, "snit": {}}
        for navn, ids in self.staenger.items():
            N, V, M = [], [], []
            for e in ids:
                k, T, _ = self._k(e)
                i, j = self.elem[e][0], self.elem[e][1]
                d = u[[3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]]
                f = k @ T @ d
                N += [-f[0], f[3]]          # træk positivt
                V += [f[1], -f[4]]
                M += [-f[2], f[5]]
            res["snit"][navn] = {"N": np.array(N), "V": np.array(V), "M": np.array(M)}
        return res


def kombiner(resultater, faktorer):
    """Lineær kombination af resultater fra loes()."""
    ud = {"u": sum(f * r["u"] for f, r in zip(faktorer, resultater)), "reak": {}, "snit": {}}
    for kn in resultater[0]["reak"]:
        ud["reak"][kn] = tuple(sum(f * r["reak"][kn][d] for f, r in zip(faktorer, resultater)) for d in (0, 1))
    for navn in resultater[0]["snit"]:
        ud["snit"][navn] = {s: sum(f * r["snit"][navn][s] for f, r in zip(faktorer, resultater)) for s in ("N", "V", "M")}
    return ud
