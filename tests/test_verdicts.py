"""Verdikte an von Hand gesetzten Zeilen: jede Schwelle der Art und jede Zahl im Text."""

import math

import vgk_evaluation as ev


def _uebersicht(ordnungen, sa="sa_std"):
    alle = {(b, f): o for (b, f), o in ordnungen.items()}
    return {"ordnungen": alle, "verschiedene": sorted(set(alle.values())), "zellen": len(alle), "sa": sa, "zeilen": [{"instanzen": 63}]}


def test_verdict_trio_dauergewinner_und_kippen():
    gleich = _uebersicht({(b, f): "HC < SA < GA" for b in (1000, 3000) for f in ("alle", "gleich")})
    art, text = ev.verdict_trio(gleich, {(1000, 3000): 0.143})
    assert art == "info" and "in allen 4 Zellen" in text and "**HC < SA < GA**" in text and "„Standard“" in text and "höchstens 14 % der 63 Instanzen" in text
    gemischt = _uebersicht({(1000, "alle"): "HC < SA < GA", (1000, "gleich"): "HC < SA < GA", (3000, "alle"): "SA < HC < GA"}, "sa_abg")
    art, text = ev.verdict_trio(gemischt, {(1000, 3000): 0.43})
    assert art == "warning" and "2 verschiedene Ordnungen" in text and "**HC < SA < GA** (2 von 3;" in text and "„abgestimmt“" in text and "43 %" in text


def _gruppen(verschieden, paar=True, median=28.7, ueber=28):
    g = {"r": 5, "verschieden": verschieden, "paare": 66, "gruppen": 12, "gleichstand": 0.012, "mit_abweichung": 0.92}
    e = {"gewaehlt": g, "namen": ["HC", "SA", "GA"], "budget": 3000, "instanzen": 63}
    if paar:
        g.update(strikt=0.297, formel=0.316)
        e.update(namen=["HC", "SA"], laeufe_median=median, laeufe_ueber_60=ueber)
    return e


def test_verdict_gruppen_schwellen_und_zahlen():
    art, text = ev.verdict_gruppen(_gruppen(0.305))
    assert art == "warning"
    for teil in ("**5 Läufen**", "3.000 Auswertungen", "**30 %**", "66 Gruppenpaare", "das Paar HC / SA", "92 % der Instanzen", "ordnen 30 %; die Formel", "sagt 32 % voraus",
                 "In 1 % der Gruppen", "im Median 29 Läufe", "bei 28 von 63 Instanzen mehr als 60"):
        assert teil in text, teil
    assert ev.verdict_gruppen(_gruppen(0.30))[0] == "info" and ev.verdict_gruppen(_gruppen(0.10))[0] == "info" and ev.verdict_gruppen(_gruppen(0.099))[0] == "success"
    art, text = ev.verdict_gruppen(_gruppen(0.2, paar=False))
    assert "das Trio HC, SA, GA" in text and "Formel" not in text and "mindestens zwei Verfahren gleichauf" in text
    text = ev.verdict_gruppen(_gruppen(0.5, median=math.inf, ueber=40))[1]
    assert "reicht auf mehr als der Hälfte der Instanzen keine Gruppengröße" in text and "40 von 63" in text


def _mass(anders_bestes, tau=(0.46, 44)):
    import vgk_compare as V
    anders = {("mittel", m): 0.05 for m in V.MASSE}
    anders[("mittel", "bestes")] = anders_bestes
    return {"budget": 10000, "instanzen": 63, "anders": anders, "tau": {("mittel", m): tau for m in V.MASSE}}


def test_verdict_mass():
    art, text = ev.verdict_mass(_mass(0.937), "bestes")
    assert art == "warning" and "10.000 Auswertungen" in text and "**94 %**" in text and "instabil" in text and "τ: 0,46 (auf 44 Instanzen nicht definiert" in text
    assert "„bester Lauf (kleinste Lücke)“ mit 94 %" in text
    art, text = ev.verdict_mass(_mass(0.937, tau=(0.95, 0)), "median")
    assert art == "success" and "**5 %**" in text and "τ: 0,95." in text and "stabil" in text
    assert ev.verdict_mass(_mass(0.2, tau=(math.nan, 63)), "bestes")[1].count("auf keiner Instanz definiert") == 1
    assert ev.verdict_mass(_mass(0.30), "bestes")[0] == "info" and ev.verdict_mass(_mass(0.31), "bestes")[0] == "warning"


