"""App-Szenarien: je Preset die erwarteten Verdikt-Zeilen (kein Preset ohne Wirkung meldet eine Wirkung), Permalink, Regler, Expander per Titel."""

from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

import vgk_constants as C

APP = str(Path(__file__).resolve().parent.parent / "app.py")


def _app(**query) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=300)
    for k, v in query.items():
        at.query_params[k] = str(v)
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texte(at) -> list:
    return [x.value for art in ("success", "info", "warning", "error") for x in getattr(at, art)]


def _mit(at, anfang: str) -> str:
    treffer = [t for t in _texte(at) if anfang in t]
    assert treffer, anfang
    return treffer[0]


def test_standard_zeigt_alle_verdikte_und_keinen_fehler():
    at = _app()
    assert not at.error
    texte = _texte(at)
    assert len(texte) == 11                       # Trio, Voraussetzung, drei Kernfragen, fünf Experimente, No-Free-Lunch
    assert "Zählweise **voll**" in _mit(at, "Alle Zahlen dieser Seite")
    assert "in allen 12 Zellen" in _mit(at, "Im Trio")
    assert len(at.get("plotly_chart")) == 9


EXPANDER = ["So funktioniert ein ehrlicher Vergleich", "Eine Instanz live nachrechnen (10 Läufe je Verfahren)", "Was in der Aussage stehen muss (Checkliste, mit zitierten Zahlen zur Zählweise)",
            "No-Free-Lunch im Kleinen (alle 81 Funktionen aufgezählt)", "📐 Mathematische Formulierung"]


def test_expander_per_titel_und_formelblock_zuletzt():
    at = _app()
    titel = [e.label for e in at.expander]
    for name in EXPANDER:
        assert name in titel
    assert titel[-1] == "📐 Mathematische Formulierung"


ERWARTET = {
    "Das Trio (HC, SA, GA)": ["Gruppen zu **15 Läufen**, 3.000 Auswertungen", "das Trio HC, SA, GA", "**27 %**", "Simulated Annealing (Standard), 3.000 Auswertungen", "Budget 1.000 · n"],
    "Gruppen zu 5 Läufen": ["Gruppen zu **5 Läufen**, 3.000 Auswertungen", "das Paar HC / SA", "**35 %**", "die Formel 2Φ(d)(1 − Φ(d)) sagt 33 % voraus"],
    "Maß wechseln": ["10.000 Auswertungen: zwischen **Mittel** und **bester Lauf (kleinste Lücke)**", "**94 %**", "auf 44 Instanzen nicht definiert"],
    "30 Tests gegen sich selbst": ["**30 Tests, 10 gegen 10 Läufe, dasselbe Verfahren (genetischer Algorithmus, 3.000 Auswertungen):**", "dieser Läufe: 74,1 %", "73,5 % (4,33 % je Einzeltest"],
    "Viele Gleichstände (HC, großes Budget)": ["**30 Tests, 5 gegen 5 Läufe, dasselbe Verfahren (Hill Climbing, 10.000 Auswertungen):**", "dieser Läufe: 48,1 %", "beschreibt diese Läufe nicht",
                                               "nie verwerfen"],
    "Quartett: Budget und Familie": ["Budget 5.000 · n Auswertungen, Gitter mit Rauschen (14 Instanzen", "**SA < ILS < MA < HC**", "Gruppenfaktor 0,69"],
}


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_jedes_preset_zeigt_seine_verdikt_zeilen(name):
    at = _app()
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception and not at.error
    alles = "\n".join(_texte(at))
    for teil in ERWARTET[name]:
        assert teil in alles, (name, teil)


def test_preset_ohne_gleichstaende_meldet_keine_warnung_im_mehrfachtest():
    """Der genetische Algorithmus bei 3.000 Auswertungen: die Linie ohne Gleichstände passt, das Verdikt warnt nicht."""
    at = _app()
    at.sidebar.button(key="preset_30 Tests gegen sich selbst").click().run()
    assert all("beschreibt diese Läufe nicht" not in t for t in _texte(at))
    assert [x.value for x in at.warning if "dasselbe Verfahren" in x.value] == []


def test_abgebrochener_abstieg_nennt_keine_rangfolge():
    at = _app(qb="30n")
    text = _mit(at, "Quartett, Budget 30 · n")
    assert "abgebrochene Abstiege" in text and "Rangfolge **" not in text


