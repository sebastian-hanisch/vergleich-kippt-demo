"""Die Handbeispiele des Plans als exakte Tests (Brüche, Ganzzahlen, Aufzählung): die Handwerte stehen als Rechnung im Test."""

import itertools
import math
from fractions import Fraction as F

import numpy as np
import pytest

import vgk_compare as V
import vgk_evaluation as ev
import vgk_nfl as N
import vgk_rangtest as R


# --- 1. No-Free-Lunch im Kleinen ------------------------------------------------------------------------------------------------
def test_nfl_alle_81_funktionen_gleiche_verteilung():
    assert len(N.klasse("alle")) == 3 ** 4 == 81
    for m in (1, 2, 3, 4):
        a, b = N.folgen_verteilung("A", "alle", m), N.folgen_verteilung("B", "alle", m)
        assert a == b and set(a.values()) == {3 ** (4 - m)}        # jede Wertefolge gleich oft
        assert N.verteilung_minimum("A", "alle", m) == N.verteilung_minimum("B", "alle", m)
    # nach 2 Auswertungen ist das Minimum 0 in (3² − 2²) · 3² = 45 von 81 Funktionen
    assert N.verteilung_minimum("A", "alle", 2)[0] == N.verteilung_minimum("B", "alle", 2)[0] == (9 - 4) * 9 == 45


def test_nfl_glatte_klasse_unterscheidet_die_verfahren():
    assert len(N.klasse("glatt")) == 12 + 17 + 12 == 41
    assert tuple(N.verteilung_minimum("A", "glatt", 1).values()) == tuple(N.verteilung_minimum("B", "glatt", 1).values()) == (12, 17, 12)
    assert tuple(N.verteilung_minimum("A", "glatt", 4).values()) == tuple(N.verteilung_minimum("B", "glatt", 4).values()) == (25, 15, 1)
    assert (N.verteilung_minimum("A", "glatt", 2)[0], N.verteilung_minimum("B", "glatt", 2)[0]) == (17, 20)
    assert (N.verteilung_minimum("A", "glatt", 3)[0], N.verteilung_minimum("B", "glatt", 3)[0]) == (21, 23)


def test_nfl_glatte_klasse_ist_nicht_unter_permutation_abgeschlossen():
    f = (0, 1, 2, 2)
    assert N.ist_glatt(f) and not N.ist_glatt((f[0], f[2], f[1], f[3]))
    assert N.abschluss_unter_permutation("glatt") == 67 and N.abschluss_unter_permutation("alle") == 81


# --- 2. Mehrfachtest exakt, 5 gegen 5 --------------------------------------------------------------------------------------------
def test_u_verteilung_fuenf_gegen_fuenf():
    anz = R.u_anzahl(5, 5)
    assert sum(anz) == math.comb(10, 5) == 252 and list(anz[:4]) == [1, 1, 2, 3]
    # Aufzählung aller Rangverteilungen: U = Rangsumme − 15 (Ränge 0..9: Summe − 10)
    zaehler = [0] * 26
    for comb in itertools.combinations(range(10), 5):
        zaehler[sum(comb) - 10] += 1
    assert tuple(zaehler) == anz


def test_exakter_test_verwirft_mit_zwei_dreiundsechzigstel():
    # U ≤ 2 oder U ≥ 23: 2 · (1 + 1 + 2) / 252 = 8/252 = 2/63; p(U = 3) = 14/252 > 0,05
    assert F(8, 252) == F(2, 63) and F(8, 252) < F(1, 20) < F(14, 252)
    assert R.verwerfung_exakter_test(5) == pytest.approx(2 / 63, rel=1e-12)
    assert R.verwerfung_ohne_gleichstand(5) == pytest.approx(2 / 63, rel=1e-12)       # die Normalnäherung verwirft bei 5 gegen 5 dieselben U
    assert R.mindestens_eine(2 / 63, 30) == pytest.approx(float(1 - F(61, 63) ** 30), rel=1e-12)
    assert abs(R.mindestens_eine(2 / 63, 30) - 0.6201) < 5e-4
    assert abs(R.mindestens_eine(0.05, 30) - 0.7854) < 5e-5