def _null(**kw):
    e = {"verfahren": "hc", "budget": 10000, "m": 30, "r": 10, "seed": 1, "wiederholungen": 100, "anteil_signifikant": 0.0297, "mindestens_eine": 0.63, "bonferroni": 1,
         "anteil_gleichstand": 1.0, "p_ohne": 0.04326, "erwartung_ohne": 0.7346, "erwartung_pool": 0.669, "bonferroni_ohne": 0.0145, "haeufigster_mittel": 0.522,
         "haeufigster_max": 1.0, "standardfehler": 0.047}
    e.update(kw)
    return e


def test_verdict_null_zahlen_und_warnschwelle():
    art, text = ev.verdict_null(_null())
    assert art == "info"                                              # 73,5 − 66,9 = 6,6 Punkte, weniger als 2 · 4,7
    for teil in ("**30 Tests, 10 gegen 10 Läufe", "Hill Climbing, 10.000 Auswertungen", "**63 %**", "3,0 % der Einzeltests", "73,5 % (4,33 % je Einzeltest, nicht 5 %)",
                 "dieser Läufe: 66,9 %", "100 % der Tests enthalten Gleichstände", "im Mittel 52 %", "(höchstens 100 %)", "Mit Bonferroni: 1 von 100 (ohne Gleichstände erwartet 1,45 %)"):
        assert teil in text, teil
    art, text = ev.verdict_null(_null(erwartung_pool=0.481, erwartung_ohne=0.62, standardfehler=0.05, r=5, bonferroni_ohne=0.0, bonferroni=0))
    assert art == "warning" and "beschreibt diese Läufe nicht" in text and "kann dieser Test nach Bonferroni nie verwerfen" in text and "kein Gewinn an Ehrlichkeit" in text
    assert ev.verdict_null(_null(erwartung_pool=0.64, standardfehler=0.047))[0] == "warning"      # 9,46 > 9,4
    assert ev.verdict_null(_null(erwartung_pool=0.641, standardfehler=0.047))[0] == "info"        # 9,36 < 9,4
    assert "**1 Test, " in ev.verdict_null(_null(m=1))[1]


def _einstellung(anders):
    zeile = {"budget": 3000, "anders": anders, "instanzen": 63, "sa_vor_hc": {"sa_std": 0, "sa_abg": 16},
             "sa_std": {"ordnung": "HC < SA < GA"}, "sa_abg": {"ordnung": "SA < HC < GA"}}
    return {"zeilen": [{"budget": 1000, "anders": 0.03}, zeile, {"budget": 10000, "anders": 0.556}]}


def test_verdict_einstellung():
    art, text = ev.verdict_einstellung(_einstellung(0.27), 3000)
    assert art == "info"
    for teil in ("3.000 Auswertungen", "**27 %** der 63 Instanzen", "gemischt", "HC < SA < GA (Standard), SA < HC < GA (abgestimmt)", "auf 0 (Standard) und 16 (abgestimmt)",
                 "1.000 / 3.000 / 10.000: 3 / 27 / 56 %"):
        assert teil in text, teil
    assert ev.verdict_einstellung(_einstellung(0.31), 3000)[0] == "warning" and ev.verdict_einstellung(_einstellung(0.05), 3000)[0] == "success"


