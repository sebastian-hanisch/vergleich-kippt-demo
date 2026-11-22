"""Claims: jede Zahl der README gegen die eingefrorenen Messreihen (exakt gegen die Dateien) oder gegen eine exakte Rechnung.

Die Tabellen der README erzeugt `tools/vgk_readme_tabellen.py`; hier wird geprüft, dass die README genau diese Tabellen enthält, und
die Zahlen des Fließtexts werden einzeln nachgerechnet. Die Messreihen selbst prüft `tests/test_data.py` (Stichproben neu gerechnet)."""

import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import vgk_constants as C
import vgk_daten as D
import vgk_evaluation as ev
import vgk_rangtest as R
import vgk_texts as T

ROOT = Path(__file__).resolve().parent.parent
README = (ROOT / "README.md").read_text(encoding="utf-8")
sys.path.insert(0, str(ROOT / "tools"))
import vgk_readme_tabellen as TAB  # noqa: E402

TRIO, QUARTETT, POOL = D.trio(), D.quartett(), D.nulltest()


def _in_readme(text: str):
    assert text in README, f"nicht in der README: {text}"


def test_readme_tabellen_stammen_aus_den_daten():
    assert TAB.ersetze(README, TAB.tabellen()) == README


def test_kurzfassung_trio():
    u = ev.trio_uebersicht(TRIO, "sa_std")
    assert u["zellen"] == 12 and u["verschiedene"] == ["HC < SA < GA"]
    assert all(z["vorn"] == {"HC": 63, "SA": 0, "GA": 0} and z["instanzen"] == 63 for z in u["zeilen"])
    a = ev.trio_uebersicht(TRIO, "sa_abg")
    assert sum(1 for o in a["ordnungen"].values() if o == "HC < SA < GA") == 11 and len(a["verschiedene"]) == 2
    assert [z["vorn"]["SA"] for z in a["zeilen"]] == [2, 16, 27]
    _in_readme("in allen 12 Zellen")
    _in_readme("HC liegt auf 63 von 63 Instanzen allein vorn")
    _in_readme("auf 2 / 16 / 27 von 63 Instanzen vor HC")
    _in_readme("(11 von 12 Zellen)")
    assert len(TRIO["familie"]) == 63 and min(TRIO["n"]) == 20 and max(TRIO["n"]) == 40
    assert set(TRIO["referenz_von"]) == {"Referenzlauf"}       # „In allen 63 Instanzen … aus einem Referenzlauf oder wird von ihm erreicht“


def _zeile_gruppen(budget, paar, sa="sa_std"):
    return {p["r"]: p for p in ev.exp_gruppen(TRIO, budget, 5, paar, sa)["kurve"]}


def test_kurzfassung_gruppen():
    r5 = " / ".join(ev.pz(_zeile_gruppen(b, "alle")[5]["verschieden"], 1) for b in C.TRIO_BUDGETS)
    r15 = " / ".join(ev.pz(_zeile_gruppen(b, "alle")[15]["verschieden"], 1) for b in C.TRIO_BUDGETS)
    assert (r5, r15) == ("29,5 / 40,8 / 51,6", "15,6 / 27,0 / 32,3")
    _in_readme(f"ordnen {r5} % der Gruppenpaare je Instanz das Trio verschieden")
    _in_readme(f"mit Gruppen zu 15 Läufen {r15} %")
    p = _zeile_gruppen(3000, "hc_sa")[5]
    assert (ev.pz(p["verschieden"], 1), ev.pz(p["strikt"], 1), ev.pz(p["formel"], 1)) == ("35,0", "34,3", "33,2")
    _in_readme("35,0 % der Gruppenpaare ordnen das Paar verschieden, 34,3 % strikt entgegengesetzt, die Formel sagt 33,2 %")
    assert p["paare"] == 66 and p["gruppen"] == 12 and _zeile_gruppen(3000, "hc_sa")[15]["paare"] == 6 and _zeile_gruppen(3000, "hc_sa")[30]["paare"] == 1
    nie = ev.exp_gruppen(TRIO, 1000, 5, "sa_ga", "sa_std")
    assert all(k["verschieden"] == 0.0 for k in nie["kurve"]) and nie["laeufe_bis_5"] == 63


