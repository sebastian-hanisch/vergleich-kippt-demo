# Ehrlicher Vergleich: wann kippt die Rangfolge? – Streamlit-Demo

Achte Demo der Reihe „Landschaften, Einstellung und Vergleich“ (Bereich Optimierung, Feld „Metaheuristiken und Suche“). Sie vergleicht eigene Umsetzungen von Suchverfahren auf erfundenen Lieferrouten (Rundtour, euklidisch, 2-opt) und fragt nicht, welches Verfahren das beste ist, sondern **was hinter dem Satz „A ist besser als B“ steht**. Die Demos „Wann lohnt Auswählen?“ und „Einstellen lohnt“ der Reihe lassen eine Annahme stehen: dass „A liegt vor B“ nach einer Messung eine Eigenschaft der Verfahren sei (sie wählen nach einem Etikett oder einer Einstellung aus einer Läufegruppe, in einem Maß, mit einer Zählweise). Diese Demo hebt die Annahme auf und zeigt, welche Teile der Aussage an der **Messung** hängen. Zur Demo „Die Nachbarschaft ändert die Landschaft“ ist sie ein Kontrast: Jene besitzt die Definitionen der Zählweisen und den Umschalter; diese rechnet nur in der Zählweise „voll“ und zitiert von dort.

Alle Instanzen sind erfunden (keine reale Datenquelle), alle Verfahren sind eigene Umsetzungen. Nichts an den Aussagen ist neu: Dass Rangfolgen von Suchverfahren an Läufezahl, Maß, Budget und Abstimmung hängen, ist Lehrbuch- und Forschungswissen (Quellen unten). Neu ist nur, dass es sich hier mit Zähleinheiten nachrechnen lässt. Aussagen darüber, welches Verfahren man auswählen sollte, macht diese Demo nicht; solche Aussagen sind in der ganzen Reihe als nicht gesichert gekennzeichnet.

## Kernfrage

1. Wie oft ändert sich die Rangfolge, wenn man nur neu würfelt?
2. Woran hängt sie sonst (Maß, Einstellung, Budget und Familie)?
3. Wie oft „findet“ man einen Unterschied, den es nicht gibt?

Kurzfassung der Messungen (jede Zahl mit Voraussetzung in den Tabellen unten; Zählweise voll, erste Verbesserung, Zufallsreihenfolge der Züge; wo nichts anderes steht: Simulated Annealing in der Einstellung „Standard“, Maß Mittel):

* **Ein Dauergewinner, der trotzdem kippt.** Im Trio aus Hill Climbing (HC), Simulated Annealing (SA) und einem genetischen Algorithmus ohne Lokalsuche (GA) ist die Ordnung der mittleren Lücke HC < SA < GA in allen 12 Zellen aus drei Budgets (1.000, 3.000, 10.000 Auswertungen) und drei Familien samt Gesamtmittel; HC liegt auf 63 von 63 Instanzen allein vorn (20 bis 40 Orte, 60 Läufe je Zelle).
* **Nur neu würfeln:** Teilt man die 60 Läufe in Gruppen zu 5, ordnen 29,5 / 40,8 / 51,6 % der Gruppenpaare je Instanz das Trio verschieden (Budget 1.000 / 3.000 / 10.000); mit Gruppen zu 15 Läufen 15,6 / 27,0 / 32,3 %.
* **Maß wechseln:** Zwischen „Mittel“ und „bester Lauf“ ist die Rangfolge auf 46,0 / 81,0 / 93,7 % der Instanzen verschieden, zwischen Mittel und Median auf 3,2 / 7,9 / 9,5 %. Die 93,7 % bei 10.000 Auswertungen entstehen großenteils durch Gleichstand beim Maß „Bestes“: auf 44 von 63 Instanzen treffen alle drei Verfahren die beste bekannte Länge (Tabelle zu Experiment 2).
* **Einstellung wechseln:** Mit einer auf getrennten Instanzen abgestimmten Einstellung von SA ist die Rangfolge auf 3,2 / 27,0 / 55,6 % der Instanzen eine andere; SA liegt dann auf 2 / 16 / 27 von 63 Instanzen vor HC, und die Ordnung HC < SA < GA gilt nicht mehr in allen Zellen (11 von 12 Zellen); HC liegt auf 61 / 47 / 36 von 63 Instanzen allein vorn und bleibt im Gesamtmittel vorn.
* **Dasselbe Verfahren gegen sich selbst:** Wer 30 Instanzen einzeln testet (10 gegen 10 Läufe, Mann-Whitney als Normalnäherung, Niveau 0,05), findet ohne Gleichstände mit 73,5 % mindestens einen „signifikanten“ Unterschied (4,326 % je Einzeltest, nicht 5 %; exakt gerechnet). Mit den Gleichständen der gemessenen Läufe sind es bei 3.000 Auswertungen 74,0 % (HC), 74,7 % (SA) und 74,1 % (GA), bei 10.000 Auswertungen für HC nur 66,9 %; bei 5 gegen 5 Läufen 48,1 % statt 62,0 %. Gemessen in je 100 Wiederholungen: Tabelle unten.
* **Budget und Familie:** Im Quartett aus HC, SA, Iterated Local Search (ILS) und einem memetischen Algorithmus (MA) auf 56 Instanzen mit 20 bis 80 Orten gibt es über vier Budgets vier verschiedene Rangfolgen der mittleren Lücke, doch bei 30 · n und 100 · n liegen HC, ILS und MA höchstens 0,5 bzw. 0,05 Punkte auseinander, ihre Reihenfolge ist dort Rauschen der Läufe (belastbar: SA ist bei 30 · n und 100 · n Letzter und bei 1.000 · n Erster, HC bei 1.000 · n und 5.000 · n Letzter; alle Familien zusammen); bei 5.000 · n Auswertungen liegt auf dem Gitter mit Rauschen SA vorn, in den drei anderen Familien ILS. Bei 30 · n Auswertungen haben nur 8 % der Läufe von HC, ILS und MA den ersten Abstieg beendet: Die Lücken sind dort abgebrochene Abstiege und keine Güte der Verfahren.

## Befunde und Korrekturen gegenüber Plan und Vormessung

Vor dem Bau gab es Messungen mit anderen Instanzen, anderen Umsetzungen und einem anderen Zufallsgenerator (im Folgenden „Vormessung“; sie ist nicht Teil dieser Demo und hier nicht nachrechenbar). Die Demo benutzt die gemeinsame Instanzbasis der Reihe und einen plattformgleichen Zufallsgenerator (SplitMix64); **jede Zahl dieser README ist mit der Demo neu gemessen**, die Zahlen der Vormessung stehen nur in dieser Tabelle.

| Aussage der Vormessung oder des Plans | Gemessen in der Demo | Folge |
|---|---|---|
| Trio mit Dauergewinner: HC < SA < GA bei allen Budgets und in allen Familien (90 Instanzen) | bestätigt mit der Einstellung „Standard“ (63 Instanzen, 12 von 12 Zellen); **mit der abgestimmten Einstellung nur noch in 11 von 12 Zellen** (SA vor HC auf bis zu 27 Instanzen; im Gesamtmittel bleibt HC vorn) | Der Satz „Familie und Budget kippen die Rangfolge nicht“ gilt nur für das Trio mit der Standard-Einstellung und dem Maß Mittel. |
| Gruppen zu 5 Läufen: 31 / 37 / 57 % der Gruppenpaare ordnen das Trio anders; zu 15 Läufen 16 / 22 / 42 % | 29,5 / 40,8 / 51,6 % und 15,6 / 27,0 / 32,3 % | bestätigt als Größenordnung; die Einzelwerte liegen bis 10 Punkte daneben |
| Mittel gegen Bestes: 72 % (3.000) und 97 % (10.000) der Instanzen; gegen Median 10 % und 33 % | 81,0 % und 93,7 %; gegen Median 7,9 % und 9,5 % | bestätigt für „Bestes“; **der Median liegt hier viel näher am Mittel** als in der Vormessung |
| Wechsel der SA-Einstellung: 0 / 12 / 30 % der Instanzen | 3,2 / 27,0 / 55,6 % | **stärker als erwartet.** Die Vormessung nannte (1,0; 2,0) „abgestimmt“; die Abstimmung der Demo wählt (0,3; 1,0) aus 20 Einstellungen. |
| Nullvergleich: 73,5 % ohne Gleichstände; mit Gleichständen 73 bis 74 % bei 3.000 Auswertungen, 69 % für HC bei 10.000 | 73,5 % (exakt, bestätigt); 74,0 / 74,7 / 74,1 %; 66,9 % | bestätigt |
| Kippformel trifft die Messung bis 2,5 Punkte (Zählung „verschieden“) und 4,3 Punkte (strikt) | größter Abstand 4,4 Punkte (strikt) und 4,1 Punkte (verschieden), Gruppen zu 3 bis 15 Läufen, 12 Zeilen | in derselben Größenordnung; bei 30 Läufen je Gruppe gibt es nur ein Gruppenpaar je Instanz, dort ist der Abstand bis 7,5 Punkte |
| Median der nötigen Läufe je Gruppe für höchstens 5 % Kippen (HC gegen SA, 3.000): 28,7; bei 28 von 90 Instanzen über 60 | 33,4; bei 25 von 63 Instanzen über 60 | bestätigt |
| Quartett, voll: bei 100 · n HC < ILS < MA < SA, bei 1.000 · n ILS < MA < SA < HC; auf dem Gitter gewinnt SA | bei 100 · n ILS < MA < HC < SA (die ersten drei innerhalb von 0,05 Punkten), bei 1.000 · n **SA < ILS < MA < HC**, bei 5.000 · n ILS < MA < SA < HC; auf dem Gitter gewinnt SA bei 1.000 · n und 5.000 · n | Das Kippen ist bestätigt, die einzelnen Rangfolgen sind andere. SA ist in der Demo je Budget abgestimmt und liegt bei 1.000 · n insgesamt vorn. |
| Gruppenfaktor 0,99 und 1,03 (voll) | 0,98 / 1,00 / 0,71 / 1,01 bei 30 · n / 100 · n / 1.000 · n / 5.000 · n | bestätigt für alle Familien zusammen bei 30 · n, 100 · n und 5.000 · n (kein großer Abstand zwischen den Gruppen (HC, SA) und (ILS, MA)); bei 1.000 · n liegt der Faktor bei 0,71, SA liegt dort vor ILS und MA; je Familie liegt der Faktor zwischen 0,54 und 1,94 (1.000 · n: 0,54 gleichverteilt, 0,56 Gitter; 5.000 · n: 1,38 gleichverteilt, 1,94 Straßennetz) |
| Vormessung mit einem Bündel aus Listen (k = 8), Warteschlange und Gewinnregel: Gruppenfaktor 1,37 und 5,45 | nicht gemessen (diese Demo rechnet nur „voll“) | Die Zahl gehört zu einer anderen Zählweise und einer anderen Umsetzung; sie steht nur hier und nicht in der App. |
| Plan: Budgets des Quartetts in Vielfachen der Kosten eines ersten Abstiegs | Der erste Abstieg kostet im Median 28 · n (20 Orte) bis 183 · n (80 Orte) Auswertungen (Tabelle unten); die Budgets 30 · n, 100 · n, 1.000 · n, 5.000 · n decken „fast kein Abstieg beendet“ bis „viele Abstiege“ ab | Messlücke des Plans geschlossen |

