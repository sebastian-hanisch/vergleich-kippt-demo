"""Lädt die eingefrorenen Messreihen (data/*.json) als numpy-Felder. Erzeugt werden sie von `tools/vgk_make_daten.py`."""

import json
from functools import lru_cache
from pathlib import Path

import numpy as np

import vgk_compare as V

DATA = Path(__file__).resolve().parent / "data"


def _lies(name: str) -> dict:
    return json.loads((DATA / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def trio() -> dict:
    """Messreihe des Trios. `laengen[v][b]`, `luecke[v][b]`, `flaeche[v][b]`: Felder (Instanzen, Läufe); Lücke und Fläche in Prozent."""
    roh = _lies("vgk_trio.json")
    inst = roh["instanzen"]
    ref = np.array([z["referenz"] for z in inst])
    aus = {"meta": {k: roh[k] for k in ("quelle", "stand", "voraussetzung", "sa_einstellungen")}, "budgets": tuple(roh["budgets"]),
           "verfahren": tuple(inst[0]["laengen"]), "familie": [z["familie"] for z in inst], "n": [z["n"] for z in inst], "referenz": ref,
           "referenz_von": [z["referenz_von"] for z in inst], "laengen": {}, "luecke": {}, "flaeche": {}}
    for v in aus["verfahren"]:
        aus["laengen"][v], aus["luecke"][v], aus["flaeche"][v] = {}, {}, {}
        for b in aus["budgets"]:
            laengen = np.array([z["laengen"][v][str(b)] for z in inst])
            aus["laengen"][v][b] = laengen
            aus["luecke"][v][b] = V.luecke(laengen, ref)
            aus["flaeche"][v][b] = V.luecke(np.array([z["flaeche"][v][str(b)] for z in inst]), ref)
    return aus


@lru_cache(maxsize=1)
def quartett() -> dict:
    """Messreihe des Quartetts. `luecke[v][stufe]`: (Instanzen, Läufe); `erster_abstieg[v]`: (Instanzen, Läufe), NaN = nicht beendet."""
    roh = _lies("vgk_quartett.json")
    inst = roh["instanzen"]
    ref = np.array([z["referenz"] for z in inst])
    aus = {"meta": {k: roh[k] for k in ("quelle", "stand", "voraussetzung", "sa_einstellungen", "ma_groesse")}, "stufen": dict(roh["stufen"]),
           "verfahren": tuple(inst[0]["laengen"]), "familie": [z["familie"] for z in inst], "n": np.array([z["n"] for z in inst]), "referenz": ref,
           "luecke": {}, "erster_abstieg": {}}
    for v in aus["verfahren"]:
        aus["luecke"][v] = {s: V.luecke(np.array([z["laengen"][v][s] for z in inst]), ref) for s in aus["stufen"]}
        if v in inst[0]["erster_abstieg"]:
            aus["erster_abstieg"][v] = np.array([[np.nan if x is None else x for x in z["erster_abstieg"][v]] for z in inst], dtype=float)
    return aus


@lru_cache(maxsize=1)
def nulltest() -> dict:
    return _lies("vgk_nulltest.json")


@lru_cache(maxsize=1)
def abstimmung() -> dict:
    return _lies("vgk_abstimmung.json")


def teil(daten: dict, start: int, stop: int) -> dict:
    """Dieselbe Messreihe (Trio oder Quartett) nur mit den Läufen start..stop-1 je Instanz: für Gegenproben mit getrennten Zufallsströmen."""
    aus = dict(daten)
    for feld in ("laengen", "luecke", "flaeche", "erster_abstieg"):
        if feld not in daten:
            continue
        aus[feld] = {}
        for v, inhalt in daten[feld].items():
            aus[feld][v] = inhalt[:, start:stop] if isinstance(inhalt, np.ndarray) else {k: x[:, start:stop] for k, x in inhalt.items()}
    return aus
