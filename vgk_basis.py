"""Gemeinsame Basis der Linie „Landschaften, Einstellung und Vergleich“: Instanzgenerator (Rundtour, NK-Modell) und Zählregeln.

Referenzfassung im Planungsordner. Jede Demo der Linie KOPIERT diese Datei als `<präfix>_basis.py` (kein Import über Ordnergrenzen)
und prüft die Kopie mit einem Test gegen `eingefroren.json` (gleiche Koordinaten, Längen und NK-Werte). Nicht in der Demo ändern:
Wünsche an die Basis gehen in den Baubericht.

Alle Zufallszahlen kommen aus SplitMix64 (Vorlage `tools/templates/rng_splitmix64_exact.py`, in der Demo als `<präfix>_rng.py`);
der Generator wird hereingereicht, damit diese Datei keinen Modulnamen kennen muss. Koordinaten sind GANZE Zahlen in 0..9999,
Abstände `math.sqrt` einer ganzen Zahl (nach IEEE 754 exakt gerundet, auf jeder Plattform gleich).

Zählregeln der Linie (Beschlüsse E12, E13, E19; Eigentümer der Definitionen ist Stück 5):
* Budget-Einheit ist die AUSWERTUNG: jede Bewertung eines Nachbarn (Längenänderung eines Zuges, beim NK-Modell der Wert eines
  Nachbarzustands) zählt 1; die Bewertung einer vollständigen Startlösung zählt 1.
* „voll“ (Standard): alle Züge der Nachbarschaft werden bewertet, keine Listen, keine Warteschlange.
* „Listen“: nur Züge, bei denen mindestens eine der neuen Kanten zwei Städte verbindet, von denen die eine zu den k nächsten der anderen gehört (symmetrische Nachbarlisten; k nennen).
* „Warteschlange“: volle Nachbarschaft, aber nur Züge an Orten, deren „don't look“-Marke nicht gesetzt ist.
* Abstiegsregel und Zugreihenfolge gehören zur Aussage: „steilster Abstieg“ (bester Zug, Gleichstand: erster in der festen
  Reihenfolge) oder „erste Verbesserung“ (Reihenfolge nennen).
"""

import math

FAMILIEN = ("gleich", "cluster", "gitter", "netz")
FAMILIEN_TEXT = {
    "gleich": "gleichverteilt",
    "cluster": "geclustert",
    "gitter": "Gitter mit Rauschen",
    "netz": "Straßennetz (Punkte entlang weniger Strecken)",
}
FELD = 10000  # Koordinaten 0..FELD-1


def instanz_seed(familie: str, n: int, idx: int) -> int:
    """Fester Zufalls-Seed je (Familie, n, laufende Nummer); getrennt von allen Lauf-Seeds der Verfahren."""
    return 1_000_003 * (FAMILIEN.index(familie) + 1) + 7919 * n + 104_729 * idx + 12_345


def lauf_seed(instanz: int, verfahren: int, lauf: int) -> int:
    """Fester Zufalls-Seed je Lauf eines Verfahrens (nie derselbe Strom wie die Instanz)."""
    return 2_000_003 * (instanz + 1) + 15_485_863 * (verfahren + 1) + 32_452_843 * (lauf + 1)


def _klemme(v: float) -> int:
    return max(0, min(FELD - 1, int(round(v))))


def rundtour_punkte(rng, familie: str, n: int) -> list:
    """n verschiedene Punkte mit ganzzahligen Koordinaten. `rng` ist ein SplitMix64-Objekt."""
    if familie not in FAMILIEN:
        raise ValueError(f"unbekannte Familie: {familie}")
    punkte, gesehen = [], set()

    def nimm(x, y):
        p = (_klemme(x), _klemme(y))
        if p not in gesehen:
            gesehen.add(p)
            punkte.append(p)

    if familie == "gleich":
        while len(punkte) < n:
            nimm(rng.below(FELD), rng.below(FELD))
    elif familie == "cluster":
        zahl = max(2, n // 10)
        zentren = [(1000 + rng.below(8000), 1000 + rng.below(8000)) for _ in range(zahl)]
        while len(punkte) < n:
            cx, cy = zentren[rng.below(zahl)]
            nimm(cx + 400.0 * rng.normal(), cy + 400.0 * rng.normal())
    elif familie == "gitter":
        seite = int(math.ceil(math.sqrt(n)))
        schritt = FELD // (seite + 1)
        zellen = [(i, j) for i in range(seite) for j in range(seite)]
        rng.shuffle(zellen)
        ruck = max(1, schritt // 4)
        for i, j in zellen:
            if len(punkte) >= n:
                break
            nimm((i + 1) * schritt + rng.below(2 * ruck + 1) - ruck, (j + 1) * schritt + rng.below(2 * ruck + 1) - ruck)
        while len(punkte) < n:  # nur falls Punkte zusammenfielen
            nimm(rng.below(FELD), rng.below(FELD))
    else:  # netz
        strecken = [((rng.below(FELD), rng.below(FELD)), (rng.below(FELD), rng.below(FELD))) for _ in range(5)]
        while len(punkte) < n:
            (ax, ay), (bx, by) = strecken[rng.below(5)]
            t = rng.random()
            nimm(ax + t * (bx - ax) + 60.0 * rng.normal(), ay + t * (by - ay) + 60.0 * rng.normal())
    return punkte


def abstaende(punkte: list) -> list:
    """Symmetrische Abstandsmatrix (Liste von Listen, float)."""
    n = len(punkte)
    d = [[0.0] * n for _ in range(n)]
    for i in range(n):
        xi, yi = punkte[i]
        for j in range(i + 1, n):
            dx, dy = xi - punkte[j][0], yi - punkte[j][1]
            d[i][j] = d[j][i] = math.sqrt(dx * dx + dy * dy)
    return d


def tourlaenge(d: list, tour: list) -> float:
    """Länge der geschlossenen Tour; summiert in Tourreihenfolge ab Position 0 (feste Reihenfolge, damit die Summe plattformgleich ist)."""
    gesamt = 0.0
    for i in range(len(tour)):
        gesamt += d[tour[i]][tour[(i + 1) % len(tour)]]
    return gesamt


def nk_tabellen(rng, n: int, k: int, stufen: int = 0) -> list:
    """NK-Modell mit zyklisch benachbarten Loci: Locus i hängt an i, i+1, …, i+k (mod n). K zählt OHNE den Locus selbst.

    stufen = 0: Beiträge gleichverteilt in [0, 1). stufen >= 2: ganzzahlige Beiträge 0..stufen-1 (grobe Fitness mit exakten Gleichständen).
    Rückgabe: n Listen mit je 2^(k+1) Beiträgen; Index = Bits (x_i, x_{i+1}, …, x_{i+k}), x_i ist das höchstwertige Bit."""
    if not 0 <= k < n:
        raise ValueError("0 <= k < n verlangt")
    groesse = 1 << (k + 1)
    if stufen:
        return [[rng.below(stufen) for _ in range(groesse)] for _ in range(n)]
    return [[rng.random() for _ in range(groesse)] for _ in range(n)]


def nk_wert(tabellen: list, x: list):
    """Summe der Beiträge (nicht durch n geteilt): float bei stufen = 0, int bei ganzzahligen Beiträgen. Größer ist besser."""
    n = len(tabellen)
    k = len(tabellen[0]).bit_length() - 2
    gesamt = 0
    for i in range(n):
        index = 0
        for j in range(k + 1):
            index = (index << 1) | x[(i + j) % n]
        gesamt += tabellen[i][index]
    return gesamt
