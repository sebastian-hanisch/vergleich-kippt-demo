"""Rechnet die eingefrorenen Messreihen der Demo vor (in Teilen, jeder Teil wenige Minuten) und prüft sie.

    python tools/vgk_make_daten.py abstimmung-trio            -> tools/teile/abstimmung_trio.json
    python tools/vgk_make_daten.py abstimmung-quartett        -> tools/teile/abstimmung_quartett.json
    python tools/vgk_make_daten.py trio <familie> <verfahren> -> tools/teile/trio_<familie>_<verfahren>.json
    python tools/vgk_make_daten.py quartett <familie>         -> tools/teile/quartett_<familie>.json
    python tools/vgk_make_daten.py referenz <trio|quartett> <familie>
    python tools/vgk_make_daten.py zusammen                   -> data/vgk_abstimmung.json, data/vgk_trio.json, data/vgk_quartett.json
    python tools/vgk_make_daten.py erwartung                  -> data/vgk_nulltest.json (braucht data/vgk_trio.json)
    python tools/vgk_make_daten.py --check                    -> rechnet Stichproben neu und vergleicht (0 Abweichungen erwartet)

Die Einstellungen von Simulated Annealing und die Größe der Population des memetischen Algorithmus stehen in `vgk_constants.py`;
`zusammen` bricht ab, wenn sie nicht zum Ergebnis der Abstimmung passen."""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import vgk_constants as C  # noqa: E402
import vgk_messung as MS  # noqa: E402

TEILE = ROOT / "tools" / "teile"
DATA = ROOT / "data"
STAND = "2026-11-21"


def _schreibe(pfad: Path, inhalt) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(json.dumps(inhalt, ensure_ascii=False, separators=(",", ":")), encoding="utf-8", newline="\n")
    print(f"geschrieben: {pfad.relative_to(ROOT)} ({pfad.stat().st_size / 1024:.0f} KB)")


def _lies(pfad: Path):
    return json.loads(pfad.read_text(encoding="utf-8"))


def _r3(x: float) -> float:
    return round(x, 3)


# ------------------------------------------------------------------------------------------------------------------------------
def abstimmung_trio():
    gitter = [(t, c) for t in C.SA_GITTER_T0F for c in C.SA_GITTER_C]
    instanzen = [(f, n, 1) for n in C.ABSTIMM_N_TRIO for f in C.TRIO_FAMILIEN]
    roh = {}
    for f, n, idx in instanzen:
        ref = min(MS.referenz_lauf(f, n, idx, k) for k in range(C.REFERENZ_LAEUFE))
        zellen = {}
        for g, cfg in enumerate(gitter):
            zellen[g] = [[MS.trio_lauf(f, n, idx, "sa_std", lauf, {"sa_std": cfg})[b][0] for lauf in range(C.ABSTIMM_LAEUFE)] for b in C.TRIO_BUDGETS]
        ref = min(ref, min(min(min(z) for z in zeilen) for zeilen in zellen.values()))
        roh[(f, n)] = (ref, zellen)
    tabelle = []
    for g, cfg in enumerate(gitter):
        je_budget = []
        for k in range(len(C.TRIO_BUDGETS)):
            luecken = [100.0 * (x - ref) / ref for ref, zellen in roh.values() for x in zellen[g][k]]
            je_budget.append(sum(luecken) / len(luecken))
        tabelle.append({"t0f": cfg[0], "c": cfg[1], "luecke_je_budget": [round(x, 4) for x in je_budget], "mittel": round(sum(je_budget) / 3, 4)})
    wahl = min(tabelle, key=lambda z: (z["mittel"], z["t0f"], z["c"]))
    _schreibe(TEILE / "abstimmung_trio.json", {"instanzen": [list(i) for i in instanzen], "laeufe": C.ABSTIMM_LAEUFE, "budgets": list(C.TRIO_BUDGETS),
                                               "gitter": tabelle, "wahl": [wahl["t0f"], wahl["c"]]})
    for z in tabelle:
        print(z)
    print("Wahl:", wahl)


