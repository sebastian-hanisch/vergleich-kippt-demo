"""Ehrlicher Vergleich: wann kippt die Rangfolge? - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Achtes Stück der Reihe „Landschaften, Einstellung und Vergleich“: Was steht hinter „Verfahren A ist besser als B“? Die Demo rechnet
auf eingefrorenen Läufen (data/, erzeugt von tools/vgk_make_daten.py) und zeigt, wie Läufezahl, Maß, Test, Einstellung, Budget und
Familie eine Rangfolge von Suchverfahren ändern.

Lauffähig mit: streamlit run app.py
"""

import time

import pandas as pd
import streamlit as st

import vgk_compare as V
import vgk_constants as C
import vgk_daten as D
import vgk_evaluation as ev
import vgk_layout as L
import vgk_messung as MS
import vgk_nfl as N
import vgk_presets as P
import vgk_rangtest as R
import vgk_texts as T
import vgk_visualization as viz

import modul_frisch

modul_frisch.aktualisieren(__file__)

st.set_page_config(page_title="Ehrlicher Vergleich – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _uebersicht(sa):
    return ev.trio_uebersicht(D.trio(), sa), ev.budget_kippen(D.trio(), sa)


@st.cache_data(show_spinner=False)
def _gruppen(budget, r, paar, sa):
    return ev.exp_gruppen(D.trio(), budget, r, paar, sa)


@st.cache_data(show_spinner=False)
def _mass(budget, sa):
    return ev.exp_mass(D.trio(), budget, sa)


@st.cache_data(show_spinner=False)
def _null(verfahren, budget, m, r, seed):
    return ev.exp_null(D.trio(), D.nulltest(), verfahren, budget, m, r, seed)


@st.cache_data(show_spinner=False)
def _modell(r, m):
    return [{"q": q, "mindestens": R.mindestens_eine(R.verwerfung_modell(q, r), m)} for q in ev.MODELL_Q]


@st.cache_data(show_spinner=False)
def _einstellung():
    return ev.exp_einstellung(D.trio())


@st.cache_data(show_spinner=False)
def _quartett(stufe, familie, laeufe):
    return ev.exp_quartett(D.quartett(), stufe, familie, laeufe)


@st.cache_data(show_spinner=False)
def _live(budget, sa):
    """Rechnet die ersten Läufe der Live-Instanz neu und vergleicht sie mit den eingefrorenen Werten."""
    f, n, idx = C.LIVE_INSTANZ
    trio = D.trio()
    zeile = next(k for k in range(len(trio["n"])) if trio["familie"][k] == f and trio["n"][k] == n)
    start = time.perf_counter()
    zeilen, gleich, gesamt = [], 0, 0
    for v in ("hc", sa, "ga"):
        neu = [round(MS.trio_lauf(f, n, idx, v, lauf)[budget][0], 3) for lauf in range(C.LIVE_LAEUFE)]
        alt = [float(x) for x in trio["laengen"][v][budget][zeile, : C.LIVE_LAEUFE]]
        gleich += sum(abs(a - b) <= 1e-9 * max(1.0, abs(b)) for a, b in zip(neu, alt))
        gesamt += len(neu)
        luecke = [100.0 * (x - trio["referenz"][zeile]) / trio["referenz"][zeile] for x in neu]
        zeilen.append({"Verfahren": ev.KURZ[v], "mittlere Lücke der 10 Läufe (%)": ev.de(sum(luecke) / len(luecke), 2), "kleinste Lücke (%)": ev.de(min(luecke), 2)})
    return zeilen, gleich, gesamt, time.perf_counter() - start


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in vgk_layout.py).
st.html(L.kopf_css(L.dunkles_design()))
with st.container(key="kopf"):
    st.title("⚖️ Ehrlicher Vergleich: wann kippt die Rangfolge?")
