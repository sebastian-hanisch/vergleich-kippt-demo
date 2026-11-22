"""Aufbau der Messreihen: welche Instanzen, welche Zufalls-Seeds, welche Budgets; ein Lauf als Funktion.

Dieselben Funktionen rechnet das Vorrechen-Skript (`tools/vgk_make_daten.py`), die Tests und die Live-Nachrechnung der App.
Instanzen kommen aus der gemeinsamen Basis der Reihe (`vgk_basis.py`), der Zufall aus SplitMix64 (`vgk_rng.py`, gepuffert in `vgk_zufall.py`)."""

import vgk_basis as basis
import vgk_constants as C
import vgk_methods as M
from vgk_rng import SplitMix64
from vgk_zufall import Strom

_CACHE = {}


def instanz(familie: str, n: int, idx: int = 0):
    """(Punkte, Abstandsmatrix) der Instanz der gemeinsamen Basis."""
    key = (familie, n, idx)
    if key not in _CACHE:
        punkte = basis.rundtour_punkte(SplitMix64(basis.instanz_seed(familie, n, idx)), familie, n)
        if len(_CACHE) > 400:
            _CACHE.clear()
        _CACHE[key] = (punkte, basis.abstaende(punkte))
    return _CACHE[key]


def strom(familie: str, n: int, idx: int, code: int, lauf: int) -> Strom:
    """Zufallsstrom eines Laufs: fester Zufalls-Seed aus Instanz, Verfahrenskennzahl und Laufnummer (nie der Strom der Instanz)."""
    return Strom(basis.lauf_seed(basis.instanz_seed(familie, n, idx), code, lauf))


def trio_instanzen() -> list:
    """63 Instanzen: je Familie eine je Ortszahl 20 bis 40; Reihenfolge nach Ortszahl, darin nach Familie (so mischt jede Teilmenge „die ersten m“ die Familien)."""
    return [(f, n, 0) for n in C.TRIO_N for f in C.TRIO_FAMILIEN]


def quartett_instanzen() -> list:
    return [(f, n, idx) for n in C.QUARTETT_N for idx in C.QUARTETT_IDX for f in C.QUARTETT_FAMILIEN]


def _flaeche(prot, budget: int) -> float:
    """Mittel der bis dahin besten Länge über die 20 Prüfpunkte des Budgets (für das Maß „Fläche unter der Laufzeitkurve“)."""
    punkte = C.PRUEFPUNKTE[budget]
    return sum(prot.stand[p][0] for p in punkte) / len(punkte)


def trio_lauf(familie: str, n: int, idx: int, verfahren: str, lauf: int, sa_einstellungen=None) -> dict:
    """Ein Lauf des Trios. Rückgabe {Budget: (Länge der besten Tour, Flächenwert)}.

    Hill Climbing und der genetische Algorithmus haben keine Einstellung, die vom Budget abhängt: ein Lauf über 10.000 Auswertungen,
    die kleineren Budgets sind sein Stand nach 1.000 und 3.000. Simulated Annealing kühlt über das Budget ab: je Budget ein eigener Lauf."""
    sa_einstellungen = sa_einstellungen or C.SA_TRIO
    _, d = instanz(familie, n, idx)
    alle = sorted({p for b in C.TRIO_BUDGETS for p in C.PRUEFPUNKTE[b]})
    aus = {}
    if verfahren in ("hc", "ga"):
        prot = M.Protokoll(alle)
        M.lauf(verfahren, d, n, C.TRIO_BUDGETS[-1], strom(familie, n, idx, C.CODE[verfahren], lauf), prot, **(M.GA_STANDARD if verfahren == "ga" else {}))
        for b in C.TRIO_BUDGETS:
            aus[b] = (M.laenge_kanonisch(d, prot.stand[b][1]), _flaeche(prot, b))
        return aus
    t0f, c = sa_einstellungen[verfahren]
    skala = M.naechster_nachbar_skala(d, n)
    for k, b in enumerate(C.TRIO_BUDGETS):
        prot = M.Protokoll(C.PRUEFPUNKTE[b])
        M.lauf_sa(d, n, b, strom(familie, n, idx, C.CODE[verfahren] + 10 * (k + 1), lauf), prot, t0f, c, skala)
        aus[b] = (M.laenge_kanonisch(d, prot.stand[b][1]), _flaeche(prot, b))
    return aus


def quartett_lauf(familie: str, n: int, idx: int, verfahren: str, lauf: int, sa_einstellungen=None, ma_groesse=None) -> dict:
    """Ein Lauf des Quartetts. Rückgabe {"laengen": {Stufe: Länge}, "erster_abstieg": Auswertungen bis zum Ende des ersten Abstiegs oder None}.

    Hill Climbing, Iterated Local Search und der memetische Algorithmus: ein Lauf über das größte Budget, die kleineren Stufen sind
    Zwischenstände. Simulated Annealing: je Stufe ein eigener Lauf mit der für diese Stufe abgestimmten Einstellung."""
    _, d = instanz(familie, n, idx)
    budgets = {s: f * n for s, f in C.QUARTETT_STUFEN.items()}
    if verfahren == "sa":
        sa_einstellungen = sa_einstellungen or C.SA_QUARTETT
        skala = M.naechster_nachbar_skala(d, n)
        laengen = {}
        for k, (s, b) in enumerate(budgets.items()):
            prot = M.Protokoll([b])
            t0f, c = sa_einstellungen[s]
            M.lauf_sa(d, n, b, strom(familie, n, idx, C.CODE["q_sa"] + 10 * (k + 1), lauf), prot, t0f, c, skala)
            laengen[s] = M.laenge_kanonisch(d, prot.stand[b][1])
        return {"laengen": laengen, "erster_abstieg": None}
    prot = M.Protokoll(budgets.values())
    parameter = {"groesse": ma_groesse or C.MA_GROESSE} if verfahren == "ma" else {}
    M.lauf(verfahren, d, n, max(budgets.values()), strom(familie, n, idx, C.CODE["q_" + verfahren], lauf), prot, **parameter)
    return {"laengen": {s: M.laenge_kanonisch(d, prot.stand[b][1]) for s, b in budgets.items()}, "erster_abstieg": prot.erster_abstieg}


def referenz_lauf(familie: str, n: int, idx: int, lauf: int) -> float:
    """Ein langer Lauf der Iterated Local Search (20.000 · n Auswertungen) für die beste bekannte Länge; kein Optimalitätsbeweis."""
    _, d = instanz(familie, n, idx)
    b = C.REFERENZ_FAKTOR * n
    prot = M.Protokoll([b])
    M.lauf_ils(d, n, b, strom(familie, n, idx, C.CODE["ref"], lauf), prot)
    return M.laenge_kanonisch(d, prot.stand[b][1])
