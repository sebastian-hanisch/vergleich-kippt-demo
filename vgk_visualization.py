"""Plotly-Figuren (alle Achsen fest, damit Touch-Scrollen nicht am Diagramm hängen bleibt)."""

import plotly.graph_objects as go

import vgk_compare as V
import vgk_evaluation as ev

FARBE = {"HC": "#2F6B65", "SA": "#c0504d", "GA": "#8064a2", "ILS": "#4c78a8", "MA": "#d98e04"}
MASS_KURZ = {"mittel": "Mittel", "median": "Median", "bestes": "Bestes", "anteil": "Anteil ≤ 2 %", "flaeche": "Fläche"}
GRAU = "rgba(120,120,120,0.75)"
BLAU = "#4c78a8"
ROT = "#c0504d"
GRUEN = "#2F6B65"


def _fest(fig, hoehe=360, **layout):
    fig.update_layout(height=hoehe, margin=dict(l=10, r=10, t=50, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), **layout)
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def build_trio(u: dict):
    """Mittlere Lücke je Verfahren und Budget."""
    fig = go.Figure()
    budgets = [ev.tsd(z["budget"]) for z in u["zeilen"]]
    for name in u["zeilen"][0]["mittel"]:
        werte = [z["mittel"][name] for z in u["zeilen"]]
        fig.add_bar(name=name, x=budgets, y=werte, marker_color=FARBE[name], text=[ev.de(w, 2) for w in werte], textposition="outside")
    fig.update_yaxes(title="mittlere Lücke in %", type="log")
    fig.update_xaxes(title="Budget (Auswertungen)", type="category")
    return _fest(fig, barmode="group")


def build_gruppen_kurve(e: dict):
    """Anteil der Gruppenpaare mit verschiedener Ordnung über die Gruppengröße; beim Paar zusätzlich strikt und Formel."""
    fig = go.Figure()
    r = [p["r"] for p in e["kurve"]]
    fig.add_scatter(x=r, y=[100 * p["verschieden"] for p in e["kurve"]], mode="lines+markers", name="gemessen: verschieden", line=dict(color=ROT))
    if "strikt" in e["kurve"][0]:
        fig.add_scatter(x=r, y=[100 * p["strikt"] for p in e["kurve"]], mode="lines+markers", name="gemessen: strikt entgegengesetzt", line=dict(color=BLAU))
        fig.add_scatter(x=r, y=[100 * p["formel"] for p in e["kurve"]], mode="lines+markers", name="Formel 2Φ(d)(1 − Φ(d))", line=dict(color=GRAU, dash="dash"))
    g = e["gewaehlt"]
    fig.add_scatter(x=[g["r"]], y=[100 * g["verschieden"]], mode="markers", name="gewählte Gruppengröße", marker=dict(size=14, color=ROT, symbol="circle-open", line=dict(width=3)))
    fig.update_xaxes(title="Läufe je Gruppe", type="category")
    fig.update_yaxes(title="Gruppenpaare (%)", range=[0, 100])
    return _fest(fig)


def build_gruppen_instanzen(e: dict):
    """Je Instanz der Anteil der Gruppenpaare mit verschiedener Ordnung, aufsteigend sortiert."""
    werte = sorted(100 * float(x) for x in e["je_instanz"])
    fig = go.Figure(go.Bar(x=list(range(1, len(werte) + 1)), y=werte, marker_color=ROT))
    fig.update_xaxes(title="Instanzen, aufsteigend sortiert")
    fig.update_yaxes(title="Gruppenpaare anders (%)", range=[0, 100])
    return _fest(fig, hoehe=300)


