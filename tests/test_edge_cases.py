"""Randfälle: Gleichstand aller Werte, ein Verfahren, eine Gruppe, ein Test, kleinste Instanzen, Budget am Rand."""

import math

import numpy as np
import pytest

import vgk_compare as V
import vgk_daten as D
import vgk_evaluation as ev
import vgk_methods as M
import vgk_nfl as N
import vgk_rangtest as R
from vgk_zufall import Strom


def test_gleichstand_aller_werte_tau_nicht_definiert_und_p_eins():
    assert V.kendall_tau_b([1.0, 1.0, 1.0], [1.0, 2.0, 3.0]) is None
    assert V.tau_mittel(np.array([[2.0, 2.0, 2.0], [1.0, 2.0, 3.0]]), np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0]])) == (1.0, 1)
    assert math.isnan(V.tau_mittel(np.array([[2.0, 2.0, 2.0]]), np.array([[1.0, 2.0, 3.0]]))[0])
    assert R.p_wert(50.0, 10, 10, float(20 ** 3 - 20)) == 1.0           # eine Gruppe aus allen 20 Werten: Varianz 0
    assert list(V.raenge(np.array([5.0, 5.0, 5.0]))) == [2.0, 2.0, 2.0]


def test_ein_verfahren_hat_immer_rang_eins():
    f = [np.arange(12.0).reshape(2, 6)]
    assert (V.instanz_raenge(f, "mittel") == 1.0).all()
    assert (V.kippen_gruppen(f, 3)["verschieden"] == 0).all()


def test_weniger_als_zwei_gruppen_ist_ein_fehler():
    with pytest.raises(ValueError):
        V.kippen_gruppen([np.zeros((2, 6)), np.ones((2, 6))], 6)
    assert V.kippen_gruppen([np.zeros((2, 6)), np.ones((2, 6))], 3)["paare"] == 1      # genau zwei Gruppen: ein Paar


def test_gruppen_zu_einem_lauf():
    a = np.array([[1.0, 3.0, 1.0, 3.0]])
    b = np.array([[2.0, 2.0, 2.0, 2.0]])
    k = V.kippen_gruppen([a, b], 1)
    # Ordnungen der vier Gruppen: A, B, A, B vorn; von 6 Paaren sind 4 verschieden und strikt entgegengesetzt
    assert k["paare"] == 6 and k["verschieden"][0] == pytest.approx(4 / 6) and k["strikt"][0] == pytest.approx(4 / 6)


def test_kippformel_ohne_streuung():
    assert V.kippformel(1.0, 0.0, 0.0, 5) == 0.0 and V.kippformel(0.0, 0.0, 0.0, 5) is None
    assert V.laeufe_fuer_fuenf_prozent(0.0, 1.0, 1.0) is None and V.laeufe_fuer_fuenf_prozent(1.0, 0.0, 0.0) == 0.0
    mittel, ohne = V.formel_mittel(np.array([[1.0, 1.0], [1.0, 3.0]]), np.array([[1.0, 1.0], [2.0, 2.0]]), 2)
    assert ohne == 1 and 0.0 < mittel <= 0.5


def test_ein_einziger_test():
    pool = np.arange(60.0).reshape(1, 60)
    e = R.nulltest(pool, 10, 200, seed=4)
    assert e["instanzen"] == 1 and e["mindestens_eine"] == e["signifikant"] == e["bonferroni_signifikant"]     # bei m = 1 ist Bonferroni dasselbe Niveau
    assert R.mindestens_eine(0.04326, 1) == pytest.approx(0.04326)


def test_fuenf_gegen_fuenf_bonferroni_bei_dreissig_tests_nie():
    pool = np.random.default_rng(5).random((30, 60))
    assert R.nulltest(pool, 5, 200, seed=5)["bonferroni_signifikant"] == 0
    trio, daten = D.trio(), D.nulltest()
    e = ev.exp_null(trio, daten, "ga", 3000, 30, 5, 1)
    assert e["bonferroni_ohne"] == 0.0 and e["bonferroni"] == 0 and "nie verwerfen" in ev.verdict_null(e)[1]


def test_pool_mit_nur_einem_wert_verwirft_nie():
    e = R.nulltest(np.full((5, 60), 7.0), 10, 50, seed=6)
    assert e["signifikant"] == 0 and e["mit_gleichstand"] == e["tests"]
    assert list(R.haeufigster_anteil(np.full((2, 60), 7.0))) == [1.0, 1.0]


def test_kleinste_instanzen_und_budget_am_rand(quadrat):
    for budget in (1, 2, 3):
        prot = M.Protokoll([budget])
        assert M.lauf_hc(quadrat, 4, budget, Strom(1), prot) == budget and sorted(prot.stand[budget][1]) == [0, 1, 2, 3]
    prot = M.Protokoll([1])
    assert M.lauf_sa(quadrat, 4, 1, Strom(1), prot, 0.3, 3.0) == 1          # Budget 1: nur die Starttour
    prot = M.Protokoll([10])
    assert M.lauf_ga(quadrat, 4, 10, Strom(1), prot) == 10                  # Budget kleiner als die Population
    assert M.kanonisch([0]) == [0] and M.kanonisch([1, 0]) == [0, 1] and M.kanonisch([2, 0, 1]) == [0, 1, 2]


def test_kein_lauf_beendet_den_ersten_abstieg():
    """Budget unter den Kosten eines Durchgangs: `erster_abstieg` bleibt leer, die Lücke ist ein abgebrochener Abstieg."""
    import vgk_basis as basis
    from vgk_rng import SplitMix64
    d = basis.abstaende(basis.rundtour_punkte(SplitMix64(basis.instanz_seed("gleich", 40, 0)), "gleich", 40))
    for verfahren in ("hc", "ils", "ma"):
        prot = M.Protokoll([700])
        M.lauf(verfahren, d, 40, 700, Strom(3), prot)                      # 40 · 37 / 2 = 740 Züge je Durchgang
        assert prot.erster_abstieg is None


def test_nfl_raender():
    assert N.verteilung_minimum("A", "alle", 4) == N.verteilung_minimum("B", "alle", 4) == {0: 65, 1: 15, 2: 1}     # 81 − 16 mit einer 0, 16 − 1 ohne 0 mit einer 1
    with pytest.raises(ValueError):
        N.klasse("unbekannt")
    assert ev.verdict_nfl("alle", 2, {0: 45, 1: 27, 2: 9}, {0: 45, 1: 27, 2: 9})[0] == "info"


def test_unbekanntes_mass_und_verfahren():
    with pytest.raises(ValueError):
        V.mass_wert(np.zeros((1, 3)), "summe")
    with pytest.raises(ValueError):
        V.mass_wert(np.zeros((1, 3)), "flaeche")
    with pytest.raises(ValueError):
        M.lauf("lkh", [[0.0]], 1, 1, Strom(1), M.Protokoll([1]))


def test_anteil_schwelle_ist_inklusive():
    assert 1 - V.mass_wert(np.array([2.0, 2.0000001, 1.0, 5.0]), "anteil") == pytest.approx(0.5)      # genau 2 % zählt, knapp darüber nicht
