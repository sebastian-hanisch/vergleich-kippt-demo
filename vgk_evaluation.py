"""Auswertungen der fünf Experimente und alle Verdikte als reine Funktionen `verdict_*(...) -> (Art, Text)`.

Die Auswertungen rechnen auf den eingefrorenen Läufen (`vgk_daten`); die Verdikte bekommen nur deren Ergebniszeilen."""

import math
from fractions import Fraction

import numpy as np

import vgk_compare as V
import vgk_rangtest as R

KURZ = {"hc": "HC", "sa_std": "SA", "sa_abg": "SA", "sa": "SA", "ga": "GA", "ils": "ILS", "ma": "MA"}
SA_TEXT = {"sa_std": "Standard", "sa_abg": "abgestimmt"}
PAARE = {"hc_sa": ("hc", "sa"), "sa_ga": ("sa", "ga"), "alle": ("hc", "sa", "ga")}
PAAR_TEXT = {"hc_sa": "HC gegen SA", "sa_ga": "SA gegen GA", "alle": "alle drei (HC, SA, GA)"}
GRUPPEN_R = (3, 5, 10, 15, 30)
FAMILIE_TEXT = {"alle": "alle Familien", "gleich": "gleichverteilt", "cluster": "geclustert", "gitter": "Gitter mit Rauschen", "netz": "Straßennetz"}
STUFE_TEXT = {"30n": "30 · n", "100n": "100 · n", "1000n": "1.000 · n", "5000n": "5.000 · n"}
ABSTIEG_SCHWELLE = 0.5      # unter diesem Anteil beendeter erster Abstiege nennt das Verdikt keine Rangfolge von HC, ILS und MA
LESEHILFE = (0.10, 0.30)    # Anteil kippender Instanzen: darunter „stabil“, dazwischen „gemischt“, darüber „instabil“ (vorab festgelegt, keine Prüfgröße)


def de(x: float, stellen: int = 1) -> str:
    """Zahl mit Dezimalkomma."""
    return f"{x:.{stellen}f}".replace(".", ",")


def tsd(n: int) -> str:
    """Ganze Zahl mit Tausenderpunkt."""
    return f"{n:,}".replace(",", ".")


def pz(anteil: float, stellen: int = 0) -> str:
    """Anteil 0..1 als Prozentzahl mit Dezimalkomma (ohne Prozentzeichen)."""
    return de(100.0 * anteil, stellen)


def lesehilfe(anteil: float) -> str:
    return "stabil" if anteil < LESEHILFE[0] else ("gemischt" if anteil <= LESEHILFE[1] else "instabil")


# ------------------------------------------------------------------------------------------------------------------------------
# Trio: Felder und Übersicht
# ------------------------------------------------------------------------------------------------------------------------------
def trio_felder(trio: dict, budget: int, sa: str, verfahren=("hc", "sa", "ga")) -> tuple:
    """(Kurznamen, Lücken, Flächen) der gewählten Verfahren; „sa“ steht für die gewählte Einstellung von Simulated Annealing."""
    schluessel = [sa if v == "sa" else v for v in verfahren]
    return [KURZ[v] for v in verfahren], [trio["luecke"][k][budget] for k in schluessel], [trio["flaeche"][k][budget] for k in schluessel]


def trio_uebersicht(trio: dict, sa: str) -> dict:
    """Mittlere Lücke je Verfahren und Budget, Ordnung gesamt und je Familie, und wie oft jedes Verfahren auf einer Instanz vorn liegt (Maß Mittel, alle Läufe)."""
    familien = sorted(set(trio["familie"]), key=trio["familie"].index)
    zeilen, ordnungen = [], {}
    for b in trio["budgets"]:
        namen, luecken, _ = trio_felder(trio, b, sa)
        mittel = [float(x.mean()) for x in luecken]
        je_instanz = np.stack([x.mean(axis=1) for x in luecken], axis=-1)
        vorn = (V.raenge(np.round(je_instanz, V.STELLEN)) == 1.0).sum(axis=0)       # nur alleinige Sieger
        ordnungen[(b, "alle")] = V.ordnung_text(namen, mittel)
        for f in familien:
            maske = np.array([x == f for x in trio["familie"]])
            ordnungen[(b, f)] = V.ordnung_text(namen, [float(x[maske].mean()) for x in luecken])
        zeilen.append({"budget": b, "mittel": dict(zip(namen, mittel)), "ordnung": ordnungen[(b, "alle")], "vorn": dict(zip(namen, (int(v) for v in vorn))),
                       "instanzen": len(trio["familie"])})
    verschiedene = sorted(set(ordnungen.values()))
    return {"zeilen": zeilen, "ordnungen": ordnungen, "verschiedene": verschiedene, "zellen": len(ordnungen), "familien": familien, "sa": sa}


