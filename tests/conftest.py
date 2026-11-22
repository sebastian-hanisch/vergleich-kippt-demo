"""Gemeinsame Fixtures: Mini-Instanzen, an denen die Einheiten von Hand geprüft werden."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vgk_basis as basis  # noqa: E402


@pytest.fixture
def quadrat():
    """Vier Orte auf den Ecken eines Quadrats mit Seite 1000: der Umfang (Länge 4000) ist die kürzeste Rundtour,
    die zwei Touren mit gekreuzten Diagonalen sind 2000 + 2000·√2 lang."""
    return basis.abstaende([(0, 0), (1000, 0), (1000, 1000), (0, 1000)])