def test_mehr_laeufe_weniger_kippen_mit_benannten_ausnahmen():
    """Zählung über alle 18 Zeilen (zwei Einstellungen, drei Budgets, drei Auswahlen): fällt der Anteil von jeder Gruppengröße zur nächsten?"""
    ausnahmen = []
    for sa in C.SA_WAHL:
        for b in C.TRIO_BUDGETS:
            for paar in C.PAARE:
                werte = [k["verschieden"] for k in ev.exp_gruppen(TRIO, b, 5, paar, sa)["kurve"]]
                if any(y > x + 1e-12 for x, y in zip(werte, werte[1:])):
                    ausnahmen.append((sa, b, paar, [k for k in range(4) if werte[k + 1] > werte[k] + 1e-12]))
    assert ausnahmen == [("sa_abg", 10000, "alle", [3]), ("sa_abg", 10000, "hc_sa", [3])]      # beide nur von 15 auf 30 Läufe
    _in_readme("in 16 der 18 Zeilen von jeder Gruppengröße zur nächsten")
    _in_readme("mit der abgestimmten Einstellung bei 10.000 Auswertungen (alle drei und HC gegen SA) von 15 auf 30 Läufe")


def test_kippformel_abstand_und_laeufebedarf():
    strikt = verschieden = dreissig = 0.0
    zeilen = 0
    for sa in C.SA_WAHL:
        for b in C.TRIO_BUDGETS:
            for paar in ("hc_sa", "sa_ga"):
                zeilen += 1
                for k in ev.exp_gruppen(TRIO, b, 5, paar, sa)["kurve"]:
                    if k["r"] == 30:
                        dreissig = max(dreissig, abs(k["strikt"] - k["formel"]))
                    else:
                        strikt = max(strikt, abs(k["strikt"] - k["formel"]))
                        verschieden = max(verschieden, abs(k["verschieden"] - k["formel"]))
    assert zeilen == 12
    assert (ev.pz(strikt, 1), ev.pz(verschieden, 1), ev.pz(dreissig, 1)) == ("4,4", "4,1", "7,5")
    _in_readme("größter Abstand 4,4 Punkte (strikt) und 4,1 Punkte (verschieden), Gruppen zu 3 bis 15 Läufen, 12 Zeilen")
    _in_readme("dort ist der Abstand bis 7,5 Punkte")
    e = ev.exp_gruppen(TRIO, 3000, 5, "hc_sa", "sa_std")
    assert ev.de(e["laeufe_median"], 1) == "33,4" and e["laeufe_ueber_60"] == 25
    _in_readme("33,4; bei 25 von 63 Instanzen über 60")


def test_kurzfassung_mass():
    bestes = " / ".join(ev.pz(ev.exp_mass(TRIO, b, "sa_std")["anders"][("mittel", "bestes")], 1) for b in C.TRIO_BUDGETS)
    median = " / ".join(ev.pz(ev.exp_mass(TRIO, b, "sa_std")["anders"][("mittel", "median")], 1) for b in C.TRIO_BUDGETS)
    assert (bestes, median) == ("46,0 / 81,0 / 93,7", "3,2 / 7,9 / 9,5")
    _in_readme(f"auf {bestes} % der Instanzen verschieden, zwischen Mittel und Median auf {median} %")
    e = ev.exp_mass(TRIO, 10000, "sa_std")
    gleichauf = next(z for z in e["tabelle"] if z["mass"] == "bestes")["alle_gleichauf"]
    assert gleichauf == 44 and e["tau"][("mittel", "bestes")][1] == 44
    # alle drei gleichauf heißt hier: jedes Verfahren hat die beste bekannte Länge mindestens einmal getroffen
    treffer = np.stack([(TRIO["luecke"][v][10000].min(axis=1) <= 1e-9) for v in ("hc", "sa_std", "ga")]).all(axis=0)
    assert int(treffer.sum()) == 44
    _in_readme("auf 44 von 63 Instanzen alle drei Verfahren gleichauf")
    assert [z["besser"] for z in ev.mass_beispiel()] == ["B", "A", "A", "A"]


def test_kurzfassung_einstellung():
    e = ev.exp_einstellung(TRIO)
    assert " / ".join(ev.pz(z["anders"], 1) for z in e["zeilen"]) == "3,2 / 27,0 / 55,6"
    _in_readme("auf 3,2 / 27,0 / 55,6 % der Instanzen eine andere")
    z = e["zeilen"][0]
    assert (ev.de(z["sa_abg"]["mittel"]["SA"], 2), ev.de(z["sa_std"]["mittel"]["SA"], 2)) == ("11,94", "11,90")
    _in_readme("(11,94 % gegen 11,90 %)")
    assert C.SA_TRIO == {"sa_std": (0.3, 3.0), "sa_abg": (0.3, 1.0)}
    _in_readme("Standard (0,3; 3,0), abgestimmt (0,3; 1,0)")


