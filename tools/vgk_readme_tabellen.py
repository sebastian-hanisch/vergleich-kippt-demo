"""Schreibt die Zahlentabellen der README aus den eingefrorenen Messreihen (zwischen den Marken <!-- TABELLE:name --> und <!-- /TABELLE:name -->).

    python tools/vgk_readme_tabellen.py --write     Tabellen in README.md ersetzen
    python tools/vgk_readme_tabellen.py --check     prüfen, dass die README die Tabellen dieser Daten enthält (Rückgabewert 1 bei Abweichung)

`tests/test_claims.py` ruft `tabellen()` auf und vergleicht mit der README: so stehen in den Tabellen nur Zahlen aus den Daten."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import vgk_constants as C  # noqa: E402
import vgk_daten as D  # noqa: E402
import vgk_evaluation as ev  # noqa: E402
import vgk_rangtest as R  # noqa: E402

SEEDS = (35, 36)      # Zufalls-Seeds der zwei Ziehungsreihen im Mehrfachtest (35 ist die Voreinstellung der App)


def _tabelle(kopf: list, zeilen: list) -> str:
    aus = ["| " + " | ".join(kopf) + " |", "|" + "---|" * len(kopf)]
    aus += ["| " + " | ".join(str(x) for x in z) + " |" for z in zeilen]
    return "\n".join(aus)


def _haelften(trio):
    return D.teil(trio, 0, 30), D.teil(trio, 30, 60)


def tab_trio() -> str:
    trio = D.trio()
    zeilen = []
    for sa in C.SA_WAHL:
        u = ev.trio_uebersicht(trio, sa)
        h = [ev.trio_uebersicht(x, sa) for x in _haelften(trio)]
        for k, z in enumerate(u["zeilen"]):
            zeilen.append([ev.SA_TEXT[sa], ev.tsd(z["budget"]), ev.de(z["mittel"]["HC"], 2), ev.de(z["mittel"]["SA"], 2), ev.de(z["mittel"]["GA"], 2), z["ordnung"],
                           f"{z['vorn']['HC']} / {z['vorn']['SA']} / {z['vorn']['GA']}",
                           "; ".join(f"{ev.de(x['zeilen'][k]['mittel']['HC'], 2)} / {ev.de(x['zeilen'][k]['mittel']['SA'], 2)} / {ev.de(x['zeilen'][k]['mittel']['GA'], 2)}" for x in h)])
    return _tabelle(["SA-Einstellung", "Budget", "HC (%)", "SA (%)", "GA (%)", "Ordnung der Mittel", "allein vorn auf Instanzen HC / SA / GA (von 63)",
                     "Gegenprobe: Mittel HC / SA / GA der Läufe 1 bis 30; 31 bis 60"], zeilen)


def tab_familien() -> str:
    trio = D.trio()
    zeilen = []
    for sa in C.SA_WAHL:
        u = ev.trio_uebersicht(trio, sa)
        kb = ev.budget_kippen(trio, sa)
        for b in trio["budgets"]:
            zeilen.append([ev.SA_TEXT[sa], ev.tsd(b)] + [u["ordnungen"][(b, f)] for f in u["familien"]])
        zeilen.append([ev.SA_TEXT[sa], "Instanzen mit anderer Rangfolge zwischen zwei Budgets",
                       " ; ".join(f"{ev.tsd(a)} ↔ {ev.tsd(b)}: {ev.pz(w, 1)} %" for (a, b), w in kb.items()), "", ""])
    return _tabelle(["SA-Einstellung", "Budget", "gleichverteilt", "geclustert", "Gitter mit Rauschen"], zeilen)


def tab_gruppen() -> str:
    trio = D.trio()
    zeilen = []
    for sa in C.SA_WAHL:
        for b in trio["budgets"]:
            for paar in C.PAARE:
                e = ev.exp_gruppen(trio, b, 5, paar, sa)
                h = [ev.exp_gruppen(x, b, 5, paar, sa)["gewaehlt"]["verschieden"] for x in _haelften(trio)]
                p = {k["r"]: k for k in e["kurve"]}
                zeilen.append([ev.SA_TEXT[sa], ev.tsd(b), ev.PAAR_TEXT[paar], " / ".join(ev.pz(p[r]["verschieden"], 1) for r in C.GRUPPEN_R),
                               " / ".join(ev.pz(p[r]["strikt"], 1) for r in C.GRUPPEN_R) if "strikt" in p[5] else "–",
                               " / ".join(ev.pz(p[r]["formel"], 1) for r in C.GRUPPEN_R) if "formel" in p[5] else "–",
                               ev.pz(p[5]["mit_abweichung"]), f"{ev.pz(h[0], 1)} / {ev.pz(h[1], 1)}",
                               (("keine" if e["laeufe_median"] == float("inf") else ev.de(e["laeufe_median"], 1)) + f" ({e['laeufe_bis_5']} / {e['laeufe_ueber_60']})") if "laeufe_median" in e else "–"])
    return _tabelle(["SA-Einstellung", "Budget", "Verfahren", "verschieden bei r = 3 / 5 / 10 / 15 / 30 (%)", "strikt entgegengesetzt (%)", "Kippformel (%)",
                     "Instanzen mit mind. einem abweichenden Paar bei r = 5 (%)", "Gegenprobe r = 5: Läufe 1 bis 30 / 31 bis 60 (%)",
                     "Läufe je Gruppe für höchstens 5 %: Median (Instanzen bis 5 / über 60)"], zeilen)


def tab_mass() -> str:
    trio = D.trio()
    zeilen = []
    for sa in C.SA_WAHL:
        for b in trio["budgets"]:
            e = ev.exp_mass(trio, b, sa)
            h = [ev.exp_mass(x, b, sa)["anders"][("mittel", "bestes")] for x in _haelften(trio)]
            gleichauf = {z["mass"]: z["alle_gleichauf"] for z in e["tabelle"]}
            zeilen.append([ev.SA_TEXT[sa], ev.tsd(b)] + [ev.pz(e["anders"][("mittel", m)], 1) for m in C.MASSE_WAHL] + [ev.pz(e["anders"][("bestes", "median")], 1),
                          " / ".join(ev.de(e["tau"][("mittel", m)][0], 2) + (f" ({e['tau'][('mittel', m)][1]})" if e["tau"][("mittel", m)][1] else "") for m in C.MASSE_WAHL),
                          f"{gleichauf['bestes']} / {gleichauf['anteil']}", f"{ev.pz(h[0], 1)} / {ev.pz(h[1], 1)}"])
    return _tabelle(["SA-Einstellung", "Budget", "Mittel gegen Median (%)", "gegen Bestes (%)", "gegen Anteil ≤ 2 % (%)", "gegen Fläche (%)", "Bestes gegen Median (%)",
                     "mittleres τ zum Mittel: Median / Bestes / Anteil / Fläche (in Klammern: Instanzen ohne definiertes τ)", "Instanzen, alle drei gleichauf: Bestes / Anteil",
                     "Gegenprobe Mittel gegen Bestes: Läufe 1 bis 30 / 31 bis 60 (%)"], zeilen)


def tab_einstellung() -> str:
    trio = D.trio()
    e = ev.exp_einstellung(trio)
    h = [ev.exp_einstellung(x) for x in _haelften(trio)]
    zeilen = [[ev.tsd(z["budget"]), ev.de(z["sa_std"]["mittel"]["SA"], 2), ev.de(z["sa_abg"]["mittel"]["SA"], 2), ev.de(z["sa_std"]["mittel"]["HC"], 2),
               z["sa_std"]["ordnung"], z["sa_abg"]["ordnung"], ev.pz(z["anders"], 1), f"{z['sa_vor_hc']['sa_std']} / {z['sa_vor_hc']['sa_abg']}",
               f"{ev.pz(h[0]['zeilen'][k]['anders'], 1)} / {ev.pz(h[1]['zeilen'][k]['anders'], 1)}"] for k, z in enumerate(e["zeilen"])]
    return _tabelle(["Budget", "SA Standard (%)", "SA abgestimmt (%)", "HC (%)", "Ordnung mit Standard", "Ordnung mit abgestimmt", "Instanzen mit anderer Rangfolge (%)",
                     "SA vor HC auf Instanzen: Standard / abgestimmt", "Gegenprobe: Läufe 1 bis 30 / 31 bis 60 (%)"], zeilen)


def tab_exakt() -> str:
    zeilen = []
    for r in C.NULL_GRUPPEN:
        p, pe = R.verwerfung_ohne_gleichstand(r), R.verwerfung_exakter_test(r)
        b, be = R.verwerfung_ohne_gleichstand(r, 0.05 / 30), R.verwerfung_exakter_test(r, 0.05 / 30)
        zeilen.append([f"{r} gegen {r}", ev.pz(p, 3), ev.pz(R.mindestens_eine(p, 30), 1), ev.pz(pe, 3), ev.pz(b, 4), ev.pz(R.mindestens_eine(b, 30), 2), ev.pz(be, 4), ev.pz(R.mindestens_eine(be, 30), 2)])
    return _tabelle(["Läufe je Gruppe", "Verwerfung je Test, Normalnäherung (%)", "mind. eine unter 30 (%)", "je Test, exakter Test (%)",
                     "Bonferroni je Test, Normalnäherung (%)", "Bonferroni unter 30 (%)", "Bonferroni je Test, exakter Test (%)", "Bonferroni unter 30, exakter Test (%)"], zeilen)


def tab_modell() -> str:
    zeilen = [[ev.de(q, 2)] + [f"{ev.pz(R.verwerfung_modell(q, r), 3)} / {ev.pz(R.mindestens_eine(R.verwerfung_modell(q, r), 30), 1)}" for r in C.NULL_GRUPPEN] for q in ev.MODELL_Q]
    return _tabelle(["q (Anteil der Läufe auf dem Bestwert)"] + [f"{r} gegen {r}: je Test / mind. eine unter 30 (%)" for r in C.NULL_GRUPPEN], zeilen)


def tab_null() -> str:
    trio, pool = D.trio(), D.nulltest()
    zeilen = []
    for v in C.TRIO_VERFAHREN:
        for b in trio["budgets"]:
            for r in C.NULL_GRUPPEN:
                e = [ev.exp_null(trio, pool, v, b, 30, r, s) for s in SEEDS]
                e63 = ev.exp_null(trio, pool, v, b, 63, r, SEEDS[0])
                zeilen.append([{"hc": "HC", "sa_std": "SA Standard", "sa_abg": "SA abgestimmt", "ga": "GA"}[v], ev.tsd(b), f"{r} gegen {r}", ev.pz(e[0]["gleichstand_pool"]),
                               f"{ev.pz(e[0]['haeufigster_mittel'])} / {ev.pz(e[0]['haeufigster_max'])}", ev.pz(e[0]["p_pool_mittel"], 2), ev.pz(e[0]["erwartung_pool"], 1),
                               ev.pz(e[0]["erwartung_ohne"], 1), f"{ev.pz(e[0]['mindestens_eine'])} / {ev.pz(e[1]['mindestens_eine'])}",
                               f"{e[0]['bonferroni']} / {e[1]['bonferroni']}", f"{ev.pz(e63['erwartung_pool'], 1)} / {ev.pz(e63['erwartung_ohne'], 1)}"])
    return _tabelle(["Verfahren", "Budget", "Gruppen", "Ziehungen mit Gleichständen (%)", "häufigster Wert unter 60 Läufen: Mittel / größter (%)", "Verwerfung je Test (%)",
                     "mind. eine unter 30, mit Gleichständen (%)", "ohne Gleichstände (%)", "gemessen, 100 Wiederholungen, Zufalls-Seed 35 / 36 (%)",
                     "Bonferroni: Wiederholungen von 100, Zufalls-Seed 35 / 36", "63 Instanzen: mit / ohne Gleichstände (%)"], zeilen)


def tab_quartett() -> str:
    q = D.quartett()
    e = ev.exp_quartett(q, "1000n", "alle", 12)
    h = [ev.exp_quartett(D.teil(q, a, b), "1000n", "alle", 6) for a, b in ((0, 6), (6, 12))]
    zeilen = []
    for f in e["familien"]:
        for s in e["stufen"]:
            z = e["raster"][(s, f)]
            zeilen.append([ev.FAMILIE_TEXT[f], ev.STUFE_TEXT[s], ev.de(z["mittel"]["hc"], 2), ev.de(z["mittel"]["sa"], 2), ev.de(z["mittel"]["ils"], 2), ev.de(z["mittel"]["ma"], 2),
                           z["ordnung"], ev.de(z["faktor"], 2), ev.pz(z["fertig_mittel"]), "; ".join(x["raster"][(s, f)]["ordnung"] for x in h)])
    return _tabelle(["Familie", "Budget", "HC (%)", "SA (%)", "ILS (%)", "MA (%)", "Rangfolge der Mittel", "Gruppenfaktor", "erster Abstieg beendet (% der Läufe von HC, ILS, MA)",
                     "Gegenprobe: Rangfolge aus den Läufen 1 bis 6; 7 bis 12"], zeilen)


def tab_abstieg() -> str:
    import numpy as np
    q = D.quartett()
    zeilen = []
    for n in C.QUARTETT_N:
        maske = q["n"] == n
        werte = np.concatenate([q["erster_abstieg"][v][maske].ravel() for v in ("hc", "ils", "ma")])
        zeilen.append([n, ev.tsd(n * (n - 3) // 2), ev.tsd(int(np.nanmedian(werte))), f"{ev.tsd(int(np.nanmin(werte)))} bis {ev.tsd(int(np.nanmax(werte)))}",
                       ev.de(float(np.nanmedian(werte)) / n, 0), int(np.isnan(werte).sum())])
    return _tabelle(["Orte n", "Züge je Durchgang n(n − 3)/2", "Auswertungen bis zum Ende des ersten Abstiegs: Median", "kleinster bis größter Wert",
                     "Median geteilt durch n", "nicht beendete Abstiege (von 288 je Ortszahl)"], zeilen)


def tab_abstimmung() -> str:
    a = D.abstimmung()
    zeilen = [[ev.de(z["t0f"], 2), ev.de(z["c"], 1)] + [ev.de(x, 2) for x in z["luecke_je_budget"]] + [ev.de(z["mittel"], 2)] for z in a["trio"]["gitter"]]
    t1 = _tabelle(["Starttemperatur (· Skala)", "Abkühlung (Zehnerpotenzen)", "Lücke bei 1.000 (%)", "bei 3.000 (%)", "bei 10.000 (%)", "Mittel der drei (%)"], zeilen)
    zeilen = [[ev.de(z["t0f"], 2), ev.de(z["c"], 1)] + [ev.de(z["luecke"][s], 2) for s in C.QUARTETT_STUFEN] for z in a["quartett"]["gitter_sa"]]
    t2 = _tabelle(["Starttemperatur (· Skala)", "Abkühlung (Zehnerpotenzen)"] + [f"Lücke bei {ev.STUFE_TEXT[s]} (%)" for s in C.QUARTETT_STUFEN], zeilen)
    zeilen = [[z["groesse"]] + [ev.de(z["luecke"][s], 2) for s in C.QUARTETT_STUFEN] + [ev.de(z["mittel"], 2)] for z in a["quartett"]["gitter_ma"]]
    t3 = _tabelle(["Größe der Population (MA)"] + [f"Lücke bei {ev.STUFE_TEXT[s]} (%)" for s in C.QUARTETT_STUFEN] + ["Mittel der vier (%)"], zeilen)
    return (f"Trio, Simulated Annealing (15 Abstimm-Instanzen, 10 Läufe je Zelle; gewählt: kleinstes Mittel der drei Budgets):\n\n{t1}\n\n"
            f"Quartett, Simulated Annealing (12 Abstimm-Instanzen, 4 Läufe je Zelle; gewählt je Budget die kleinste Lücke):\n\n{t2}\n\n"
            f"Quartett, memetischer Algorithmus (dieselben Instanzen; gewählt: kleinstes Mittel der vier Budgets):\n\n{t3}")


def tabellen() -> dict:
    return {"trio": tab_trio(), "familien": tab_familien(), "gruppen": tab_gruppen(), "mass": tab_mass(), "einstellung": tab_einstellung(), "exakt": tab_exakt(),
            "modell": tab_modell(), "null": tab_null(), "quartett": tab_quartett(), "abstieg": tab_abstieg(), "abstimmung": tab_abstimmung()}


def ersetze(text: str, tabs: dict) -> str:
    for name, inhalt in tabs.items():
        a, b = f"<!-- TABELLE:{name} -->", f"<!-- /TABELLE:{name} -->"
        if a not in text or b not in text:
            raise SystemExit(f"Marke {name} fehlt in der README")
        vor, rest = text.split(a, 1)
        _, nach = rest.split(b, 1)
        text = f"{vor}{a}\n{inhalt}\n{b}{nach}"
    return text


if __name__ == "__main__":
    readme = ROOT / "README.md"
    if "--write" not in sys.argv and "--check" not in sys.argv:
        for name, inhalt in tabellen().items():
            print(f"== {name}\n{inhalt}\n")
        sys.exit(0)
    alt = readme.read_text(encoding="utf-8")
    neu = ersetze(alt, tabellen())
    if "--write" in sys.argv:
        readme.write_text(neu, encoding="utf-8", newline="\n")
        print("README-Tabellen geschrieben")
    else:
        print("README-Tabellen stimmen" if neu == alt else "README-Tabellen weichen ab")
        sys.exit(0 if neu == alt else 1)
