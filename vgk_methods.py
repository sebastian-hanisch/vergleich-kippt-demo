"""Die Verfahren des Vergleichs, eigene Umsetzungen: Abstieg mit Neustarts, Annealing, genetischer Algorithmus, iterierte Lokalsuche,
memetischer Algorithmus. Alle arbeiten auf einer Rundtour mit der 2-opt-Nachbarschaft und zählen Auswertungen.

Zählregel (Kopf von `vgk_basis.py`): die Bewertung einer vollständigen Tour zählt 1 (Starttour, Kind einer Kreuzung), jede Bewertung
eines Zugs (Längenänderung) zählt 1, auch die einer Störung. Zählweise „voll“: alle n(n-3)/2 Züge der 2-opt-Nachbarschaft, keine Listen,
keine Warteschlange. Abstiegsregel: erste Verbesserung; Zugreihenfolge: je Abstieg eine neue Zufallsreihenfolge aller Züge, die zyklisch
durchlaufen wird, bis n(n-3)/2 Züge in Folge keine Verbesserung brachten. Kein Lauf überschreitet sein Budget.

Der Zufall kommt aus einem Objekt mit `next_u64`, `below`, `random`, `shuffle`, `permutation`, `werte` (`vgk_zufall.Strom`)."""

import decimal
import math

import vgk_basis as basis

EPS = 1e-7           # Verbesserung heißt: Längenänderung < -EPS (Koordinaten 0..9999, Längen um 10^4 bis 10^5)
_KONTEXT = decimal.Context(prec=40)

VERFAHREN_TEXT = {
    "hc": "Hill Climbing mit Neustarts (HC)",
    "sa": "Simulated Annealing (SA)",
    "ga": "genetischer Algorithmus (GA)",
    "ils": "Iterated Local Search (ILS)",
    "ma": "memetischer Algorithmus (MA)",
}
GA_STANDARD = {"pop": 30, "turnier": 3, "p_kreuz": 0.9, "p_mut": 0.5, "elite": 2}
MA_P_MUT = 0.3


# ------------------------------------------------------------------------------------------------------------------------------
# Bausteine
# ------------------------------------------------------------------------------------------------------------------------------
def zugliste(n: int) -> list:
    """Alle 2-opt-Züge als Positionspaare (i, j): der Zug dreht tour[i..j] um und ersetzt die Kanten vor i und nach j. n(n-3)/2 Züge."""
    return [(i, j) for i in range(1, n - 1) for j in range(i + 1, n) if not (i == 1 and j == n - 1)]


def zug_delta(d, tour, n, i, j) -> float:
    """Längenänderung des Zugs (i, j): zwei neue Kanten minus zwei entfernte."""
    a, b, c = tour[i - 1], tour[i], tour[j]
    e = tour[j + 1] if j + 1 < n else tour[0]
    return d[a][c] + d[b][e] - d[a][b] - d[c][e]


def kanonisch(tour: list) -> list:
    """Dieselbe Rundtour mit Ort 0 vorn und der kleineren Nachbarnummer an zweiter Stelle (Drehung und Richtung entfernt)."""
    k = tour.index(0)
    t = tour[k:] + tour[:k]
    if len(t) > 2 and t[1] > t[-1]:
        t = [t[0]] + t[:0:-1]
    return t


def laenge_kanonisch(d, tour: list) -> float:
    """Tourlänge der kanonischen Fassung: zwei Läufe mit derselben Rundtour bekommen bitgleich dieselbe Länge."""
    return basis.tourlaenge(d, kanonisch(tour))


def naechster_nachbar_skala(d, n: int) -> float:
    """Mittlere Kantenlänge der Nächster-Nachbar-Tour ab Ort 0 (Gleichstand: kleinere Nummer); Maßstab der Annealing-Temperatur."""
    besucht = [False] * n
    besucht[0] = True
    ort, summe = 0, 0.0
    for _ in range(n - 1):
        zeile = d[ort]
        ziel = min((j for j in range(n) if not besucht[j]), key=lambda j: (zeile[j], j))
        summe += zeile[ziel]
        besucht[ziel] = True
        ort = ziel
    return (summe + d[ort][0]) / n


def abkuehlfaktor(c: float, schritte: int) -> float:
    """10^(-c/schritte), mit `decimal` gerechnet (ohne die Potenzfunktion der C-Bibliothek, also auf jeder Plattform dieselben Bits)."""
    if schritte <= 0:
        return 1.0
    return float(_KONTEXT.power(decimal.Decimal(10), _KONTEXT.divide(decimal.Decimal(repr(-float(c))), decimal.Decimal(schritte))))


