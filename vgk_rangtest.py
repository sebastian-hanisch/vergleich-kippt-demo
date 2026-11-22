"""Rangtest des Mehrfachtest-Experiments: Mann-Whitney-U, zweiseitig, als Normalnäherung mit Stetigkeits- und Gleichstandskorrektur.

Dieselbe Variante rechnet `scipy.stats.mannwhitneyu(..., method="asymptotic")`; scipy ist nur in den Tests das Orakel. Dazu:
die exakte Verteilung von U ohne Gleichstände (Rekursion), daraus die exakte Verwerfungswahrscheinlichkeit dieser Testvariante bei
gleichen Verfahren; das Gleichstandsmodell (jeder Lauf trifft mit Wahrscheinlichkeit q denselben Bestwert); der Nullvergleich aus
einem Pool von Läufen (zwei Gruppen ohne Zurücklegen gezogen)."""

import math
from functools import lru_cache

import numpy as np

import vgk_zufall as Z

NIVEAU = 0.05


@lru_cache(maxsize=None)
def u_anzahl(a: int, b: int) -> tuple:
    """Zahl der Anordnungen von a x-Werten und b y-Werten ohne Gleichstände je U = Zahl der Paare x > y (Index = U)."""
    if a == 0 or b == 0:
        return (1,)
    res = [0] * (a * b + 1)
    for u, c in enumerate(u_anzahl(a - 1, b)):   # größter Wert ist ein x: er schlägt alle b y
        res[u + b] += c
    for u, c in enumerate(u_anzahl(a, b - 1)):   # größter Wert ist ein y
        res[u] += c
    return tuple(res)


def varianz_u(n1: int, n2: int, gleich_summe: float = 0.0) -> float:
    """Varianz von U unter der Nullannahme; `gleich_summe` = Summe von t³ − t über die Gruppen gleicher Werte (Gleichstandskorrektur)."""
    n = n1 + n2
    return n1 * n2 / 12.0 * ((n + 1) - gleich_summe / (n * (n - 1)))


def p_wert(u1: float, n1: int, n2: int, gleich_summe: float = 0.0) -> float:
    """Zweiseitiger p-Wert der Normalnäherung mit Stetigkeitskorrektur. Sind alle Werte gleich (Varianz 0), ist p = 1."""
    var = varianz_u(n1, n2, gleich_summe)
    if var <= 0.0:
        return 1.0
    u = max(u1, n1 * n2 - u1)
    z = (u - n1 * n2 / 2.0 - 0.5) / math.sqrt(var)
    return min(1.0, math.erfc(z / math.sqrt(2.0)))


def u_statistik(x, y) -> tuple:
    """(U der x-Gruppe: Paare x > y plus halbe Gleichstände, Summe von t³ − t über die Gleichstandsgruppen aller Werte)."""
    u = sum(1.0 if xi > yj else (0.5 if xi == yj else 0.0) for xi in x for yj in y)
    alle = list(x) + list(y)
    gleich = 0
    for wert in set(alle):
        t = alle.count(wert)
        gleich += t ** 3 - t
    return u, float(gleich)


def mann_whitney(x, y) -> float:
    """p-Wert für zwei Gruppen von Läufen."""
    u, gleich = u_statistik(x, y)
    return p_wert(u, len(x), len(y), gleich)


def z_schwelle(niveau: float) -> float:
    """z mit erfc(z/√2) = niveau (Bisektion): der Test verwirft genau dann, wenn sein z darüber liegt."""
    lo, hi = 0.0, 40.0
    for _ in range(200):
        mitte = (lo + hi) / 2.0
        if math.erfc(mitte / math.sqrt(2.0)) > niveau:
            lo = mitte
        else:
            hi = mitte
    return (lo + hi) / 2.0


def verwerfung_ohne_gleichstand(r: int, niveau: float = NIVEAU) -> float:
    """Exakte Wahrscheinlichkeit, dass die Normalnäherung bei zwei Gruppen zu r Läufen DESSELBEN Verfahrens verwirft (keine Gleichstände)."""
    anz = u_anzahl(r, r)
    return sum(c for u, c in enumerate(anz) if p_wert(u, r, r) < niveau) / sum(anz)


