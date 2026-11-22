"""Vergleich von Verfahren aus Läufegruppen: Maße, Rangfolgen mit Gleichständen, Kendall τ_b, Kippen, Kippformel.

Begriffe: Lücke eines Laufs = (Länge − beste bekannte Länge) / beste bekannte Länge in Prozent. Ein Maß macht aus den Lücken einer
Läufegruppe eine Zahl („kleiner ist besser“). Die Rangfolge einer Instanz ist der Vektor der Ränge der Verfahren; Gleichstände bekommen
mittlere Ränge. Zwei Rangfolgen heißen verschieden, wenn die Rangvektoren nicht gleich sind."""

import math

import numpy as np

MASSE = ("mittel", "median", "bestes", "anteil", "flaeche")
MASS_TEXT = {
    "mittel": "Mittel der Lücke",
    "median": "Median der Lücke",
    "bestes": "bester Lauf (kleinste Lücke)",
    "anteil": "Anteil der Läufe mit Lücke ≤ 2 %",
    "flaeche": "Fläche unter der Laufzeitkurve",
}
ANTEIL_SCHWELLE = 2.0     # Prozent Lücke
STELLEN = 9               # Maßwerte werden vor dem Vergleich auf so viele Stellen gerundet (Gleichstand = gleich nach dem Runden)
D_FUENF_PROZENT = 1.9488  # d mit 2Φ(d)(1 − Φ(d)) = 0,05


def luecke(laengen, referenz):
    """Lücke in Prozent; `referenz` je Instanz (erste Achse)."""
    laengen = np.asarray(laengen, dtype=float)
    ref = np.asarray(referenz, dtype=float).reshape((-1,) + (1,) * (laengen.ndim - 1))
    return 100.0 * (laengen - ref) / ref


def mass_wert(luecken: np.ndarray, mass: str, flaechen: np.ndarray | None = None) -> np.ndarray:
    """Maß über die letzte Achse (die Läufe einer Gruppe), als „kleiner ist besser“. Beim Anteil ≤ 2 % ist das 1 − Anteil."""
    if mass == "mittel":
        wert = luecken.mean(axis=-1)
    elif mass == "median":
        wert = np.median(luecken, axis=-1)
    elif mass == "bestes":
        wert = luecken.min(axis=-1)
    elif mass == "anteil":
        wert = 1.0 - (luecken <= ANTEIL_SCHWELLE).mean(axis=-1)
    elif mass == "flaeche":
        if flaechen is None:
            raise ValueError("das Maß Fläche braucht die Flächenwerte der Läufe")
        wert = flaechen.mean(axis=-1)
    else:
        raise ValueError(f"unbekanntes Maß: {mass}")
    return np.round(wert, STELLEN)


def raenge(werte: np.ndarray) -> np.ndarray:
    """Ränge über die letzte Achse (1 = kleinster Wert), Gleichstände als mittlere Ränge."""
    werte = np.asarray(werte, dtype=float)
    kleiner = (werte[..., None, :] < werte[..., :, None]).sum(axis=-1)
    gleich = (werte[..., None, :] == werte[..., :, None]).sum(axis=-1)
    return kleiner + (gleich + 1) / 2.0


def kendall_tau_b(a, b):
    """Kendall τ_b zweier Wertevektoren; None, wenn einer von beiden nur Gleichstände hat (τ nicht definiert)."""
    a, b = [float(x) for x in a], [float(x) for x in b]
    gleich_ordnung = gegen = nur_a = nur_b = 0
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            da = (a[i] > a[j]) - (a[i] < a[j])
            db = (b[i] > b[j]) - (b[i] < b[j])
            if da and db:
                if da == db:
                    gleich_ordnung += 1
                else:
                    gegen += 1
            elif da:
                nur_a += 1
            elif db:
                nur_b += 1
    nenner = math.sqrt((gleich_ordnung + gegen + nur_a) * (gleich_ordnung + gegen + nur_b))
    if nenner == 0:
        return None
    return (gleich_ordnung - gegen) / nenner


