"""Konstanten: Aufbau der Messreihen, Regler-Grenzen, Farben und Presets."""

# --- Messreihe „Trio“ (Hill Climbing, Simulated Annealing, genetischer Algorithmus) ---------------------------------------------
TRIO_FAMILIEN = ("gleich", "cluster", "gitter")
TRIO_N = tuple(range(20, 41))                    # je Familie eine Instanz je Ortszahl: 63 Instanzen
TRIO_BUDGETS = (1000, 3000, 10000)
TRIO_LAEUFE = 60
TRIO_VERFAHREN = ("hc", "sa_std", "sa_abg", "ga")
# Prüfpunkte für das Maß „Fläche unter der Laufzeitkurve“: 20 Punkte, im Logarithmus gleich weit von 50 bis zum Budget (einmal gerechnet, hier fest).
PRUEFPUNKTE = {
    1000: (50, 59, 69, 80, 94, 110, 129, 151, 177, 207, 242, 283, 332, 388, 455, 532, 623, 730, 854, 1000),
    3000: (50, 62, 77, 95, 118, 147, 182, 226, 280, 348, 431, 535, 664, 823, 1021, 1267, 1572, 1950, 2418, 3000),
    10000: (50, 66, 87, 115, 153, 202, 266, 352, 465, 615, 813, 1074, 1420, 1877, 2480, 3278, 4332, 5725, 7566, 10000),
}
# Simulated Annealing im Trio: (Starttemperatur als Vielfaches der Skala, Abkühlung in Zehnerpotenzen über das Budget).
# „Standard“ ist die Einstellung der Vormessung; „abgestimmt“ ist das Ergebnis von `tools/vgk_make_daten.py abstimmung` (data/vgk_abstimmung.json).
SA_TRIO = {"sa_std": (0.3, 3.0), "sa_abg": (0.3, 1.0)}
SA_GITTER_T0F = (0.03, 0.1, 0.3, 1.0)
SA_GITTER_C = (0.5, 1.0, 2.0, 3.0, 4.0)
ABSTIMM_N_TRIO = (22, 26, 30, 34, 38)           # Abstimm-Instanzen: laufende Nummer 1 (die Messung nutzt Nummer 0)
ABSTIMM_LAEUFE = 10

# --- Messreihe „Quartett“ (Hill Climbing, Simulated Annealing, Iterated Local Search, memetischer Algorithmus) -------------------
QUARTETT_FAMILIEN = ("gleich", "cluster", "gitter", "netz")
QUARTETT_N = (20, 30, 40, 50, 60, 70, 80)
QUARTETT_IDX = (0, 1)                            # 4 Familien × 7 Ortszahlen × 2 = 56 Instanzen
QUARTETT_VERFAHREN = ("hc", "sa", "ils", "ma")
QUARTETT_LAEUFE = 12
QUARTETT_STUFEN = {"30n": 30, "100n": 100, "1000n": 1000, "5000n": 5000}   # Budget = Faktor · Ortszahl
SA_QUARTETT = {"30n": (0.3, 2.0), "100n": (0.1, 2.0), "1000n": (0.3, 0.5), "5000n": (0.3, 1.0)}
MA_GROESSE = 4
MA_GITTER = (2, 4, 8, 16)
ABSTIMM_N_QUARTETT = (30, 50, 70)                # Abstimm-Instanzen: laufende Nummer 2
REFERENZ_FAKTOR = 20000
REFERENZ_LAEUFE = 2

# Verfahrenskennzahlen für die Zufalls-Seeds der Läufe (vgk_basis.lauf_seed); Simulated Annealing addiert 10 · (Nummer des Budgets).
CODE = {"hc": 0, "sa_std": 1, "sa_abg": 2, "ga": 3, "q_hc": 100, "q_sa": 101, "q_ils": 102, "q_ma": 103, "ref": 200, "abstimm": 300}

# --- Regler der Seitenleiste -----------------------------------------------------------------------------------------------------
GRUPPEN_R = (3, 5, 10, 15, 30)
PAARE = ("alle", "hc_sa", "sa_ga")
MASSE_WAHL = ("median", "bestes", "anteil", "flaeche")       # das Maß, das gegen das Mittel gestellt wird
SA_WAHL = ("sa_std", "sa_abg")
NULL_VERFAHREN = ("hc", "sa", "ga")
NULL_GRUPPEN = (5, 10, 20)
M_MIN, M_MAX = 1, len(TRIO_N) * len(TRIO_FAMILIEN)
SEED_MAX = 999999
Q_FAMILIEN = ("alle",) + QUARTETT_FAMILIEN
Q_LAEUFE = (3, 6, 12)
LIVE_INSTANZ = ("gleich", 30, 0)                             # die Instanz der Live-Nachrechnung
LIVE_LAEUFE = 10

DEFAULTS = {"budget": 3000, "gruppe": 15, "paar": "alle", "mass": "median", "sa": "sa_std", "null_verfahren": "sa", "m": 30, "null_gruppe": 10,
            "seed": 35, "q_budget": "1000n", "q_familie": "alle", "q_laeufe": 12}

PRESETS = {
    "Das Trio (HC, SA, GA)": dict(DEFAULTS),
    "Gruppen zu 5 Läufen": dict(DEFAULTS, gruppe=5, paar="hc_sa"),
    "Maß wechseln": dict(DEFAULTS, mass="bestes", budget=10000),
    "30 Tests gegen sich selbst": dict(DEFAULTS, null_verfahren="ga"),
    "Viele Gleichstände (HC, großes Budget)": dict(DEFAULTS, null_verfahren="hc", budget=10000, null_gruppe=5),
    "Quartett: Budget und Familie": dict(DEFAULTS, q_budget="5000n", q_familie="gitter"),
}
PRESET_HELP = {
    "Das Trio (HC, SA, GA)": "Die Voreinstellung: Hill Climbing, Simulated Annealing und genetischer Algorithmus bei 3.000 Auswertungen, Gruppen zu 15 Läufen.",
    "Gruppen zu 5 Läufen": "Experiment 1: das Paar HC gegen SA mit Gruppen zu 5 Läufen; wie oft ordnen zwei Gruppen das Paar verschieden?",
    "Maß wechseln": "Experiment 2: Mittel gegen den besten Lauf bei 10.000 Auswertungen.",
    "30 Tests gegen sich selbst": "Experiment 3: der genetische Algorithmus gegen sich selbst, 30 Instanzen, 10 gegen 10 Läufe; hier gibt es die wenigsten Gleichstände.",
    "Viele Gleichstände (HC, großes Budget)": "Experiment 3: Hill Climbing gegen sich selbst bei 10.000 Auswertungen, 5 gegen 5 Läufe; viele Läufe treffen denselben Wert.",
    "Quartett: Budget und Familie": "Experiment 5: HC, SA, ILS und MA auf dem Gitter mit Rauschen bei 5.000 · n Auswertungen.",
}