st.markdown(
    """
**„Verfahren A ist besser als B“** steht nie allein in einer Rangfolge, sondern in einem Satz mit **Läufezahl, Maß, Test, Einstellung, Budget, Familie und Zählweise**.
Diese Demo vergleicht eigene Umsetzungen von Suchverfahren auf erfundenen Lieferrouten (Rundtour, euklidisch, 2-opt) und misst, wie oft dieselbe Rangfolge
herauskommt, wenn man nur neu würfelt, das Maß wechselt, die Einstellung ändert oder dasselbe Verfahren gegen sich selbst testet.
Sie ist das achte Stück der Reihe „Landschaften, Einstellung und Vergleich“ und hebt eine Annahme der Stücke über das Auswählen und das Einstellen von Verfahren auf:
dass „A liegt vor B“ nach einer Messung eine Eigenschaft der Verfahren sei. Nichts davon ist neu; neu ist nur, dass es sich hier mit Zähleinheiten nachrechnen lässt.

Weiter unten: fünf Abschnitte **🔬 Experiment**, **🚧 Wo die Annahmen enden** und die Expander **Was in der Aussage stehen muss**, **No-Free-Lunch im Kleinen** und **📐 Mathematische Formulierung**.
"""
)


with st.expander("So funktioniert ein ehrlicher Vergleich", expanded=True):
    st.markdown(
        """
1. **Läufegruppe:** Jedes Verfahren läuft auf jeder Instanz mehrmals mit getrennten Zufalls-Seeds. Die **Lücke** eines Laufs ist (Länge − beste bekannte Länge) / beste bekannte Länge in Prozent; die beste bekannte Länge ist nicht als optimal bewiesen.
2. **Maß und Rangfolge:** Ein Maß macht aus den Lücken einer Gruppe eine Zahl; die Rangfolge ordnet die Verfahren danach. Gleichstände bekommen mittlere Ränge.
3. **Kippen:** Zwei Bedingungen (zwei Läufegruppen, zwei Maße, zwei Einstellungen, zwei Budgets) kippen die Rangfolge einer Instanz, wenn ihre Rangvektoren verschieden sind. Gezählt wird immer mit Einheit: Anteil der Instanzen oder Anteil der Gruppenpaare je Instanz.
4. **Warum das zählt:** Eine Rangfolge aus wenigen Läufen ist zum Teil Rauschen. Wer viele Instanzen einzeln testet, findet auch zwischen zwei Gruppen desselben Verfahrens „signifikante“ Unterschiede.
        """
    )
    st.markdown("**Die Verfahren (Erklärtabelle)**")
    st.markdown(T.VERFAHREN_TABELLE)
    st.markdown("**Die Maße**")
    st.markdown(T.MASS_TABELLE)

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

P.load_permalink_settings()
P.init_session_state_defaults()