def verwerfung_exakter_test(r: int, niveau: float = NIVEAU) -> float:
    """Dasselbe für den exakten Test (p = 2 · P(U ≤ u), ohne Gleichstände): zum Vergleich der Testvarianten."""
    anz = u_anzahl(r, r)
    gesamt = sum(anz)
    kum, summe = [], 0
    for c in anz:
        summe += c
        kum.append(summe)
    treffer = 0
    for u, c in enumerate(anz):
        klein = min(u, r * r - u)
        if min(1.0, 2.0 * kum[klein] / gesamt) < niveau:
            treffer += c
    return treffer / gesamt


def verwerfung_modell(q: float, r: int = 10, niveau: float = NIVEAU) -> float:
    """Gleichstandsmodell, exakt: jeder Lauf trifft mit Wahrscheinlichkeit q denselben Bestwert, sonst einen stetigen Wert darüber."""
    gesamt = 0.0
    for a in range(r + 1):
        wa = math.comb(r, a) * q ** a * (1 - q) ** (r - a)
        for b in range(r + 1):
            w = wa * math.comb(r, b) * q ** b * (1 - q) ** (r - b)
            if w == 0.0 or a + b == 2 * r:        # alle Werte gleich: p = 1, keine Verwerfung
                continue
            anz = u_anzahl(r - a, r - b)
            t = a + b
            gleich = float(t ** 3 - t) if t >= 2 else 0.0
            # U der x-Gruppe: a·b Gleichstände zu 1/2, die r − a stetigen x schlagen die b Bestwerte von y, dazu U' der stetigen Werte
            treffer = sum(c for u, c in enumerate(anz) if p_wert(a * b / 2.0 + (r - a) * b + u, r, r, gleich) < niveau)
            gesamt += w * treffer / sum(anz)
    return gesamt


def mindestens_eine(p: float, m: int) -> float:
    """Wahrscheinlichkeit für mindestens eine Verwerfung unter m unabhängigen Tests mit Verwerfungswahrscheinlichkeit p."""
    return 1.0 - (1.0 - p) ** m


# ------------------------------------------------------------------------------------------------------------------------------
# Viele Tests auf einmal (numpy)
# ------------------------------------------------------------------------------------------------------------------------------
def z_werte(x: np.ndarray, y: np.ndarray) -> tuple:
    """Für Felder (..., r) und (..., r): (z der Normalnäherung, hat der Test Gleichstände?). Varianz 0 gibt z = −∞ (nie Verwerfung)."""
    r1, r2 = x.shape[-1], y.shape[-1]
    groesser = (x[..., :, None] > y[..., None, :]).sum(axis=(-1, -2))
    gleich = (x[..., :, None] == y[..., None, :]).sum(axis=(-1, -2))
    u = groesser + 0.5 * gleich
    alle = np.concatenate([x, y], axis=-1)
    vielfach = (alle[..., :, None] == alle[..., None, :]).sum(axis=-1)       # wie oft jeder Wert vorkommt
    gleich_summe = (vielfach.astype(float) ** 2 - 1.0).sum(axis=-1)           # Summe über die Werte von t² − 1 = Summe über die Gruppen von t³ − t
    n = r1 + r2
    var = r1 * r2 / 12.0 * ((n + 1) - gleich_summe / (n * (n - 1)))
    gross = np.maximum(u, r1 * r2 - u)
    with np.errstate(divide="ignore", invalid="ignore"):
        z = np.where(var > 0, (gross - r1 * r2 / 2.0 - 0.5) / np.sqrt(np.where(var > 0, var, 1.0)), -np.inf)
    return z, gleich_summe > 0


def ziehe_gruppen(pool: np.ndarray, r: int, ziehungen: int, seed: int) -> tuple:
    """Je Zeile des Pools (Instanz) und je Ziehung zwei Gruppen zu r Läufen ohne Zurücklegen. Rückgabe zwei Felder (Ziehungen, Instanzen, r)."""
    zahl_inst, zahl_laeufe = pool.shape
    if 2 * r > zahl_laeufe:
        raise ValueError("zwei Gruppen passen nicht in den Pool")
    schluessel = Z.block(seed, 0, ziehungen * zahl_inst * zahl_laeufe).reshape(ziehungen, zahl_inst, zahl_laeufe)
    ordnung = np.argsort(schluessel, axis=-1, kind="stable")[..., : 2 * r]
    werte = np.take_along_axis(np.broadcast_to(pool, (ziehungen, zahl_inst, zahl_laeufe)), ordnung, axis=-1)
    return werte[..., :r], werte[..., r:]