def budget_kippen(trio: dict, sa: str) -> dict:
    """Anteil der Instanzen, deren Rangfolge (Maß Mittel, alle Läufe) sich zwischen zwei Budgets unterscheidet."""
    rang = {b: V.instanz_raenge(trio_felder(trio, b, sa)[1], "mittel") for b in trio["budgets"]}
    bs = trio["budgets"]
    return {(bs[i], bs[j]): V.anteil_andere_ordnung(rang[bs[i]], rang[bs[j]]) for i in range(len(bs)) for j in range(i + 1, len(bs))}


def verdict_trio(u: dict, kippen_budget: dict) -> tuple:
    """Gibt es im Trio einen Dauergewinner über Budgets und Familien (Maß Mittel, alle Läufe)?"""
    groesster = max(kippen_budget.values())
    zusatz = (f" Je Instanz gerechnet unterscheidet sich die Rangfolge zwischen zwei Budgets in höchstens {pz(groesster)} % der {u['zeilen'][0]['instanzen']} Instanzen.")
    if len(u["verschiedene"]) == 1:
        return "info", (f"Im Trio ist die Ordnung der mittleren Lücke in allen {u['zellen']} Zellen aus Budget und Familie dieselbe: **{u['verschiedene'][0]}** "
                        f"(Maß Mittel, 60 Läufe je Instanz, Simulated Annealing in der Einstellung „{SA_TEXT[u['sa']]}“). Budget und Familie kippen diese Rangfolge hier nicht; "
                        "die Messung kippt sie trotzdem (Experimente 1 bis 4)." + zusatz)
    haeufig = max(u["verschiedene"], key=lambda o: sum(1 for x in u["ordnungen"].values() if x == o))
    zahl = sum(1 for x in u["ordnungen"].values() if x == haeufig)
    return "warning", (f"Im Trio gibt es {len(u['verschiedene'])} verschiedene Ordnungen der mittleren Lücke in den {u['zellen']} Zellen aus Budget und Familie; "
                       f"am häufigsten **{haeufig}** ({zahl} von {u['zellen']}; Maß Mittel, 60 Läufe je Instanz, Simulated Annealing in der Einstellung „{SA_TEXT[u['sa']]}“). "
                       "Schon Budget oder Familie ändern hier die Rangfolge." + zusatz)