with st.sidebar:
    P.sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Trio: HC, SA, GA")
    budget = st.select_slider("Budget (Auswertungen)", options=list(C.TRIO_BUDGETS), key="budget_select", format_func=ev.tsd,
                              help="Budget der Läufe in den Experimenten 1 bis 4.")
    sa = st.selectbox("Einstellung von Simulated Annealing", C.SA_WAHL, key="sa_select", format_func=lambda k: ev.SA_TEXT[k],
                      help="Welche Einstellung in den Experimenten 1 bis 3 als „SA“ antritt. Experiment 4 zeigt immer beide.")
    st.markdown("**Experiment 1: Läufegruppen**")
    gruppe = st.select_slider("Läufe je Gruppe", options=list(C.GRUPPEN_R), key="gruppe_select",
                              help="Die 60 Läufe je Instanz werden in getrennte Gruppen dieser Größe geteilt.")
    paar = st.selectbox("Verglichene Verfahren", C.PAARE, key="paar_select", format_func=lambda k: ev.PAAR_TEXT[k],
                        help="Für ein Paar zeigt das Experiment zusätzlich die strikte Zählung und die Kippformel.")
    st.markdown("**Experiment 2: Maß**")
    mass = st.selectbox("Maß gegen das Mittel", C.MASSE_WAHL, key="mass_select", format_func=lambda k: V.MASS_TEXT[k],
                        help="Das Maß, dessen Rangfolge mit der des Mittels verglichen wird.")
    st.markdown("**Experiment 3: Mehrfachtest**")
    null_verfahren = st.selectbox("Verfahren gegen sich selbst", C.NULL_VERFAHREN, key="null_verfahren_select", format_func=lambda k: ev.KURZ[k],
                                  help="Beide Gruppen stammen aus den Läufen dieses einen Verfahrens.")
    m = st.slider("Zahl der Tests (Instanzen)", C.M_MIN, C.M_MAX, key="m_slider", help="Je Instanz ein Test; getestet werden die ersten m Instanzen der Messreihe.")
    null_gruppe = st.select_slider("Läufe je Gruppe im Test", options=list(C.NULL_GRUPPEN), key="null_gruppe_select",
                                   help="Zwei Gruppen dieser Größe werden ohne Zurücklegen aus den 60 Läufen der Instanz gezogen.")
    seed = st.number_input("Zufalls-Seed der Ziehungen", 0, C.SEED_MAX, key="seed_input", step=1)
    st.button("🎲 Neue Ziehungen", width="stretch", on_click=P.randomize_seed)
    st.header("⚙️ Quartett: HC, SA, ILS, MA")
    q_budget = st.select_slider("Budget", options=list(C.QUARTETT_STUFEN), key="q_budget_select", format_func=lambda k: ev.STUFE_TEXT[k],
                                help="Budget als Vielfaches der Ortszahl n.")
    q_familie = st.selectbox("Familie", C.Q_FAMILIEN, key="q_familie_select", format_func=lambda k: ev.FAMILIE_TEXT[k])
    q_laeufe = st.select_slider("Läufe je Verfahren und Instanz", options=list(C.Q_LAEUFE), key="q_laeufe_select",
                                help="Die ersten k der 12 eingefrorenen Läufe gehen in die Mittel ein.")

P.sync_query_params({"budget_select": int(budget), "sa_select": sa, "gruppe_select": int(gruppe), "paar_select": paar, "mass_select": mass,
                     "null_verfahren_select": null_verfahren, "m_slider": int(m), "null_gruppe_select": int(null_gruppe), "seed_input": int(seed),
                     "q_budget_select": q_budget, "q_familie_select": q_familie, "q_laeufe_select": int(q_laeufe)})

budget, gruppe, m, null_gruppe, seed, q_laeufe = int(budget), int(gruppe), int(m), int(null_gruppe), int(seed), int(q_laeufe)
null_schluessel = sa if null_verfahren == "sa" else null_verfahren
uebersicht, kippen_budget = _uebersicht(sa)
e_gruppen = _gruppen(budget, gruppe, paar, sa)
e_mass = _mass(budget, sa)
e_null = _null(null_schluessel, budget, m, null_gruppe, seed)
e_einst = _einstellung()
e_quartett = _quartett(q_budget, q_familie, q_laeufe)

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis: das Trio über Budgets und Familien")
st.caption(f"63 erfundene Instanzen (je 21 gleichverteilt, geclustert, Gitter mit Rauschen; 20 bis 40 Orte), 60 Läufe je Verfahren und Instanz; "
           f"Simulated Annealing in der Einstellung „{ev.SA_TEXT[sa]}“.")
spalten = st.columns(len(uebersicht["zeilen"]))
for spalte, z in zip(spalten, uebersicht["zeilen"]):
    spalte.metric(f"Ordnung bei {ev.tsd(z['budget'])} Auswertungen", z["ordnung"],
                  delta=" · ".join(f"{name} vorn auf {zahl}" for name, zahl in z["vorn"].items()) + f" von {z['instanzen']} Instanzen", delta_color="off")
st.plotly_chart(viz.build_trio(uebersicht), width="stretch", key="trio_chart")
st.caption("Mittlere Lücke über alle Instanzen und Läufe (logarithmische Achse). „Vorn“ zählt Instanzen, auf denen ein Verfahren allein die kleinste mittlere Lücke hat.")
art, text = ev.verdict_trio(uebersicht, kippen_budget)
getattr(st, art)(text)

