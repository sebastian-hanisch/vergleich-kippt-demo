"""No-Free-Lunch im Kleinen: Suchraum {0, 1, 2, 3}, Werte {0, 1, 2}, alle 3⁴ = 81 Funktionen, zwei Suchverfahren ohne Wiederholung.

Verfahren A tastet von links nach rechts ab. Verfahren B beginnt bei Punkt 3, geht bei Wert 0 zum Punkt 2, sonst zum Punkt 0, und
danach zum kleinsten noch nicht besuchten Punkt. Kleiner ist besser; „Minimum nach m Auswertungen“ ist der beste gesehene Wert."""

import itertools
from collections import Counter

PUNKTE = (0, 1, 2, 3)
WERTE = (0, 1, 2)
KLASSEN = ("alle", "glatt")
KLASSEN_TEXT = {"alle": "alle 81 Funktionen", "glatt": "glatte Funktionen (Nachbarwerte unterscheiden sich um höchstens 1)"}


def alle_funktionen() -> list:
    return [tuple(v) for v in itertools.product(WERTE, repeat=len(PUNKTE))]


def ist_glatt(f) -> bool:
    return all(abs(f[x + 1] - f[x]) <= 1 for x in range(len(f) - 1))


def klasse(name: str) -> list:
    if name == "alle":
        return alle_funktionen()
    if name == "glatt":
        return [f for f in alle_funktionen() if ist_glatt(f)]
    raise ValueError(f"unbekannte Klasse: {name}")


def verfahren_a(f) -> tuple:
    """Folge der beobachteten Werte beim Abtasten von links nach rechts."""
    return tuple(f[x] for x in PUNKTE)


def verfahren_b(f) -> tuple:
    """Folge der beobachteten Werte des Verfahrens, das auf den ersten Wert reagiert."""
    besucht = [3, 2 if f[3] == 0 else 0]
    besucht += [x for x in PUNKTE if x not in besucht]
    return tuple(f[x] for x in besucht)


VERFAHREN = {"A": verfahren_a, "B": verfahren_b}


def verteilung_minimum(verfahren: str, klassenname: str, m: int) -> dict:
    """Wie viele Funktionen der Klasse haben nach m Auswertungen den besten Wert 0, 1, 2?"""
    zaehler = Counter(min(VERFAHREN[verfahren](f)[:m]) for f in klasse(klassenname))
    return {w: zaehler.get(w, 0) for w in WERTE}


def folgen_verteilung(verfahren: str, klassenname: str, m: int) -> Counter:
    """Häufigkeit jeder beobachteten Wertefolge der Länge m über die Klasse."""
    return Counter(VERFAHREN[verfahren](f)[:m] for f in klasse(klassenname))


def abschluss_unter_permutation(klassenname: str) -> int:
    """Zahl der Funktionen, die man aus der Klasse durch Vertauschen der Punkte erhält (gleich der Klassengröße heißt: abgeschlossen)."""
    menge = set()
    for f in klasse(klassenname):
        for p in itertools.permutations(PUNKTE):
            menge.add(tuple(f[p[x]] for x in PUNKTE))
    return len(menge)
