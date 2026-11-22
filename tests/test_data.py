"""Eingefrorene Messreihen: Aufbau, Stimmigkeit und Stichproben neu gerechnet (als Band, weil die Exponentialfunktion des Annealing aus der C-Bibliothek kommt)."""

import json
from pathlib import Path

import numpy as np
import pytest

import vgk_constants as C
import vgk_daten as D
import vgk_messung as MS
import vgk_rangtest as R

DATA = Path(__file__).resolve().parent.parent / "data"
TRIO, QUARTETT, POOL = D.trio(), D.quartett(), D.nulltest()


@pytest.mark.parametrize("name", ["vgk_trio.json", "vgk_quartett.json", "vgk_nulltest.json", "vgk_abstimmung.json"])
def test_jede_datei_nennt_quelle_stand_und_voraussetzung(name):
    roh = json.loads((DATA / name).read_text(encoding="utf-8"))
    assert roh["quelle"].startswith("tools/vgk_make_daten.py") and roh["stand"] == "2026-11-21" and len(roh["voraussetzung"]) > 40


def test_aufbau_trio():
    assert TRIO["budgets"] == C.TRIO_BUDGETS and TRIO["verfahren"] == C.TRIO_VERFAHREN
    assert list(zip(TRIO["familie"], TRIO["n"])) == [(f, n) for f, n, _ in MS.trio_instanzen()]
    for v in C.TRIO_VERFAHREN:
        for b in C.TRIO_BUDGETS:
            assert TRIO["laengen"][v][b].shape == (63, C.TRIO_LAEUFE) and TRIO["flaeche"][v][b].shape == (63, C.TRIO_LAEUFE)
            assert TRIO["luecke"][v][b].min() >= 0.0                      # kein Lauf unterbietet die Referenz
    assert json.loads((DATA / "vgk_trio.json").read_text(encoding="utf-8"))["sa_einstellungen"] == {k: list(v) for k, v in C.SA_TRIO.items()}


def test_trio_mehr_budget_ist_nie_schlechter_bei_gemeinsamen_laeufen():
    """HC und GA: die kleineren Budgets sind Zwischenstände desselben Laufs, die beste Länge kann nur fallen."""
    for v in ("hc", "ga"):
        l1, l3, l10 = (TRIO["laengen"][v][b] for b in C.TRIO_BUDGETS)
        assert (l3 <= l1).all() and (l10 <= l3).all()
    # die Fläche (Mittel der besten Länge über die Prüfpunkte) liegt nie unter dem Endstand
    for v in C.TRIO_VERFAHREN:
        for b in C.TRIO_BUDGETS:
            assert (TRIO["flaeche"][v][b] >= TRIO["luecke"][v][b] - 1e-6).all()