Bauliche Abweichungen vom Plan: (1) 63 statt 90 Instanzen im Trio (je Familie eine je Ortszahl 20 bis 40) und 56 statt 120 im Quartett; (2) der Pool des Mehrfachtests sind die 60 Läufe je Instanz (der Plan erwog 200); (3) die Störung von ILS und MA ist die Double-Bridge mit vier ersetzten Kanten über die ganze Tour, nicht der Abschnittstausch der Vormessung; (4) der Regler „Wiederholungen“ entfällt (fest 100), dafür gibt es den Zufalls-Seed der Ziehungen; (5) die Zusatzbudgets 30.000 und 100.000 des Trios sind nicht gemessen; (6) kein PDF-Export.

## Modell

**Aufgabe.** Rundtour durch n Orte mit ganzzahligen Koordinaten in 0 bis 9.999 und euklidischen Abständen. Vier Familien der gemeinsamen Instanzbasis der Reihe: gleichverteilt, geclustert, Gitter mit Rauschen und Straßennetz (Punkte entlang weniger Strecken; nur im Quartett).

**Lücke** eines Laufs = (Länge − beste bekannte Länge) / beste bekannte Länge in Prozent. Die beste bekannte Länge ist die kürzeste Tour aller Läufe der jeweiligen Messreihe und zweier Referenzläufe (Iterated Local Search mit 20.000 · n Auswertungen); sie ist **nicht als optimal bewiesen**. In allen 63 Instanzen des Trios stammt sie aus einem Referenzlauf oder wird von ihm erreicht.

**Budget und Zählweise.** Einheit ist die Auswertung: Jede Bewertung eines Zugs (Längenänderung) zählt 1, jede Bewertung einer vollständigen Tour (Starttour, Kind einer Kreuzung) zählt 1, jede Störung zählt 1. Zählweise **voll**: alle n(n − 3)/2 Züge der 2-opt-Nachbarschaft, keine Listen, keine Warteschlange. Abstiegsregel: **erste Verbesserung**; Zugreihenfolge: je Abstieg eine neue Zufallsreihenfolge aller Züge, zyklisch durchlaufen, bis n(n − 3)/2 Züge in Folge keine Verbesserung brachten. Kein Lauf überschreitet sein Budget.

Die Verfahren:

| Kürzel | Verfahren | Was es tut (eigene Umsetzung) | Einstellung |
|---|---|---|---|
| HC | Hill Climbing mit Neustarts | Zufallstour, 2-opt-Abstieg bis kein Zug mehr verbessert, dann neue Zufallstour | keine |
| SA | Simulated Annealing | je Schritt ein zufälliger 2-opt-Zug; angenommen, wenn er nicht verlängert, sonst mit Wahrscheinlichkeit exp(−Änderung/T); T fällt geometrisch | Starttemperatur (Vielfaches der mittleren Kante der Nächster-Nachbar-Tour) und Abkühlung in Zehnerpotenzen über das Budget |
| GA | genetischer Algorithmus ohne Lokalsuche | 30 Touren; Turnierauswahl (3), Order Crossover (Wahrscheinlichkeit 0,9), Umkehrmutation (0,5), die besten 2 bleiben | fest |
| ILS | Iterated Local Search (iterierte Lokalsuche mit 2-opt) | 2-opt-Abstieg, dann wiederholt Double-Bridge (vier Kanten ersetzt) und neuer Abstieg; die neue Tour gilt, wenn sie nicht länger ist | keine |
| MA | memetischer Algorithmus | Population von 2-opt-Optima; Zweierturnier, Order Crossover, mit Wahrscheinlichkeit 0,3 eine Double-Bridge, 2-opt-Abstieg; ersetzt die längste Tour | Größe der Population |

Der genetische Algorithmus ohne Lokalsuche ist mit Absicht ein schwaches Verfahren: Das Trio soll einen klaren Dauergewinner haben, an dem sich zeigen lässt, dass die Messung trotzdem kippt.

Die Maße einer Läufegruppe:

| Maß einer Läufegruppe | Rechnung | besser ist |
|---|---|---|
| Mittel | Mittel der Lücken der Läufe | kleiner |
| Median | mittlerer Wert der sortierten Lücken | kleiner |
| Bestes | kleinste Lücke der Gruppe | kleiner |
| Anteil ≤ 2 % | Anteil der Läufe mit Lücke höchstens 2 % | größer |
| Fläche | Mittel der bis dahin besten Lücke über 20 Prüfpunkte, die im Logarithmus gleich weit von 50 Auswertungen bis zum Budget liegen | kleiner |

**Rangfolge und Kippen.** Die Rangfolge einer Instanz ist der Vektor der Ränge der Verfahren nach einem Maß; Gleichstände (gleiche Maßwerte nach Runden auf neun Stellen) bekommen mittlere Ränge. Zwei Bedingungen **kippen** die Rangfolge einer Instanz, wenn die Rangvektoren verschieden sind. Für ein Paar von Verfahren gibt es zwei Zählungen: **verschieden** (ein Gleichstand in nur einer Gruppe zählt mit) und **strikt entgegengesetzt** (jede Gruppe sieht ein anderes Verfahren vorn). Zähleinheiten: Anteil der Instanzen oder Anteil der Gruppenpaare je Instanz, gemittelt über die Instanzen. Vorab festgelegte Lesehilfe ohne Prüfwert: unter 10 % stabil, bis 30 % gemischt, darüber instabil.

**Rangtest.** Mann-Whitney-U, zweiseitig, Niveau 0,05, als Normalnäherung mit Stetigkeits- und Gleichstandskorrektur, selbst geschrieben (`vgk_rangtest.py`); dieselbe Variante rechnet `scipy.stats.mannwhitneyu` mit `method="asymptotic"`, scipy ist nur in den Tests das Orakel. Sind alle Werte gleich, ist p = 1. Bonferroni: Schwelle 0,05 / m. Gleichstand heißt hier: gleiche Tourlänge nach Runden auf 0,001.

Die Formeln (Lücke, Kendall τ_b, Kippformel, Varianz mit Gleichstandskorrektur, Mehrfachtest) stehen im Expander „📐 Mathematische Formulierung“ der App.

## Methodik

* **Messreihe Trio** (`data/vgk_trio.json`): 63 Instanzen (drei Familien, je eine Instanz je Ortszahl 20 bis 40, laufende Nummer 0 der gemeinsamen Basis), vier Verfahren (HC, SA Standard, SA abgestimmt, GA), 60 Läufe, Budgets 1.000, 3.000 und 10.000. HC und GA haben keine Einstellung, die vom Budget abhängt: ein Lauf über 10.000 Auswertungen, die kleineren Budgets sind sein Stand nach 1.000 und 3.000. SA kühlt über das Budget ab: je Budget ein eigener Lauf.
* **Messreihe Quartett** (`data/vgk_quartett.json`): 56 Instanzen (vier Familien, Ortszahlen 20, 30, …, 80, laufende Nummern 0 und 1), vier Verfahren, 12 Läufe, Budgets 30 · n, 100 · n, 1.000 · n und 5.000 · n. HC, ILS und MA: ein Lauf über 5.000 · n, die kleineren Budgets sind Zwischenstände; SA: je Budget ein eigener Lauf.
* **Abstimmung** (`data/vgk_abstimmung.json`): auf Instanzen, die nicht zur Messung gehören (laufende Nummern 1 und 2), mit denselben Zählregeln. Trio: 20 Einstellungen von SA, gewählt die mit dem kleinsten Mittel der Lücke über die drei Budgets. Quartett: je Budget die beste von 20 Einstellungen von SA; für MA die Populationsgröße mit dem kleinsten Mittel über die vier Budgets. HC und ILS haben keine Einstellung. Die Raster stehen unten; bei 1.000 · n liegt die gewählte Einstellung am Rand des Rasters (Abkühlung 0,5 Zehnerpotenzen), bei 30 · n und 100 · n sind die Unterschiede im Raster vermutlich kleiner als sein Rauschen (4 Läufe je Zelle; die Streuung ist nicht gespeichert).
* **Läufegruppen:** Die 60 Läufe je Instanz werden in ihrer Reihenfolge in getrennte Gruppen zu r Läufen geteilt (r = 5: 12 Gruppen, 66 Gruppenpaare; r = 15: 4 Gruppen, 6 Paare; r = 30: 2 Gruppen, 1 Paar).
* **Mehrfachtest:** Je Wiederholung und Instanz werden zwei Gruppen ohne Zurücklegen aus den 60 Läufen desselben Verfahrens gezogen. Die App rechnet 100 Wiederholungen mit dem gewählten Zufalls-Seed; die Erwartung „mit den Gleichständen dieser Läufe“ ist vorgerechnet (`data/vgk_nulltest.json`: je Instanz 4.000 Ziehungen, daraus 1 − Produkt(1 − p_i) über die getesteten Instanzen). Getestet werden die ersten m Instanzen der Messreihe (nach Ortszahl geordnet, darin die drei Familien).
* **Gegenproben:** Jede Tabelle des Trios nennt dieselbe Kennzahl getrennt für die Läufe 1 bis 30 und 31 bis 60 (zwei getrennte Zufallsströme), die des Quartetts für die Läufe 1 bis 6 und 7 bis 12, der Mehrfachtest für zwei Zufalls-Seeds der Ziehungen.