class Protokoll:
    """Hält die beste Tour eines Laufs fest und ihren Stand an festen Prüfpunkten (Zahl der Auswertungen)."""

    def __init__(self, pruefpunkte):
        self.punkte = sorted(set(int(p) for p in pruefpunkte))
        self.best = math.inf
        self.best_tour = None
        self._k = 0
        self.nxt = self.punkte[0] if self.punkte else math.inf
        self.stand = {}            # Prüfpunkt -> (beste Länge fortgeschrieben, beste Tour)
        self.erster_abstieg = None  # Auswertungen bis zum Ende des ersten Abstiegs (None: nicht beendet oder Verfahren ohne Abstieg)

    def neu(self, laenge: float, tour: list) -> None:
        self.best = laenge
        self.best_tour = tour[:]

    def punkt(self, ev: int) -> None:
        while ev >= self.nxt:
            self.stand[self.nxt] = (self.best, self.best_tour)
            self._k += 1
            self.nxt = self.punkte[self._k] if self._k < len(self.punkte) else math.inf

    def abschluss(self, ev: int) -> None:
        """Prüfpunkte, die der Lauf nicht mehr erreicht hat (sollte nicht vorkommen), bekommen den Endstand."""
        while self._k < len(self.punkte):
            self.stand[self.punkte[self._k]] = (self.best, self.best_tour)
            self._k += 1
        self.nxt = math.inf


def starttour(rng, n: int) -> list:
    tour = list(range(n))
    rng.shuffle(tour)
    return tour


def abstieg(d, n, tour, laenge, zuege, ordnung, ev, budget, prot):
    """2-opt-Abstieg mit erster Verbesserung; `tour` wird verändert. Rückgabe (Länge, Auswertungen, beendet?).

    Beendet heißt: alle Züge der Nachbarschaft wurden nach der letzten Verbesserung einmal bewertet, keiner verbessert."""
    zahl = len(zuege)
    p = ohne = 0
    while ohne < zahl and ev < budget:
        i, j = zuege[ordnung[p]]
        p += 1
        if p == zahl:
            p = 0
        a = tour[i - 1]
        b = tour[i]
        c = tour[j]
        e = tour[j + 1] if j + 1 < n else tour[0]
        delta = d[a][c] + d[b][e] - d[a][b] - d[c][e]
        ev += 1
        if delta < -EPS:
            tour[i:j + 1] = tour[i:j + 1][::-1]
            laenge += delta
            ohne = 0
            if laenge < prot.best - EPS:
                prot.neu(laenge, tour)
        else:
            ohne += 1
        if ev >= prot.nxt:
            prot.punkt(ev)
    return laenge, ev, ohne >= zahl


def doppelbruecke(d, tour, n, rng):
    """Double-Bridge: die Tour wird ab einer Zufallsposition in vier Abschnitte A B C D (je mindestens zwei Orte) geteilt und als
    A D C B wieder zusammengesetzt; vier Kanten werden ersetzt. Rückgabe (neue Tour, Längenänderung). Verlangt n >= 8."""
    if n < 8:
        raise ValueError("Double-Bridge verlangt mindestens 8 Orte")
    dreh = rng.below(n)
    c1, c2, c3 = sorted((rng.below(n - 7), rng.below(n - 7), rng.below(n - 7)))
    p1, p2, p3 = 2 + c1, 4 + c2, 6 + c3
    t = tour[dreh:] + tour[:dreh]
    a, b, c, e = t[:p1], t[p1:p2], t[p2:p3], t[p3:]
    alt = d[a[-1]][b[0]] + d[b[-1]][c[0]] + d[c[-1]][e[0]] + d[e[-1]][a[0]]
    neu = d[a[-1]][e[0]] + d[e[-1]][c[0]] + d[c[-1]][b[0]] + d[b[-1]][a[0]]
    return a + e + c + b, neu - alt


def kreuzung_ox(p1, p2, a, b, n):
    """Order Crossover: das Stück p1[a:b] bleibt an seinem Platz, der Rest folgt in der Reihenfolge von p2 ab Position b."""
    kind = [-1] * n
    stueck = p1[a:b]
    kind[a:b] = stueck
    drin = set(stueck)
    rest = [x for x in (p2[b:] + p2[:b]) if x not in drin]
    for platz, x in zip(list(range(b, n)) + list(range(0, a)), rest):
        kind[platz] = x
    return kind