def ordnung_text(namen, werte) -> str:
    """„HC < SA = GA“: Verfahren nach dem Wert, Gleichstände mit Gleichheitszeichen."""
    werte = [round(float(w), STELLEN) for w in werte]
    paare = sorted(zip(werte, range(len(namen))))
    text = namen[paare[0][1]]
    for (w0, _), (w1, k) in zip(paare, paare[1:]):
        text += (" = " if w1 == w0 else " < ") + namen[k]
    return text


def gruppen(feld: np.ndarray, r: int) -> np.ndarray:
    """(Instanzen, Läufe) -> (Instanzen, G, r): die Läufe in ihrer Reihenfolge in G = Läufe // r getrennte Gruppen geteilt."""
    zahl = feld.shape[1] // r
    return feld[:, : zahl * r].reshape(feld.shape[0], zahl, r)


def gruppen_raenge(luecken: list, r: int, mass: str = "mittel", flaechen: list | None = None) -> np.ndarray:
    """Rangvektoren (Instanzen, Gruppen, Verfahren): je Gruppe von r Läufen die Rangfolge der Verfahren nach dem Maß."""
    werte = [mass_wert(gruppen(x, r), mass, None if flaechen is None else gruppen(flaechen[k], r)) for k, x in enumerate(luecken)]
    return raenge(np.stack(werte, axis=-1))


def kippen_gruppen(luecken: list, r: int, mass: str = "mittel", flaechen: list | None = None) -> dict:
    """Wie oft ordnen zwei Läufegruppen die Verfahren verschieden? Alle Gruppenpaare je Instanz.

    Rückgabe: `verschieden` (Anteil je Instanz), `strikt` (nur bei genau zwei Verfahren: Anteil der Paare mit strikt entgegengesetzter
    Ordnung), `gleichstand` (Anteil der Gruppen mit mindestens einem Gleichstand), `paare` (Zahl der Gruppenpaare je Instanz)."""
    rang = gruppen_raenge(luecken, r, mass, flaechen)
    zahl = rang.shape[1]
    if zahl < 2:
        raise ValueError("mindestens zwei Gruppen nötig")
    g, h = np.triu_indices(zahl, k=1)
    anders = (rang[:, g, :] != rang[:, h, :]).any(axis=-1)
    sortiert = np.sort(rang, axis=-1)
    aus = {"verschieden": anders.mean(axis=1), "paare": len(g), "gruppen": zahl,
           "gleichstand": (sortiert[..., 1:] == sortiert[..., :-1]).any(axis=-1).mean(axis=1)}
    if rang.shape[-1] == 2:
        zeichen = np.sign(rang[..., 0] - rang[..., 1])
        aus["strikt"] = (zeichen[:, g] * zeichen[:, h] < 0).mean(axis=1)
    return aus


def phi(z: float) -> float:
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def kippformel(delta: float, s1: float, s2: float, r: int):
    """Normalmodell für EIN Paar von Verfahren: Wahrscheinlichkeit, dass zwei unabhängige Gruppen zu r Läufen strikt entgegengesetzt
    ordnen, 2Φ(d)(1 − Φ(d)) mit d = |δ|√r / √(s1² + s2²). Ohne Streuung: 0 bei δ ≠ 0, None bei δ = 0 (nicht definiert)."""
    streuung = math.sqrt(s1 * s1 + s2 * s2)
    if streuung == 0.0:
        return None if delta == 0 else 0.0
    d = abs(delta) * math.sqrt(r) / streuung
    return 2.0 * phi(d) * (1.0 - phi(d))


def laeufe_fuer_fuenf_prozent(delta: float, s1: float, s2: float):
    """Läufe je Gruppe, ab denen die Kippformel höchstens 5 % gibt; None bei δ = 0 (keine Gruppengröße reicht)."""
    if delta == 0:
        return None
    return (D_FUENF_PROZENT * math.sqrt(s1 * s1 + s2 * s2) / abs(delta)) ** 2