def test_permalink_setzt_die_regler_und_begrenzt():
    at = _app(b=10000, sa="sa_abg", r=5, paar="sa_ga", mass="flaeche", nv="hc", m=999, nr=20, seed=7, qb="100n", qf="netz", ql=6)
    s = at.session_state
    assert (s["budget_select"], s["sa_select"], s["gruppe_select"], s["paar_select"], s["mass_select"]) == (10000, "sa_abg", 5, "sa_ga", "flaeche")
    assert (s["null_verfahren_select"], s["m_slider"], s["null_gruppe_select"], s["seed_input"]) == ("hc", C.M_MAX, 20, 7)
    assert (s["q_budget_select"], s["q_familie_select"], s["q_laeufe_select"]) == ("100n", "netz", 6)
    assert "Simulated Annealing in der Einstellung „abgestimmt“" in _mit(at, "Im Trio")
    assert "Straßennetz (14 Instanzen, 6 Läufe" in _mit(at, "Quartett, Budget 100 · n")
    assert "**63 Tests, 20 gegen 20 Läufe" in "\n".join(_texte(at))


def test_permalink_uebergeht_unbekannte_werte():
    at = _app(b=1234, paar="unsinn", m="abc", qb="7n")
    s = at.session_state
    assert (s["budget_select"], s["paar_select"], s["m_slider"], s["q_budget_select"]) == (3000, "alle", 30, "1000n")


def test_adresszeile_spiegelt_die_einstellungen():
    at = _app()
    at.sidebar.button(key="preset_Maß wechseln").click().run()
    assert at.query_params["b"] in ("10000", ["10000"]) and at.query_params["mass"] in ("bestes", ["bestes"])


def test_neue_ziehungen_aendern_nur_den_mehrfachtest():
    at = _app()
    vorher = _texte(at)
    at.sidebar.number_input(key="seed_input").set_value(36).run()
    nachher = _texte(at)
    geaendert = [k for k, (a, b) in enumerate(zip(vorher, nachher)) if a != b]
    assert geaendert and all("dasselbe Verfahren" in nachher[k] for k in geaendert)


def test_sa_einstellung_wirkt_auf_trio_und_mehrfachtest():
    at = _app()
    at.sidebar.selectbox(key="sa_select").set_value("sa_abg").run()
    assert "2 verschiedene Ordnungen" in _mit(at, "Im Trio")
    assert "Simulated Annealing (abgestimmt)" in "\n".join(_texte(at))


def test_no_free_lunch_regler():
    at = _app()
    at.selectbox(key="nfl_klasse").set_value("glatt").run()
    assert "A das Minimum 0 in 17, B in 20 von 41" in "\n".join(_texte(at))
    at.slider(key="nfl_m").set_value(3).run()
    assert "A das Minimum 0 in 21, B in 23 von 41" in "\n".join(_texte(at))
    at.slider(key="nfl_m").set_value(4).run()
    assert "dieselbe Verteilung" in "\n".join(_texte(at))


def test_live_nachrechnung_stimmt_mit_den_eingefrorenen_laeufen():
    at = _app()
    at.button(key="live_button").click().run(timeout=300)
    assert not at.exception
    text = _mit(at, "neu gerechneten Läufen")
    zahl = int(text.split(" von ")[0])
    assert zahl >= 27 and "von 30" in text                # Band: höchstens drei Läufe dürfen an der letzten Binärstelle der Plattform abweichen


def test_jede_reglerstellung_der_auswahlen_laeuft():
    at = _app()
    for key, werte in (("budget_select", C.TRIO_BUDGETS), ("gruppe_select", C.GRUPPEN_R), ("null_gruppe_select", C.NULL_GRUPPEN), ("q_budget_select", tuple(C.QUARTETT_STUFEN)),
                       ("q_laeufe_select", C.Q_LAEUFE)):
        for w in werte:
            at.sidebar.select_slider(key=key).set_value(w).run()
            assert not at.exception, (key, w)
    for key, werte in (("paar_select", C.PAARE), ("mass_select", C.MASSE_WAHL), ("null_verfahren_select", C.NULL_VERFAHREN), ("q_familie_select", C.Q_FAMILIEN)):
        for w in werte:
            at.sidebar.selectbox(key=key).set_value(w).run()
            assert not at.exception, (key, w)
    at.sidebar.slider(key="m_slider").set_value(1).run()
    assert not at.exception and "**1 Test, " in "\n".join(_texte(at))