def abstimmung_quartett(laeufe=4):
    gitter = [(t, c) for t in C.SA_GITTER_T0F for c in C.SA_GITTER_C]
    instanzen = [(f, n, 2) for n in C.ABSTIMM_N_QUARTETT for f in C.QUARTETT_FAMILIEN]
    stufen = list(C.QUARTETT_STUFEN)
    roh = {}
    for f, n, idx in instanzen:
        ref = min(MS.referenz_lauf(f, n, idx, k) for k in range(C.REFERENZ_LAEUFE))
        sa = {g: [MS.quartett_lauf(f, n, idx, "sa", lauf, {s: cfg for s in stufen})["laengen"] for lauf in range(laeufe)] for g, cfg in enumerate(gitter)}
        ma = {p: [MS.quartett_lauf(f, n, idx, "ma", lauf, ma_groesse=p)["laengen"] for lauf in range(laeufe)] for p in C.MA_GITTER}
        ref = min([ref] + [x for zs in list(sa.values()) + list(ma.values()) for z in zs for x in z.values()])
        roh[(f, n)] = (ref, sa, ma)
        print(f, n, "fertig", flush=True)

    def mittel(werte_von):
        return {s: round(sum(100.0 * (z[s] - ref) / ref for ref, sa, ma in roh.values() for z in werte_von(sa, ma)) / (len(roh) * laeufe), 4) for s in stufen}

    tab_sa = [{"t0f": cfg[0], "c": cfg[1], "luecke": mittel(lambda sa, ma, g=g: sa[g])} for g, cfg in enumerate(gitter)]
    tab_ma = [{"groesse": p, "luecke": mittel(lambda sa, ma, p=p: ma[p])} for p in C.MA_GITTER]
    for z in tab_ma:
        z["mittel"] = round(sum(z["luecke"].values()) / len(stufen), 4)
    wahl_sa = {}
    for s in stufen:
        z = min(tab_sa, key=lambda z: (z["luecke"][s], z["t0f"], z["c"]))
        wahl_sa[s] = [z["t0f"], z["c"]]
    wahl_ma = min(tab_ma, key=lambda z: (z["mittel"], z["groesse"]))["groesse"]
    _schreibe(TEILE / "abstimmung_quartett.json", {"instanzen": [list(i) for i in instanzen], "laeufe": laeufe, "gitter_sa": tab_sa, "gitter_ma": tab_ma,
                                                   "wahl_sa": wahl_sa, "wahl_ma": wahl_ma})
    for z in tab_sa + tab_ma:
        print(z)
    print("Wahl SA:", wahl_sa, "Wahl MA:", wahl_ma)


def teil_trio(familie: str, verfahren: str):
    aus = []
    for n in C.TRIO_N:
        laeufe = [MS.trio_lauf(familie, n, 0, verfahren, lauf) for lauf in range(C.TRIO_LAEUFE)]
        aus.append({"n": n, "laengen": {str(b): [_r3(z[b][0]) for z in laeufe] for b in C.TRIO_BUDGETS},
                    "flaeche": {str(b): [round(z[b][1], 2) for z in laeufe] for b in C.TRIO_BUDGETS}})
    _schreibe(TEILE / f"trio_{familie}_{verfahren}.json", aus)


def teil_quartett(familie: str):
    aus = []
    for n in C.QUARTETT_N:
        for idx in C.QUARTETT_IDX:
            zeile = {"n": n, "idx": idx, "laengen": {}, "erster_abstieg": {}}
            for v in C.QUARTETT_VERFAHREN:
                laeufe = [MS.quartett_lauf(familie, n, idx, v, lauf) for lauf in range(C.QUARTETT_LAEUFE)]
                zeile["laengen"][v] = {s: [_r3(z["laengen"][s]) for z in laeufe] for s in C.QUARTETT_STUFEN}
                if v != "sa":
                    zeile["erster_abstieg"][v] = [z["erster_abstieg"] for z in laeufe]
            aus.append(zeile)
        print(familie, n, "fertig", flush=True)
    _schreibe(TEILE / f"quartett_{familie}.json", aus)