def build_mass_matrix(e: dict):
    """Anteil der Instanzen mit verschiedener Rangfolge zwischen je zwei Maßen."""
    namen = [MASS_KURZ[m] for m in V.MASSE]
    z = [[100 * e["anders"][(a, b)] for b in V.MASSE] for a in V.MASSE]
    fig = go.Figure(go.Heatmap(z=z, x=namen, y=namen, zmin=0, zmax=100, colorscale="Reds", colorbar=dict(title=dict(text="%", side="top"), nticks=4)))
    for i, a in enumerate(V.MASSE):
        for j, b in enumerate(V.MASSE):
            fig.add_annotation(x=namen[j], y=namen[i], text=ev.pz(e["anders"][(a, b)]), showarrow=False, bgcolor="rgba(255,255,255,0.88)", font=dict(color="#222222"))
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickangle=0)
    return _fest(fig, hoehe=340)


def build_null(e: dict):
    """Gemessener Anteil der Wiederholungen mit mindestens einer Verwerfung, daneben die zwei Bezugslinien."""
    fig = go.Figure()
    namen = ["mit Bonferroni<br>(gemessen)", "erwartet mit den<br>Gleichständen", "erwartet ohne<br>Gleichstände", "gemessen<br>(100 Wiederh.)"]
    werte = [100.0 * e["bonferroni"] / e["wiederholungen"], 100 * e["erwartung_pool"], 100 * e["erwartung_ohne"], 100 * e["mindestens_eine"]]
    fig.add_bar(y=namen, x=werte, orientation="h", marker_color=[GRUEN, BLAU, GRAU, ROT], text=[ev.de(w, 1) for w in werte], textposition="outside")
    fig.update_xaxes(title="mind. eine Verwerfung (%)", range=[0, 115])
    return _fest(fig, hoehe=300, showlegend=False, title=dict(text=f"{e['m']} Tests, {e['r']} gegen {e['r']} Läufe", font=dict(size=13)))


def build_modell(kurve: list, m: int, r: int):
    """Gleichstandsmodell: mindestens eine Verwerfung unter m Tests über den Anteil q der Läufe auf dem Bestwert."""
    fig = go.Figure(go.Scatter(x=[k["q"] for k in kurve], y=[100 * k["mindestens"] for k in kurve], mode="lines+markers", line=dict(color=BLAU)))
    fig.update_xaxes(title="Anteil q der Läufe auf dem Bestwert")
    fig.update_yaxes(title="mind. eine Verwerfung (%)", range=[0, 100])
    return _fest(fig, hoehe=300, title=dict(text=f"Modell, exakt: {m} Tests, {r} gegen {r} Läufe", font=dict(size=13)))


def build_haeufigster(e: dict):
    werte = sorted(100 * x for x in e["haeufigster"])
    fig = go.Figure(go.Bar(x=list(range(1, len(werte) + 1)), y=werte, marker_color=BLAU))
    fig.update_xaxes(title="getestete Instanzen, aufsteigend sortiert")
    fig.update_yaxes(title="häufigster Wert (%)", range=[0, 100])
    return _fest(fig, hoehe=300)


def build_einstellung(e: dict):
    fig = go.Figure(go.Bar(x=[ev.tsd(z["budget"]) for z in e["zeilen"]], y=[100 * z["anders"] for z in e["zeilen"]], marker_color=ROT,
                           text=[ev.pz(z["anders"]) for z in e["zeilen"]], textposition="outside"))
    fig.update_xaxes(title="Budget (Auswertungen)", type="category")
    fig.update_yaxes(title="Instanzen anders (%)", range=[0, 110])
    return _fest(fig, hoehe=300)


def build_quartett(e: dict, familie: str):
    """Mittlere Lücke der vier Verfahren über die Budgetstufen (gewählte Familie)."""
    fig = go.Figure()
    stufen = [ev.STUFE_TEXT[s] for s in e["stufen"]]
    for v, name in (("hc", "HC"), ("sa", "SA"), ("ils", "ILS"), ("ma", "MA")):
        fig.add_scatter(x=stufen, y=[max(e["raster"][(s, familie)]["mittel"][v], 0.005) for s in e["stufen"]], mode="lines+markers", name=name, line=dict(color=FARBE[name]))
    fig.update_xaxes(title="Budget (Auswertungen)", type="category")
    fig.update_yaxes(title="mittlere Lücke (%, log)", type="log")
    return _fest(fig)
