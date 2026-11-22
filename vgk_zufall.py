"""Gepufferter Zufallsstrom: dieselbe SplitMix64-Folge wie `vgk_rng.SplitMix64`, aber blockweise mit numpy erzeugt.

Die Verfahren ziehen Millionen Zufallszahlen; `Strom` liefert sie aus einem Puffer. `tests/test_zufall.py` prüft, dass die Folge
bitgleich zu `vgk_rng.SplitMix64` ist (der k-te Wert ist die Mischfunktion von Zufalls-Seed + k · GAMMA, also unabhängig vom Puffer)."""

import numpy as np

MASKE = (1 << 64) - 1
GAMMA = 0x9E3779B97F4A7C15
_C1 = np.uint64(0xBF58476D1CE4E5B9)
_C2 = np.uint64(0x94D049BB133111EB)
_ZWEI_HOCH_53 = float(1 << 53)


def block(seed: int, start: int, anzahl: int) -> np.ndarray:
    """Die Werte Nummer start+1 … start+anzahl der SplitMix64-Folge zum Zufalls-Seed (uint64)."""
    k = np.arange(start + 1, start + anzahl + 1, dtype=np.uint64)
    with np.errstate(over="ignore"):
        z = np.uint64(seed & MASKE) + k * np.uint64(GAMMA)
        z = (z ^ (z >> np.uint64(30))) * _C1
        z = (z ^ (z >> np.uint64(27))) * _C2
        return z ^ (z >> np.uint64(31))


class Strom:
    """Zufallsstrom mit der Schnittstelle, die die Verfahren brauchen. Jede Methode verbraucht eine feste Zahl von Werten."""

    PUFFER = 4096

    def __init__(self, seed: int):
        self.seed = seed & MASKE
        self.gezogen = 0          # Zahl der bisher verbrauchten Werte der Folge
        self._puffer = []
        self._i = 0

    def next_u64(self) -> int:
        if self._i >= len(self._puffer):
            self._puffer = block(self.seed, self.gezogen, self.PUFFER).tolist()
            self._i = 0
        wert = self._puffer[self._i]
        self._i += 1
        self.gezogen += 1
        return wert

    def werte(self, anzahl: int) -> list:
        """Die nächsten `anzahl` Werte als Liste ganzer Zahlen."""
        rest = self._puffer[self._i:]
        if len(rest) >= anzahl:
            self._i += anzahl
            self.gezogen += anzahl
            return rest[:anzahl]
        neu = block(self.seed, self.gezogen + len(rest), anzahl - len(rest)).tolist()
        self._puffer, self._i = [], 0
        self.gezogen += anzahl
        return rest + neu

    def random(self) -> float:
        return (self.next_u64() >> 11) / _ZWEI_HOCH_53

    def below(self, n: int) -> int:
        return self.next_u64() % n

    def shuffle(self, items: list) -> None:
        for i in range(len(items) - 1, 0, -1):
            j = self.next_u64() % (i + 1)
            items[i], items[j] = items[j], items[i]

    def permutation(self, m: int) -> list:
        """Zufällige Reihenfolge von 0..m-1: m Werte ziehen, stabil nach ihnen sortieren (bei gleichen Werten gewinnt der kleinere Index)."""
        return np.argsort(np.array(self.werte(m), dtype=np.uint64), kind="stable").tolist()


def permutation_referenz(rng, m: int) -> list:
    """Dieselbe Reihenfolge wie `Strom.permutation`, mit einem beliebigen Generator, der `next_u64` hat (Rechenweg ohne numpy, für Tests)."""
    werte = [rng.next_u64() for _ in range(m)]
    return sorted(range(m), key=werte.__getitem__)
