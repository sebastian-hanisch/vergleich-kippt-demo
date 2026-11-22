"""Zähltest: die gezählten Auswertungen stimmen mit der Handzählung an einer Mini-Instanz und mit einem zählenden Umschlag überein.

Handzählung am Quadrat (vier Orte, zwei 2-opt-Züge): vom Umfang aus bewertet der Abstieg beide Züge, keiner verbessert: 2 Auswertungen.
Von einer Tour mit gekreuzten Diagonalen verbessert genau ein Zug (er entfernt die Diagonalen); der andere führt zur zweiten gekreuzten
Tour (Änderung 0). Steht der verbessernde Zug vorn: 1 + 2 = 3 Auswertungen; steht er hinten: 2 + 2 = 4.

Umschlag (anderer Rechenweg): gezählt werden die Zugriffe auf die Abstandsmatrix. Eine volle Tourbewertung liest n Abstände, eine
Zugbewertung 4, eine Double-Bridge 8. Aus der Zahl der Zugriffe und der Zahl der Starttouren, Kinder und Störungen folgt die Zahl
der Auswertungen, ohne den Zähler der Verfahren zu benutzen."""

import math

import pytest

import vgk_basis as basis
import vgk_methods as M
from vgk_rng import SplitMix64
from vgk_zufall import Strom


class Zeile(list):
    zugriffe = 0

    def __getitem__(self, k):
        Zeile.zugriffe += 1
        return list.__getitem__(self, k)


def _instanz(n, familie="gleich"):
    punkte = basis.rundtour_punkte(SplitMix64(basis.instanz_seed(familie, n, 0)), familie, n)
    return basis.abstaende(punkte)


def _gezaehlt(d):
    Zeile.zugriffe = 0
    return [Zeile(z) for z in d]


def test_zugzahl_am_quadrat_und_allgemein():
    assert M.zugliste(4) == [(1, 2), (2, 3)]
    for n in range(4, 60):
        assert len(M.zugliste(n)) == n * (n - 3) // 2


def test_handzaehlung_abstieg_vom_umfang(quadrat):
    prot = M.Protokoll([100])
    laenge, ev, fertig = M.abstieg(quadrat, 4, [0, 1, 2, 3], 4000.0, M.zugliste(4), [0, 1], 0, 100, prot)
    assert (laenge, ev, fertig) == (4000.0, 2, True)


def test_handzaehlung_abstieg_von_der_gekreuzten_tour(quadrat):
    kreuz = 2000.0 + 2000.0 * math.sqrt(2.0)
    # Tour 0-2-1-3: Zug (1, 2) dreht die Orte 2 und 1 um und gibt den Umfang; Zug (2, 3) gibt die andere gekreuzte Tour
    for ordnung, soll in (([0, 1], 3), ([1, 0], 4)):
        tour = [0, 2, 1, 3]
        prot = M.Protokoll([100])
        laenge, ev, fertig = M.abstieg(quadrat, 4, tour, kreuz, M.zugliste(4), ordnung, 0, 100, prot)
        assert ev == soll and fertig
        assert laenge == pytest.approx(4000.0, rel=1e-12) and basis.tourlaenge(quadrat, tour) == 4000.0


def test_handzaehlung_budget_bricht_den_abstieg_ab(quadrat):
    prot = M.Protokoll([100])
    tour = [0, 2, 1, 3]
    _, ev, fertig = M.abstieg(quadrat, 4, tour, 4828.0, M.zugliste(4), [1, 0], 5, 7, prot)   # Startstand 5, Budget 7: nur zwei Bewertungen
    assert ev == 7 and not fertig and basis.tourlaenge(quadrat, tour) == 4000.0


def test_handzaehlung_hill_climbing_am_quadrat(quadrat):
    """Jeder Neustart kostet 1 (Starttour) + 2, 3 oder 4 (Abstieg); der Lauf endet genau am Budget."""
    prot = M.Protokoll([50])
    assert M.lauf_hc(quadrat, 4, 50, Strom(5), prot) == 50
    assert prot.erster_abstieg in (3, 4, 5)
    assert M.laenge_kanonisch(quadrat, prot.stand[50][1]) == 4000.0


@pytest.mark.parametrize("n,budget", [(8, 400), (12, 3000), (25, 9000)])
def test_umschlag_hill_climbing(n, budget, monkeypatch):
    d = _gezaehlt(_instanz(n))
    starts = []
    echt = M.starttour
    monkeypatch.setattr(M, "starttour", lambda rng, m: starts.append(1) or echt(rng, m))
    ev = M.lauf_hc(d, n, budget, Strom(11), M.Protokoll([budget]))
    s = len(starts)
    assert (Zeile.zugriffe - n * s) % 4 == 0
    assert ev == budget == s + (Zeile.zugriffe - n * s) // 4


@pytest.mark.parametrize("n,budget", [(8, 500), (20, 4000)])
def test_umschlag_annealing(n, budget):
    d = _gezaehlt(_instanz(n, "cluster"))
    ev = M.lauf_sa(d, n, budget, Strom(12), M.Protokoll([budget]), 0.3, 3.0, skala=500.0)
    assert ev == budget == 1 + (Zeile.zugriffe - n) // 4 and (Zeile.zugriffe - n) % 4 == 0


@pytest.mark.parametrize("n,budget", [(8, 300), (15, 2000)])
def test_umschlag_genetischer_algorithmus(n, budget):
    d = _gezaehlt(_instanz(n, "gitter"))
    ev = M.lauf_ga(d, n, budget, Strom(13), M.Protokoll([budget]))
    assert ev == budget and Zeile.zugriffe == n * budget


@pytest.mark.parametrize("verfahren,n,budget", [("ils", 9, 2000), ("ils", 20, 20000), ("ma", 9, 3000), ("ma", 20, 30000)])
def test_umschlag_ils_und_memetisch(verfahren, n, budget, monkeypatch):
    d = _gezaehlt(_instanz(n, "netz"))
    zahl = {"start": 0, "kind": 0, "stoerung": 0}
    echt_start, echt_ox, echt_db = M.starttour, M.kreuzung_ox, M.doppelbruecke

    def start(rng, m):
        zahl["start"] += 1
        return echt_start(rng, m)

    def ox(*a):
        zahl["kind"] += 1
        return echt_ox(*a)

    def db(*a):
        zahl["stoerung"] += 1
        return echt_db(*a)

    monkeypatch.setattr(M, "starttour", start)
    monkeypatch.setattr(M, "kreuzung_ox", ox)
    monkeypatch.setattr(M, "doppelbruecke", db)
    ev = M.lauf(verfahren, d, n, budget, Strom(14), M.Protokoll([budget]), groesse=4)
    voll = zahl["start"] + zahl["kind"]
    zuege, rest = divmod(Zeile.zugriffe - n * voll - 8 * zahl["stoerung"], 4)
    assert rest == 0 and zahl["stoerung"] > 0
    assert ev == budget == voll + zahl["stoerung"] + zuege