with st.expander("Eine Instanz live nachrechnen (10 Läufe je Verfahren)"):
    st.markdown(f"Rechnet auf der Instanz „gleichverteilt, {C.LIVE_INSTANZ[1]} Orte“ die ersten {C.LIVE_LAEUFE} Läufe von HC, SA und GA mit denselben Zufalls-Seeds neu "
                "und vergleicht sie mit den eingefrorenen Werten.")
    if st.button("▶ Nachrechnen", key="live_button"):
        with st.spinner("Rechne 30 Läufe neu (etwa 2 bis 6 Sekunden) …"):
            zeilen, gleich, gesamt, dauer = _live(budget, sa)
        st.dataframe(pd.DataFrame(zeilen), hide_index=True, width="stretch")
        art, text = ev.verdict_live(gleich, gesamt, dauer, budget)
        getattr(st, art)(text)

# --- Kernfragen ----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfragen")
st.info(T.VORAUSSETZUNG)
st.markdown("**1. Wie oft ändert sich die Rangfolge, wenn man nur neu würfelt?**")
art, text = ev.verdict_gruppen(e_gruppen)
getattr(st, art)(text)
st.markdown("**2. Woran hängt sie sonst (Maß, Einstellung, Budget und Familie)?**")
art, text = ev.verdict_woran(e_mass, e_einst, kippen_budget, uebersicht, budget)
getattr(st, art)(text)
st.markdown("**3. Wie oft „findet“ man einen Unterschied, den es nicht gibt?**")
art, text = ev.verdict_null(e_null)
getattr(st, art)(text)

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Läufegruppen. Wie oft kippt die Ordnung nur durch Würfeln?")
st.caption(f"Die 60 Läufe je Instanz werden in getrennte Gruppen geteilt; jedes Paar von Gruppen wird verglichen (Maß Mittel, {ev.tsd(budget)} Auswertungen). "
           "„Verschieden“ zählt auch Paare, in denen nur eine Gruppe einen Gleichstand zeigt; „strikt entgegengesetzt“ zählt nur Paare, in denen jede Gruppe ein anderes Verfahren vorn sieht.")
links, rechts = st.columns(2)
links.plotly_chart(viz.build_gruppen_kurve(e_gruppen), width="stretch", key="gruppen_kurve")
rechts.plotly_chart(viz.build_gruppen_instanzen(e_gruppen), width="stretch", key="gruppen_instanzen")
st.dataframe(pd.DataFrame([{
    "Läufe je Gruppe": p["r"], "Gruppen": p["gruppen"], "Gruppenpaare": p["paare"], "verschieden (%)": ev.pz(p["verschieden"], 1),
    "strikt entgegengesetzt (%)": ev.pz(p["strikt"], 1) if "strikt" in p else "–", "Formel (%)": ev.pz(p["formel"], 1) if "formel" in p else "–",
    "Gruppen mit Gleichstand (%)": ev.pz(p["gleichstand"], 1), "Instanzen mit mind. einem abweichenden Paar (%)": ev.pz(p["mit_abweichung"])} for p in e_gruppen["kurve"]]),
    hide_index=True, width="stretch")
if paar == "alle":
    st.caption("Die Kippformel gilt für ein Paar von Verfahren; für die Ordnung des Trios gibt es keine Formelspalte. Bei 30 Läufen je Gruppe gibt es nur ein Gruppenpaar je Instanz.")
else:
    st.caption("Formel: 2Φ(d)(1 − Φ(d)) mit d = |δ|·√r / √(s₁² + s₂²), je Instanz aus den 60 Läufen geschätzt und gemittelt. Bei 30 Läufen je Gruppe gibt es nur ein Gruppenpaar je Instanz.")
art, text = ev.verdict_gruppen(e_gruppen)
getattr(st, art)(text)

