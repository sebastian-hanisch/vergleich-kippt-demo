"""Texte, die wortgleich in App und README stehen (ein Test vergleicht beide Fassungen)."""

VORAUSSETZUNG = (
    "Alle Zahlen dieser Seite: Zählweise **voll** (jede Bewertung eines Nachbarn zählt eine Auswertung, alle Züge der 2-opt-Nachbarschaft, "
    "keine Listen, keine Warteschlange; jede Starttour und jede Störung zählt 1), Abstiegsregel **erste Verbesserung**, Zugreihenfolge: je Abstieg "
    "eine neue Zufallsreihenfolge aller Züge, zyklisch durchlaufen. Wie sich Vergleiche mit Listen oder Warteschlange ändern, zeigt die Demo "
    "„Die Nachbarschaft ändert die Landschaft“ dieser Reihe; hier gibt es dazu keinen Umschalter."
)

VERFAHREN_TABELLE = """
| Kürzel | Verfahren | Was es tut (eigene Umsetzung) | Einstellung |
|---|---|---|---|
| HC | Hill Climbing mit Neustarts | Zufallstour, 2-opt-Abstieg bis kein Zug mehr verbessert, dann neue Zufallstour | keine |
| SA | Simulated Annealing | je Schritt ein zufälliger 2-opt-Zug; angenommen, wenn er nicht verlängert, sonst mit Wahrscheinlichkeit exp(−Änderung/T); T fällt geometrisch | Starttemperatur (Vielfaches der mittleren Kante der Nächster-Nachbar-Tour) und Abkühlung in Zehnerpotenzen über das Budget |
| GA | genetischer Algorithmus ohne Lokalsuche | 30 Touren; Turnierauswahl (3), Order Crossover (Wahrscheinlichkeit 0,9), Umkehrmutation (0,5), die besten 2 bleiben | fest |
| ILS | Iterated Local Search (iterierte Lokalsuche mit 2-opt) | 2-opt-Abstieg, dann wiederholt Double-Bridge (vier Kanten ersetzt) und neuer Abstieg; die neue Tour gilt, wenn sie nicht länger ist | keine |
| MA | memetischer Algorithmus | Population von 2-opt-Optima; Zweierturnier, Order Crossover, mit Wahrscheinlichkeit 0,3 eine Double-Bridge, 2-opt-Abstieg; ersetzt die längste Tour | Größe der Population |
"""

MASS_TABELLE = """
| Maß einer Läufegruppe | Rechnung | besser ist |
|---|---|---|
| Mittel | Mittel der Lücken der Läufe | kleiner |
| Median | mittlerer Wert der sortierten Lücken | kleiner |
| Bestes | kleinste Lücke der Gruppe | kleiner |
| Anteil ≤ 2 % | Anteil der Läufe mit Lücke höchstens 2 % | größer |
| Fläche | Mittel der bis dahin besten Lücke über 20 Prüfpunkte, die im Logarithmus gleich weit von 50 Auswertungen bis zum Budget liegen | kleiner |
"""

# Zahlen der Demo „Die Nachbarschaft ändert die Landschaft“ (Ordner nachbarschaft-landschaft-demo), wörtlich aus deren README,
# Abschnitt „Zitierbare Zahlen mit Voraussetzung, Fundstelle und Test“. tests/test_claims.py prüft die Zeichenfolgen gegen jene README, wenn der Ordner daneben liegt.
ZITAT_QUELLE = "README der Demo „Die Nachbarschaft ändert die Landschaft“, Abschnitt „Zitierbare Zahlen mit Voraussetzung, Fundstelle und Test“"
ZITATE_STUECK5 = {
    "dreiopt": "Lücke 75,72 % (voll), 3,78 % (Listen, k = 8), 1,11 % (Warteschlange)",
    "dreiopt_voraussetzung": "3-opt, n = 50, Abstieg mit Neustarts, 800.000 Auswertungen, steilster Abstieg über die je Zählweise bewerteten Züge, 18 Instanzen, 72 Läufe; Referenz nicht bewiesen optimal",
    "rang": "Rang 1: 2-opt in 27 (voll), 33 (Listen), 28 (Warteschlange) von je 36 Zellen; 3-opt in 0 von 108",
    "tau": "Kendall τ 0,67 bis 0,89 (voll / Listen), 0,56 bis 0,78 (voll / Warteschlange), 0,61 bis 0,94 (Listen / Warteschlange)",
    "schritt": "Schrittkosten 72.475 (voll) und 8.604 (Warteschlange) für 3-opt, 1.175 und 94 für 2-opt",
}