## Befunde (gemessen, keine Behauptungen)

Alle Tabellen schreibt `tools/vgk_readme_tabellen.py` aus den eingefrorenen Messreihen; `tests/test_claims.py` vergleicht sie mit dieser README.

### Das Trio über Budgets und Familien

Mittlere Lücke über 63 Instanzen und 60 Läufe.

<!-- TABELLE:trio -->
| SA-Einstellung | Budget | HC (%) | SA (%) | GA (%) | Ordnung der Mittel | allein vorn auf Instanzen HC / SA / GA (von 63) | Gegenprobe: Mittel HC / SA / GA der Läufe 1 bis 30; 31 bis 60 |
|---|---|---|---|---|---|---|---|
| Standard | 1.000 | 9,02 | 11,90 | 57,20 | HC < SA < GA | 63 / 0 / 0 | 9,13 / 11,77 / 57,18; 8,91 / 12,03 / 57,22 |
| Standard | 3.000 | 3,52 | 4,66 | 17,99 | HC < SA < GA | 63 / 0 / 0 | 3,53 / 4,64 / 17,93; 3,50 / 4,67 / 18,05 |
| Standard | 10.000 | 1,61 | 3,06 | 3,91 | HC < SA < GA | 63 / 0 / 0 | 1,59 / 3,07 / 3,88; 1,63 / 3,05 / 3,95 |
| abgestimmt | 1.000 | 9,02 | 11,94 | 57,20 | HC < SA < GA | 61 / 2 / 0 | 9,13 / 12,10 / 57,18; 8,91 / 11,78 / 57,22 |
| abgestimmt | 3.000 | 3,52 | 3,81 | 17,99 | HC < SA < GA | 47 / 16 / 0 | 3,53 / 3,79 / 17,93; 3,50 / 3,83 / 18,05 |
| abgestimmt | 10.000 | 1,61 | 1,73 | 3,91 | HC < SA < GA | 36 / 27 / 0 | 1,59 / 1,70 / 3,88; 1,63 / 1,76 / 3,95 |
<!-- /TABELLE:trio -->

Ordnung der Familienmittel (je 21 Instanzen) und Anteil der Instanzen, deren Rangfolge sich zwischen zwei Budgets unterscheidet:

<!-- TABELLE:familien -->
| SA-Einstellung | Budget | gleichverteilt | geclustert | Gitter mit Rauschen |
|---|---|---|---|---|
| Standard | 1.000 | HC < SA < GA | HC < SA < GA | HC < SA < GA |
| Standard | 3.000 | HC < SA < GA | HC < SA < GA | HC < SA < GA |
| Standard | 10.000 | HC < SA < GA | HC < SA < GA | HC < SA < GA |
| Standard | Instanzen mit anderer Rangfolge zwischen zwei Budgets | 1.000 ↔ 3.000: 1,6 % ; 1.000 ↔ 10.000: 12,7 % ; 3.000 ↔ 10.000: 14,3 % |  |  |
| abgestimmt | 1.000 | HC < SA < GA | HC < SA < GA | HC < SA < GA |
| abgestimmt | 3.000 | HC < SA < GA | HC < SA < GA | HC < SA < GA |
| abgestimmt | 10.000 | HC < SA < GA | SA < HC < GA | HC < SA < GA |
| abgestimmt | Instanzen mit anderer Rangfolge zwischen zwei Budgets | 1.000 ↔ 3.000: 28,6 % ; 1.000 ↔ 10.000: 42,9 % ; 3.000 ↔ 10.000: 36,5 % |  |  |
<!-- /TABELLE:familien -->

### Experiment 1: Läufegruppen

Anteil der Gruppenpaare je Instanz mit verschiedener Ordnung, gemittelt über 63 Instanzen (Maß Mittel). Kippformel: 2Φ(d)(1 − Φ(d)) mit d = |δ|·√r / √(s₁² + s₂²), je Instanz aus den 60 Läufen geschätzt; sie gilt für ein Paar von Verfahren und die strikte Zählung und ist wegen der Normalannahme eine Näherung (die Lücken sind rechtsschief).

<!-- TABELLE:gruppen -->
| SA-Einstellung | Budget | Verfahren | verschieden bei r = 3 / 5 / 10 / 15 / 30 (%) | strikt entgegengesetzt (%) | Kippformel (%) | Instanzen mit mind. einem abweichenden Paar bei r = 5 (%) | Gegenprobe r = 5: Läufe 1 bis 30 / 31 bis 60 (%) | Läufe je Gruppe für höchstens 5 %: Median (Instanzen bis 5 / über 60) |
|---|---|---|---|---|---|---|---|---|
| Standard | 1.000 | alle drei (HC, SA, GA) | 35,9 / 29,5 / 22,3 / 15,6 / 6,3 | – | – | 87 | 33,1 / 25,9 | – |
| Standard | 1.000 | HC gegen SA | 35,9 / 29,5 / 22,3 / 15,6 / 6,3 | 35,9 / 29,5 / 22,3 / 15,6 / 6,3 | 35,4 / 29,4 / 20,3 / 15,6 / 9,3 | 87 | 33,1 / 25,9 | 22,5 (0 / 14) |
| Standard | 1.000 | SA gegen GA | 0,0 / 0,0 / 0,0 / 0,0 / 0,0 | 0,0 / 0,0 / 0,0 / 0,0 / 0,0 | 0,0 / 0,0 / 0,0 / 0,0 / 0,0 | 0 | 0,0 / 0,0 | 0,3 (63 / 0) |
| Standard | 3.000 | alle drei (HC, SA, GA) | 46,2 / 40,8 / 30,1 / 27,0 / 12,7 | – | – | 97 | 39,6 / 41,2 | – |
| Standard | 3.000 | HC gegen SA | 38,9 / 35,0 / 25,6 / 23,8 / 12,7 | 38,1 / 34,3 / 25,6 / 23,8 / 12,7 | 38,2 / 33,2 / 25,5 / 21,0 / 14,3 | 87 | 33,7 / 35,8 | 33,4 (0 / 25) |
| Standard | 3.000 | SA gegen GA | 8,6 / 6,2 / 4,6 / 3,2 / 0,0 | 8,6 / 6,2 / 4,6 / 3,2 / 0,0 | 8,3 / 6,4 / 4,4 / 3,3 / 1,8 | 19 | 6,9 / 5,6 | 1,1 (50 / 3) |
| Standard | 10.000 | alle drei (HC, SA, GA) | 60,4 / 51,6 / 39,8 / 32,3 / 20,6 | – | – | 100 | 52,4 / 52,1 | – |
| Standard | 10.000 | HC gegen SA | 25,6 / 19,4 / 11,6 / 7,4 / 1,6 | 22,4 / 18,2 / 11,6 / 7,4 / 1,6 | 26,1 / 19,0 / 10,5 / 6,8 / 3,0 | 60 | 17,0 / 20,8 | 11,9 (8 / 4) |
| Standard | 10.000 | SA gegen GA | 40,2 / 35,4 / 30,3 / 26,2 / 19,0 | 39,4 / 34,9 / 30,3 / 26,2 / 19,0 | 40,2 / 36,1 / 29,5 / 25,4 / 19,0 | 89 | 38,4 / 34,5 | 57,6 (2 / 31) |
| abgestimmt | 1.000 | alle drei (HC, SA, GA) | 34,3 / 27,3 / 17,1 / 14,3 / 12,7 | – | – | 89 | 27,6 / 27,6 | – |
| abgestimmt | 1.000 | HC gegen SA | 34,3 / 27,3 / 17,1 / 14,3 / 12,7 | 34,1 / 27,3 / 17,1 / 14,3 / 12,7 | 34,7 / 28,5 / 19,7 / 15,2 / 9,9 | 89 | 27,6 / 27,6 | 20,3 (0 / 13) |
| abgestimmt | 1.000 | SA gegen GA | 0,0 / 0,0 / 0,0 / 0,0 / 0,0 | 0,0 / 0,0 / 0,0 / 0,0 / 0,0 | 0,0 / 0,0 / 0,0 / 0,0 / 0,0 | 0 | 0,0 / 0,0 | 0,2 (63 / 0) |
| abgestimmt | 3.000 | alle drei (HC, SA, GA) | 50,8 / 47,4 / 40,1 / 36,5 / 33,3 | – | – | 98 | 49,5 / 47,3 | – |
| abgestimmt | 3.000 | HC gegen SA | 47,4 / 46,2 / 39,5 / 36,5 / 33,3 | 45,9 / 45,2 / 39,5 / 36,5 / 33,3 | 45,2 / 42,8 / 38,2 / 35,0 / 29,5 | 98 | 48,1 / 46,5 | 179,9 (0 / 44) |
| abgestimmt | 3.000 | SA gegen GA | 4,6 / 1,5 / 0,5 / 0,0 / 0,0 | 4,6 / 1,5 / 0,5 / 0,0 / 0,0 | 4,3 / 2,3 / 0,7 / 0,2 / 0,0 | 8 | 2,1 / 1,1 | 0,9 (51 / 0) |
| abgestimmt | 10.000 | alle drei (HC, SA, GA) | 58,5 / 47,0 / 38,6 / 31,5 / 31,7 | – | – | 98 | 46,6 / 47,0 | – |
| abgestimmt | 10.000 | HC gegen SA | 45,3 / 39,5 / 35,1 / 29,4 / 31,7 | 39,4 / 35,8 / 33,2 / 28,3 / 31,7 | 42,4 / 39,1 / 33,6 / 30,2 / 24,2 | 94 | 40,3 / 38,3 | 107,0 (1 / 37) |
| abgestimmt | 10.000 | SA gegen GA | 17,6 / 8,2 / 4,6 / 2,4 / 0,0 | 16,3 / 8,0 / 4,6 / 2,4 / 0,0 | 19,5 / 12,4 / 5,5 / 3,2 / 1,1 | 35 | 7,5 / 9,3 | 7,0 (20 / 1) |
<!-- /TABELLE:gruppen -->