# ------------------------------------------------------------------------------------------------------------------------------
# Verfahren. Jedes gibt die Zahl der verbrauchten Auswertungen zurück; die Ergebnisse stehen im Protokoll.
# ------------------------------------------------------------------------------------------------------------------------------
def lauf_hc(d, n, budget, rng, prot, zuege=None):
    """Abstieg mit Neustarts: Zufallstour, 2-opt-Abstieg bis zum Stillstand, neue Zufallstour, bis das Budget verbraucht ist."""
    zuege = zuege or zugliste(n)
    ev = 0
    erster = True
    while ev < budget:
        tour = starttour(rng, n)
        laenge = basis.tourlaenge(d, tour)
        ev += 1
        if laenge < prot.best - EPS:
            prot.neu(laenge, tour)
        if ev >= prot.nxt:
            prot.punkt(ev)
        laenge, ev, fertig = abstieg(d, n, tour, laenge, zuege, rng.permutation(len(zuege)), ev, budget, prot)
        if erster and fertig:
            prot.erster_abstieg = ev
        erster = False
    prot.abschluss(ev)
    return ev


def lauf_sa(d, n, budget, rng, prot, t0f, c, skala=None, zuege=None):
    """Annealing: je Schritt ein zufälliger 2-opt-Zug; angenommen, wenn er nicht verlängert, sonst mit Wahrscheinlichkeit exp(-Änderung/T).

    Starttemperatur t0f · Skala (mittlere Kantenlänge der Nächster-Nachbar-Tour), geometrische Abkühlung um c Zehnerpotenzen über das Budget."""
    zuege = zuege or zugliste(n)
    zahl = len(zuege)
    skala = naechster_nachbar_skala(d, n) if skala is None else skala
    tour = starttour(rng, n)
    laenge = basis.tourlaenge(d, tour)
    ev = 1
    prot.neu(laenge, tour)
    if ev >= prot.nxt:
        prot.punkt(ev)
    temperatur = t0f * skala
    alpha = abkuehlfaktor(c, budget - 1)
    exp = math.exp
    while ev < budget:
        stueck = rng.werte(2 * min(2048, budget - ev))
        for q in range(0, len(stueck), 2):
            i, j = zuege[stueck[q] % zahl]
            a = tour[i - 1]
            b = tour[i]
            cc = tour[j]
            e = tour[j + 1] if j + 1 < n else tour[0]
            delta = d[a][cc] + d[b][e] - d[a][b] - d[cc][e]
            ev += 1
            if delta <= 0.0 or (stueck[q + 1] >> 11) / 9007199254740992.0 < exp(-delta / temperatur):
                tour[i:j + 1] = tour[i:j + 1][::-1]
                laenge += delta
                if laenge < prot.best - EPS:
                    prot.neu(laenge, tour)
            temperatur *= alpha
            if ev >= prot.nxt:
                prot.punkt(ev)
    prot.abschluss(ev)
    return ev


def lauf_ga(d, n, budget, rng, prot, pop=30, turnier=3, p_kreuz=0.9, p_mut=0.5, elite=2):
    """Einfacher genetischer Algorithmus ohne Lokalsuche: Turnierauswahl, Order Crossover, Umkehrmutation, die besten `elite` bleiben."""
    tl = basis.tourlaenge
    touren, werte = [], []
    ev = 0
    for _ in range(pop):
        if ev >= budget:
            break
        t = starttour(rng, n)
        w = tl(d, t)
        ev += 1
        touren.append(t)
        werte.append(w)
        if w < prot.best - EPS:
            prot.neu(w, t)
        if ev >= prot.nxt:
            prot.punkt(ev)
    while ev < budget:
        zahl = len(touren)
        rang = sorted(range(zahl), key=lambda k: (werte[k], k))
        neu_t = [touren[k] for k in rang[:elite]]
        neu_w = [werte[k] for k in rang[:elite]]
        while len(neu_t) < zahl and ev < budget:
            eltern = []
            for _ in range(2):
                kandidaten = [rng.below(zahl) for _ in range(turnier)]
                eltern.append(touren[min(kandidaten, key=lambda k: (werte[k], k))])
            if rng.random() < p_kreuz:
                a, b = sorted((rng.below(n + 1), rng.below(n + 1)))
                kind = kreuzung_ox(eltern[0], eltern[1], a, b, n)
            else:
                kind = eltern[0][:]
            if rng.random() < p_mut:
                i, j = sorted((rng.below(n), rng.below(n)))
                kind[i:j + 1] = kind[i:j + 1][::-1]
            w = tl(d, kind)
            ev += 1
            if w < prot.best - EPS:
                prot.neu(w, kind)
            neu_t.append(kind)
            neu_w.append(w)
            if ev >= prot.nxt:
                prot.punkt(ev)
        touren, werte = neu_t, neu_w
    prot.abschluss(ev)
    return ev