def paar_kennzahlen(a: np.ndarray, b: np.ndarray) -> dict:
    """Je Instanz δ (Unterschied der Mittel), s1, s2 (Standardabweichung der Läufe, Stichprobe) für zwei Verfahren."""
    return {"delta": a.mean(axis=1) - b.mean(axis=1), "s1": a.std(axis=1, ddof=1), "s2": b.std(axis=1, ddof=1)}


def formel_mittel(a: np.ndarray, b: np.ndarray, r: int) -> tuple:
    """(Mittel der Kippformel über die Instanzen, auf denen sie definiert ist; Zahl der Instanzen ohne Definition)."""
    k = paar_kennzahlen(a, b)
    werte = [kippformel(float(d), float(s1), float(s2), r) for d, s1, s2 in zip(k["delta"], k["s1"], k["s2"])]
    gut = [w for w in werte if w is not None]
    return (sum(gut) / len(gut) if gut else float("nan")), len(werte) - len(gut)


def instanz_raenge(luecken: list, mass: str, flaechen: list | None = None) -> np.ndarray:
    """Rangvektoren (Instanzen, Verfahren) aus allen Läufen je Instanz."""
    werte = [mass_wert(x, mass, None if flaechen is None else flaechen[k]) for k, x in enumerate(luecken)]
    return raenge(np.stack(werte, axis=-1))


def anteil_andere_ordnung(rang_a: np.ndarray, rang_b: np.ndarray) -> float:
    """Anteil der Instanzen (erste Achse), deren Rangvektoren sich unterscheiden."""
    return float((rang_a != rang_b).any(axis=-1).mean())


def tau_mittel(rang_a: np.ndarray, rang_b: np.ndarray) -> tuple:
    """(mittleres τ_b über die Instanzen, auf denen es definiert ist; Zahl der Instanzen ohne Definition)."""
    werte = [kendall_tau_b(x, y) for x, y in zip(rang_a, rang_b)]
    gut = [w for w in werte if w is not None]
    return (sum(gut) / len(gut) if gut else float("nan")), len(werte) - len(gut)


def gruppenfaktor(mittel: dict) -> float:
    """F: die kleinere der mittleren Lücken von HC und SA geteilt durch die größere von ILS und MA (ohne Lücke der zweiten Gruppe: unendlich)."""
    oben = min(mittel["hc"], mittel["sa"])
    unten = max(mittel["ils"], mittel["ma"])
    return math.inf if unten == 0 else oben / unten


def kippen_binomial(pa, pb, r: int) -> dict:
    """Exaktes Beispiel mit Erfolg ja/nein je Lauf (mehr Erfolge ist besser): zwei Verfahren mit Erfolgswahrscheinlichkeit pa und pb,
    Gruppen zu r Läufen. Mit Brüchen als Eingabe sind die Ergebnisse Brüche.

    Rückgabe: P(A vorn), P(B vorn), P(Gleichstand) einer Gruppe; `verschieden` und `strikt` für zwei unabhängige Gruppen."""
    def pmf(k, p):
        return math.comb(r, k) * p ** k * (1 - p) ** (r - k)

    a_vorn = sum(pmf(i, pa) * pmf(j, pb) for i in range(r + 1) for j in range(r + 1) if i > j)
    b_vorn = sum(pmf(i, pa) * pmf(j, pb) for i in range(r + 1) for j in range(r + 1) if i < j)
    gleich = 1 - a_vorn - b_vorn
    return {"a_vorn": a_vorn, "b_vorn": b_vorn, "gleich": gleich,
            "verschieden": 1 - (a_vorn * a_vorn + b_vorn * b_vorn + gleich * gleich), "strikt": 2 * a_vorn * b_vorn}