# ------------------------------------------------------------------------------------------------------------------------------
# Experiment 1: Läufegruppen
# ------------------------------------------------------------------------------------------------------------------------------
def exp_gruppen(trio: dict, budget: int, r: int, paar: str, sa: str) -> dict:
    namen, luecken, _ = trio_felder(trio, budget, sa, PAARE[paar])
    ist_paar = len(namen) == 2
    kurve = []
    for rr in GRUPPEN_R:
        if luecken[0].shape[1] // rr < 2:      # weniger als zwei Gruppen: kein Gruppenpaar (nur bei Teilmengen der Läufe)
            continue
        k = V.kippen_gruppen(luecken, rr)
        punkt = {"r": rr, "verschieden": float(k["verschieden"].mean()), "paare": k["paare"], "gruppen": k["gruppen"],
                 "gleichstand": float(k["gleichstand"].mean()), "mit_abweichung": float((k["verschieden"] > 0).mean())}
        if ist_paar:
            punkt["strikt"] = float(k["strikt"].mean())
            punkt["formel"], punkt["formel_undefiniert"] = V.formel_mittel(luecken[0], luecken[1], rr)
        kurve.append(punkt)
    aus = {"paar": paar, "namen": namen, "budget": budget, "r": r, "sa": sa, "kurve": kurve, "gewaehlt": next(p for p in kurve if p["r"] == r),
           "instanzen": luecken[0].shape[0], "je_instanz": V.kippen_gruppen(luecken, r)["verschieden"]}
    if ist_paar:
        k = V.paar_kennzahlen(luecken[0], luecken[1])
        bedarf = [V.laeufe_fuer_fuenf_prozent(float(d), float(s1), float(s2)) for d, s1, s2 in zip(k["delta"], k["s1"], k["s2"])]
        endlich = [math.inf if x is None else x for x in bedarf]
        aus["laeufe_median"] = float(np.median(endlich))
        aus["laeufe_ueber_60"] = int(sum(x > 60 for x in endlich))
        aus["laeufe_bis_5"] = int(sum(x <= 5 for x in endlich))
    return aus


def verdict_gruppen(e: dict) -> tuple:
    g = e["gewaehlt"]
    wer = "das Paar " + " / ".join(e["namen"]) if len(e["namen"]) == 2 else "das Trio " + ", ".join(e["namen"])
    text = (f"Gruppen zu **{g['r']} Läufen**, {tsd(e['budget'])} Auswertungen: im Mittel über {e['instanzen']} Instanzen ordnen **{pz(g['verschieden'])} %** der "
            f"{g['paare']} Gruppenpaare je Instanz {wer} verschieden (Maß Mittel, Gleichstand zählt als verschieden); "
            f"auf {pz(g['mit_abweichung'])} % der Instanzen weicht mindestens ein Paar ab.")
    if "strikt" in g:
        text += (f" Strikt entgegengesetzt ordnen {pz(g['strikt'])} %; die Formel 2Φ(d)(1 − Φ(d)) sagt {pz(g['formel'])} % voraus "
                 f"(Normalannahme, Näherung). In {pz(g['gleichstand'])} % der Gruppen liegen die zwei Verfahren gleichauf.")
        if math.isinf(e["laeufe_median"]):
            text += f" Für höchstens 5 % Kippen reicht auf mehr als der Hälfte der Instanzen keine Gruppengröße (kein Unterschied der Mittel); bei {e['laeufe_ueber_60']} von {e['instanzen']} Instanzen wären mehr als 60 Läufe nötig."
        else:
            text += (f" Für höchstens 5 % Kippen braucht eine Instanz nach der Formel im Median {de(e['laeufe_median'], 0)} Läufe je Gruppe "
                     f"(bei {e['laeufe_ueber_60']} von {e['instanzen']} Instanzen mehr als 60).")
    else:
        text += f" In {pz(g['gleichstand'])} % der Gruppen liegen mindestens zwei Verfahren gleichauf."
    art = "success" if g["verschieden"] < LESEHILFE[0] else ("info" if g["verschieden"] <= LESEHILFE[1] else "warning")
    return art, text


# ------------------------------------------------------------------------------------------------------------------------------
# Experiment 2: das Maß
# ------------------------------------------------------------------------------------------------------------------------------
def exp_mass(trio: dict, budget: int, sa: str) -> dict:
    namen, luecken, flaechen = trio_felder(trio, budget, sa)
    rang = {m: V.instanz_raenge(luecken, m, flaechen) for m in V.MASSE}
    tabelle = []
    for m in V.MASSE:
        werte = np.stack([V.mass_wert(x, m, flaechen[k]) for k, x in enumerate(luecken)], axis=-1)
        if m == "anteil":
            werte = 1.0 - werte
        tabelle.append({"mass": m, "mittel": dict(zip(namen, (float(x) for x in werte.mean(axis=0)))),
                        "mittlerer_rang": dict(zip(namen, (float(x) for x in rang[m].mean(axis=0)))),
                        "ordnung": V.ordnung_text(namen, [float(x) for x in rang[m].mean(axis=0)]),
                        "alle_gleichauf": int((rang[m] == rang[m][:, :1]).all(axis=1).sum())})
    anders, tau = {}, {}
    for a in V.MASSE:
        for b in V.MASSE:
            anders[(a, b)] = V.anteil_andere_ordnung(rang[a], rang[b])
            tau[(a, b)] = V.tau_mittel(rang[a], rang[b])
    return {"budget": budget, "sa": sa, "namen": namen, "tabelle": tabelle, "anders": anders, "tau": tau, "instanzen": luecken[0].shape[0]}