def lauf_ils(d, n, budget, rng, prot, zuege=None):
    """Iterierte Lokalsuche: Abstieg, dann wiederholt Double-Bridge und neuer Abstieg; die neue Tour gilt, wenn sie nicht länger ist."""
    zuege = zuege or zugliste(n)
    tour = starttour(rng, n)
    laenge = basis.tourlaenge(d, tour)
    ev = 1
    prot.neu(laenge, tour)
    if ev >= prot.nxt:
        prot.punkt(ev)
    laenge, ev, fertig = abstieg(d, n, tour, laenge, zuege, rng.permutation(len(zuege)), ev, budget, prot)
    if fertig:
        prot.erster_abstieg = ev
    while ev < budget:
        t2, delta = doppelbruecke(d, tour, n, rng)
        l2 = laenge + delta
        ev += 1
        if l2 < prot.best - EPS:
            prot.neu(l2, t2)
        if ev >= prot.nxt:
            prot.punkt(ev)
        l2, ev, _ = abstieg(d, n, t2, l2, zuege, rng.permutation(len(zuege)), ev, budget, prot)
        if l2 <= laenge + EPS:
            tour, laenge = t2, l2
    prot.abschluss(ev)
    return ev


def lauf_ma(d, n, budget, rng, prot, groesse=8, zuege=None):
    """Memetischer Algorithmus: eine Population von 2-opt-Optima; je Schritt zwei Eltern (Zweierturnier), Order Crossover,
    mit Wahrscheinlichkeit 0,3 eine Double-Bridge, 2-opt-Abstieg; das Kind ersetzt die längste Tour, wenn es kürzer und neu ist."""
    zuege = zuege or zugliste(n)
    zahl = len(zuege)
    tl = basis.tourlaenge
    touren, werte, schluessel = [], [], set()
    ev = 0
    erster = True
    versuche = 0
    while len(touren) < groesse and ev < budget and versuche < 4 * groesse:
        versuche += 1
        t = starttour(rng, n)
        w = tl(d, t)
        ev += 1
        if w < prot.best - EPS:
            prot.neu(w, t)
        if ev >= prot.nxt:
            prot.punkt(ev)
        w, ev, fertig = abstieg(d, n, t, w, zuege, rng.permutation(zahl), ev, budget, prot)
        if erster and fertig:
            prot.erster_abstieg = ev
        erster = False
        k = tuple(kanonisch(t))
        if k not in schluessel:
            schluessel.add(k)
            touren.append(t)
            werte.append(w)
    while ev < budget:
        m = len(touren)
        eltern = []
        for _ in range(2):
            i, j = rng.below(m), rng.below(m)
            eltern.append(touren[i] if (werte[i], i) <= (werte[j], j) else touren[j])
        a, b = sorted((rng.below(n + 1), rng.below(n + 1)))
        kind = kreuzung_ox(eltern[0], eltern[1], a, b, n)
        w = tl(d, kind)
        ev += 1
        if w < prot.best - EPS:
            prot.neu(w, kind)
        if ev >= prot.nxt:
            prot.punkt(ev)
        if ev >= budget:
            break
        if rng.random() < MA_P_MUT:
            kind, delta = doppelbruecke(d, kind, n, rng)
            w += delta
            ev += 1
            if w < prot.best - EPS:
                prot.neu(w, kind)
            if ev >= prot.nxt:
                prot.punkt(ev)
            if ev >= budget:
                break
        w, ev, _ = abstieg(d, n, kind, w, zuege, rng.permutation(zahl), ev, budget, prot)
        schlecht = max(range(m), key=lambda q: (werte[q], q))
        k = tuple(kanonisch(kind))
        if w < werte[schlecht] - EPS and k not in schluessel:
            schluessel.discard(tuple(kanonisch(touren[schlecht])))
            schluessel.add(k)
            touren[schlecht] = kind
            werte[schlecht] = w
    prot.abschluss(ev)
    return ev


def lauf(verfahren: str, d, n, budget, rng, prot, **parameter):
    """Ein Lauf eines Verfahrens nach seinem Kurznamen; `parameter` sind die Einstellungen des Verfahrens."""
    if verfahren == "hc":
        return lauf_hc(d, n, budget, rng, prot)
    if verfahren == "sa":
        return lauf_sa(d, n, budget, rng, prot, parameter["t0f"], parameter["c"], parameter.get("skala"))
    if verfahren == "ga":
        return lauf_ga(d, n, budget, rng, prot, **{k: parameter[k] for k in GA_STANDARD if k in parameter})
    if verfahren == "ils":
        return lauf_ils(d, n, budget, rng, prot)
    if verfahren == "ma":
        return lauf_ma(d, n, budget, rng, prot, parameter.get("groesse", 8))
    raise ValueError(f"unbekanntes Verfahren: {verfahren}")
