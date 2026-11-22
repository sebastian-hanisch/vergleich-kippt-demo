"""Kopie-Test: `vgk_basis.py` ist die unveränderte gemeinsame Basis der Linie, `vgk_rng.py` die unveränderte SplitMix64-Vorlage.

Geprüft wird gegen `tests/data/basis_eingefroren.json` (Kopie von `gemeinsam/eingefroren.json` der Planung): dieselben Koordinaten,
Längen und NK-Werte wie die Referenzfassung. Längen als repr(float): die Basis rechnet nur mit `math.sqrt` ganzer Zahlen."""

import json
from pathlib import Path

import vgk_basis as b
from vgk_rng import SplitMix64

DATEN = json.loads((Path(__file__).resolve().parent / "data" / "basis_eingefroren.json").read_text(encoding="utf-8"))


def test_splitmix64_erste_werte():
    rng = SplitMix64(0)
    assert rng.next_u64() == 0xE220A8397B1DCDAF       # bekannter Prüfwert von SplitMix64 für den Zustand 0
    assert SplitMix64(1234567).next_u64() == 6457827717110365317


def test_rundtour_instanzen_wie_eingefroren():
    assert len(DATEN["rundtour"]) == 12
    for z in DATEN["rundtour"]:
        assert b.instanz_seed(z["familie"], z["n"], z["idx"]) == z["seed"]
        punkte = b.rundtour_punkte(SplitMix64(z["seed"]), z["familie"], z["n"])
        assert len(set(punkte)) == z["n"]
        assert [list(p) for p in punkte[:4]] == z["erste_punkte"]
        assert sum(p[0] for p in punkte) == z["summe_x"] and sum(p[1] for p in punkte) == z["summe_y"]
        assert repr(b.tourlaenge(b.abstaende(punkte), list(range(z["n"])))) == z["laenge_identitaet"]


def test_nk_werte_wie_eingefroren():
    for z in DATEN["nk"]:
        n = z["n"]
        tab = b.nk_tabellen(SplitMix64(z["seed"]), n, z["k"], z["stufen"])
        zustaende = [[0] * n, [1] * n, [(i * 7 + 3) % 2 for i in range(n)], [1 if i % 3 == 0 else 0 for i in range(n)]]
        assert [repr(b.nk_wert(tab, x)) for x in zustaende] == z["werte"]


def test_lauf_seeds_wie_eingefroren():
    assert b.lauf_seed(0, 0, 0) == DATEN["seeds"]["lauf_seed_0_0_0"] and b.lauf_seed(5, 2, 7) == DATEN["seeds"]["lauf_seed_5_2_7"]


def test_familien_der_basis():
    assert b.FAMILIEN == ("gleich", "cluster", "gitter", "netz")
    assert all("strasse" not in name for name in b.FAMILIEN)
