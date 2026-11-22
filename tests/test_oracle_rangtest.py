"""Orakel für Rangtest, Rangfolgen und Kippformel (anderer Rechenweg: scipy, vollständige Aufzählung, Simulation mit anderem Zufallsstrom)."""

import itertools
import math

import numpy as np
import pytest

import vgk_compare as V
import vgk_rangtest as R
from vgk_rng import SplitMix64

stats = pytest.importorskip("scipy.stats")


def _zufallspaar(rng, r, stufen):
    """Zwei Gruppen mit Werten aus `stufen` möglichen Zahlen (kleine Stufenzahl: viele Gleichstände)."""
    return [rng.below(stufen) for _ in range(r)], [rng.below(stufen) for _ in range(r)]


def test_p_wert_gegen_scipy_mit_und_ohne_gleichstaende():
    rng = SplitMix64(2026)
    for k in range(400):
        r = (5, 10, 20)[k % 3]
        x, y = _zufallspaar(rng, r, (3, 8, 40, 10**6)[k % 4])
        if len(set(x + y)) == 1:
            continue
        soll = stats.mannwhitneyu(x, y, alternative="two-sided", method="asymptotic", use_continuity=True)
        u, gleich = R.u_statistik(y, x)          # scipy: Statistik der ersten Gruppe = Paare x > y; hier aus Sicht von y gerechnet und gespiegelt
        assert r * r - u == pytest.approx(soll.statistic)
        assert R.mann_whitney(x, y) == pytest.approx(soll.pvalue, rel=1e-12, abs=1e-15)


def test_alle_werte_gleich_gibt_p_eins():
    assert R.mann_whitney([3] * 10, [3] * 10) == 1.0
    z, gleich = R.z_werte(np.full((1, 10), 3.0), np.full((1, 10), 3.0))
    assert z[0] == -np.inf and gleich[0]