st.markdown("---")
st.subheader("🔬 Experiment 2: Das Maß")
st.caption(f"Rangfolge von HC, SA und GA je Instanz aus allen 60 Läufen, je Maß ({ev.tsd(budget)} Auswertungen). Die Matrix zeigt den Anteil der Instanzen, "
           "auf denen zwei Maße verschiedene Rangfolgen geben.")
st.plotly_chart(viz.build_mass_matrix(e_mass), width="stretch", key="mass_matrix")
links, rechts = st.columns(2)
with links:
    st.dataframe(pd.DataFrame([{
        "Maß": V.MASS_TEXT[z["mass"]], "HC": ev.de(z["mittel"]["HC"], 2), "SA": ev.de(z["mittel"]["SA"], 2), "GA": ev.de(z["mittel"]["GA"], 2),
        "Ordnung nach mittlerem Rang": z["ordnung"], "Instanzen, alle drei gleichauf": z["alle_gleichauf"]} for z in e_mass["tabelle"]]), hide_index=True, width="stretch")
    st.caption("Werte: Mittel des Maßes über die Instanzen (Lücken in %, Anteil als Bruchteil der Läufe).")
with rechts:
    st.markdown("**Handbeispiel (gesetzte Zahlen):** fünf Läufe, Lücken A = (2, 2, 2, 2, 12), B = (3, 3, 3, 3, 3).")
    st.dataframe(pd.DataFrame([{"Maß": V.MASS_TEXT[z["mass"]], "A": ev.de(z["A"], 1), "B": ev.de(z["B"], 1), "besser": z["besser"]} for z in ev.mass_beispiel()]),
                 hide_index=True, width="stretch")
    st.caption("Ein einziger Lauf (12) entscheidet das Mittel; nach den drei anderen Maßen ist A besser.")
art, text = ev.verdict_mass(e_mass, mass)
getattr(st, art)(text)

st.markdown("---")
st.subheader("🔬 Experiment 3: Mehrfachtest, dasselbe Verfahren gegen sich selbst")
st.caption("Je Instanz zwei Gruppen aus den 60 Läufen desselben Verfahrens (ohne Zurücklegen), Mann-Whitney-U zweiseitig als Normalnäherung mit Stetigkeits- und "
           "Gleichstandskorrektur, Niveau 0,05; 100 Wiederholungen. Es gibt hier keinen wahren Unterschied: jede Verwerfung ist ein Fehlalarm.")
links, rechts = st.columns(2)
links.plotly_chart(viz.build_null(e_null), width="stretch", key="null_chart")
rechts.plotly_chart(viz.build_modell(_modell(null_gruppe, m), m, null_gruppe), width="stretch", key="modell_chart")
st.plotly_chart(viz.build_haeufigster(e_null), width="stretch", key="haeufigster_chart")
st.caption("Unten: je getesteter Instanz der Anteil des häufigsten Werts unter den 60 Läufen. Rechts oben das Modell „jeder Lauf trifft mit Wahrscheinlichkeit q denselben Bestwert“ "
           "(exakt gerechnet). Holm und Benjamini-Hochberg zeigt die Demo „Mehrfachtests und Gewinnerfluch“; hier steht nur die Zeile mit Bonferroni.")
art, text = ev.verdict_null(e_null)
getattr(st, art)(text)

st.markdown("---")
st.subheader("🔬 Experiment 4: Die Einstellung")
ein = e_einst["einstellungen"]
st.caption(f"Simulated Annealing in zwei Einstellungen: Standard (Starttemperatur {ev.de(ein['sa_std'][0], 1)} · Skala, Abkühlung um {ev.de(ein['sa_std'][1], 1)} Zehnerpotenzen) und "
           f"abgestimmt ({ev.de(ein['sa_abg'][0], 1)} · Skala, {ev.de(ein['sa_abg'][1], 1)} Zehnerpotenzen; beste von 20 Einstellungen auf 15 Instanzen, die nicht zur Messung gehören). "
           "HC und GA bleiben, wie sie sind.")