Lesebeispiel: HC gegen SA (Standard) bei 3.000 Auswertungen und Gruppen zu 5 Läufen: 35,0 % der Gruppenpaare ordnen das Paar verschieden, 34,3 % strikt entgegengesetzt, die Formel sagt 33,2 %. SA gegen GA bei 1.000 Auswertungen kippt in keinem Gruppenpaar: Der Abstand ist dort so groß, dass schon 5 Läufe auf allen 63 Instanzen reichen. Mehr Läufe je Gruppe erhöhen den Anteil in 16 der 18 Zeilen von jeder Gruppengröße zur nächsten nicht; die zwei Ausnahmen stehen mit der abgestimmten Einstellung bei 10.000 Auswertungen (alle drei und HC gegen SA) von 15 auf 30 Läufe, wo es nur noch ein Gruppenpaar je Instanz gibt.

### Experiment 2: Das Maß

Anteil der 63 Instanzen mit verschiedener Rangfolge von HC, SA und GA zwischen zwei Maßen (alle 60 Läufe je Instanz).

<!-- TABELLE:mass -->
| SA-Einstellung | Budget | Mittel gegen Median (%) | gegen Bestes (%) | gegen Anteil ≤ 2 % (%) | gegen Fläche (%) | Bestes gegen Median (%) | mittleres τ zum Mittel: Median / Bestes / Anteil / Fläche (in Klammern: Instanzen ohne definiertes τ) | Instanzen, alle drei gleichauf: Bestes / Anteil | Gegenprobe Mittel gegen Bestes: Läufe 1 bis 30 / 31 bis 60 (%) |
|---|---|---|---|---|---|---|---|---|---|
| Standard | 1.000 | 3,2 | 46,0 | 49,2 | 9,5 | 46,0 | 0,98 / 0,85 / 0,93 (21) / 0,94 | 0 / 21 | 44,4 / 36,5 |
| Standard | 3.000 | 7,9 | 81,0 | 20,6 | 6,3 | 77,8 | 0,95 / 0,76 (13) / 0,91 / 0,96 | 13 / 0 | 73,0 / 63,5 |
| Standard | 10.000 | 9,5 | 93,7 | 20,6 | 12,7 | 93,7 | 0,98 / 0,46 (44) / 0,93 / 0,92 | 44 / 0 | 90,5 / 95,2 |
| abgestimmt | 1.000 | 4,8 | 42,9 | 58,7 | 4,8 | 42,9 | 0,97 / 0,86 / 0,87 (21) / 0,97 | 0 / 21 | 38,1 / 39,7 |
| abgestimmt | 3.000 | 23,8 | 77,8 | 33,3 | 27,0 | 77,8 | 0,86 / 0,78 (13) / 0,83 / 0,82 | 13 / 0 | 71,4 / 68,3 |
| abgestimmt | 10.000 | 28,6 | 88,9 | 30,2 | 41,3 | 88,9 | 0,89 / 0,75 (44) / 0,88 / 0,72 | 44 / 0 | 95,2 / 93,7 |
<!-- /TABELLE:mass -->

Beim Maß „Bestes“ liegen bei 10.000 Auswertungen auf 44 von 63 Instanzen alle drei Verfahren gleichauf (jedes hat in 60 Läufen mindestens einmal die beste bekannte Länge getroffen); Kendall τ ist dort nicht definiert, und die Rangfolge unterscheidet sich schon deshalb von der des Mittels. Der hohe Anteil bei „Bestes“ sagt also vor allem: Dieses Maß trennt die Verfahren bei großem Budget nicht mehr.

Handbeispiel (gesetzte Zahlen): fünf Läufe mit Lücken A = (2, 2, 2, 2, 12) und B = (3, 3, 3, 3, 3). Mittel 4 gegen 3 (B besser), Median 2 gegen 3, Bestes 2 gegen 3, Anteil ≤ 2 % 0,8 gegen 0 (jeweils A besser).

### Experiment 3: Mehrfachtest, dasselbe Verfahren gegen sich selbst

Exakt ohne Gleichstände (aus der Verteilung von U; „unter 30“ heißt mindestens eine Verwerfung unter 30 unabhängigen Tests):

<!-- TABELLE:exakt -->
| Läufe je Gruppe | Verwerfung je Test, Normalnäherung (%) | mind. eine unter 30 (%) | je Test, exakter Test (%) | Bonferroni je Test, Normalnäherung (%) | Bonferroni unter 30 (%) | Bonferroni je Test, exakter Test (%) | Bonferroni unter 30, exakter Test (%) |
|---|---|---|---|---|---|---|---|
| 5 gegen 5 | 3,175 | 62,0 | 3,175 | 0,0000 | 0,00 | 0,0000 | 0,00 |
| 10 gegen 10 | 4,326 | 73,5 | 4,326 | 0,0487 | 1,45 | 0,1505 | 4,42 |
| 20 gegen 20 | 4,909 | 77,9 | 4,909 | 0,1160 | 3,42 | 0,1593 | 4,67 |
<!-- /TABELLE:exakt -->

Das Niveau 0,05 ist die Schwelle des p-Werts; weil die Verteilung von U diskret ist, schöpft der Test sie nicht aus (4,326 % je Test bei 10 gegen 10, 3,175 % bei 5 gegen 5). Bei 5 gegen 5 Läufen kann der Test nach Bonferroni bei 30 Einzeltests nie verwerfen (kleinster exakter p-Wert 2/252). Die Bonferroni-Zahl hängt an der Testvariante: 1,45 % mit der Normalnäherung, 4,42 % mit dem exakten Test (10 gegen 10).

Gleichstandsmodell, exakt gerechnet: Jeder Lauf trifft mit Wahrscheinlichkeit q denselben Bestwert, sonst einen stetigen Wert darüber.

<!-- TABELLE:modell -->
| q (Anteil der Läufe auf dem Bestwert) | 5 gegen 5: je Test / mind. eine unter 30 (%) | 10 gegen 10: je Test / mind. eine unter 30 (%) | 20 gegen 20: je Test / mind. eine unter 30 (%) |
|---|---|---|---|
| 0,00 | 3,175 / 62,0 | 4,326 / 73,5 | 4,909 / 77,9 |
| 0,10 | 3,168 / 61,9 | 4,367 / 73,8 | 4,854 / 77,5 |
| 0,20 | 3,153 / 61,7 | 4,368 / 73,8 | 4,801 / 77,1 |
| 0,30 | 3,204 / 62,4 | 4,375 / 73,9 | 4,773 / 76,9 |
| 0,40 | 3,297 / 63,4 | 4,335 / 73,5 | 4,753 / 76,8 |
| 0,50 | 3,182 / 62,1 | 4,257 / 72,9 | 4,767 / 76,9 |
| 0,60 | 2,589 / 54,5 | 4,208 / 72,5 | 4,748 / 76,8 |
| 0,70 | 1,564 / 37,7 | 4,091 / 71,4 | 4,721 / 76,6 |
| 0,80 | 0,561 / 15,5 | 3,216 / 62,5 | 4,721 / 76,6 |
| 0,90 | 0,061 / 1,8 | 0,922 / 24,3 | 3,746 / 68,2 |
| 0,95 | 0,005 / 0,1 | 0,124 / 3,7 | 1,159 / 29,5 |
<!-- /TABELLE:modell -->

Mit den Läufen der Messreihe (die ersten 30 Instanzen, wo nichts anderes steht):

