"""Orakel für die Bausteine der Verfahren (anderer Rechenweg: Aufzählung über Kantenmengen, volle Neubewertung, Held-Karp, Aufzählung aller Touren)."""

import itertools

import pytest

import vgk_basis as basis
import vgk_methods as M
from vgk_rng import SplitMix64
from vgk_zufall import Strom


def _instanz(n, familie="gleich", idx=0):
    return basis.abstaende(basis.rundtour_punkte(SplitMix64(basis.instanz_seed(familie, n, idx)), familie, n))


def _kanten(tour):
    return frozenset(frozenset((tour[k], tour[(k + 1) % len(tour)])) for k in range(len(tour)))


def _held_karp(d):
    n = len(d)
    best = {(1, 0): 0.0}
    for groesse in range(2, n + 1):
        for teil in itertools.combinations(range(1, n), groesse - 1):
            maske = 1 | sum(1 << k for k in teil)
            for j in teil:
                vor = maske ^ (1 << j)
                best[(maske, j)] = min(best[(vor, k)] + d[k][j] for k in ([0] if vor == 1 else teil) if k != j)
    voll = (1 << n) - 1
    return min(best[(voll, j)] + d[j][0] for j in range(1, n))


@pytest.mark.parametrize("n", [5, 6, 7, 8])
def test_zugliste_ist_genau_die_menge_der_touren_mit_zwei_getauschten_kanten(n):
    """Aufzählung aller Rundtouren: Nachbarn sind die Touren, die genau n − 2 Kanten mit der Ausgangstour teilen."""
    start = list(range(n))
    k0 = _kanten(start)
    soll = {_kanten([0] + list(p)) for p in itertools.permutations(range(1, n))}
    soll = {k for k in soll if len(k & k0) == n - 2}
    ist = set()
    for i, j in M.zugliste(n):
        t = start[:]
        t[i:j + 1] = t[i:j + 1][::-1]
        ist.add(_kanten(t))
    assert ist == soll and len(ist) == len(M.zugliste(n)) == n * (n - 3) // 2


def test_zug_delta_gegen_volle_neubewertung():
    rng = SplitMix64(1)
    for n in (5, 9, 23, 40):
        d = _instanz(n, "cluster")
        tour = list(range(n))
        rng.shuffle(tour)
        for i, j in M.zugliste(n):
            neu = tour[:]
            neu[i:j + 1] = neu[i:j + 1][::-1]
            assert M.zug_delta(d, tour, n, i, j) == pytest.approx(basis.tourlaenge(d, neu) - basis.tourlaenge(d, tour), abs=1e-6)