def nulltest(pool: np.ndarray, r: int, wiederholungen: int, seed: int, niveau: float = NIVEAU) -> dict:
    """Dasselbe Verfahren gegen sich selbst: je Wiederholung und Instanz ein Test zweier Gruppen aus dem Pool der Instanz.

    `pool`: (Instanzen, Läufe). Zählt Einzeltests und Wiederholungen mit mindestens einer Verwerfung, ohne Korrektur und mit Bonferroni."""
    m = pool.shape[0]
    x, y = ziehe_gruppen(pool, r, wiederholungen, seed)
    z, hat_gleich = z_werte(x, y)
    verworfen = z > z_schwelle(niveau)
    bonferroni = z > z_schwelle(niveau / m)
    return {
        "tests": int(verworfen.size), "wiederholungen": wiederholungen, "instanzen": m,
        "signifikant": int(verworfen.sum()),
        "mindestens_eine": int(verworfen.any(axis=1).sum()),
        "bonferroni_mindestens_eine": int(bonferroni.any(axis=1).sum()),
        "bonferroni_signifikant": int(bonferroni.sum()),
        "mit_gleichstand": int(hat_gleich.sum()),
    }


def pool_wahrscheinlichkeit(pool: np.ndarray, r: int, ziehungen: int, seed: int, niveau: float = NIVEAU) -> tuple:
    """Je Instanz: geschätzte Verwerfungswahrscheinlichkeit und Anteil der Ziehungen mit Gleichständen (aus `ziehungen` Ziehungen)."""
    x, y = ziehe_gruppen(pool, r, ziehungen, seed)
    z, hat_gleich = z_werte(x, y)
    return (z > z_schwelle(niveau)).mean(axis=0), hat_gleich.mean(axis=0)


def haeufigster_anteil(pool: np.ndarray) -> np.ndarray:
    """Je Instanz der Anteil des häufigsten Werts unter den Läufen des Pools."""
    return (pool[:, :, None] == pool[:, None, :]).sum(axis=-1).max(axis=-1) / pool.shape[1]


def erwartung_aus_pool(p_je_instanz) -> float:
    """Mindestens eine Verwerfung unter den Tests der gewählten Instanzen: 1 − Produkt(1 − p_i)."""
    return float(1.0 - np.prod(1.0 - np.asarray(p_je_instanz, dtype=float)))


POOL_ZIEHUNGEN = 4000
POOL_GRUPPEN = (5, 10, 20)
POOL_SEED = 2026112108


def pool_erwartung_datei(trio: dict, stand: str, ziehungen: int = POOL_ZIEHUNGEN, seed: int = POOL_SEED) -> dict:
    """Inhalt von data/vgk_nulltest.json: je Verfahren, Budget und Gruppengröße die Verwerfungswahrscheinlichkeit je Instanz."""
    aus = {"quelle": "tools/vgk_make_daten.py erwartung (vgk_rangtest.pool_erwartung_datei)", "stand": stand,
           "voraussetzung": (f"je Instanz {ziehungen} Ziehungen zweier Gruppen ohne Zurücklegen aus den 60 Läufen von data/vgk_trio.json; Mann-Whitney als Normalnäherung "
                             "mit Stetigkeits- und Gleichstandskorrektur, Niveau 0,05; Standardfehler je Instanz höchstens 0,4 Prozentpunkte"),
           "ziehungen": ziehungen, "zellen": {}}
    for k, v in enumerate(trio["verfahren"]):
        for j, b in enumerate(trio["budgets"]):
            pool = trio["laengen"][v][b]
            zelle = {"haeufigster": [round(float(x), 4) for x in haeufigster_anteil(pool)]}
            for r in POOL_GRUPPEN:
                p, g = pool_wahrscheinlichkeit(pool, r, ziehungen, seed + 1000 * k + 100 * j + r)
                zelle[str(r)] = {"p": [round(float(x), 5) for x in p], "gleichstand": [round(float(x), 4) for x in g]}
            aus["zellen"][f"{v}|{b}"] = zelle
    return aus
