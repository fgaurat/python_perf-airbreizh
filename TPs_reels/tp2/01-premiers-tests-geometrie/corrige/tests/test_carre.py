from geo.carre import Carre
from geo.rectangle import Rectangle


def test_surface():
    assert Carre(3).surface == 9


def test_setter_cote_modifie_la_surface():
    c = Carre(2)
    c.cote = 5
    assert c.surface == 25


def test_cote_suit_la_longueur():
    c = Carre(2)
    c.longueur = 7
    assert c.cote == 7


def test_carre_egal_rectangle_de_memes_dimensions():
    # Décision : l'égalité porte sur les dimensions, pas sur la classe.
    assert Carre(2) == Rectangle(2, 2)