CHECKLISTE = f"""
| Was in der Aussage „A ist besser als B“ stehen muss | Warum | Wo auf dieser Seite |
|---|---|---|
| Zahl der Läufe je Gruppe | kleine Gruppen ordnen dieselben Verfahren verschieden | Experiment 1 |
| Maß (Mittel, Median, Bestes, Anteil, Fläche) | das Maß ändert die Rangfolge | Experiment 2 |
| Test, Testvariante, Zahl der Tests, Umgang mit Gleichständen | viele Tests finden Unterschiede, die es nicht gibt | Experiment 3 |
| Einstellung der Verfahren und wie sie gefunden wurde | eine andere Einstellung, eine andere Rangfolge | Experiment 4 |
| Budget und Instanzfamilie | beide können die Rangfolge kippen | Experiment 5 |
| Zählweise der Auswertungen | dieselbe Nachbarschaft, andere Zählweise, anderes Ergebnis | nur zitiert, siehe unten |
| Abstiegsregel und Zugreihenfolge | bei erster Verbesserung ist die Reihenfolge eine eigene Stellschraube | hier festgelegt, nichts über andere behauptet |

**Zur Zählweise zeigt diese Demo keine eigene Messung.** Sie zitiert die Demo „Die Nachbarschaft ändert die Landschaft“ dieser Reihe, die den Umschalter besitzt:

* {ZITATE_STUECK5["dreiopt"]} ({ZITATE_STUECK5["dreiopt_voraussetzung"]}).
* {ZITATE_STUECK5["rang"]} (n = 30, 50, 100; zwei Verfahren; drei Familien; zwei Budgets).
* {ZITATE_STUECK5["tau"]} (sechs Gruppen aus Stadtzahl und Verfahren, je Mittel über sechs Zellen).
* {ZITATE_STUECK5["schritt"]} (n = 50).

Fundstelle: {ZITAT_QUELLE}. Dort heißt „Listen“: mindestens eine neue Kante verbindet eine Stadt mit einem ihrer k = 8 nächsten Nachbarn, jeder Zug zählt einmal.
"""

ANNAHMEN = """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| Eigene Umsetzungen, 2-opt, 20 bis 80 Orte, erfundene Instanzen | Andere Verfahren, Nachbarschaften, Größen oder reale Daten können andere Rangfolgen und andere Kippanteile geben; nichts hier ist eine Aussage über Verfahrensklassen. | - |
| Zählweise voll, erste Verbesserung, Zufallsreihenfolge der Züge | Mit Listen oder Warteschlange kostet ein Schritt weniger, und die Rangfolge kann sich ändern (zitierte Zahlen im Expander „Was in der Aussage stehen muss“). | Demo „Die Nachbarschaft ändert die Landschaft“ |
| Die beste bekannte Länge ist die Referenz der Lücke | Sie ist nicht als optimal bewiesen; eine kürzere Tour würde alle Lücken verschieben, die Rangfolgen je Instanz nicht. | - |
| Zwei Gruppen aus demselben Pool von 60 Läufen | Die Gruppen sind ohne Zurücklegen gezogen und unter der Nullannahme austauschbar; ein größerer Pool gäbe dieselbe Erwartung mit weniger Rauschen der Schätzung. | - |
| Normalannahme der Kippformel | Lücken sind rechtsschief und haben Gleichstände; die Formel ist eine Näherung für ein Paar von Verfahren und die strikte Zählung. | - |
| Unabhängige Tests | Die Tests verschiedener Instanzen sind unabhängig; bei abhängigen Tests gilt 1 − Produkt(1 − p) nicht. | Demo „Mehrfachtests und Gewinnerfluch“ (Korrekturverfahren im Einzelnen) |
"""
