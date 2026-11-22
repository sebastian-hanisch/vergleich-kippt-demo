"""Der gepufferte Zufallsstrom liefert bitgleich die Folge von `vgk_rng.SplitMix64` (anderer Rechenweg: numpy-Block gegen Python-Ganzzahlen)."""

import pytest

from vgk_rng import SplitMix64
from vgk_zufall import Strom, block, permutation_referenz


@pytest.mark.parametrize("seed", [0, 1, 1234567, 2**64 - 1, 2**70 + 5])
def test_block_ist_die_splitmix_folge(seed):
    rng = SplitMix64(seed)
    assert block(seed, 0, 3000).tolist() == [rng.next_u64() for _ in range(3000)]


def test_block_ab_einer_spaeteren_stelle():
    rng = SplitMix64(99)
    folge = [rng.next_u64() for _ in range(500)]
    assert block(99, 137, 200).tolist() == folge[137:337]


def test_strom_mischt_einzelwerte_und_bloecke_ohne_luecke():
    s, r = Strom(42), SplitMix64(42)
    for schritt in range(40):
        assert s.next_u64() == r.next_u64()
        assert s.werte(schritt * 97) == [r.next_u64() for _ in range(schritt * 97)]
        assert s.below(17) == r.below(17)
        assert s.random() == r.random()
    assert s.gezogen == 40 * 3 + 97 * sum(range(40))


def test_shuffle_wie_die_vorlage():
    a, b = list(range(50)), list(range(50))
    Strom(7).shuffle(a)
    SplitMix64(7).shuffle(b)
    assert a == b and sorted(a) == list(range(50))


def test_permutation_gegen_sortieren_ohne_numpy():
    for m in (1, 2, 5, 170, 5000):
        s = Strom(3)
        s.below(5)
        r = SplitMix64(3)
        r.below(5)
        p = s.permutation(m)
        assert p == permutation_referenz(r, m) and sorted(p) == list(range(m))
        assert s.next_u64() == r.next_u64()