def teil_referenz(reihe: str, familie: str):
    paare = [(n, 0) for n in C.TRIO_N] if reihe == "trio" else [(n, idx) for n in C.QUARTETT_N for idx in C.QUARTETT_IDX]
    aus = [{"n": n, "idx": idx, "laengen": [_r3(MS.referenz_lauf(familie, n, idx, k)) for k in range(C.REFERENZ_LAEUFE)]} for n, idx in paare]
    _schreibe(TEILE / f"referenz_{reihe}_{familie}.json", aus)


# ------------------------------------------------------------------------------------------------------------------------------
def zusammen():
    at, aq = _lies(TEILE / "abstimmung_trio.json"), _lies(TEILE / "abstimmung_quartett.json")
    if tuple(at["wahl"]) != C.SA_TRIO["sa_abg"]:
        sys.exit(f"SA_TRIO['sa_abg'] = {C.SA_TRIO['sa_abg']} passt nicht zur Abstimmung {at['wahl']}")
    if {s: tuple(v) for s, v in aq["wahl_sa"].items()} != C.SA_QUARTETT or aq["wahl_ma"] != C.MA_GROESSE:
        sys.exit(f"SA_QUARTETT/MA_GROESSE passen nicht zur Abstimmung: {aq['wahl_sa']}, {aq['wahl_ma']}")
    _schreibe(DATA / "vgk_abstimmung.json", {
        "quelle": "tools/vgk_make_daten.py abstimmung-trio und abstimmung-quartett", "stand": STAND,
        "voraussetzung": "Abstimm-Instanzen sind nicht Teil der Messung (laufende Nummer 1 bzw. 2 der gemeinsamen Basis); Zählweise voll; Lücke gegen die beste bekannte Länge der Abstimm-Läufe und zweier Referenzläufe",
        "trio": at, "quartett": aq})

    instanzen = []
    for n in C.TRIO_N:
        for f in C.TRIO_FAMILIEN:
            zeile = {"familie": f, "n": n, "idx": 0, "laengen": {}, "flaeche": {}}
            for v in C.TRIO_VERFAHREN:
                teil = next(z for z in _lies(TEILE / f"trio_{f}_{v}.json") if z["n"] == n)
                zeile["laengen"][v], zeile["flaeche"][v] = teil["laengen"], teil["flaeche"]
            ref = next(z for z in _lies(TEILE / f"referenz_trio_{f}.json") if z["n"] == n)["laengen"]
            alle = [x for v in zeile["laengen"].values() for b in v.values() for x in b]
            zeile["referenz"] = min(alle + ref)
            zeile["referenz_von"] = "Referenzlauf" if min(ref) <= min(alle) else "Messlauf"
            instanzen.append(zeile)
    _schreibe(DATA / "vgk_trio.json", {
        "quelle": "tools/vgk_make_daten.py trio/referenz/zusammen", "stand": STAND,
        "voraussetzung": ("Instanzen der gemeinsamen Basis (Familie, Ortszahl 20 bis 40, laufende Nummer 0), erfunden; Zählweise voll; Hill Climbing mit erster Verbesserung "
                          "in zufälliger zyklischer Zugreihenfolge je Abstieg; 60 Läufe je Zelle; Längen auf 0,001 gerundet"),
        "felder": {"laengen": "Länge der besten Tour je Lauf nach dem Budget (Auswertungen)", "flaeche": "Mittel der bis dahin besten Länge über 20 Prüfpunkte",
                   "referenz": "beste bekannte Länge (kleinste aller Läufe dieser Datei und zweier Referenzläufe mit Iterated Local Search); nicht als optimal bewiesen"},
        "sa_einstellungen": {k: list(v) for k, v in C.SA_TRIO.items()}, "budgets": list(C.TRIO_BUDGETS), "laeufe": C.TRIO_LAEUFE, "instanzen": instanzen})

    instanzen = []
    for n in C.QUARTETT_N:
        for idx in C.QUARTETT_IDX:
            for f in C.QUARTETT_FAMILIEN:
                teil = next(z for z in _lies(TEILE / f"quartett_{f}.json") if z["n"] == n and z["idx"] == idx)
                ref = next(z for z in _lies(TEILE / f"referenz_quartett_{f}.json") if z["n"] == n and z["idx"] == idx)["laengen"]
                alle = [x for v in teil["laengen"].values() for s in v.values() for x in s]
                instanzen.append({"familie": f, "n": n, "idx": idx, "laengen": teil["laengen"], "erster_abstieg": teil["erster_abstieg"],
                                  "referenz": min(alle + ref), "referenz_von": "Referenzlauf" if min(ref) <= min(alle) else "Messlauf"})
    _schreibe(DATA / "vgk_quartett.json", {
        "quelle": "tools/vgk_make_daten.py quartett/referenz/zusammen", "stand": STAND,
        "voraussetzung": ("Instanzen der gemeinsamen Basis (vier Familien, Ortszahlen 20 bis 80, laufende Nummern 0 und 1), erfunden; Zählweise voll; erste Verbesserung in "
                          "zufälliger zyklischer Zugreihenfolge je Abstieg; 12 Läufe je Zelle; Budget = Faktor · Ortszahl; Längen auf 0,001 gerundet"),
        "felder": {"laengen": "Länge der besten Tour je Lauf und Budgetstufe", "erster_abstieg": "Auswertungen bis zum Ende des ersten Abstiegs (null: im größten Budget nicht beendet)",
                   "referenz": "beste bekannte Länge (kleinste aller Läufe dieser Datei und zweier Referenzläufe); nicht als optimal bewiesen"},
        "sa_einstellungen": {k: list(v) for k, v in C.SA_QUARTETT.items()}, "ma_groesse": C.MA_GROESSE, "stufen": C.QUARTETT_STUFEN, "laeufe": C.QUARTETT_LAEUFE,
        "instanzen": instanzen})