def verdict_mass(e: dict, mass: str) -> tuple:
    a = e["anders"][("mittel", mass)]
    tau, ohne = e["tau"][("mittel", mass)]
    text = (f"{tsd(e['budget'])} Auswertungen: zwischen **Mittel** und **{V.MASS_TEXT[mass]}** ist die Rangfolge von HC, SA und GA auf **{pz(a)} %** der "
            f"{e['instanzen']} Instanzen verschieden (60 Läufe je Instanz; Lesehilfe: {lesehilfe(a)}).")
    if math.isnan(tau):
        text += " Kendall τ ist auf keiner Instanz definiert."
    else:
        text += f" Mittleres Kendall τ: {de(tau, 2)}" + (f" (auf {ohne} Instanzen nicht definiert, weil ein Maß alle drei gleich bewertet)." if ohne else ".")
    andere = {m: e["anders"][("mittel", m)] for m in V.MASSE if m != "mittel"}
    groesst = max(andere, key=andere.get)
    text += f" Am weitesten vom Mittel entfernt ist hier „{V.MASS_TEXT[groesst]}“ mit {pz(andere[groesst])} %."
    return ("success" if a < LESEHILFE[0] else ("info" if a <= LESEHILFE[1] else "warning")), text


def mass_beispiel() -> list:
    """Handbeispiel: fünf Läufe, Lücken A = (2, 2, 2, 2, 12), B = (3, 3, 3, 3, 3); je Maß der Wert beider Verfahren und wer besser ist."""
    a, b = np.array([2.0, 2, 2, 2, 12]), np.array([3.0, 3, 3, 3, 3])
    zeilen = []
    for m in ("mittel", "median", "bestes", "anteil"):
        wa, wb = float(V.mass_wert(a, m)), float(V.mass_wert(b, m))
        zeige = (1 - wa, 1 - wb) if m == "anteil" else (wa, wb)
        zeilen.append({"mass": m, "A": zeige[0], "B": zeige[1], "besser": "A" if wa < wb else ("B" if wb < wa else "gleich")})
    return zeilen


# ------------------------------------------------------------------------------------------------------------------------------
# Experiment 3: Mehrfachtest, dasselbe Verfahren gegen sich selbst
# ------------------------------------------------------------------------------------------------------------------------------
MODELL_Q = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95)
WIEDERHOLUNGEN = 100


def exp_null(trio: dict, pooldaten: dict, verfahren: str, budget: int, m: int, r: int, seed: int) -> dict:
    """`verfahren`: Schlüssel der Messreihe (hc, sa_std, sa_abg, ga). Die ersten m Instanzen der Messreihe werden getestet."""
    pool = trio["laengen"][verfahren][budget][:m]
    erg = R.nulltest(pool, r, WIEDERHOLUNGEN, seed)
    zelle = pooldaten["zellen"][f"{verfahren}|{budget}"]
    p_pool = zelle[str(r)]["p"][:m]
    p_ohne = R.verwerfung_ohne_gleichstand(r)
    p_bonf = R.verwerfung_ohne_gleichstand(r, R.NIVEAU / m)
    erwartung_pool = R.erwartung_aus_pool(p_pool)
    return {
        "verfahren": verfahren, "budget": budget, "m": m, "r": r, "seed": seed, "wiederholungen": WIEDERHOLUNGEN,
        "anteil_signifikant": erg["signifikant"] / erg["tests"], "mindestens_eine": erg["mindestens_eine"] / WIEDERHOLUNGEN,
        "bonferroni": erg["bonferroni_mindestens_eine"], "anteil_gleichstand": erg["mit_gleichstand"] / erg["tests"],
        "p_ohne": p_ohne, "erwartung_ohne": R.mindestens_eine(p_ohne, m), "erwartung_pool": erwartung_pool, "p_pool_mittel": float(np.mean(p_pool)),
        "bonferroni_ohne": R.mindestens_eine(p_bonf, m), "gleichstand_pool": float(np.mean(zelle[str(r)]["gleichstand"][:m])),
        "haeufigster_mittel": float(np.mean(zelle["haeufigster"][:m])), "haeufigster_max": float(np.max(zelle["haeufigster"][:m])),
        "haeufigster": zelle["haeufigster"][:m],
        "standardfehler": math.sqrt(max(erwartung_pool * (1 - erwartung_pool), 0.0) / WIEDERHOLUNGEN),
    }