def test_abstieg_endet_in_einem_optimum_der_vollen_nachbarschaft():
    for seed in range(20):
        n = 12 + seed
        d = _instanz(n, ("gleich", "cluster", "gitter", "netz")[seed % 4])
        rng = Strom(seed)
        tour = M.starttour(rng, n)
        prot = M.Protokoll([10**9])
        laenge, ev, fertig = M.abstieg(d, n, tour, basis.tourlaenge(d, tour), M.zugliste(n), rng.permutation(n * (n - 3) // 2), 0, 10**9, prot)
        assert fertig and laenge == pytest.approx(basis.tourlaenge(d, tour), rel=1e-12)
        # anderer Rechenweg: jede Umkehrung eines Abschnitts der Tour voll neu bewertet
        for a in range(n):
            for b in range(a + 1, n):
                neu = tour[:a] + tour[a:b + 1][::-1] + tour[b + 1:]
                assert basis.tourlaenge(d, neu) >= laenge - 1e-6


def test_doppelbruecke_ersetzt_genau_vier_kanten_und_die_laengenaenderung_stimmt():
    for seed in range(200):
        n = 8 + seed % 30
        d = _instanz(n, "gleich", seed % 3)
        rng = Strom(1000 + seed)
        tour = M.starttour(rng, n)
        neu, delta = M.doppelbruecke(d, tour, n, rng)
        assert sorted(neu) == list(range(n))
        assert len(_kanten(neu) - _kanten(tour)) == 4 and len(_kanten(tour) - _kanten(neu)) == 4
        assert delta == pytest.approx(basis.tourlaenge(d, neu) - basis.tourlaenge(d, tour), abs=1e-6)


def test_doppelbruecke_verlangt_acht_orte():
    with pytest.raises(ValueError):
        M.doppelbruecke(_instanz(7), list(range(7)), 7, Strom(1))


def test_kreuzung_von_hand_und_als_permutation():
    # p1[2:5] = 2, 3, 4 bleibt; der Rest in der Reihenfolge von p2 ab Position 5 (2, 1, 0, 7, 6, 5, 4, 3) ohne 2, 3, 4: 1, 0, 7, 6, 5
    # auf die Plätze 5, 6, 7, 0, 1
    assert M.kreuzung_ox([0, 1, 2, 3, 4, 5, 6, 7], [7, 6, 5, 4, 3, 2, 1, 0], 2, 5, 8) == [6, 5, 2, 3, 4, 1, 0, 7]
    rng = SplitMix64(4)
    for _ in range(300):
        n = 5 + rng.below(30)
        p1, p2 = list(range(n)), list(range(n))
        rng.shuffle(p1)
        rng.shuffle(p2)
        a, b = sorted((rng.below(n + 1), rng.below(n + 1)))
        kind = M.kreuzung_ox(p1, p2, a, b, n)
        assert sorted(kind) == list(range(n)) and kind[a:b] == p1[a:b]


def test_kanonische_tour_ist_dieselbe_rundtour_und_eindeutig():
    rng = SplitMix64(8)
    for _ in range(200):
        n = 3 + rng.below(20)
        t = list(range(n))
        rng.shuffle(t)
        k = M.kanonisch(t)
        assert _kanten(k) == _kanten(t) and k[0] == 0
        dreh = rng.below(n)
        gespiegelt = (t[dreh:] + t[:dreh])[::-1]
        assert M.kanonisch(gespiegelt) == k


@pytest.mark.parametrize("n,familie", [(8, "gleich"), (9, "cluster"), (10, "gitter"), (11, "netz"), (12, "gleich")])
def test_lange_laeufe_treffen_auf_kleinen_instanzen_die_kuerzeste_tour_nach_held_karp(n, familie):
    d = _instanz(n, familie)
    optimum = _held_karp(d)
    for verfahren, par in (("hc", {}), ("ils", {}), ("ma", {"groesse": 4}), ("sa", {"t0f": 0.3, "c": 1.0})):
        beste = []
        for lauf in range(3):
            prot = M.Protokoll([20000])
            M.lauf(verfahren, d, n, 20000, Strom(50 + lauf), prot, **par)
            laenge = M.laenge_kanonisch(d, prot.stand[20000][1])
            assert laenge >= optimum - 1e-6                      # nie kürzer als das bewiesene Optimum
            beste.append(laenge)
        assert min(beste) == pytest.approx(optimum, rel=1e-9), verfahren


def test_held_karp_gegen_aufzaehlung_aller_touren():
    for n in (5, 6, 7, 8):
        d = _instanz(n, "cluster", 1)
        brute = min(basis.tourlaenge(d, [0] + list(p)) for p in itertools.permutations(range(1, n)))
        assert _held_karp(d) == pytest.approx(brute, rel=1e-12)


def test_abkuehlfaktor_gegen_potenz():
    for c, schritte in ((3.0, 999), (1.0, 2999), (0.5, 9999), (2.0, 1)):
        assert M.abkuehlfaktor(c, schritte) == pytest.approx(10.0 ** (-c / schritte), rel=1e-15)
        assert M.abkuehlfaktor(c, schritte) ** schritte == pytest.approx(10.0 ** (-c), rel=1e-9)
    assert M.abkuehlfaktor(3.0, 0) == 1.0


def test_skala_ist_die_mittlere_kante_der_naechster_nachbar_tour(quadrat):
    assert M.naechster_nachbar_skala(quadrat, 4) == 1000.0     # 0 -> 1 -> 2 -> 3 -> 0 (Gleichstand: kleinere Nummer), vier Seiten


def test_protokoll_haelt_den_stand_an_den_pruefpunkten():
    prot = M.Protokoll([5, 10])
    prot.neu(9.0, [0, 1, 2])
    prot.punkt(4)
    assert prot.stand == {}
    prot.punkt(5)
    prot.neu(7.0, [0, 2, 1])
    prot.punkt(10)
    assert prot.stand[5] == (9.0, [0, 1, 2]) and prot.stand[10] == (7.0, [0, 2, 1])


def test_strom_und_vorlage_geben_denselben_lauf():
    """Die Verfahren hängen nur an der Zufallsfolge: mit der SplitMix64-Vorlage (ohne Puffer, ohne numpy) kommt dieselbe Tour heraus."""
    class Vorlage(SplitMix64):
        def werte(self, anzahl):
            return [self.next_u64() for _ in range(anzahl)]

        def permutation(self, m):
            w = self.werte(m)
            return sorted(range(m), key=w.__getitem__)

    d = _instanz(14, "netz")
    for verfahren, par in (("hc", {}), ("sa", {"t0f": 0.3, "c": 3.0}), ("ga", {}), ("ils", {}), ("ma", {})):
        p1, p2 = M.Protokoll([3000]), M.Protokoll([3000])
        M.lauf(verfahren, d, 14, 3000, Strom(77), p1, **par)
        M.lauf(verfahren, d, 14, 3000, Vorlage(77), p2, **par)
        assert p1.stand[3000][1] == p2.stand[3000][1] and p1.erster_abstieg == p2.erster_abstieg