def erwartung():
    import vgk_daten as D
    import vgk_rangtest as R
    _schreibe(DATA / "vgk_nulltest.json", R.pool_erwartung_datei(D.trio(), stand=STAND))


def check() -> int:
    """Stichproben neu rechnen: je Reihe einige Zellen, exakt verglichen (auf dieser Plattform und Python-Version)."""
    fehler = geprueft = 0
    trio = {(z["familie"], z["n"]): z for z in _lies(DATA / "vgk_trio.json")["instanzen"]}
    for f, n, v, laeufe in (("gleich", 20, "hc", range(60)), ("cluster", 31, "sa_std", range(20)), ("gitter", 40, "sa_abg", range(20)), ("gleich", 27, "ga", range(6))):
        for lauf in laeufe:
            neu = MS.trio_lauf(f, n, 0, v, lauf)
            for b in C.TRIO_BUDGETS:
                geprueft += 2
                fehler += _r3(neu[b][0]) != trio[(f, n)]["laengen"][v][str(b)][lauf]
                fehler += round(neu[b][1], 2) != trio[(f, n)]["flaeche"][v][str(b)][lauf]
    quartett = {(z["familie"], z["n"], z["idx"]): z for z in _lies(DATA / "vgk_quartett.json")["instanzen"]}
    for f, n, idx, v in (("netz", 20, 0, "hc"), ("gleich", 30, 1, "sa"), ("gitter", 40, 0, "ils"), ("cluster", 30, 1, "ma")):
        for lauf in range(4):
            neu = MS.quartett_lauf(f, n, idx, v, lauf)
            for s in C.QUARTETT_STUFEN:
                geprueft += 1
                fehler += _r3(neu["laengen"][s]) != quartett[(f, n, idx)]["laengen"][v][s][lauf]
            if v != "sa":
                geprueft += 1
                fehler += neu["erster_abstieg"] != quartett[(f, n, idx)]["erster_abstieg"][v][lauf]
    print(f"GESAMT: {geprueft} Prüfungen, {fehler} Abweichungen")
    return 1 if fehler else 0


if __name__ == "__main__":
    start = time.perf_counter()
    arg = sys.argv[1:]
    if not arg:
        sys.exit(__doc__)
    if arg[0] == "--check":
        code = check()
        print(f"{time.perf_counter() - start:.0f} s")
        sys.exit(code)
    {"abstimmung-trio": abstimmung_trio, "abstimmung-quartett": abstimmung_quartett, "trio": teil_trio, "quartett": teil_quartett,
     "referenz": teil_referenz, "zusammen": zusammen, "erwartung": erwartung}[arg[0]](*arg[1:])
    print(f"{time.perf_counter() - start:.0f} s")