def verdict_null(e: dict) -> tuple:
    name = {"hc": "Hill Climbing", "sa_std": "Simulated Annealing (Standard)", "sa_abg": "Simulated Annealing (abgestimmt)", "ga": "genetischer Algorithmus"}[e["verfahren"]]
    test = "Tests" if e["m"] != 1 else "Test"
    text = (f"**{e['m']} {test}, {e['r']} gegen {e['r']} Läufe, dasselbe Verfahren ({name}, {tsd(e['budget'])} Auswertungen):** in **{pz(e['mindestens_eine'])} %** der "
            f"{e['wiederholungen']} Wiederholungen ist mindestens ein Test „signifikant“ (Niveau 0,05; {pz(e['anteil_signifikant'], 1)} % der Einzeltests). "
            f"Erwartung ohne Gleichstände: {pz(e['erwartung_ohne'], 1)} % ({pz(e['p_ohne'], 2)} % je Einzeltest, nicht 5 %); mit den Gleichständen dieser Läufe: "
            f"{pz(e['erwartung_pool'], 1)} %. {pz(e['anteil_gleichstand'])} % der Tests enthalten Gleichstände; der häufigste Wert stellt im Mittel "
            f"{pz(e['haeufigster_mittel'])} % der 60 Läufe einer Instanz (höchstens {pz(e['haeufigster_max'])} %).")
    if e["bonferroni_ohne"] == 0.0:
        text += f" Mit Bonferroni: {e['bonferroni']} von {e['wiederholungen']}; bei {e['r']} gegen {e['r']} Läufen und {e['m']} Tests kann dieser Test nach Bonferroni nie verwerfen."
    else:
        text += f" Mit Bonferroni: {e['bonferroni']} von {e['wiederholungen']} (ohne Gleichstände erwartet {pz(e['bonferroni_ohne'], 2)} %)."
    if abs(e["erwartung_ohne"] - e["erwartung_pool"]) > 2 * e["standardfehler"] and e["standardfehler"] > 0:
        text += (" **Die Linie „ohne Gleichstände“ beschreibt diese Läufe nicht:** sie liegt mehr als zwei Standardfehler der Messung neben der Erwartung mit Gleichständen. "
                 "Der Rückgang ist kein Gewinn an Ehrlichkeit; bei vielen gleichen Werten sieht der Test nur weniger.")
        return "warning", text
    return "info", text


# ------------------------------------------------------------------------------------------------------------------------------
# Experiment 4: die Einstellung
# ------------------------------------------------------------------------------------------------------------------------------
def exp_einstellung(trio: dict) -> dict:
    zeilen = []
    for b in trio["budgets"]:
        zeile = {"budget": b}
        raenge = {}
        for sa in ("sa_std", "sa_abg"):
            namen, luecken, _ = trio_felder(trio, b, sa)
            zeile[sa] = {"mittel": dict(zip(namen, (float(x.mean()) for x in luecken))), "ordnung": V.ordnung_text(namen, [float(x.mean()) for x in luecken])}
            raenge[sa] = V.instanz_raenge(luecken, "mittel")
        zeile["anders"] = V.anteil_andere_ordnung(raenge["sa_std"], raenge["sa_abg"])
        zeile["sa_vor_hc"] = {sa: int((raenge[sa][:, 1] < raenge[sa][:, 0]).sum()) for sa in raenge}
        zeile["instanzen"] = raenge["sa_std"].shape[0]
        zeilen.append(zeile)
    return {"zeilen": zeilen, "einstellungen": trio["meta"]["sa_einstellungen"]}


