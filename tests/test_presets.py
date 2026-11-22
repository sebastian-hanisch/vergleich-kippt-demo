"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, Namen und Hilfetexte passen zu den Werten."""

import vgk_constants as C
import vgk_presets as P


def test_jedes_preset_hat_hilfe_und_alle_schluessel():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS) == set(C.DEFAULTS), name
        assert C.PRESET_HELP[name]


def test_presetwerte_liegen_in_den_reglergrenzen():
    for name, preset in C.PRESETS.items():
        for key, state_key in P.PRESET_KEYS.items():
            spec = P.SETTING_SPECS[state_key]
            if spec.options is not None:
                assert preset[key] in spec.options, (name, key)
            else:
                assert spec.lo <= preset[key] <= spec.hi, (name, key)


def test_standard_preset_ist_die_voreinstellung():
    erstes = next(iter(C.PRESETS))
    assert C.PRESETS[erstes] == C.DEFAULTS
    assert {P.PRESET_KEYS[k]: v for k, v in C.DEFAULTS.items()} == {k: s.default for k, s in P.SETTING_SPECS.items()}


def test_presets_sind_paarweise_verschieden():
    werte = [tuple(sorted(p.items())) for p in C.PRESETS.values()]
    assert len(set(werte)) == len(werte) == 6


def test_setting_specs_decken_jeden_preset_schluessel_und_eindeutige_url_parameter():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    params = [s.url_param for s in P.SETTING_SPECS.values()]
    assert len(set(params)) == len(params)


def test_namen_und_hilfetexte_passen_zu_den_werten():
    p = C.PRESETS
    assert p["Gruppen zu 5 Läufen"]["gruppe"] == 5 and p["Gruppen zu 5 Läufen"]["paar"] == "hc_sa" and "HC gegen SA" in C.PRESET_HELP["Gruppen zu 5 Läufen"]
    assert p["Maß wechseln"]["mass"] == "bestes" and p["Maß wechseln"]["budget"] == 10000 and "10.000" in C.PRESET_HELP["Maß wechseln"]
    assert p["30 Tests gegen sich selbst"]["m"] == 30 and p["30 Tests gegen sich selbst"]["null_gruppe"] == 10 and p["30 Tests gegen sich selbst"]["null_verfahren"] == "ga"
    viele = p["Viele Gleichstände (HC, großes Budget)"]
    assert (viele["null_verfahren"], viele["budget"], viele["null_gruppe"]) == ("hc", 10000, 5) and "5 gegen 5" in C.PRESET_HELP["Viele Gleichstände (HC, großes Budget)"]
    q = p["Quartett: Budget und Familie"]
    assert (q["q_budget"], q["q_familie"]) == ("5000n", "gitter") and "5.000 · n" in C.PRESET_HELP["Quartett: Budget und Familie"]
    assert "3.000 Auswertungen" in C.PRESET_HELP["Das Trio (HC, SA, GA)"] and C.DEFAULTS["budget"] == 3000 and C.DEFAULTS["gruppe"] == 15


def test_regler_grenzen_passen_zur_messreihe():
    assert C.M_MAX == 63 and max(C.NULL_GRUPPEN) * 2 <= C.TRIO_LAEUFE and max(C.GRUPPEN_R) * 2 <= C.TRIO_LAEUFE and max(C.Q_LAEUFE) == C.QUARTETT_LAEUFE