def test_bonferroni_kann_bei_fuenf_gegen_fuenf_nie_verwerfen():
    # kleinster exakter p-Wert 2/252 liegt über der Schwelle 0,05/30 = 1/600; die Normalnäherung verwirft dort ebenfalls nie
    assert F(2, 252) > F(1, 600)
    assert R.verwerfung_exakter_test(5, 0.05 / 30) == 0.0
    assert R.verwerfung_ohne_gleichstand(5, 0.05 / 30) == 0.0


# --- 3. Kippen durch kleine Läufegruppen ----------------------------------------------------------------------------------------
def test_kippen_binomial_von_hand():
    k = V.kippen_binomial(F(3, 5), F(2, 5), 1)
    assert (k["a_vorn"], k["b_vorn"], k["gleich"]) == (F(9, 25), F(4, 25), F(12, 25))
    assert k["verschieden"] == 1 - F(81 + 16 + 144, 625) == F(384, 625)
    assert k["strikt"] == F(72, 625)
    assert k["verschieden"] == k["strikt"] + 2 * k["gleich"] * (1 - k["gleich"]) and 2 * k["gleich"] * (1 - k["gleich"]) == F(312, 625)


def test_kippen_binomial_verschieden_faellt_strikt_steigt():
    werte = {r: V.kippen_binomial(F(3, 5), F(2, 5), r) for r in (1, 3, 5)}
    assert [round(float(werte[r]["verschieden"]), 3) for r in (1, 3, 5)] == [0.614, 0.595, 0.531]
    assert all(abs(float(werte[r]["strikt"]) - soll) < 1e-3 for r, soll in ((1, 0.115), (3, 0.195), (5, 0.211)))


def test_kippformel_handwerte():
    assert V.kippformel(1.0, 1.0, 0.0, 1) == pytest.approx(2 * V.phi(1.0) * (1 - V.phi(1.0)))
    assert abs(V.kippformel(1.0, 1.0, 0.0, 1) - 0.2670) < 1e-4                   # d = 1
    assert V.kippformel(0.0, 1.0, 1.0, 7) == pytest.approx(0.5)                   # kein Unterschied: Münzwurf
    d = 1 * math.sqrt(5) / math.sqrt(8)                                           # r = 5, δ = 1, s1 = s2 = 2
    assert abs(d - 0.7906) < 1e-4 and abs(V.kippformel(1.0, 2.0, 2.0, 5) - 0.3371) < 5e-4
    assert abs(2 * V.phi(V.D_FUENF_PROZENT) * (1 - V.phi(V.D_FUENF_PROZENT)) - 0.05) < 1e-5


# --- 4. Das Maß ändert die Rangfolge --------------------------------------------------------------------------------------------
def test_mass_aendert_die_rangfolge():
    a, b = np.array([2.0, 2, 2, 2, 12]), np.array([3.0, 3, 3, 3, 3])
    assert (V.mass_wert(a, "mittel"), V.mass_wert(b, "mittel")) == (4.0, 3.0)            # B besser
    assert (V.mass_wert(a, "median"), V.mass_wert(b, "median")) == (2.0, 3.0)            # A besser
    assert (V.mass_wert(a, "bestes"), V.mass_wert(b, "bestes")) == (2.0, 3.0)            # A besser
    assert (1 - V.mass_wert(a, "anteil"), 1 - V.mass_wert(b, "anteil")) == (pytest.approx(0.8), 0.0)   # Anteil ≤ 2 %: A besser
    zeilen = ev.mass_beispiel()
    assert [z["besser"] for z in zeilen] == ["B", "A", "A", "A"]


# --- 5. Zählweise: Kosten je Schritt und das gesetzte Modell --------------------------------------------------------------------
def test_zugzahlen_und_verhaeltnis():
    for n, m, k in ((30, 405, 54), (50, 1175, 94), (100, 4850, 194)):
        assert ev.zuege_voll(n) == n * (n - 3) // 2 == m and ev.zuege_warteschlange(n) == 2 * (n - 3) == k
        assert F(m, k) == F(n, 4)
    assert 240000 // 4850 == 49 and 240000 // 194 == 1237