def verdict_einstellung(e: dict, budget: int) -> tuple:
    z = next(x for x in e["zeilen"] if x["budget"] == budget)
    alle = " / ".join(pz(x["anders"]) for x in e["zeilen"])
    budgets = " / ".join(tsd(x["budget"]) for x in e["zeilen"])
    text = (f"Wechsel der Einstellung von Simulated Annealing (Standard gegen abgestimmt), {tsd(budget)} Auswertungen: die Rangfolge des Trios ist auf **{pz(z['anders'])} %** "
            f"der {z['instanzen']} Instanzen verschieden (Maß Mittel, 60 Läufe; Lesehilfe: {lesehilfe(z['anders'])}). Ordnung der Mittel: {z['sa_std']['ordnung']} (Standard), "
            f"{z['sa_abg']['ordnung']} (abgestimmt). SA liegt vor HC auf {z['sa_vor_hc']['sa_std']} (Standard) und {z['sa_vor_hc']['sa_abg']} (abgestimmt) Instanzen. "
            f"Über die Budgets {budgets}: {alle} %.")
    return ("success" if z["anders"] < LESEHILFE[0] else ("info" if z["anders"] <= LESEHILFE[1] else "warning")), text


# ------------------------------------------------------------------------------------------------------------------------------
# Experiment 5: Budget und Familie am Quartett
# ------------------------------------------------------------------------------------------------------------------------------
def quartett_zelle(q: dict, stufe: str, familie: str, laeufe: int) -> dict:
    maske = np.ones(len(q["familie"]), dtype=bool) if familie == "alle" else np.array([f == familie for f in q["familie"]])
    mittel = {v: float(q["luecke"][v][stufe][maske, :laeufe].mean()) for v in q["verfahren"]}
    budget = q["stufen"][stufe] * q["n"][maske]
    fertig = {v: float((q["erster_abstieg"][v][maske, :laeufe] <= budget[:, None]).mean()) for v in q["erster_abstieg"]}
    namen = [KURZ[v] for v in q["verfahren"]]
    return {"stufe": stufe, "familie": familie, "mittel": mittel, "ordnung": V.ordnung_text(namen, [mittel[v] for v in q["verfahren"]]),
            "faktor": V.gruppenfaktor(mittel), "fertig": fertig, "fertig_mittel": float(np.mean(list(fertig.values()))),
            "instanzen": int(maske.sum()), "laeufe": laeufe, "sieger": min(q["verfahren"], key=lambda v: (round(mittel[v], V.STELLEN), q["verfahren"].index(v)))}


def exp_quartett(q: dict, stufe: str, familie: str, laeufe: int) -> dict:
    stufen = list(q["stufen"])
    familien = ["alle"] + sorted(set(q["familie"]), key=q["familie"].index)
    raster = {(s, f): quartett_zelle(q, s, f, laeufe) for s in stufen for f in familien}
    werte = lambda z: [round(z["mittel"][v], V.STELLEN) for v in q["verfahren"]]   # noqa: E731
    tau_stufen = {(a, b): V.kendall_tau_b(werte(raster[(a, familie)]), werte(raster[(b, familie)])) for a in stufen for b in stufen}
    tau_familien = {(a, b): V.kendall_tau_b(werte(raster[(stufe, a)]), werte(raster[(stufe, b)])) for a in familien[1:] for b in familien[1:]}
    return {"zelle": raster[(stufe, familie)], "raster": raster, "stufen": stufen, "familien": familien, "tau_stufen": tau_stufen, "tau_familien": tau_familien,
            "ordnungen_stufen": [raster[(s, familie)]["ordnung"] for s in stufen], "ordnungen_familien": [raster[(stufe, f)]["ordnung"] for f in familien[1:]],
            "sieger_familien": {f: raster[(stufe, f)]["sieger"] for f in familien[1:]}}