def _quartett(fertig, stufen_ordnungen, familien_ordnungen, faktor=0.71):
    zelle = {"stufe": "1000n", "familie": "alle", "instanzen": 56, "laeufe": 12, "mittel": {"hc": 2.159, "sa": 1.413, "ils": 1.65, "ma": 1.999},
             "ordnung": "SA < ILS < MA < HC", "faktor": faktor, "fertig_mittel": fertig}
    return {"zelle": zelle, "stufen": ["30n", "100n", "1000n", "5000n"], "ordnungen_stufen": stufen_ordnungen, "ordnungen_familien": familien_ordnungen,
            "sieger_familien": {"gleich": "sa", "cluster": "ils", "gitter": "sa", "netz": "ma"}}


def test_verdict_quartett_rangfolge_und_abgebrochener_abstieg():
    art, text = ev.verdict_quartett(_quartett(1.0, ["a", "b", "c", "d"], ["x", "y", "x", "z"]))
    assert art == "warning"
    for teil in ("Budget 1.000 · n", "alle Familien (56 Instanzen, 12 Läufe", "HC 2,16 %, SA 1,41 %, ILS 1,65 %, MA 2,00 %", "**SA < ILS < MA < HC**", "Gruppenfaktor 0,71",
                 "100 % der Läufe", "über die 4 Budgets", "4 verschiedene Rangfolgen", "über die 4 Familien bei diesem Budget 3", "ILS, MA, SA", "kippen die Rangfolge"):
        assert teil.lower() in text.lower(), teil
    art, text = ev.verdict_quartett(_quartett(0.49, ["a"] * 4, ["x"] * 4))
    assert art == "warning" and "Nur **49 %**" in text and "abgebrochene Abstiege" in text and "Rangfolge **" not in text      # keine Rangfolge der drei
    art, text = ev.verdict_quartett(_quartett(0.5, ["a"] * 4, ["x"] * 4))
    assert art == "info" and "Hier kippt nichts." in text and "50 % der Läufe" in text
    assert "unendlich" in ev.verdict_quartett(_quartett(1.0, ["a"] * 4, ["x"] * 4, faktor=math.inf))[1]


def test_verdict_woran():
    import vgk_compare as V
    mass = {"instanzen": 63, "anders": {("mittel", m): w for m, w in zip(V.MASSE, (0.0, 0.08, 0.81, 0.21, 0.06))}}
    einst = {"zeilen": [{"budget": 3000, "anders": 0.27}]}
    u = {"zellen": 12, "verschiedene": ["HC < SA < GA"]}
    art, text = ev.verdict_woran(mass, einst, {(1000, 3000): 0.02, (3000, 10000): 0.14}, u, 3000)
    assert art == "warning"
    for teil in ("63 Instanzen", "3.000 Auswertungen", "81 % (instabil)", "27 % (gemischt)", "14 % (gemischt)", "in allen 12 Zellen dieselbe"):
        assert teil in text, teil
    mass["anders"][("mittel", "bestes")] = 0.09
    art, text = ev.verdict_woran(mass, einst, {(1000, 3000): 0.02}, {"zellen": 12, "verschiedene": ["a", "b"]}, 3000)
    assert art == "info" and "21 % (gemischt)" in text and "2 % (stabil)" in text and "2 verschiedene Formen" in text


def test_verdict_live_und_nfl():
    art, text = ev.verdict_live(30, 30, 2.345, 3000)
    assert art == "success" and "30 von 30" in text and "3.000 Auswertungen" in text and "2,3 s" in text
    art, text = ev.verdict_live(29, 30, 2.0, 3000)
    assert art == "warning" and "29 von 30" in text
    art, text = ev.verdict_nfl("glatt", 2, {0: 17, 1: 20, 2: 4}, {0: 20, 1: 18, 2: 3})
    assert art == "warning" and "A das Minimum 0 in 17, B in 20 von 41" in text and "Rundtouren sind keine solche Klasse" in text
    art, text = ev.verdict_nfl("alle", 2, {0: 45, 1: 27, 2: 9}, {0: 45, 1: 27, 2: 9})
    assert art == "info" and "Minimum 0 in 45 von 81" in text


def test_zahlformate():
    assert ev.de(3.14159, 2) == "3,14" and ev.pz(0.4081, 1) == "40,8" and ev.tsd(10000) == "10.000" and ev.tsd(999) == "999"