def test_aufbau_quartett():
    assert tuple(QUARTETT["stufen"]) == tuple(C.QUARTETT_STUFEN) and QUARTETT["verfahren"] == C.QUARTETT_VERFAHREN
    assert list(zip(QUARTETT["familie"], QUARTETT["n"])) == [(f, n) for f, n, _ in MS.quartett_instanzen()]
    for v in C.QUARTETT_VERFAHREN:
        for s in C.QUARTETT_STUFEN:
            assert QUARTETT["luecke"][v][s].shape == (56, C.QUARTETT_LAEUFE) and QUARTETT["luecke"][v][s].min() >= 0.0
    assert set(QUARTETT["erster_abstieg"]) == {"hc", "ils", "ma"}
    for v in ("hc", "ils", "ma"):
        stufen = list(C.QUARTETT_STUFEN)
        for a, b in zip(stufen, stufen[1:]):
            assert (QUARTETT["luecke"][v][b] <= QUARTETT["luecke"][v][a] + 1e-9).all()
        # ein Abstieg bewertet nach der letzten Verbesserung alle n(n-3)/2 Züge: der erste Abstieg kostet mindestens 1 + n(n-3)/2
        n = QUARTETT["n"][:, None]
        assert (QUARTETT["erster_abstieg"][v] >= 1 + n * (n - 3) // 2).all()


def _anteil_gleich(neu, alt):
    return float(np.mean(np.abs(np.asarray(neu) - np.asarray(alt)) <= 1e-9 * np.maximum(1.0, np.abs(alt))))


@pytest.mark.parametrize("familie,n,verfahren,laeufe", [("gleich", 20, "hc", 20), ("cluster", 33, "hc", 10), ("gitter", 24, "sa_std", 12), ("gleich", 29, "sa_abg", 12), ("cluster", 21, "ga", 3)])
def test_trio_stichprobe_neu_gerechnet(familie, n, verfahren, laeufe):
    zeile = next(k for k in range(63) if TRIO["familie"][k] == familie and TRIO["n"][k] == n)
    neu = [MS.trio_lauf(familie, n, 0, verfahren, lauf) for lauf in range(laeufe)]
    for b in C.TRIO_BUDGETS:
        assert _anteil_gleich([round(z[b][0], 3) for z in neu], TRIO["laengen"][verfahren][b][zeile, :laeufe]) >= 0.9, (verfahren, b)


@pytest.mark.parametrize("familie,n,idx,verfahren", [("netz", 20, 0, "hc"), ("gleich", 30, 1, "sa"), ("gitter", 20, 1, "ils"), ("cluster", 30, 0, "ma")])
def test_quartett_stichprobe_neu_gerechnet(familie, n, idx, verfahren):
    roh = json.loads((DATA / "vgk_quartett.json").read_text(encoding="utf-8"))["instanzen"]
    zeile = next(z for z in roh if (z["familie"], z["n"], z["idx"]) == (familie, n, idx))
    neu = [MS.quartett_lauf(familie, n, idx, verfahren, lauf) for lauf in range(3)]
    for s in C.QUARTETT_STUFEN:
        assert _anteil_gleich([round(z["laengen"][s], 3) for z in neu], zeile["laengen"][verfahren][s][:3]) >= 0.66
    if verfahren != "sa":
        assert [z["erster_abstieg"] for z in neu] == zeile["erster_abstieg"][verfahren][:3]


def test_referenz_ist_die_kuerzeste_bekannte_tour():
    roh = json.loads((DATA / "vgk_trio.json").read_text(encoding="utf-8"))["instanzen"]
    for z in roh[:6]:
        alle = [x for v in z["laengen"].values() for b in v.values() for x in b]
        assert z["referenz"] <= min(alle)
        assert round(MS.referenz_lauf(z["familie"], z["n"], 0, 0), 3) >= z["referenz"]     # kein Referenzlauf ist kürzer als die gespeicherte Referenz


def test_pool_erwartung_aufbau():
    assert set(POOL["zellen"]) == {f"{v}|{b}" for v in C.TRIO_VERFAHREN for b in C.TRIO_BUDGETS}
    for zelle in POOL["zellen"].values():
        assert len(zelle["haeufigster"]) == 63 and all(1 / 60 - 1e-9 <= x <= 1.0 for x in zelle["haeufigster"])
        for r in C.NULL_GRUPPEN:
            assert len(zelle[str(r)]["p"]) == 63 and all(0.0 <= x <= 0.12 for x in zelle[str(r)]["p"])


@pytest.mark.parametrize("verfahren,budget,r", [("hc", 10000, 10), ("ga", 3000, 10), ("sa_std", 3000, 5), ("hc", 3000, 20)])
def test_pool_erwartung_gegen_einen_zweiten_zufallsstrom(verfahren, budget, r):
    """Gegenprobe: dieselbe Schätzung mit anderem Zufalls-Seed und 2.000 Ziehungen; das Mittel der p_i liegt im Band (4 Standardfehler), ebenso der häufigste Wert exakt."""
    pool = TRIO["laengen"][verfahren][budget]
    zelle = POOL["zellen"][f"{verfahren}|{budget}"]
    p, gleich = R.pool_wahrscheinlichkeit(pool, r, 2000, seed=987654321)
    alt = np.array(zelle[str(r)]["p"])
    fehler = np.sqrt(alt.mean() * (1 - alt.mean()) / (63 * 2000) + alt.mean() * (1 - alt.mean()) / (63 * POOL["ziehungen"]))
    assert abs(p.mean() - alt.mean()) < 4 * fehler
    assert abs(gleich.mean() - np.mean(zelle[str(r)]["gleichstand"])) < 0.02
    assert np.allclose(R.haeufigster_anteil(pool), zelle["haeufigster"], atol=1e-4)


def test_instanz_ganz_ohne_streuung_verwirft_nie():
    """Hill Climbing bei 10.000 Auswertungen: auf Instanzen, deren 60 Läufe alle denselben Wert haben, ist die Verwerfungswahrscheinlichkeit 0."""
    zelle = POOL["zellen"]["hc|10000"]
    einwertig = [k for k, x in enumerate(zelle["haeufigster"]) if x == 1.0]
    assert einwertig
    for r in C.NULL_GRUPPEN:
        assert all(zelle[str(r)]["p"][k] == 0.0 for k in einwertig)