links, rechts = st.columns(2)
links.plotly_chart(viz.build_einstellung(e_einst), width="stretch", key="einstellung_chart")
rechts.dataframe(pd.DataFrame([{
    "Budget": ev.tsd(z["budget"]), "SA Standard (%)": ev.de(z["sa_std"]["mittel"]["SA"], 2), "SA abgestimmt (%)": ev.de(z["sa_abg"]["mittel"]["SA"], 2),
    "HC (%)": ev.de(z["sa_std"]["mittel"]["HC"], 2), "GA (%)": ev.de(z["sa_std"]["mittel"]["GA"], 2),
    "SA vor HC: Standard / abgestimmt (Instanzen)": f"{z['sa_vor_hc']['sa_std']} / {z['sa_vor_hc']['sa_abg']}"} for z in e_einst["zeilen"]]), hide_index=True, width="stretch")
rechts.caption("Mittlere Lücke über 63 Instanzen und 60 Läufe. Was beim Einstellen selbst zu beachten ist, zeigt die Demo „Einstellen lohnt“ dieser Reihe; hier ist die Einstellung Teil der Aussage.")
art, text = ev.verdict_einstellung(e_einst, budget)
getattr(st, art)(text)

st.markdown("---")
st.subheader("🔬 Experiment 5: Budget und Familie am Quartett")
st.caption("56 erfundene Instanzen (vier Familien, 20 bis 80 Orte), 12 Läufe je Verfahren; Budget als Vielfaches der Ortszahl n. Simulated Annealing ist je Budget "
           "auf Instanzen abgestimmt, die nicht zur Messung gehören; der memetische Algorithmus hat die Populationsgröße 4. Gruppenfaktor = kleinere der mittleren Lücken von HC und SA "
           "geteilt durch die größere von ILS und MA.")
links, rechts = st.columns(2)
links.plotly_chart(viz.build_quartett(e_quartett, q_familie), width="stretch", key="quartett_chart")
rechts.dataframe(pd.DataFrame([{
    "Budget": ev.STUFE_TEXT[s], "Rangfolge der mittleren Lücke": e_quartett["raster"][(s, q_familie)]["ordnung"],
    "Gruppenfaktor": ev.de(e_quartett["raster"][(s, q_familie)]["faktor"], 2),
    "erster Abstieg beendet (%)": ev.pz(e_quartett["raster"][(s, q_familie)]["fertig_mittel"])} for s in e_quartett["stufen"]]), hide_index=True, width="stretch")
rechts.dataframe(pd.DataFrame([{
    "Familie": ev.FAMILIE_TEXT[f], "Rangfolge bei " + ev.STUFE_TEXT[q_budget]: e_quartett["raster"][(q_budget, f)]["ordnung"],
    "kleinste Lücke": ev.KURZ[e_quartett["raster"][(q_budget, f)]["sieger"]]} for f in e_quartett["familien"]]), hide_index=True, width="stretch")
rechts.caption("Oben: die gewählte Familie über die Budgets. Unten: das gewählte Budget über die Familien. „Erster Abstieg beendet“: Anteil der Läufe von HC, ILS und MA.")
art, text = ev.verdict_quartett(e_quartett)
getattr(st, art)(text)

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(T.ANNAHMEN)

st.markdown("---")