def verdict_quartett(e: dict) -> tuple:
    z = e["zelle"]
    kopf = (f"Quartett, Budget {STUFE_TEXT[z['stufe']]} Auswertungen, {FAMILIE_TEXT[z['familie']]} ({z['instanzen']} Instanzen, {z['laeufe']} Läufe je Verfahren und Instanz, "
            f"Zählweise voll): mittlere Lücke HC {de(z['mittel']['hc'], 2)} %, SA {de(z['mittel']['sa'], 2)} %, ILS {de(z['mittel']['ils'], 2)} %, MA {de(z['mittel']['ma'], 2)} %. ")
    anteil = z["fertig_mittel"]
    if anteil < ABSTIEG_SCHWELLE:
        return "warning", (kopf + f"Nur **{pz(anteil)} %** der Läufe von HC, ILS und MA haben den ersten Abstieg beendet. Bis dahin tun diese drei Verfahren nach ihrer Bauart dasselbe "
                           "(Zufallstour, ein 2-opt-Abstieg); ihre Lücken sind hier **abgebrochene Abstiege und keine Güte der Verfahren**, deshalb nennt dieses Verdikt keine Rangfolge der drei.")
    verschiedene_stufen = len(set(e["ordnungen_stufen"]))
    verschiedene_familien = len(set(e["ordnungen_familien"]))
    sieger = sorted(set(KURZ[v] for v in e["sieger_familien"].values()))
    faktor = "unendlich (ILS und MA ohne Lücke)" if math.isinf(z["faktor"]) else de(z["faktor"], 2)
    text = (kopf + f"Rangfolge **{z['ordnung']}**, Gruppenfaktor {faktor}; {pz(anteil)} % der Läufe von HC, ILS und MA haben den ersten Abstieg beendet. "
            f"Über die {len(e['stufen'])} Budgets gibt es in dieser Auswahl {verschiedene_stufen} verschiedene Rangfolgen, über die {len(e['ordnungen_familien'])} Familien bei diesem Budget "
            f"{verschiedene_familien} (kleinste mittlere Lücke je Familie: {', '.join(sieger)}).")
    kippt = verschiedene_stufen > 1 or verschiedene_familien > 1
    if verschiedene_stufen > 1:
        text += (" Bei 30 · n und 100 · n liegen HC, ILS und MA in den Messungen der README (alle Familien) höchstens 0,5 bzw. 0,05 Punkte auseinander; "
                 "ihre Reihenfolge ist dort Rauschen der Läufe und zählt in dieser Zahl mit.")
    return ("warning" if kippt else "info"), text + (" Budget oder Familie kippen die Rangfolge des Quartetts." if kippt else " Hier kippt nichts.")


# ------------------------------------------------------------------------------------------------------------------------------
# Checkliste: Rechenbeispiel zur Zählweise (gesetzte Zahlen, keine Messung)
# ------------------------------------------------------------------------------------------------------------------------------
def zuege_voll(n: int) -> int:
    """Züge der 2-opt-Nachbarschaft: Kosten eines Schritts in der Zählweise voll."""
    return n * (n - 3) // 2


def zuege_warteschlange(n: int) -> int:
    """2-opt-Züge, die eine der beiden Tourkanten einer Stadt entfernen: Kosten eines Schritts mit der Warteschlange."""
    return 2 * (n - 3)