def test_abstimmung_passt_zu_den_konstanten():
    a = D.abstimmung()
    assert tuple(a["trio"]["wahl"]) == C.SA_TRIO["sa_abg"] and len(a["trio"]["gitter"]) == 20 and len(a["trio"]["instanzen"]) == 15
    assert {s: tuple(v) for s, v in a["quartett"]["wahl_sa"].items()} == C.SA_QUARTETT and a["quartett"]["wahl_ma"] == C.MA_GROESSE == 4
    assert len(a["quartett"]["gitter_sa"]) == 20 and len(a["quartett"]["instanzen"]) == 12 and a["quartett"]["laeufe"] == 4
    assert C.SA_QUARTETT["1000n"][1] == min(C.SA_GITTER_C)                      # „am Rand des Rasters (Abkühlung 0,5 Zehnerpotenzen)“
    # die Abstimm-Instanzen gehören nicht zur Messung
    assert all(i[2] == 1 for i in a["trio"]["instanzen"]) and all(i[2] == 2 for i in a["quartett"]["instanzen"])
    assert set(C.QUARTETT_IDX) == {0, 1}


def test_kurzfassung_mehrfachtest():
    assert ev.pz(R.verwerfung_ohne_gleichstand(10), 3) == "4,326"
    assert [ev.pz(R.mindestens_eine(R.verwerfung_ohne_gleichstand(r), 30), 1) for r in (5, 10, 20)] == ["62,0", "73,5", "77,9"]
    pool = {v: ev.exp_null(TRIO, POOL, v, 3000, 30, 10, 35) for v in ("hc", "sa_std", "ga")}
    assert [ev.pz(pool[v]["erwartung_pool"], 1) for v in pool] == ["74,0", "74,7", "74,1"]
    assert [ev.pz(pool[v]["gleichstand_pool"]) for v in pool] == ["97", "89", "33"]
    hc = ev.exp_null(TRIO, POOL, "hc", 10000, 30, 10, 35)
    hc5 = ev.exp_null(TRIO, POOL, "hc", 10000, 30, 5, 35)
    assert (ev.pz(hc["erwartung_pool"], 1), ev.pz(hc5["erwartung_pool"], 1), ev.pz(hc5["erwartung_ohne"], 1)) == ("66,9", "48,1", "62,0")
    assert ev.pz(hc["haeufigster_mittel"]) == "52" and hc["haeufigster_max"] == 1.0
    _in_readme("74,0 % (HC), 74,7 % (SA) und 74,1 % (GA), bei 10.000 Auswertungen für HC nur 66,9 %; bei 5 gegen 5 Läufen 48,1 % statt 62,0 %")
    _in_readme("97 % (HC), 89 % (SA Standard) und 33 % (GA) der Ziehungen Gleichstände")
    _in_readme("im Mittel stellt der häufigste Wert 52 % der 60 Läufe, auf einzelnen Instanzen alle 60")
    assert R.verwerfung_ohne_gleichstand(5, 0.05 / 30) == 0.0
    # Standardfehler eines Anteils um 0,7 aus 100 Wiederholungen: rund 4,5 Punkte
    assert 0.043 < math.sqrt(0.735 * 0.265 / 100) < 0.047
    _in_readme("Standardfehler von rund 4,5 Punkten")


def test_gemessener_mehrfachtest_liegt_im_band_der_erwartung():
    """Je Verfahren und Budget (10 gegen 10, 30 Tests, zwei Zufalls-Seeds): gemessener Anteil höchstens 4 Standardfehler neben der Erwartung mit Gleichständen."""
    for v in C.TRIO_VERFAHREN:
        for b in C.TRIO_BUDGETS:
            for seed in TAB.SEEDS:
                e = ev.exp_null(TRIO, POOL, v, b, 30, 10, seed)
                assert abs(e["mindestens_eine"] - e["erwartung_pool"]) < 4 * e["standardfehler"], (v, b, seed)