def test_u_verteilung_gegen_scipy_exakt_und_aufzaehlung():
    for a, b in ((3, 4), (5, 5), (6, 3)):
        zaehler = [0] * (a * b + 1)
        for comb in itertools.combinations(range(a + b), a):      # Plätze der x-Werte in der sortierten Folge
            zaehler[sum(comb) - a * (a - 1) // 2] += 1
        assert tuple(zaehler) == R.u_anzahl(a, b)
    anz = R.u_anzahl(10, 10)
    assert anz == anz[::-1] and sum(anz) == 184756
    kum = np.cumsum(anz) / 184756
    for u in (0, 7, 10, 23, 30):
        x = list(range(10))
        # eine Anordnung mit genau u Paaren x > y bauen: y-Werte 100..109, die x-Werte einzeln nach oben schieben
        y = [100 + k for k in range(10)]
        rest = u
        for k in range(9, -1, -1):
            schub = min(10, rest)
            x[k] = 99.5 + schub + 0.001 * k if schub else x[k]
            rest -= schub
        assert sum(xi > yj for xi in x for yj in y) == u
        assert stats.mannwhitneyu(x, y, alternative="two-sided", method="exact").pvalue == pytest.approx(min(1.0, 2 * kum[u]), rel=1e-9)


def test_verwerfung_ohne_gleichstand_gegen_aufzaehlung_mit_scipy():
    """7 gegen 7: alle C(14, 7) = 3432 Rangverteilungen, je p-Wert von scipy (asymptotisch); der Anteil unter 0,05 ist die exakte Wahrscheinlichkeit."""
    r = 7
    treffer = 0
    for comb in itertools.combinations(range(2 * r), r):
        x = list(comb)
        y = [k for k in range(2 * r) if k not in comb]
        treffer += stats.mannwhitneyu(x, y, alternative="two-sided", method="asymptotic").pvalue < 0.05
    assert math.comb(14, 7) == 3432
    assert R.verwerfung_ohne_gleichstand(r) == pytest.approx(treffer / 3432, rel=1e-12)


def test_gleichstandsmodell_gegen_simulation():
    """Band: 20.000 simulierte Tests je q, Abweichung höchstens 4 Standardfehler."""
    for q, seed in ((0.3, 1), (0.8, 2), (0.9, 3)):
        rng = np.random.default_rng(seed)
        zahl = 20000
        roh = rng.random((zahl, 20))
        werte = np.where(rng.random((zahl, 20)) < q, 0.0, 1.0 + roh)
        z, _ = R.z_werte(werte[:, :10], werte[:, 10:])
        anteil = (z > R.z_schwelle(0.05)).mean()
        p = R.verwerfung_modell(q)
        assert abs(anteil - p) < 4 * math.sqrt(p * (1 - p) / zahl)


def test_viele_tests_auf_einmal_gleich_einzeltests():
    rng = SplitMix64(5)
    x = np.array([[rng.below(6) for _ in range(10)] for _ in range(300)], dtype=float)
    y = np.array([[rng.below(6) for _ in range(10)] for _ in range(300)], dtype=float)
    z, gleich = R.z_werte(x, y)
    for k in range(300):
        p = R.mann_whitney(list(x[k]), list(y[k]))
        assert (z[k] > R.z_schwelle(0.05)) == (p < 0.05)
        assert gleich[k] == (len(set(list(x[k]) + list(y[k]))) < 20)
        if np.isfinite(z[k]):
            assert math.erfc(z[k] / math.sqrt(2)) == pytest.approx(p, rel=1e-9) or p == 1.0


def test_z_schwelle_gegen_normalverteilung():
    assert R.z_schwelle(0.05) == pytest.approx(stats.norm.isf(0.025), rel=1e-12)
    assert R.z_schwelle(0.05 / 30) == pytest.approx(stats.norm.isf(0.025 / 30), rel=1e-12)


def test_gruppen_ziehen_ohne_zuruecklegen_und_unabhaengig():
    pool = np.arange(3 * 60, dtype=float).reshape(3, 60)
    x, y = R.ziehe_gruppen(pool, 10, 500, seed=9)
    assert x.shape == y.shape == (500, 3, 10)
    for w in range(500):
        for i in range(3):
            beide = np.concatenate([x[w, i], y[w, i]])
            assert len(set(beide)) == 20 and set(beide) <= set(pool[i])       # kein Lauf doppelt, alle aus dem Pool der Instanz
    # jeder Lauf kommt etwa gleich oft in eine Gruppe (Erwartung 1/3 je Ziehung); Band 5 Standardfehler
    haeufig = np.array([(x[:, 0, :] == v).sum() + (y[:, 0, :] == v).sum() for v in pool[0]]) / 500
    assert np.all(np.abs(haeufig - 1 / 3) < 5 * math.sqrt((1 / 3) * (2 / 3) / 500))
    with pytest.raises(ValueError):
        R.ziehe_gruppen(pool[:, :15], 10, 5, seed=1)


def test_nulltest_auf_stetigen_werten_trifft_die_exakte_erwartung():
    """Pool ohne Gleichstände: der Anteil verworfener Einzeltests liegt im Band um 4,326 %, mindestens eine unter 30 im Band um 73,5 %."""
    pool = np.random.default_rng(11).random((30, 60))
    erg = R.nulltest(pool, 10, 600, seed=3)
    p = R.verwerfung_ohne_gleichstand(10)
    assert erg["tests"] == 18000 and erg["mit_gleichstand"] == 0
    assert abs(erg["signifikant"] / 18000 - p) < 4 * math.sqrt(p * (1 - p) / 18000)
    e = R.mindestens_eine(p, 30)
    assert abs(erg["mindestens_eine"] / 600 - e) < 4 * math.sqrt(e * (1 - e) / 600)
    assert erg["bonferroni_mindestens_eine"] <= erg["mindestens_eine"] and erg["bonferroni_signifikant"] <= erg["signifikant"]


def test_haeufigster_anteil_und_erwartung_aus_pool():
    pool = np.array([[1.0] * 45 + list(range(2, 17)), list(range(60))], dtype=float)
    assert list(R.haeufigster_anteil(pool)) == [45 / 60, 1 / 60]
    assert R.erwartung_aus_pool([0.5, 0.5]) == pytest.approx(0.75) and R.erwartung_aus_pool([0.0, 0.0]) == 0.0


def test_kendall_tau_b_gegen_scipy():
    rng = SplitMix64(31)
    for _ in range(300):
        k = 3 + rng.below(4)
        a = [rng.below(4) for _ in range(k)]
        b = [rng.below(4) for _ in range(k)]
        ist = V.kendall_tau_b(a, b)
        soll = stats.kendalltau(a, b).statistic
        if ist is None:
            assert math.isnan(soll)
        else:
            assert ist == pytest.approx(soll, abs=1e-12)


def test_raenge_gegen_scipy_rankdata():
    rng = SplitMix64(32)
    werte = np.array([[rng.below(5) for _ in range(4)] for _ in range(200)], dtype=float)
    assert np.array_equal(V.raenge(werte), stats.rankdata(werte, axis=-1, method="average"))


def test_kippformel_gegen_simulation_aus_normalzahlen():
    """Zwei Gruppenmittel je Verfahren aus Normalzahlen: Anteil strikt entgegengesetzter Ordnungen im Band von 4 Standardfehlern."""
    rng = np.random.default_rng(7)
    zahl = 40000
    for delta, s1, s2, r in ((1.0, 2.0, 3.0, 5), (0.0, 1.0, 1.0, 5), (2.0, 2.0, 2.0, 15), (0.5, 1.0, 4.0, 3)):
        a = rng.normal(delta, s1, (zahl, 2, r)).mean(axis=-1)
        b = rng.normal(0.0, s2, (zahl, 2, r)).mean(axis=-1)
        zeichen = np.sign(a - b)
        anteil = (zeichen[:, 0] * zeichen[:, 1] < 0).mean()
        p = V.kippformel(delta, s1, s2, r)
        assert abs(anteil - p) < 4 * math.sqrt(p * (1 - p) / zahl)


def test_kippen_gruppen_gegen_schleife():
    """Kleine Felder, Gruppenpaare von Hand durchgezählt (Schleife statt Feldrechnung)."""
    rng = SplitMix64(40)
    a = np.array([[rng.below(4) for _ in range(12)] for _ in range(5)], dtype=float)
    b = np.array([[rng.below(4) for _ in range(12)] for _ in range(5)], dtype=float)
    erg = V.kippen_gruppen([a, b], 3)
    assert erg["gruppen"] == 4 and erg["paare"] == 6
    for i in range(5):
        ordnung = []
        for g in range(4):
            ma, mb = round(sum(a[i, 3 * g:3 * g + 3]) / 3, 9), round(sum(b[i, 3 * g:3 * g + 3]) / 3, 9)
            ordnung.append(int(ma > mb) - int(ma < mb))
        paare = list(itertools.combinations(ordnung, 2))
        assert erg["verschieden"][i] == pytest.approx(sum(p != q for p, q in paare) / 6)
        assert erg["strikt"][i] == pytest.approx(sum(p * q < 0 for p, q in paare) / 6)
        assert erg["gleichstand"][i] == pytest.approx(sum(o == 0 for o in ordnung) / 4)