def gesetztes_modell(budget: int = 2_000_000) -> dict:
    """Gesetztes Rechenbeispiel (keine Messung): Lücke nach s Schritten = max(Boden, 50 · ρ^s); 2-opt ρ = 9/10, Boden 1; 3-opt ρ = 4/5, Boden 1/2.

    n = 100; Zugzahlen je Schritt: 2-opt 4.850 (voll) und 194 (Warteschlange), 3-opt 622.450 und 37.154. Rückgabe je Zählweise (Schritte, Lücken) für (2-opt, 3-opt)."""
    kosten = {"voll": (4850, 622450), "warteschlange": (194, 37154)}
    rho, boden = (Fraction(9, 10), Fraction(4, 5)), (Fraction(1), Fraction(1, 2))
    aus = {}
    for name, (k2, k3) in kosten.items():
        schritte = (budget // k2, budget // k3)
        aus[name] = {"schritte": schritte, "luecke": tuple(max(boden[i], Fraction(50) * rho[i] ** schritte[i]) for i in range(2)), "kosten": (k2, k3)}
    return aus


def verdict_nfl(klasse: str, m: int, vert_a: dict, vert_b: dict) -> tuple:
    zahl = sum(vert_a.values())
    if vert_a == vert_b:
        return "info", (f"Nach {m} Auswertungen haben A und B dieselbe Verteilung des besten Werts über die {zahl} Funktionen dieser Klasse "
                        f"(Minimum 0 in {vert_a[0]} von {zahl}). Auf dieser Klasse ist keines der zwei Verfahren im Mittel besser.")
    return "warning", (f"Nach {m} Auswertungen findet A das Minimum 0 in {vert_a[0]}, B in {vert_b[0]} von {zahl} Funktionen dieser Klasse: die Verfahren unterscheiden sich, "
                       "sobald man Annahmen über die Klasse macht. Die Aussage gilt für diese Klasse; Rundtouren sind keine solche Klasse.")


def verdict_woran(mass: dict, einstellung: dict, kippen_budget: dict, uebersicht: dict, budget: int) -> tuple:
    """Kernfrage 2: woran hängt die Rangfolge des Trios außer am Würfeln? Je Achse der Anteil der Instanzen mit anderer Rangfolge."""
    a_mass = max(mass["anders"][("mittel", m)] for m in V.MASSE if m != "mittel")
    a_einst = next(x for x in einstellung["zeilen"] if x["budget"] == budget)["anders"]
    a_budget = max(kippen_budget.values())
    achsen = [("Maß (Mittel gegen das am weitesten entfernte Maß)", a_mass), ("Einstellung von Simulated Annealing", a_einst), ("Budget (größter Wert über die Budgetpaare)", a_budget)]
    teile = "; ".join(f"{name}: {pz(wert)} % ({lesehilfe(wert)})" for name, wert in achsen)
    familie = (f"die Ordnung der Familienmittel ist in allen {uebersicht['zellen']} Zellen dieselbe" if len(uebersicht["verschiedene"]) == 1
               else f"die Ordnung der Familienmittel nimmt {len(uebersicht['verschiedene'])} verschiedene Formen an")
    instabil = sum(1 for _, wert in achsen if wert > LESEHILFE[1])
    text = (f"Anteil der {mass['instanzen']} Instanzen mit anderer Rangfolge des Trios bei {tsd(budget)} Auswertungen (Maß Mittel, 60 Läufe je Instanz, wo nichts anderes steht). "
            f"{teile}. Familie: {familie}. Die Lesehilfe (unter 10 % stabil, bis 30 % gemischt, darüber instabil) ist vorab festgelegt und keine Prüfgröße.")
    return ("warning" if instabil else "info"), text


def verdict_live(gleich: int, gesamt: int, dauer: float, budget: int) -> tuple:
    """Live-Nachrechnung: wie viele der neu gerechneten Läufe stimmen mit den eingefrorenen Längen überein?"""
    kopf = f"{gleich} von {gesamt} neu gerechneten Läufen haben bei {tsd(budget)} Auswertungen dieselbe Länge wie in der eingefrorenen Messreihe (Rechenzeit {de(dauer, 1)} s)."
    if gleich == gesamt:
        return "success", kopf + " Die Messreihe lässt sich aus den Zufalls-Seeds nachrechnen."
    return "warning", kopf + " Abweichungen können an der letzten Binärstelle der Exponentialfunktion einer anderen Plattform liegen (Simulated Annealing); die Aussagen der Seite hängen nicht an einzelnen Läufen."