with st.expander("Was in der Aussage stehen muss (Checkliste, mit zitierten Zahlen zur Zählweise)"):
    st.markdown(T.CHECKLISTE)
    modell = ev.gesetztes_modell()
    st.markdown("**Rechenbeispiel zur Zählweise (gesetzte Zahlen, keine Messung).** 2-opt hat je Schritt n(n − 3)/2 Züge in der Zählweise voll und 2(n − 3) Züge je Stadt mit der "
                "Warteschlange; das Verhältnis ist n/4. Gesetztes Modell bei n = 100 und 2.000.000 Auswertungen: Lücke nach s Schritten = max(Boden, 50 · ρˢ), "
                "2-opt mit ρ = 9/10 und Boden 1, 3-opt mit ρ = 4/5 und Boden 1/2.")
    st.dataframe(pd.DataFrame([{
        "Zählweise": name, "Kosten je Schritt 2-opt / 3-opt": f"{ev.tsd(z['kosten'][0])} / {ev.tsd(z['kosten'][1])}",
        "Schritte im Budget 2-opt / 3-opt": f"{ev.tsd(z['schritte'][0])} / {ev.tsd(z['schritte'][1])}",
        "Lücke im Modell 2-opt / 3-opt (%)": f"{ev.de(float(z['luecke'][0]), 1)} / {ev.de(float(z['luecke'][1]), 1)}",
        "besser im Modell": "2-opt" if z["luecke"][0] < z["luecke"][1] else "3-opt"} for name, z in (("voll", modell["voll"]), ("Warteschlange", modell["warteschlange"]))]),
        hide_index=True, width="stretch")
    st.caption("Im gesetzten Modell dreht allein die Zählweise die Rangfolge um. Die Messung dazu steht in der zitierten Demo, nicht hier.")

with st.expander("No-Free-Lunch im Kleinen (alle 81 Funktionen aufgezählt)"):
    st.markdown("Suchraum {0, 1, 2, 3}, Werte {0, 1, 2} (kleiner ist besser), alle 3⁴ = 81 Funktionen. **Verfahren A** tastet von links nach rechts ab. **Verfahren B** beginnt bei Punkt 3, "
                "geht bei Wert 0 zum Punkt 2, sonst zum Punkt 0, danach zum kleinsten noch nicht besuchten Punkt. Der Satz von Wolpert und Macready (1997) sagt: gemittelt über **alle** "
                "Funktionen leisten je zwei Verfahren dasselbe. Er dient hier als Rahmen (ohne Annahmen über die Klasse keine Vorhersage), nicht als Erklärung für die Messungen oben.")
    nfl_klasse = st.selectbox("Klasse der Funktionen", N.KLASSEN, key="nfl_klasse", format_func=lambda k: N.KLASSEN_TEXT[k])
    nfl_m = st.slider("Auswertungen m", 1, 4, 2, key="nfl_m")
    vert_a, vert_b = N.verteilung_minimum("A", nfl_klasse, nfl_m), N.verteilung_minimum("B", nfl_klasse, nfl_m)
    st.dataframe(pd.DataFrame([{"bester Wert nach m Auswertungen": w, "Verfahren A (Funktionen)": vert_a[w], "Verfahren B (Funktionen)": vert_b[w]} for w in N.WERTE]),
                 hide_index=True, width="stretch")
    art, text = ev.verdict_nfl(nfl_klasse, nfl_m, vert_a, vert_b)
    getattr(st, art)(text)
    st.caption(f"Die Klasse hat {len(N.klasse(nfl_klasse))} Funktionen; durch Vertauschen der Punkte entstehen daraus {N.abschluss_unter_permutation(nfl_klasse)}. "
               "Dass der Satz genau für Klassen gilt, die unter solchen Vertauschungen abgeschlossen sind, stammt aus Sekundärquellen (nicht gelesen).")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben und gesucht.** Gegeben sind Verfahren $v = 1, \dots, k$, Instanzen $i$ und je Verfahren und Instanz Läufe mit Tourlängen $L_{v,i,1}, \dots, L_{v,i,r}$ nach einem Budget von $B$ Auswertungen. Gesucht ist keine beste Tour, sondern die Antwort auf die Frage, wie fest die Rangfolge der Verfahren ist.

| Symbol | Bedeutung |
|---|---|
| $L^{*}_i$ | beste bekannte Länge der Instanz $i$ (nicht als optimal bewiesen) |
| $g$ | Lücke eines Laufs in Prozent |
| $r$ | Läufe je Gruppe |
| $m$ | Zahl der Tests (Instanzen) |
| $U$ | Statistik des Rangtests: Paare (x, y) mit x größer als y, Gleichstände halb |
| $t_j$ | Größe der j-ten Gruppe gleicher Werte unter den $2r$ Werten eines Tests |
| $\delta, s_1, s_2$ | Unterschied der mittleren Lücken zweier Verfahren und die Standardabweichungen ihrer Läufe |
| $\Phi$ | Verteilungsfunktion der Standardnormalverteilung |