def test_gesetztes_modell_rangumkehr():
    tab = ev.gesetztes_modell()
    assert (tab["voll"]["schritte"], tab["warteschlange"]["schritte"]) == ((412, 3), (10309, 53))
    assert tab["voll"]["luecke"] == (F(1), F(50) * F(4, 5) ** 3) and float(tab["voll"]["luecke"][1]) == 25.6
    assert tab["warteschlange"]["luecke"] == (F(1), F(1, 2))
    assert tab["voll"]["luecke"][0] < tab["voll"]["luecke"][1] and tab["warteschlange"]["luecke"][1] < tab["warteschlange"]["luecke"][0]


# --- 6. Kendall τ von Hand ---------------------------------------------------------------------------------------------------------
def test_kendall_tau_von_hand():
    # Ränge 2-opt, Or-opt, Vereinigung, 3-opt: (1, 2, 3, 4) gegen (2, 4, 1, 3): 3 Paare gleich, 3 entgegengesetzt
    assert V.kendall_tau_b([1, 2, 3, 4], [2, 4, 1, 3]) == 0.0
    moeglich = {F(c - (6 - c), 6) for c in range(7)}
    assert sorted(moeglich) == [F(k, 3) for k in range(-3, 4)]
    assert V.kendall_tau_b([1, 2, 3, 4], [1, 2, 4, 3]) == pytest.approx(2 / 3)
    assert V.kendall_tau_b([1, 1, 1, 1], [1, 2, 3, 4]) is None


# --- 7. Mehrfachtest mit Gleichständen --------------------------------------------------------------------------------------------
def test_gleichstand_von_hand():
    x, y = (0, 0, 0, 1, 2), (0, 0, 3, 4, 5)
    u, gleich = R.u_statistik(x, y)
    assert u == 3 * 2 * 0.5 + 2 * 2 == 7.0 and gleich == 5 ** 3 - 5 == 120.0
    assert R.varianz_u(5, 5) == pytest.approx(275 / 12)                                   # 25 · 11 / 12
    assert R.varianz_u(5, 5, 120.0) == pytest.approx(float(F(25, 12) * (11 - F(120, 90)))) == pytest.approx(725 / 36)
    assert R.p_wert(7, 5, 5, 120.0) < R.p_wert(7, 5, 5)                                  # dieselbe Statistik, kleinerer p-Wert


@pytest.mark.parametrize("q,soll", [(0.0, 0.04326), (0.3, 0.04375), (0.5, 0.04257), (0.7, 0.04091), (0.8, 0.03216), (0.9, 0.00922)])
def test_gleichstandsmodell_werte_des_plans(q, soll):
    assert abs(R.verwerfung_modell(q) - soll) < 1e-5


def test_gleichstandsmodell_unter_dreissig_tests():
    assert abs(R.mindestens_eine(R.verwerfung_modell(0.0), 30) - 0.7346) < 5e-4
    assert abs(R.mindestens_eine(R.verwerfung_modell(0.9), 30) - 0.243) < 1e-3


def test_bonferroni_testvariante():
    anz = R.u_anzahl(10, 10)
    assert sum(anz) == math.comb(20, 10) == 184756
    schwelle = 0.05 / 30
    assert max(u for u in range(51) if R.p_wert(u, 10, 10) < schwelle) == 7
    assert abs(R.verwerfung_ohne_gleichstand(10, schwelle) - 0.000487) < 1e-6 and abs(R.verwerfung_exakter_test(10, schwelle) - 0.001505) < 1e-6
    assert abs(R.mindestens_eine(R.verwerfung_ohne_gleichstand(10, schwelle), 30) - 0.0145) < 1e-4
    assert abs(R.mindestens_eine(R.verwerfung_exakter_test(10, schwelle), 30) - 0.0442) < 1e-4


@pytest.mark.parametrize("r,soll", [(5, 0.03175), (10, 0.04326), (20, 0.04909)])
def test_andere_gruppengroessen_ohne_gleichstand(r, soll):
    assert abs(R.verwerfung_ohne_gleichstand(r) - soll) < 5e-6
