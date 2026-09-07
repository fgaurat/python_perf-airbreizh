import math

import pytest

from geo.cercle import Cercle


@pytest.mark.parametrize(
    ("rayon", "attendue"),
    [
        pytest.param(1, math.pi, id="unite"),
        pytest.param(2, 4 * math.pi, id="rayon_2"),
        pytest.param(0, 0, id="nul"),
        pytest.param(0.5, math.pi / 4, id="flottant"),
    ],
)
def test_surface(rayon, attendue):
    assert Cercle(rayon).surface == pytest.approx(attendue)


def test_surface_en_dur_est_illisible():
    # Le même test que "rayon_2", écrit avec le nombre en dur.
    # Il passe, mais personne ne saura d'où vient 12.566370614359172.
    assert Cercle(2).surface == 12.566370614359172


def test_rayon_par_defaut():
    assert Cercle().rayon == 1


def test_setter_rayon_modifie_la_surface():
    c = Cercle(1)
    c.rayon = 3
    assert c.surface == pytest.approx(9 * math.pi)