**Lücke.**

$$g_{v,i,l} = 100 \cdot \frac{L_{v,i,l} - L^{*}_i}{L^{*}_i}$$

**Maße einer Läufegruppe** (kleiner ist besser, außer beim Anteil): Mittel, Median, Minimum, Anteil der Läufe mit $g \le 2$, und die Fläche als Mittel der bis dahin besten Lücke über 20 Prüfpunkte.

**Kippen.** Zwei Bedingungen $a$, $b$ geben auf einer Instanz Rangvektoren $R^{a}$, $R^{b}$ (mittlere Ränge bei Gleichstand). Die Instanz kippt, wenn $R^{a} \ne R^{b}$. Für ein Paar von Verfahren heißt die Ordnung **strikt entgegengesetzt**, wenn $a$ das eine und $b$ das andere Verfahren vorn sieht.

**Kendall** $\tau_b$ zweier Rangvektoren, mit $C$ gleich geordneten, $D$ entgegengesetzt geordneten Paaren und $T_a$, $T_b$ Paaren mit Gleichstand nur in $a$ bzw. nur in $b$:

$$\tau_b = \frac{C - D}{\sqrt{(C + D + T_a)(C + D + T_b)}}$$

**Kippformel** (Normalannahme, ein Paar von Verfahren, zwei unabhängige Gruppen zu $r$ Läufen, strikte Zählung):

$$P(\text{kippen}) = 2\,\Phi(d)\,\bigl(1 - \Phi(d)\bigr), \qquad d = \frac{|\delta|\,\sqrt{r}}{\sqrt{s_1^2 + s_2^2}}$$

**Rangtest** (Mann-Whitney-U, zweiseitig, Normalnäherung mit Stetigkeits- und Gleichstandskorrektur, zwei Gruppen zu $r$ Läufen):

$$\sigma_U^2 = \frac{r^2}{12}\left((2r + 1) - \frac{\sum_j (t_j^3 - t_j)}{2r\,(2r - 1)}\right)$$

$$z = \frac{\max(U,\; r^2 - U) - r^2/2 - 1/2}{\sigma_U}, \qquad p = 2\,\bigl(1 - \Phi(z)\bigr)$$

Der Test verwirft bei $p < 0{,}05$; sind alle Werte gleich, ist $p = 1$. Mit **Bonferroni** verwirft er bei $p < 0{,}05/m$.

**Mehrfachtest.** Verwirft jeder von $m$ unabhängigen Tests mit Wahrscheinlichkeit $p_i$, obwohl es keinen Unterschied gibt, dann ist

$$P(\text{mindestens eine Verwerfung}) = 1 - \prod_{i=1}^{m} (1 - p_i)$$

Ohne Gleichstände ist $p_i$ für alle Instanzen gleich und folgt exakt aus der Verteilung von $U$ (bei 10 gegen 10 Läufen 4,326 %, nicht 5 %: die Verteilung von $U$ ist diskret, der Test schöpft die Schwelle nicht aus).

**Zählweise voll.** Jede Bewertung eines Zugs zählt 1, jede Bewertung einer vollständigen Tour zählt 1; die 2-opt-Nachbarschaft hat $n(n-3)/2$ Züge.

Das ist kein Optimierungsmodell, sondern die Liste der Rechenregeln dieser Seite; die Verfahren selbst stehen in der Erklärtabelle oben.

**Literatur.** D. H. Wolpert, W. G. Macready, „No Free Lunch Theorems for Optimization“, IEEE Transactions on Evolutionary Computation 1(1), 1997, 67–82 (gelesen: Abstract und Einleitung). Die Präzisierung auf unter Permutation abgeschlossene Funktionsmengen (Igel und Toussaint 2003) ist nicht gelesen.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
