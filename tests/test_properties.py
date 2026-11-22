"""Eigenschaften: Invarianten der Maße, Rangfolgen, des Kippens und des Rangtests (fester Zufalls-Seed, je 20 bis 50 Fälle)."""

import math

import numpy as np
import pytest

import vgk_basis as basis
import vgk_compare as V
import vgk_constants as C
import vgk_evaluation as ev
import vgk_methods as M
import vgk_rangtest as R
from vgk_rng import SplitMix64
from vgk_zufall import Strom


def _felder(seed, verfahren=3, instanzen=20, laeufe=30, stufen=12):
    rng = SplitMix64(seed)
    return [np.array([[rng.below(stufen) + k for _ in range(laeufe)] for _ in range(instanzen)], dtype=float) for k in range(verfahren)]


@pytest.mark.parametrize("seed", range(5))
def test_umnummerieren_der_verfahren_aendert_die_rangfolge_nur_in_den_namen(seed):
    f = _felder(seed)
    r1 = V.instanz_raenge(f, "mittel")
    r2 = V.instanz_raenge([f[2], f[0], f[1]], "mittel")
    assert np.array_equal(r1[:, [2, 0, 1]], r2)
    k1, k2 = V.kippen_gruppen(f, 5), V.kippen_gruppen([f[2], f[0], f[1]], 5)
    assert np.allclose(k1["verschieden"], k2["verschieden"]) and np.allclose(k1["gleichstand"], k2["gleichstand"])


@pytest.mark.parametrize("faktor", [0.5, 2.0, 8.0])
def test_skalieren_aller_luecken_aendert_ordnung_und_tau_nicht(faktor):
    f = _felder(11)
    g = [x * faktor for x in f]
    for mass in ("mittel", "median", "bestes"):
        assert np.allclose(V.mass_wert(g[0], mass), faktor * V.mass_wert(f[0], mass))
        assert np.array_equal(V.instanz_raenge(f, mass), V.instanz_raenge(g, mass))
    assert np.allclose(V.kippen_gruppen(f, 5)["verschieden"], V.kippen_gruppen(g, 5)["verschieden"])
    assert V.kippformel(1.0, 2.0, 3.0, 5) == pytest.approx(V.kippformel(faktor, 2 * faktor, 3 * faktor, 5))


def test_vertauschen_der_laeufe_innerhalb_einer_gruppe_aendert_nichts():
    f = _felder(12, laeufe=30)
    perm = np.concatenate([np.arange(5)[::-1] + 5 * g for g in range(6)])        # jede Fünfergruppe in sich umgedreht
    g = [x[:, perm] for x in f]
    a, b = V.kippen_gruppen(f, 5), V.kippen_gruppen(g, 5)
    assert np.array_equal(a["verschieden"], b["verschieden"])
    assert np.array_equal(V.instanz_raenge(f, "median"), V.instanz_raenge(g, "median"))


def test_identische_laeufemengen_gleichstand_und_p_eins():
    f = _felder(13, verfahren=1)[0]
    rang = V.instanz_raenge([f, f.copy()], "mittel")
    assert (rang == 1.5).all()
    k = V.kippen_gruppen([f, f.copy()], 5)
    assert (k["verschieden"] == 0).all() and (k["gleichstand"] == 1).all() and (k["strikt"] == 0).all()
    for zeile in f[:5]:
        assert R.mann_whitney(list(zeile), list(zeile)) == 1.0          # U liegt genau in der Mitte


def test_verschieden_ist_mindestens_strikt_und_gleich_ohne_gleichstaende():
    f = _felder(14, verfahren=2, stufen=4)
    k = V.kippen_gruppen(f, 3)
    assert (k["verschieden"] >= k["strikt"] - 1e-12).all() and (k["verschieden"] > k["strikt"]).any()
    stetig = [np.random.default_rng(s).random((20, 30)) for s in (1, 2)]
    k = V.kippen_gruppen(stetig, 3)
    assert np.array_equal(k["verschieden"], k["strikt"]) and (k["gleichstand"] == 0).all()


def test_identische_verfahren_kippen_im_mittel_zur_haelfte():
    """Zwei Verfahren mit derselben stetigen Verteilung: zwei Gruppen ordnen sie mit Wahrscheinlichkeit 1/2 verschieden (Band)."""
    rng = np.random.default_rng(15)
    a, b = rng.random((400, 60)), rng.random((400, 60))
    anteil = V.kippen_gruppen([a, b], 30)["verschieden"].mean()            # ein Gruppenpaar je Instanz, 400 unabhängige Instanzen
    assert abs(anteil - 0.5) < 4 * math.sqrt(0.25 / 400)
    assert V.kippformel(0.0, 1.0, 1.0, 30) == pytest.approx(0.5)


def test_kippformel_faellt_mit_der_gruppengroesse_und_mit_dem_abstand():
    werte = [V.kippformel(1.0, 2.0, 2.0, r) for r in C.GRUPPEN_R]
    assert all(x > y for x, y in zip(werte, werte[1:]))
    assert V.kippformel(2.0, 2.0, 2.0, 5) < V.kippformel(1.0, 2.0, 2.0, 5) < 0.5
    bedarf = V.laeufe_fuer_fuenf_prozent(1.0, 2.0, 2.0)
    assert V.kippformel(1.0, 2.0, 2.0, math.ceil(bedarf)) <= 0.05 < V.kippformel(1.0, 2.0, 2.0, math.floor(bedarf) - 1)