def test_kurzfassung_quartett():
    e = ev.exp_quartett(QUARTETT, "5000n", "alle", 12)
    assert len(QUARTETT["familie"]) == 56 and min(QUARTETT["n"]) == 20 and max(QUARTETT["n"]) == 80
    assert len(set(e["ordnungen_stufen"])) == 4
    assert e["ordnungen_stufen"] == ["HC < MA < ILS < SA", "ILS < MA < HC < SA", "SA < ILS < MA < HC", "ILS < MA < SA < HC"]
    assert e["sieger_familien"] == {"gleich": "ils", "cluster": "ils", "gitter": "sa", "netz": "ils"}
    assert ev.exp_quartett(QUARTETT, "1000n", "alle", 12)["sieger_familien"]["gitter"] == "sa"
    r = e["raster"]
    assert [ev.de(r[(s, "alle")]["faktor"], 2) for s in e["stufen"]] == ["0,98", "1,00", "0,71", "1,01"]
    assert [ev.pz(r[(s, "alle")]["fertig_mittel"]) for s in e["stufen"]] == ["8", "51", "100", "100"]
    for s, grenze in (("30n", 0.5), ("100n", 0.05)):
        werte = [round(r[(s, "alle")]["mittel"][v], 2) for v in ("hc", "ils", "ma")]
        assert max(werte) - min(werte) <= grenze + 1e-9
    # ab 1.000 · n ist HC in drei von vier Familien Letzter, auf dem Straßennetz nicht
    for s in ("1000n", "5000n"):
        letzter = {f: r[(s, f)]["ordnung"].split(" < ")[-1] for f in C.QUARTETT_FAMILIEN}
        assert letzter == {"gleich": "HC", "cluster": "HC", "gitter": "HC", "netz": "SA"}
    # die Reihenfolge von HC, ILS und MA bei 30 · n und 100 · n wechselt zwischen den Hälften der Läufe
    for s in ("30n", "100n"):
        halb = [ev.exp_quartett(D.teil(QUARTETT, a, b), "1000n", "alle", 6)["raster"][(s, "alle")]["ordnung"] for a, b in ((0, 6), (6, 12))]
        assert halb[0] != halb[1]
    _in_readme("über vier Budgets vier verschiedene Rangfolgen")
    _in_readme("nur 8 % der Läufe von HC, ILS und MA den ersten Abstieg beendet")
    _in_readme("0,98 / 1,00 / 0,71 / 1,01 bei 30 · n / 100 · n / 1.000 · n / 5.000 · n")


def test_kosten_des_ersten_abstiegs():
    je_n = {}
    for n in C.QUARTETT_N:
        maske = QUARTETT["n"] == n
        werte = np.concatenate([QUARTETT["erster_abstieg"][v][maske].ravel() for v in ("hc", "ils", "ma")])
        assert len(werte) == 288 and not np.isnan(werte).any()
        je_n[n] = float(np.median(werte)) / n
    assert (ev.de(je_n[20], 0), ev.de(je_n[80], 0)) == ("28", "183")
    assert all(je_n[a] < je_n[b] for a, b in zip(C.QUARTETT_N, C.QUARTETT_N[1:]))
    _in_readme("im Median 28 · n (20 Orte) bis 183 · n (80 Orte)")


def test_rechenbeispiel_zur_zaehlweise_im_text():
    assert (ev.zuege_voll(30), ev.zuege_warteschlange(30), ev.zuege_voll(100), ev.zuege_warteschlange(100)) == (405, 54, 4850, 194)
    m = ev.gesetztes_modell()
    assert m["voll"]["schritte"] == (412, 3) and m["warteschlange"]["schritte"] == (10309, 53)
    assert [float(x) for x in m["voll"]["luecke"] + m["warteschlange"]["luecke"]] == [1.0, 25.6, 1.0, 0.5]
    _in_readme("erlaubt „voll“ 412 und 3 Schritte (Lücken 1 und 25,6: 2-opt besser), die Warteschlange 10.309 und 53 Schritte (Lücken 1 und 0,5: 3-opt besser)")


def test_texte_stehen_wortgleich_in_app_und_readme():
    for block in (T.VERFAHREN_TABELLE, T.MASS_TABELLE, T.CHECKLISTE):
        _in_readme(block.strip())
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    for name in ("T.VORAUSSETZUNG", "T.VERFAHREN_TABELLE", "T.MASS_TABELLE", "T.CHECKLISTE", "T.ANNAHMEN"):
        assert name in app


def test_zitate_stehen_in_der_quelle():
    """Die zitierten Zahlen der Demo „Die Nachbarschaft ändert die Landschaft“ wörtlich in deren README (nur, wenn der Ordner daneben liegt)."""
    quelle = ROOT.parent / "nachbarschaft-landschaft-demo" / "README.md"
    if not quelle.exists():
        pytest.skip("die zitierte Demo liegt nicht neben diesem Ordner")
    text = quelle.read_text(encoding="utf-8")
    assert "### Zitierbare Zahlen mit Voraussetzung, Fundstelle und Test" in text
    for zitat in T.ZITATE_STUECK5.values():
        assert zitat in text, zitat
        _in_readme(zitat)


def test_testzahl_der_readme():
    """Die Gesamtzahl der Tests in der README stimmt mit der Sammlung überein."""
    aus = subprocess.run([sys.executable, "-m", "pytest", "--collect-only", "-q", "-p", "no:cacheprovider", str(ROOT / "tests")], capture_output=True, text=True, cwd=ROOT, timeout=300)
    zahl = int(aus.stdout.strip().splitlines()[-1].split()[0])
    _in_readme(f"{zahl} Tests (`python -m pytest tests -q`)")