<!-- TABELLE:null -->
| Verfahren | Budget | Gruppen | Ziehungen mit Gleichständen (%) | häufigster Wert unter 60 Läufen: Mittel / größter (%) | Verwerfung je Test (%) | mind. eine unter 30, mit Gleichständen (%) | ohne Gleichstände (%) | gemessen, 100 Wiederholungen, Zufalls-Seed 35 / 36 (%) | Bonferroni: Wiederholungen von 100, Zufalls-Seed 35 / 36 | 63 Instanzen: mit / ohne Gleichstände (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| HC | 1.000 | 5 gegen 5 | 51 | 12 / 47 | 3,20 | 62,3 | 62,0 | 70 / 68 | 0 / 0 | 86,7 / 86,9 |
| HC | 1.000 | 10 gegen 10 | 75 | 12 / 47 | 4,32 | 73,4 | 73,5 | 63 / 76 | 2 / 1 | 93,8 / 93,8 |
| HC | 1.000 | 20 gegen 20 | 91 | 12 / 47 | 4,79 | 77,1 | 77,9 | 82 / 75 | 1 / 7 | 95,9 / 95,8 |
| HC | 3.000 | 5 gegen 5 | 82 | 26 / 82 | 3,05 | 60,5 | 62,0 | 69 / 61 | 0 / 0 | 86,4 / 86,9 |
| HC | 3.000 | 10 gegen 10 | 97 | 26 / 82 | 4,38 | 74,0 | 73,5 | 68 / 77 | 1 / 1 | 93,8 / 93,8 |
| HC | 3.000 | 20 gegen 20 | 100 | 26 / 82 | 4,84 | 77,5 | 77,9 | 73 / 77 | 2 / 2 | 95,6 / 95,8 |
| HC | 10.000 | 5 gegen 5 | 98 | 52 / 100 | 2,15 | 48,1 | 62,0 | 49 / 51 | 0 / 0 | 82,5 / 86,9 |
| HC | 10.000 | 10 gegen 10 | 100 | 52 / 100 | 3,60 | 66,9 | 73,5 | 63 / 67 | 1 / 1 | 92,6 / 93,8 |
| HC | 10.000 | 20 gegen 20 | 100 | 52 / 100 | 4,37 | 73,9 | 77,9 | 76 / 79 | 0 / 3 | 94,9 / 95,8 |
| SA Standard | 1.000 | 5 gegen 5 | 27 | 7 / 17 | 3,26 | 63,0 | 62,0 | 64 / 64 | 0 / 0 | 87,4 / 86,9 |
| SA Standard | 1.000 | 10 gegen 10 | 47 | 7 / 17 | 4,39 | 74,0 | 73,5 | 69 / 77 | 2 / 1 | 94,0 / 93,8 |
| SA Standard | 1.000 | 20 gegen 20 | 69 | 7 / 17 | 4,86 | 77,5 | 77,9 | 83 / 73 | 2 / 2 | 95,4 / 95,8 |
| SA Standard | 3.000 | 5 gegen 5 | 66 | 15 / 53 | 3,35 | 64,0 | 62,0 | 54 / 61 | 0 / 0 | 87,7 / 86,9 |
| SA Standard | 3.000 | 10 gegen 10 | 89 | 15 / 53 | 4,47 | 74,7 | 73,5 | 70 / 73 | 1 / 0 | 94,2 / 93,8 |
| SA Standard | 3.000 | 20 gegen 20 | 99 | 15 / 53 | 4,73 | 76,6 | 77,9 | 76 / 76 | 4 / 0 | 95,5 / 95,8 |
| SA Standard | 10.000 | 5 gegen 5 | 83 | 24 / 85 | 3,10 | 61,1 | 62,0 | 60 / 61 | 0 / 0 | 86,9 / 86,9 |
| SA Standard | 10.000 | 10 gegen 10 | 96 | 24 / 85 | 4,30 | 73,3 | 73,5 | 68 / 67 | 0 / 3 | 94,1 / 93,8 |
| SA Standard | 10.000 | 20 gegen 20 | 100 | 24 / 85 | 4,74 | 76,7 | 77,9 | 77 / 74 | 3 / 2 | 95,4 / 95,8 |
| SA abgestimmt | 1.000 | 5 gegen 5 | 22 | 5 / 17 | 3,22 | 62,5 | 62,0 | 62 / 63 | 0 / 0 | 87,0 / 86,9 |
| SA abgestimmt | 1.000 | 10 gegen 10 | 44 | 5 / 17 | 4,29 | 73,2 | 73,5 | 75 / 75 | 1 / 3 | 93,8 / 93,8 |
| SA abgestimmt | 1.000 | 20 gegen 20 | 64 | 5 / 17 | 4,89 | 77,8 | 77,9 | 84 / 83 | 3 / 0 | 95,6 / 95,8 |
| SA abgestimmt | 3.000 | 5 gegen 5 | 77 | 20 / 80 | 3,22 | 62,6 | 62,0 | 61 / 63 | 0 / 0 | 87,0 / 86,9 |
| SA abgestimmt | 3.000 | 10 gegen 10 | 95 | 20 / 80 | 4,30 | 73,3 | 73,5 | 70 / 72 | 3 / 2 | 93,8 / 93,8 |
| SA abgestimmt | 3.000 | 20 gegen 20 | 98 | 20 / 80 | 4,78 | 77,0 | 77,9 | 77 / 83 | 7 / 4 | 95,7 / 95,8 |
| SA abgestimmt | 10.000 | 5 gegen 5 | 97 | 42 / 98 | 2,56 | 54,2 | 62,0 | 54 / 59 | 0 / 0 | 84,8 / 86,9 |
| SA abgestimmt | 10.000 | 10 gegen 10 | 100 | 42 / 98 | 4,06 | 71,2 | 73,5 | 71 / 65 | 0 / 0 | 93,3 / 93,8 |
| SA abgestimmt | 10.000 | 20 gegen 20 | 100 | 42 / 98 | 4,65 | 76,1 | 77,9 | 76 / 76 | 0 / 1 | 95,3 / 95,8 |
| GA | 1.000 | 5 gegen 5 | 0 | 2 / 2 | 3,22 | 62,6 | 62,0 | 64 / 60 | 0 / 0 | 86,8 / 86,9 |
| GA | 1.000 | 10 gegen 10 | 0 | 2 / 2 | 4,31 | 73,3 | 73,5 | 72 / 78 | 0 / 2 | 93,8 / 93,8 |
| GA | 1.000 | 20 gegen 20 | 0 | 2 / 2 | 5,02 | 78,7 | 77,9 | 79 / 71 | 4 / 2 | 96,0 / 95,8 |
| GA | 3.000 | 5 gegen 5 | 17 | 5 / 18 | 3,16 | 61,8 | 62,0 | 70 / 68 | 0 / 0 | 86,8 / 86,9 |
| GA | 3.000 | 10 gegen 10 | 33 | 5 / 18 | 4,40 | 74,1 | 73,5 | 71 / 78 | 0 / 3 | 93,7 / 93,8 |
| GA | 3.000 | 20 gegen 20 | 44 | 5 / 18 | 4,93 | 78,0 | 77,9 | 75 / 74 | 1 / 3 | 95,8 / 95,8 |
| GA | 10.000 | 5 gegen 5 | 78 | 20 / 50 | 3,26 | 63,0 | 62,0 | 53 / 61 | 0 / 0 | 87,5 / 86,9 |
| GA | 10.000 | 10 gegen 10 | 95 | 20 / 50 | 4,45 | 74,4 | 73,5 | 74 / 74 | 3 / 3 | 94,1 / 93,8 |
| GA | 10.000 | 20 gegen 20 | 100 | 20 / 50 | 4,71 | 76,5 | 77,9 | 77 / 76 | 2 / 0 | 95,5 / 95,8 |
<!-- /TABELLE:null -->

Lesart: Die Linie „ohne Gleichstände“ ist keine Eigenschaft des Tests, sondern ein Grenzfall. Bei 3.000 Auswertungen und 10 gegen 10 Läufen enthalten zwar 97 % (HC), 89 % (SA Standard) und 33 % (GA) der Ziehungen Gleichstände, die Erwartung bleibt aber bei 74,0 bis 74,7 %. Erst wenn ein Wert die Läufe beherrscht, fällt sie: HC bei 10.000 Auswertungen (im Mittel stellt der häufigste Wert 52 % der 60 Läufe, auf einzelnen Instanzen alle 60) 66,9 % statt 73,5 %, bei 5 gegen 5 Läufen 48,1 % statt 62,0 %. Der Rückgang ist kein Gewinn an Ehrlichkeit; der Test sieht bei vielen gleichen Werten nur weniger. Die gemessenen Anteile aus 100 Wiederholungen haben einen Standardfehler von rund 4,5 Punkten.

### Experiment 4: Die Einstellung

Einstellungen von SA als (Starttemperatur in Vielfachen der Skala; Abkühlung in Zehnerpotenzen): Standard (0,3; 3,0), abgestimmt (0,3; 1,0).

<!-- TABELLE:einstellung -->
| Budget | SA Standard (%) | SA abgestimmt (%) | HC (%) | Ordnung mit Standard | Ordnung mit abgestimmt | Instanzen mit anderer Rangfolge (%) | SA vor HC auf Instanzen: Standard / abgestimmt | Gegenprobe: Läufe 1 bis 30 / 31 bis 60 (%) |
|---|---|---|---|---|---|---|---|---|
| 1.000 | 11,90 | 11,94 | 9,02 | HC < SA < GA | HC < SA < GA | 3,2 | 0 / 2 | 9,5 / 3,2 |
| 3.000 | 4,66 | 3,81 | 3,52 | HC < SA < GA | HC < SA < GA | 27,0 | 0 / 16 | 22,2 / 31,7 |
| 10.000 | 3,06 | 1,73 | 1,61 | HC < SA < GA | HC < SA < GA | 55,6 | 0 / 27 | 54,0 / 50,8 |
<!-- /TABELLE:einstellung -->

Bei 1.000 Auswertungen ist die abgestimmte Einstellung nicht besser als die Standard-Einstellung (11,94 % gegen 11,90 %); gewählt wurde sie nach dem Mittel über die drei Budgets.

### Experiment 5: Budget und Familie am Quartett

Mittlere Lücke über die Instanzen der Familie (je 14, zusammen 56) und 12 Läufe. Gruppenfaktor = kleinere der mittleren Lücken von HC und SA geteilt durch die größere von ILS und MA.

<!-- TABELLE:quartett -->
| Familie | Budget | HC (%) | SA (%) | ILS (%) | MA (%) | Rangfolge der Mittel | Gruppenfaktor | erster Abstieg beendet (% der Läufe von HC, ILS, MA) | Gegenprobe: Rangfolge aus den Läufen 1 bis 6; 7 bis 12 |
|---|---|---|---|---|---|---|---|---|---|
| alle Familien | 30 · n | 28,09 | 31,08 | 28,59 | 28,50 | HC < MA < ILS < SA | 0,98 | 8 | HC < MA < ILS < SA; HC < ILS < MA < SA |
| alle Familien | 100 · n | 6,41 | 8,52 | 6,36 | 6,40 | ILS < MA < HC < SA | 1,00 | 51 | MA < ILS < HC < SA; HC < ILS < MA < SA |
| alle Familien | 1.000 · n | 2,16 | 1,41 | 1,65 | 2,00 | SA < ILS < MA < HC | 0,71 | 100 | SA < ILS < MA < HC; SA < ILS < MA < HC |
| alle Familien | 5.000 · n | 1,19 | 0,64 | 0,55 | 0,64 | ILS < MA < SA < HC | 1,01 | 100 | ILS < MA < SA < HC; ILS < SA < MA < HC |
| gleichverteilt | 30 · n | 28,38 | 31,10 | 29,31 | 29,38 | HC < ILS < MA < SA | 0,97 | 10 | HC < MA < ILS < SA; HC < ILS < MA < SA |
| gleichverteilt | 100 · n | 7,90 | 10,85 | 8,12 | 8,06 | HC < MA < ILS < SA | 0,97 | 51 | HC < MA < ILS < SA; HC < ILS < MA < SA |
| gleichverteilt | 1.000 · n | 2,87 | 1,42 | 2,17 | 2,66 | SA < ILS < MA < HC | 0,54 | 100 | SA < ILS < MA < HC; SA < ILS < MA < HC |
| gleichverteilt | 5.000 · n | 1,37 | 0,96 | 0,60 | 0,70 | ILS < MA < SA < HC | 1,38 | 100 | ILS < MA < SA < HC; ILS < MA < SA < HC |
| geclustert | 30 · n | 28,81 | 30,57 | 27,41 | 27,38 | MA < ILS < HC < SA | 1,05 | 10 | MA < HC < ILS < SA; ILS < MA < HC < SA |
| geclustert | 100 · n | 5,99 | 7,12 | 5,20 | 5,33 | ILS < MA < HC < SA | 1,12 | 49 | ILS < MA < HC < SA; ILS < MA < HC < SA |
| geclustert | 1.000 · n | 1,68 | 1,30 | 1,28 | 1,58 | ILS < SA < MA < HC | 0,82 | 100 | SA < ILS < HC < MA; ILS < SA < MA < HC |
| geclustert | 5.000 · n | 0,83 | 0,57 | 0,48 | 0,53 | ILS < MA < SA < HC | 1,08 | 100 | ILS < SA < MA < HC; MA < ILS < SA < HC |
| Gitter mit Rauschen | 30 · n | 22,87 | 26,02 | 23,52 | 22,91 | HC < MA < ILS < SA | 0,97 | 9 | HC < ILS < MA < SA; MA < HC < ILS < SA |
| Gitter mit Rauschen | 100 · n | 7,31 | 8,59 | 7,66 | 7,52 | HC < MA < ILS < SA | 0,95 | 54 | HC < ILS < MA < SA; HC < MA < ILS < SA |
| Gitter mit Rauschen | 1.000 · n | 3,62 | 1,85 | 2,61 | 3,31 | SA < ILS < MA < HC | 0,56 | 100 | SA < ILS < MA < HC; SA < ILS < MA < HC |
| Gitter mit Rauschen | 5.000 · n | 2,44 | 0,88 | 1,09 | 1,27 | SA < ILS < MA < HC | 0,69 | 100 | SA < ILS < MA < HC; SA < ILS < MA < HC |
| Straßennetz | 30 · n | 32,27 | 36,64 | 34,10 | 34,31 | HC < ILS < MA < SA | 0,94 | 5 | HC < MA < ILS < SA; HC < ILS < MA < SA |
| Straßennetz | 100 · n | 4,44 | 7,54 | 4,47 | 4,69 | HC < ILS < MA < SA | 0,95 | 50 | MA < ILS < HC < SA; HC < ILS < MA < SA |
| Straßennetz | 1.000 · n | 0,47 | 1,08 | 0,54 | 0,45 | MA < HC < ILS < SA | 0,88 | 100 | HC < MA < ILS < SA; MA < HC < ILS < SA |
| Straßennetz | 5.000 · n | 0,11 | 0,16 | 0,04 | 0,06 | ILS < MA < HC < SA | 1,94 | 100 | ILS < MA < HC < SA; ILS < MA < SA < HC |
<!-- /TABELLE:quartett -->

Kosten des ersten Abstiegs (Läufe von HC, ILS und MA, je Ortszahl 8 Instanzen):

<!-- TABELLE:abstieg -->
| Orte n | Züge je Durchgang n(n − 3)/2 | Auswertungen bis zum Ende des ersten Abstiegs: Median | kleinster bis größter Wert | Median geteilt durch n | nicht beendete Abstiege (von 288 je Ortszahl) |
|---|---|---|---|---|---|
| 20 | 170 | 560 | 322 bis 1.045 | 28 | 0 |
| 30 | 405 | 1.501 | 991 bis 2.914 | 50 | 0 |
| 40 | 740 | 2.977 | 1.870 bis 5.332 | 74 | 0 |
| 50 | 1.175 | 4.927 | 3.021 bis 9.779 | 99 | 0 |
| 60 | 1.710 | 7.627 | 5.075 bis 13.208 | 127 | 0 |
| 70 | 2.345 | 10.765 | 6.419 bis 19.838 | 154 | 0 |
| 80 | 3.080 | 14.628 | 8.600 bis 22.504 | 183 | 0 |
<!-- /TABELLE:abstieg -->

Lesart: Bei 30 · n und 100 · n liegen HC, ILS und MA über alle 56 Instanzen höchstens 0,5 und 0,05 Punkte auseinander (je Familie bis zu 2,03 beim Straßennetz bei 30 · n und 0,79 bei geclusterten Instanzen bei 100 · n). Bis zum Ende des ersten Abstiegs tun die drei nach ihrer Bauart dasselbe; ihre Reihenfolge ist dort Rauschen der Läufe und wechselt zwischen den zwei Hälften der Läufe. Das Verdikt der App nennt deshalb keine Rangfolge der drei, solange weniger als die Hälfte der Läufe den ersten Abstieg beendet hat. Ab 1.000 · n reicht das Budget in allen Läufen für mindestens drei erste Abstiege (größter gemessener erster Abstieg 283 · n); dort ist HC in drei von vier Familien Letzter, auf dem Straßennetz aber nicht.

### Abstimmung

<!-- TABELLE:abstimmung -->
Trio, Simulated Annealing (15 Abstimm-Instanzen, 10 Läufe je Zelle; gewählt: kleinstes Mittel der drei Budgets):

| Starttemperatur (· Skala) | Abkühlung (Zehnerpotenzen) | Lücke bei 1.000 (%) | bei 3.000 (%) | bei 10.000 (%) | Mittel der drei (%) |
|---|---|---|---|---|---|
| 0,03 | 0,5 | 12,21 | 4,29 | 3,86 | 6,79 |
| 0,03 | 1,0 | 11,98 | 4,20 | 3,94 | 6,71 |
| 0,03 | 2,0 | 12,40 | 4,19 | 4,23 | 6,94 |
| 0,03 | 3,0 | 11,58 | 4,56 | 4,64 | 6,93 |
| 0,03 | 4,0 | 11,19 | 4,64 | 4,58 | 6,80 |
| 0,10 | 0,5 | 11,94 | 3,94 | 2,77 | 6,21 |
| 0,10 | 1,0 | 11,30 | 4,27 | 3,05 | 6,20 |
| 0,10 | 2,0 | 12,28 | 4,12 | 3,48 | 6,63 |
| 0,10 | 3,0 | 11,24 | 4,59 | 3,79 | 6,54 |
| 0,10 | 4,0 | 11,32 | 4,37 | 3,61 | 6,43 |
| 0,30 | 0,5 | 12,76 | 3,63 | 1,34 | 5,91 |
| 0,30 | 1,0 | 10,94 | 3,40 | 1,71 | 5,35 |
| 0,30 | 2,0 | 11,13 | 4,03 | 2,44 | 5,86 |
| 0,30 | 3,0 | 11,31 | 3,98 | 3,13 | 6,14 |
| 0,30 | 4,0 | 11,74 | 4,36 | 3,36 | 6,49 |
| 1,00 | 0,5 | 26,95 | 16,08 | 10,18 | 17,73 |
| 1,00 | 1,0 | 16,74 | 5,84 | 2,07 | 8,22 |
| 1,00 | 2,0 | 12,03 | 3,94 | 1,88 | 5,95 |
| 1,00 | 3,0 | 12,15 | 4,04 | 2,50 | 6,23 |
| 1,00 | 4,0 | 12,14 | 4,21 | 2,76 | 6,37 |

Quartett, Simulated Annealing (12 Abstimm-Instanzen, 4 Läufe je Zelle; gewählt je Budget die kleinste Lücke):

| Starttemperatur (· Skala) | Abkühlung (Zehnerpotenzen) | Lücke bei 30 · n (%) | Lücke bei 100 · n (%) | Lücke bei 1.000 · n (%) | Lücke bei 5.000 · n (%) |
|---|---|---|---|---|---|
| 0,03 | 0,5 | 25,88 | 7,14 | 3,97 | 4,63 |
| 0,03 | 1,0 | 26,33 | 6,76 | 4,21 | 5,10 |
| 0,03 | 2,0 | 27,07 | 7,22 | 4,33 | 5,45 |
| 0,03 | 3,0 | 28,12 | 7,70 | 4,56 | 5,56 |
| 0,03 | 4,0 | 27,44 | 8,11 | 4,76 | 5,71 |
| 0,10 | 0,5 | 28,95 | 7,26 | 2,40 | 1,75 |
| 0,10 | 1,0 | 28,55 | 7,46 | 2,71 | 2,12 |
| 0,10 | 2,0 | 29,12 | 6,73 | 3,42 | 2,94 |
| 0,10 | 3,0 | 30,43 | 7,34 | 3,70 | 3,12 |
| 0,10 | 4,0 | 29,77 | 7,19 | 4,40 | 3,27 |
| 0,30 | 0,5 | 27,94 | 7,70 | 1,38 | 0,53 |
| 0,30 | 1,0 | 28,70 | 6,87 | 1,67 | 0,34 |
| 0,30 | 2,0 | 25,42 | 7,51 | 2,25 | 0,91 |
| 0,30 | 3,0 | 29,49 | 7,43 | 3,00 | 1,03 |
| 0,30 | 4,0 | 28,47 | 7,10 | 3,19 | 1,52 |
| 1,00 | 0,5 | 45,09 | 22,53 | 10,69 | 7,77 |
| 1,00 | 1,0 | 33,74 | 10,76 | 1,90 | 0,71 |
| 1,00 | 2,0 | 28,40 | 7,11 | 1,96 | 0,81 |
| 1,00 | 3,0 | 28,72 | 6,89 | 2,20 | 0,86 |
| 1,00 | 4,0 | 29,65 | 6,96 | 2,51 | 1,09 |

Quartett, memetischer Algorithmus (dieselben Instanzen; gewählt: kleinstes Mittel der vier Budgets):

| Größe der Population (MA) | Lücke bei 30 · n (%) | Lücke bei 100 · n (%) | Lücke bei 1.000 · n (%) | Lücke bei 5.000 · n (%) | Mittel der vier (%) |
|---|---|---|---|---|---|
| 2 | 24,63 | 5,89 | 1,81 | 0,64 | 8,24 |
| 4 | 24,63 | 5,89 | 1,89 | 0,52 | 8,23 |
| 8 | 24,63 | 5,89 | 1,96 | 0,59 | 8,26 |
| 16 | 24,63 | 5,89 | 2,06 | 0,60 | 8,29 |
<!-- /TABELLE:abstimmung -->

### Zitierte Zahlen zur Zählweise (nicht in dieser Demo gemessen)

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

* Lücke 75,72 % (voll), 3,78 % (Listen, k = 8), 1,11 % (Warteschlange) (3-opt, n = 50, Abstieg mit Neustarts, 800.000 Auswertungen, steilster Abstieg über die je Zählweise bewerteten Züge, 18 Instanzen, 72 Läufe; Referenz nicht bewiesen optimal).
* Rang 1: 2-opt in 27 (voll), 33 (Listen), 28 (Warteschlange) von je 36 Zellen; 3-opt in 0 von 108 (n = 30, 50, 100; zwei Verfahren; drei Familien; zwei Budgets).
* Kendall τ 0,67 bis 0,89 (voll / Listen), 0,56 bis 0,78 (voll / Warteschlange), 0,61 bis 0,94 (Listen / Warteschlange) (sechs Gruppen aus Stadtzahl und Verfahren, je Mittel über sechs Zellen).
* Schrittkosten 72.475 (voll) und 8.604 (Warteschlange) für 3-opt, 1.175 und 94 für 2-opt (n = 50).

Fundstelle: README der Demo „Die Nachbarschaft ändert die Landschaft“, Abschnitt „Zitierbare Zahlen mit Voraussetzung, Fundstelle und Test“. Dort heißt „Listen“: mindestens eine neue Kante verbindet eine Stadt mit einem ihrer k = 8 nächsten Nachbarn, jeder Zug zählt einmal.

Die zitierten Messungen benutzen den steilsten Abstieg, diese Demo die erste Verbesserung; die Zahlen sind deshalb kein Vergleich mit den Tabellen oben, sondern der Beleg, dass die Zählweise in die Aussage gehört.

Rechenbeispiel der App dazu (gesetzte Zahlen, keine Messung): 2-opt hat n(n − 3)/2 Züge je Schritt in der Zählweise voll und 2(n − 3) je Stadt mit der Warteschlange (405 und 54 bei n = 30, 4.850 und 194 bei n = 100; Verhältnis n/4). Im gesetzten Modell „Lücke nach s Schritten = max(Boden, 50 · ρˢ)“ mit ρ = 9/10 und Boden 1 für 2-opt, ρ = 4/5 und Boden 1/2 für 3-opt, n = 100 und 2.000.000 Auswertungen erlaubt „voll“ 412 und 3 Schritte (Lücken 1 und 25,6: 2-opt besser), die Warteschlange 10.309 und 53 Schritte (Lücken 1 und 0,5: 3-opt besser).

### No-Free-Lunch im Kleinen

Suchraum {0, 1, 2, 3}, Werte {0, 1, 2}, alle 3⁴ = 81 Funktionen aufgezählt; Verfahren A tastet von links nach rechts ab, Verfahren B beginnt bei Punkt 3, geht bei Wert 0 zum Punkt 2, sonst zum Punkt 0, danach zum kleinsten noch nicht besuchten Punkt. Über alle 81 Funktionen ist die Verteilung des besten Werts nach m = 1 bis 4 Auswertungen für beide gleich (Minimum 0 nach zwei Auswertungen in 45 von 81). Auf den 41 glatten Funktionen (Nachbarwerte unterscheiden sich um höchstens 1) findet A das Minimum 0 nach zwei Auswertungen in 17, B in 20 Funktionen, nach drei in 21 gegen 23. Die glatte Klasse ist nicht unter Vertauschen der Punkte abgeschlossen (ihr Abschluss hat 67 Funktionen). Das ist die Aussage der Quelle im Kleinen und dient als Rahmen (ohne Annahmen über die Klasse keine Vorhersage); eine Aussage über Rundtouren ist es nicht, und eine Erklärung der Messungen oben auch nicht.

### Zahl → Test

| Zahl oder Aussage | Test | Art |
|---|---|---|
| alle Tabellen zwischen den Marken | `tests/test_claims.py::test_readme_tabellen_stammen_aus_den_daten` | exakt gegen die eingefrorenen Dateien |
| Kurzfassung: 12 von 12 Zellen, 63 von 63; 11 von 12, 2 / 16 / 27 | `test_kurzfassung_trio` | exakt gegen die Dateien |
| 29,5 / 40,8 / 51,6 % und 15,6 / 27,0 / 32,3 %; Lesebeispiel 35,0 / 34,3 / 33,2 %; 16 von 18 Zeilen | `test_kurzfassung_gruppen`, `test_mehr_laeufe_weniger_kippen_mit_benannten_ausnahmen` | exakt gegen die Dateien |
| größter Abstand Formel gegen Messung 4,4 und 4,1 Punkte, bei 30 Läufen 7,5; Median 33,4 Läufe, 25 von 63 | `test_kippformel_abstand_und_laeufebedarf` | exakt gegen die Dateien |
| 46,0 / 81,0 / 93,7 %; 3,2 / 7,9 / 9,5 %; 44 von 63 gleichauf | `test_kurzfassung_mass` | exakt gegen die Dateien |
| 3,2 / 27,0 / 55,6 %; 11,94 gegen 11,90 % | `test_kurzfassung_einstellung` | exakt gegen die Dateien |
| 4,326 %, 73,5 %, 62,0 %, 77,9 %, 1,45 % und 4,42 %, Modellwerte | `tests/test_handbeispiel.py`, `tests/test_oracle_rangtest.py` | exakt, gegen Aufzählung und scipy |
| 74,0 / 74,7 / 74,1 %, 66,9 %, 48,1 %; 97 / 89 / 33 %; 52 % | `test_kurzfassung_mehrfachtest` | exakt gegen die Dateien; die Pool-Erwartung zusätzlich als Band gegen einen zweiten Zufallsstrom (`tests/test_data.py`) |
| vier Budgets, vier Rangfolgen; SA auf dem Gitter; 8 %; Abstände 0,5 und 0,05 Punkte; Gruppenfaktoren | `test_kurzfassung_quartett` | exakt gegen die Dateien |
| Kosten des ersten Abstiegs 28 · n bis 183 · n | `test_kosten_des_ersten_abstiegs` | exakt gegen die Dateien |
| zitierte Zahlen der Demo „Die Nachbarschaft ändert die Landschaft“ | `test_zitate_stehen_in_der_quelle` | Zeichenfolge gegen deren README, wenn der Ordner daneben liegt (sonst übersprungen) |
| No-Free-Lunch: 81, 45, 41, 17 gegen 20, 21 gegen 23, 67; gesetztes Modell 412, 3, 10.309, 53 | `tests/test_handbeispiel.py` | exakt |
| Die eingefrorenen Läufe selbst | `tests/test_data.py` (Stichproben neu gerechnet), `tools/vgk_make_daten.py --check` | Band (Anteil gleicher Läufe) im Test, exakt im Werkzeug auf der Bau-Plattform |

Nicht im Test, nur Messung dieser README: die Rechenzeiten und die Laufzeit der Tests.

## Ehrliche Grenzen

* **Eigene Umsetzungen, kleine Instanzen.** Alle Aussagen gelten für diese Umsetzungen, 20 bis 80 Orte, diese Budgets, die Zählweise voll und die erste Verbesserung mit Zufallsreihenfolge. Sie sind keine Aussagen über die Verfahrensklassen; ein genetischer Algorithmus mit Lokalsuche oder ein Simulated Annealing mit anderer Nachbarschaft kann sich anders verhalten.
* **Das Trio ist mit Absicht ungleich.** Der Dauergewinner entsteht auch dadurch, dass der genetische Algorithmus keine Lokalsuche hat und SA in der Standard-Einstellung nicht abgestimmt ist. Mit der abgestimmten Einstellung gilt die Ordnung HC < SA < GA nur noch in 11 von 12 Zellen, und HC liegt bei 10.000 Auswertungen nur noch auf 36 von 63 Instanzen allein vorn.
* **Die Abstimmung ist grob:** 20 Einstellungen, 15 und 12 Instanzen, im Quartett 4 Läufe je Zelle; bei 1.000 · n liegt die Wahl am Rand des Rasters. Eine feinere Abstimmung könnte SA weiter nach vorn bringen; HC, ILS und MA haben außer der Populationsgröße keine abgestimmte Einstellung.
* **Budgets teilen sich Läufe.** Bei HC, GA, ILS und MA sind die kleineren Budgets Zwischenstände desselben Laufs; der Vergleich zweier Budgets ist deshalb weniger verrauscht als mit getrennten Läufen.
* **Der Pool hat 60 Läufe.** Die Erwartung „mit Gleichständen“ gilt für Gruppen, die ohne Zurücklegen aus diesen 60 Läufen gezogen sind; je Instanz ist sie aus 4.000 Ziehungen geschätzt (Standardfehler höchstens 0,4 Punkte je Instanz).
* **Die beste bekannte Länge ist nicht bewiesen optimal.** Für 8 bis 12 Orte prüfen die Tests die Verfahren gegen Held-Karp; für die Messreihen gibt es keinen Beweis.
* **Die Kippformel** ist eine Näherung für ein Paar von Verfahren; für die Ordnung dreier Verfahren gibt es hier keine Formel.
* **Nicht im Browser geprüft** ist, was unter „Tests“ so genannt ist.

## Tests

235 Tests (`python -m pytest tests -q`), Laufzeit beim Bau 96 bis 131 Sekunden mit vier Prozessen (`-n 4`, drei Läufe auf einer mitbenutzten Maschine; in einem Prozess nicht gemessen); die Zeiten sind Messungen dieser README, kein Test.

| Art | Datei | Tests |
|---|---|---|
| Handbeispiele des Plans als exakte Tests (No-Free-Lunch, Mann-Whitney 5 gegen 5, Kippen mit Brüchen, Maße, Zugzahlen, gesetztes Modell, Kendall τ, Gleichstände) | `tests/test_handbeispiel.py` | 25 |
| Orakel: Zugmenge gegen Aufzählung über Kantenmengen, Längenänderung gegen Neubewertung, Abstieg gegen alle Umkehrungen, Double-Bridge (vier Kanten), Held-Karp gegen Aufzählung, lange Läufe gegen Held-Karp | `tests/test_oracle_methods.py` | 20 |
| Orakel: p-Wert und Ränge gegen scipy, Verteilung von U gegen Aufzählung und scipy (exakt), Verwerfungswahrscheinlichkeit gegen Aufzählung, Gleichstandsmodell und Kippformel gegen Simulation, Kendall τ gegen scipy | `tests/test_oracle_rangtest.py` | 14 |
| Zähltest: Handzählung am Quadrat und zählender Umschlag um die Abstandsmatrix für alle fünf Verfahren | `tests/test_zaehlung.py` | 16 |
| Zufallsstrom bitgleich zur SplitMix64-Vorlage | `tests/test_zufall.py` | 9 |
| Kopie-Test der gemeinsamen Basis und des Zufallsgenerators | `tests/test_kopie.py` | 5 |
| Eigenschaften (Umnummerieren, Skalieren, Vertauschen, identische Verfahren, Monotonie, Bonferroni, Budget, kein toter Zweig) | `tests/test_properties.py` | 25 |
| Randfälle | `tests/test_edge_cases.py` | 13 |
| Eingefrorene Messreihen: Aufbau, Stimmigkeit, Stichproben neu gerechnet, Pool-Erwartung gegen einen zweiten Zufallsstrom | `tests/test_data.py` | 23 |
| Claims: Zahlen und Tabellen der README | `tests/test_claims.py` | 16 |
| Verdikte an handgesetzten Werten | `tests/test_verdicts.py` | 9 |
| App: Smoke-Test der Vorlage, Szenarien je Preset, Layout, Presets, Footer, Laufzeit-Importe, Neuladen der Module | `tests/test_app.py`, `tests/test_app_szenarien.py`, `tests/test_layout.py`, `tests/test_presets.py`, `tests/test_footer.py`, `tests/test_runtime_imports.py`, `tests/test_modul_frisch.py` | 3 + 18 + 22 + 7 + 2 + 1 + 7 |

Exakt gerechnete Größen (Zugzahlen, Brüche der Handbeispiele, Verteilung von U) werden exakt verglichen, Gleitkommagrößen mit relativer Toleranz 1e-9, Zufallsanteile als Band mit Standardfehler. Die Tabellen der README werden gegen die eingefrorenen Dateien verglichen, nicht neu gemessen; neu gerechnet werden nur Stichproben der Läufe (als Band: mindestens 90 % der Läufe gleich). Es gibt keine Mutationstests. Was die Tests nicht prüfen: die Messreihen als Ganzes und die Darstellung im Browser.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-App |
| `vgk_basis.py` | gemeinsame Instanzbasis der Reihe (unveränderte Kopie, Kopie-Test) |
| `vgk_rng.py` | SplitMix64 (unveränderte Kopie der Vorlage) |
| `vgk_zufall.py` | dieselbe Zufallsfolge blockweise mit numpy (bitgleich, Test) |
| `vgk_methods.py` | die fünf Verfahren, 2-opt-Abstieg, Double-Bridge, Zählung der Auswertungen |
| `vgk_messung.py` | Aufbau der Messreihen: Instanzen, Zufalls-Seeds, ein Lauf als Funktion |
| `vgk_compare.py` | Maße, Rangfolgen mit Gleichständen, Kendall τ_b, Kippen, Kippformel |
| `vgk_rangtest.py` | Mann-Whitney als Normalnäherung, exakte Verteilung von U, Gleichstandsmodell, Nullvergleich aus dem Pool |
| `vgk_nfl.py` | No-Free-Lunch im Kleinen (Aufzählung) |
| `vgk_daten.py` | lädt die eingefrorenen Messreihen |
| `vgk_evaluation.py` | Auswertungen der Experimente, alle Verdikte als reine Funktionen |
| `vgk_texts.py` | Texte, die wortgleich in App und README stehen |
| `vgk_constants.py`, `vgk_presets.py`, `vgk_layout.py`, `vgk_visualization.py` | Konstanten und Presets, Permalink, fester Kopf, Abbildungen |
| `modul_frisch.py` | lädt geänderte Hilfsmodule nach einem Update neu |
| `data/vgk_trio.json`, `data/vgk_quartett.json`, `data/vgk_nulltest.json`, `data/vgk_abstimmung.json` | eingefrorene Messreihen, je mit Quelle, Stand und Voraussetzung |
| `tools/vgk_make_daten.py` | rechnet die Messreihen in Teilen vor, `--check` rechnet Stichproben neu |
| `tools/vgk_readme_tabellen.py` | schreibt und prüft die Tabellen dieser README |
| `tools/teile/` | Zwischenstände der Vorrechnung (in `.gitignore`, nicht im Repo) |
| `tests/` | siehe oben |

## 🚧 Bewusst nicht enthalten und nicht gemessen

* **Kein Umschalter für die Zählweise.** Listen und Warteschlange sind hier nicht gemessen, auch nicht für das Quartett; die Zahlen dazu sind Zitate.
* **Andere Tests:** Wilcoxon für gepaarte Stichproben, t-Test, Friedman-Test und ein Vorzeichentest sind nicht gemessen (Läufe verschiedener Verfahren sind hier nicht gepaart). Holm und Benjamini-Hochberg zeigt die Demo „Mehrfachtests und Gewinnerfluch“; hier steht nur die Zeile mit Bonferroni.
* **Erwartung mit Gleichständen unter Bonferroni** ist nicht vorgerechnet (nur die Linie ohne Gleichstände und die Messung).
* **Größere Pools** (mehr als 60 Läufe), Budgets über 10.000 im Trio und über 5.000 · n im Quartett, mehr als 80 Orte: nicht gemessen.
* **Die Familie Straßennetz im Trio** und mehr als vier Familien: nicht gemessen.
* **Maße „Fläche“ und „Anteil ≤ 2 %“ für das Quartett,** Läufegruppen und Mehrfachtest am Quartett: nicht gemessen.
* **Steilster Abstieg, andere Zugreihenfolgen, andere Nachbarschaften** (Or-opt, 3-opt): nicht gemessen; dazu die Demo „Die Nachbarschaft ändert die Landschaft“.
* **LKH, EAX, Concorde** sind nicht verwendet; über sie sagt die Demo nichts.
* **Die Präzisierung des No-Free-Lunch-Satzes** auf unter Permutation abgeschlossene Funktionsmengen ist nur im Kleinen nachgerechnet, die Quelle dazu nicht gelesen.
* **PDF-Export:** nicht enthalten. **Kein Mutationstest.**

## Quellen

* D. H. Wolpert, W. G. Macready, „No Free Lunch Theorems for Optimization“, IEEE Transactions on Evolutionary Computation 1(1), 1997, 67–82. **Gelesen:** Abstract und Einleitung. Sinngemäß: Gemittelt über alle Optimierungsprobleme ist die Durchschnittsleistung je zweier Verfahren gleich.
* C. Igel, M. Toussaint (2003, Information Processing Letters 86, 317–321) zur Präzisierung auf unter Permutation abgeschlossene Funktionsmengen: **nicht gelesen**, nur aus Sekundärquellen bekannt.
* D. Vermetten u. a., arXiv 2402.09800 (2024): „Large-scale Benchmarking of Metaphor-based Optimization Heuristics“ (Vermetten, Doerr, Wang, Kononova, Bäck): 294 metapherbasierte Implementierungen auf den BBOB-Testfunktionen (stetige Testfunktionen, nicht Rundtouren); untersucht, wie sich Budget und Leistungsmaß auf den Vergleich auswirken. **Gelesen:** Zusammenfassung und ein Auszug; nicht auf Rundtouren übertragen.
* Die Ursprungsarbeiten zu Mann-Whitney, Bonferroni, Kendall τ, 2-opt, Simulated Annealing, Iterated Local Search und memetischen Algorithmen sind **nicht gelesen** und deshalb nicht zitiert; die Namen sind die der Lehrbücher.

## Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pip install -r requirements-dev.txt`, dann `pytest tests/ -q`.

Gebaut mit Streamlit, Plotly, pandas und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html).
