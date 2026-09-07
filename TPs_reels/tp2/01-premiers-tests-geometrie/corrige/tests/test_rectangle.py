import pytest

from geo.erreurs import DimensionInvalide
from geo.rectangle import Rectangle

# ---------------------------------------------------------------- nominal


@pytest.mark.parametrize(
    ("longueur", "largeur", "attendue"),
    [
        pytest.param(2, 3, 6, id="entiers"),
        pytest.param(0, 3, 0, id="largeur_nulle"),
        pytest.param(2.5, 2, 5.0, id="flottant"),
        pytest.param(10_000, 10_000, 100_000_000, id="grand"),
    ],
)
def test_surface(longueur, largeur, attendue):
    assert Rectangle(longueur, largeur).surface == attendue


def test_memes_dimensions_sont_egaux():
    assert Rectangle(2, 3) == Rectangle(2, 3)


def test_dimensions_differentes_ne_sont_pas_egaux():
    assert Rectangle(2, 3) != Rectangle(3, 2)


def test_comparaison_avec_autre_type():
    assert Rectangle(2, 3) != "2;3"


def test_setter_longueur_modifie_la_surface():
    r = Rectangle(2, 3)
    r.longueur = 4
    assert r.surface == 12


# ---------------------------------------------------------------- build_from_str


def test_build_from_str_nominal():
    assert Rectangle.build_from_str("2;3") == Rectangle(2, 3)


def test_build_from_str_tolere_les_espaces():
    assert Rectangle.build_from_str(" 2 ; 3 ") == Rectangle(2, 3)


@pytest.mark.parametrize(
    "chaine",
    [
        pytest.param("2;3;4", id="trop_de_valeurs"),
        pytest.param("2", id="pas_assez_de_valeurs"),
        pytest.param("", id="vide"),
        pytest.param("a;b", id="non_numerique"),
        pytest.param("2,5;3", id="virgule_decimale"),
    ],
)
def test_build_from_str_refuse_les_chaines_mal_formees(chaine):
    with pytest.raises(DimensionInvalide):
        Rectangle.build_from_str(chaine)


def test_build_from_str_message_explique_le_format():
    with pytest.raises(DimensionInvalide, match="longueur;largeur"):
        Rectangle.build_from_str("2;3;4")


# ---------------------------------------------------------------- erreurs attendues


def test_setter_longueur_negative_refusee():
    r = Rectangle(2, 3)
    with pytest.raises(DimensionInvalide, match="longueur"):
        r.longueur = -1


def test_setter_largeur_negative_refusee():
    r = Rectangle(2, 3)
    with pytest.raises(DimensionInvalide, match="largeur"):
        r.largeur = -1


@pytest.mark.parametrize(
    ("longueur", "largeur"),
    [
        pytest.param(-2, 3, id="longueur_negative"),
        pytest.param(2, -3, id="largeur_negative"),
        pytest.param(-2, -3, id="les_deux"),
    ],
)
def test_constructeur_refuse_les_dimensions_negatives(longueur, largeur):
    with pytest.raises(DimensionInvalide):
        Rectangle(longueur, largeur)


def test_erreur_refusee_ne_modifie_pas_le_rectangle():
    r = Rectangle(2, 3)
    with pytest.raises(DimensionInvalide):
        r.longueur = -1
    assert r.longueur == 2


def test_dimension_nulle_acceptee():
    # Décision : un rectangle dégénéré n'est pas une erreur.
    assert Rectangle(0, 0).surface == 0


# ---------------------------------------------------------------- cas limites


def test_rectangle_non_hashable():
    # __eq__ est défini, __hash__ vaut donc None : un objet mutable comparé par
    # valeur ne peut pas être une clé. Le test documente ce comportement.
    with pytest.raises(TypeError, match="unhashable"):
        {Rectangle(2, 3)}


# ---------------------------------------------------------------- état global


def test_compteur():
    Rectangle(1, 1)
    Rectangle(1, 1)
    assert Rectangle.get_cpt() == 2


def test_compteur_repart_de_zero_grace_a_la_fixture():
    # Sans la fixture autouse de conftest.py, ce test dépendrait de test_compteur.
    assert Rectangle.get_cpt() == 0