def test_bonferroni_verwirft_nie_mehr_als_ohne_korrektur():
    rng = np.random.default_rng(16)
    for stufen in (3, 50):
        pool = rng.integers(0, stufen, (40, 60)).astype(float)
        for r in C.NULL_GRUPPEN:
            e = R.nulltest(pool, r, 60, seed=r)
            assert e["bonferroni_signifikant"] <= e["signifikant"] and e["bonferroni_mindestens_eine"] <= e["mindestens_eine"]
            assert 0 <= e["signifikant"] <= e["tests"] == 60 * 40


def test_gleichstandsmodell_bleibt_unter_der_grenze_und_endet_bei_null():
    werte = [R.verwerfung_modell(k / 20) for k in range(20)]
    assert max(werte) < 0.0438                       # nur für dieses Modell bei 10 gegen 10 gezeigt
    assert R.verwerfung_modell(1.0) == 0.0
    assert werte[14] > werte[16] > werte[18] > werte[19]


def test_mindestens_eine_waechst_mit_der_zahl_der_tests():
    p = R.verwerfung_ohne_gleichstand(10)
    werte = [R.mindestens_eine(p, m) for m in (1, 5, 10, 20, 30, 100)]
    assert all(x < y for x, y in zip(werte, werte[1:])) and werte[0] == pytest.approx(p)
    assert [round(100 * w, 1) for w in werte] == [4.3, 19.8, 35.7, 58.7, 73.5, 98.8]


def test_u_verteilung_ist_symmetrisch_und_vollstaendig():
    for a, b in ((5, 5), (10, 10), (20, 20), (4, 9)):
        anz = R.u_anzahl(a, b)
        assert anz == anz[::-1] and sum(anz) == math.comb(a + b, a) and len(anz) == a * b + 1


@pytest.mark.parametrize("verfahren", ["hc", "sa", "ga", "ils", "ma"])
def test_jeder_lauf_nutzt_genau_sein_budget_und_liefert_eine_rundtour(verfahren):
    for k, (familie, n) in enumerate((("gleich", 12), ("cluster", 20), ("gitter", 27), ("netz", 33))):
        d = basis.abstaende(basis.rundtour_punkte(SplitMix64(basis.instanz_seed(familie, n, 0)), familie, n))
        prot = M.Protokoll([500, 2000, 6000])
        ev_zahl = M.lauf(verfahren, d, n, 6000, Strom(k), prot, t0f=0.3, c=3.0)
        assert ev_zahl == 6000 and sorted(prot.stand) == [500, 2000, 6000]
        laengen = [M.laenge_kanonisch(d, prot.stand[p][1]) for p in (500, 2000, 6000)]
        assert laengen[0] >= laengen[1] >= laengen[2]                                     # die beste Tour wird nie schlechter
        assert sorted(prot.stand[6000][1]) == list(range(n))
        assert prot.stand[6000][0] == pytest.approx(laengen[2], rel=1e-9)                 # fortgeschriebene Länge = neu gerechnete Länge


def test_gleicher_zufalls_seed_gleicher_lauf_anderer_seed_anderer_lauf():
    d = basis.abstaende(basis.rundtour_punkte(SplitMix64(basis.instanz_seed("gleich", 25, 0)), "gleich", 25))
    touren = []
    for seed in (1, 1, 2):
        prot = M.Protokoll([800])
        M.lauf_sa(d, 25, 800, Strom(seed), prot, 0.3, 3.0)
        touren.append(prot.stand[800][1])
    assert touren[0] == touren[1] and touren[0] != touren[2]


def test_jede_variante_laeuft_wirklich():
    """Kein toter Zweig: die vier Verfahren des Quartetts und die zwei SA-Einstellungen geben auf derselben Instanz verschiedene Ergebnisse."""
    import vgk_messung as MS
    q = {v: MS.quartett_lauf("gleich", 30, 0, v, 0)["laengen"] for v in C.QUARTETT_VERFAHREN}
    assert len({tuple(round(x, 3) for x in werte.values()) for werte in q.values()}) == 4
    a, b = MS.trio_lauf("gleich", 30, 0, "sa_std", 0), MS.trio_lauf("gleich", 30, 0, "sa_abg", 0)
    assert [a[k][0] for k in C.TRIO_BUDGETS] != [b[k][0] for k in C.TRIO_BUDGETS]


def test_gruppenfaktor_und_ordnungstext():
    assert V.gruppenfaktor({"hc": 4.0, "sa": 6.0, "ils": 1.0, "ma": 2.0}) == 2.0
    assert V.gruppenfaktor({"hc": 4.0, "sa": 6.0, "ils": 0.0, "ma": 0.0}) == math.inf
    assert V.ordnung_text(["HC", "SA", "GA"], [2.0, 1.0, 3.0]) == "SA < HC < GA"
    assert V.ordnung_text(["HC", "SA", "GA"], [1.0, 1.0, 3.0]) == "HC = SA < GA"
    assert ev.lesehilfe(0.09) == "stabil" and ev.lesehilfe(0.10) == "gemischt" and ev.lesehilfe(0.30) == "gemischt" and ev.lesehilfe(0.31) == "instabil"
