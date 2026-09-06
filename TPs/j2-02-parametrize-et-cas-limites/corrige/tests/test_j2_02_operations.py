"""Tests des opérations de la calculatrice.

Les huit tests de départ sont devenus des cas paramétrés, des cas limites, des
erreurs attendues et des propriétés. Lisez `pytest --collect-only -q` : c'est
la spécification du module.
"""

import pytest
from calcul.operations import (
    DivisionParZero,
    ErreurCalcul,
    HorsDomaine,
    SerieVide,
    additionner,
    arrondir,
    diviser,
    moyenne,
    multiplier,
    pourcentage,
    puissance,
    racine,
    soustraire,
)

# --- 1. Fusion par paramétrisation --------------------------------------------------


@pytest.mark.parametrize(
    ("a", "b", "attendu"),
    [
        pytest.param(2, 3, 5, id="petits_entiers"),
        pytest.param(10, 20, 30, id="dizaines"),
        pytest.param(100, 200, 300, id="centaines"),
        pytest.param(-2, 3, 1, id="un_negatif"),
        pytest.param(-2, -3, -5, id="deux_negatifs"),
        pytest.param(0, 0, 0, id="zeros"),
        pytest.param(0.1, 0.2, 0.3, id="flottants"),
        pytest.param(1e15, 1, 1e15 + 1, id="grand_nombre"),
    ],
)
def test_additionner(a, b, attendu):
    assert additionner(a, b) == pytest.approx(attendu)


@pytest.mark.parametrize(
    ("a", "b", "attendu"),
    [
        pytest.param(10, 4, 2.5, id="non_entier"),
        pytest.param(10, 5, 2, id="entier"),
        pytest.param(1, 3, 0.3333333333, id="periodique"),
        pytest.param(-10, 4, -2.5, id="negatif"),
        pytest.param(0, 7, 0, id="zero_dividende"),
        pytest.param(1, 1e-9, 1e9, id="tres_petit_diviseur"),
    ],
)
def test_diviser(a, b, attendu):
    assert diviser(a, b) == pytest.approx(attendu)


@pytest.mark.parametrize(
    ("base", "exposant", "attendu"),
    [
        pytest.param(2, 10, 1024, id="entier"),
        pytest.param(2, -1, 0.5, id="exposant_negatif"),
        pytest.param(9, 0.5, 3, id="exposant_fractionnaire"),
        pytest.param(5, 0, 1, id="exposant_nul"),
        pytest.param(0, 0, 1, id="zero_puissance_zero"),
        pytest.param(-2, 3, -8, id="base_negative_exposant_impair"),
        pytest.param(-2, 2, 4, id="base_negative_exposant_pair"),
    ],
)
def test_puissance(base, exposant, attendu):
    assert puissance(base, exposant) == pytest.approx(attendu)


@pytest.mark.parametrize(
    ("x", "attendu"),
    [
        pytest.param(16, 4, id="carre_parfait"),
        pytest.param(2, 1.4142135624, id="irrationnel"),
        pytest.param(0, 0, id="zero"),
        pytest.param(0.25, 0.5, id="inferieur_a_un"),
    ],
)
def test_racine(x, attendu):
    assert racine(x) == pytest.approx(attendu)


# --- 2. Cas limites ----------------------------------------------------------------


@pytest.mark.parametrize(
    ("x", "decimales", "attendu"),
    [
        pytest.param(3.14159, 2, 3.14, id="troncature"),
        pytest.param(3.14159, 0, 3.0, id="zero_decimale"),
        pytest.param(2.5, 0, 3.0, id="demi_vers_le_haut"),
        pytest.param(2.675, 2, 2.68, id="demi_vers_le_haut_binaire"),
        pytest.param(-2.5, 0, -3.0, id="demi_negatif"),
        pytest.param(1.005, 2, 1.01, id="le_classique_du_web"),
        pytest.param(7, 2, 7.0, id="entier_inchange"),
    ],
)
def test_arrondir_commercial(x, decimales, attendu):
    """Deux de ces cas échouaient avec `round()` : 2.5 → 2 (au pair) et 2.675 → 2.67 (binaire)."""
    assert arrondir(x, decimales) == attendu


@pytest.mark.parametrize(
    ("valeurs", "attendue"),
    [
        pytest.param([1, 2, 3], 2, id="trois_valeurs"),
        pytest.param([5], 5, id="une_seule_valeur"),
        pytest.param([4, 4, 4, 4], 4, id="serie_constante"),
        pytest.param([-1, 1], 0, id="negatifs"),
        pytest.param([0.1, 0.2, 0.3], 0.2, id="flottants"),
    ],
)
def test_moyenne(valeurs, attendue):
    assert moyenne(valeurs) == pytest.approx(attendue)


@pytest.mark.parametrize(
    ("valeur", "taux", "attendu"),
    [(200, 15, 30), (200, 0, 0), (200, 100, 200), (50, 200, 100), (80, 12.5, 10)],
)
def test_pourcentage(valeur, taux, attendu):
    assert pourcentage(valeur, taux) == pytest.approx(attendu)


# --- 3. Erreurs attendues ----------------------------------------------------------


@pytest.mark.parametrize("b", [0, 0.0, -0.0], ids=["int", "float", "moins_zero"])
def test_division_par_zero(b):
    with pytest.raises(DivisionParZero, match="10 / 0"):
        diviser(10, b)


@pytest.mark.parametrize("x", [-1, -1e-9, -1e9], ids=["moins_un", "presque_zero", "tres_negatif"])
def test_racine_d_un_negatif(x):
    with pytest.raises(HorsDomaine, match="argument négatif"):
        racine(x)


def test_racine_de_zero_est_dans_le_domaine():
    assert racine(0) == 0


def test_moyenne_d_une_serie_vide():
    with pytest.raises(SerieVide, match="série vide"):
        moyenne([])


def test_zero_puissance_negative_est_une_division_par_zero():
    with pytest.raises(DivisionParZero):
        puissance(0, -1)


def test_arrondir_a_un_nombre_negatif_de_decimales():
    with pytest.raises(HorsDomaine, match="decimales = -1"):
        arrondir(1.5, -1)


def test_toutes_les_erreurs_derivent_d_une_racine_commune():
    for exc in (DivisionParZero, HorsDomaine, SerieVide):
        assert issubclass(exc, ErreurCalcul)


# --- 4. Propriétés (sans valeur de référence) -----------------------------------------

COUPLES = [(2, 3), (-4, 7), (0.1, 0.2), (1e6, 1e-6), (0, 0)]


@pytest.mark.parametrize(("a", "b"), COUPLES)
def test_l_addition_est_commutative(a, b):
    assert additionner(a, b) == additionner(b, a)


@pytest.mark.parametrize(("a", "b"), COUPLES)
def test_soustraire_annule_additionner(a, b):
    assert soustraire(additionner(a, b), b) == pytest.approx(a)


@pytest.mark.parametrize(("a", "b"), [couple for couple in COUPLES if couple[1] != 0])
def test_multiplier_annule_diviser(a, b):
    assert multiplier(diviser(a, b), b) == pytest.approx(a)


@pytest.mark.parametrize("x", [0, 1, 2, 10, 0.5, 1e6])
def test_la_racine_au_carre_redonne_l_argument(x):
    assert puissance(racine(x), 2) == pytest.approx(x)


@pytest.mark.parametrize("valeurs", [[3, 1, 2], [10, -4, 7, 2], [0.5], [-1, -1, -1]])
def test_la_moyenne_est_toujours_entre_le_min_et_le_max(valeurs):
    assert min(valeurs) <= moyenne(valeurs) <= max(valeurs)


@pytest.mark.parametrize("x", [3.14159, 2.675, 2.5, -7.777])
def test_arrondir_est_idempotent(x):
    une_fois = arrondir(x)
    assert arrondir(une_fois) == une_fois


@pytest.mark.parametrize("valeur", [0, 1, 37.5, -12])
def test_cent_pour_cent_redonne_la_valeur(valeur):
    assert pourcentage(valeur, 100) == pytest.approx(valeur)


# --- 5. Le contrat de type -------------------------------------------------------------


@pytest.mark.parametrize(
    "resultat",
    [
        additionner(2, 3),
        soustraire(5, 2),
        multiplier(2, 3),
        diviser(6, 3),
        puissance(2, 3),
        racine(16),
        arrondir(7, 0),
        moyenne([1, 2, 3]),
    ],
    ids=[
        "additionner",
        "soustraire",
        "multiplier",
        "diviser",
        "puissance",
        "racine",
        "arrondir",
        "moyenne",
    ],
)
def test_le_resultat_est_toujours_un_float(resultat):
    """Le code de départ renvoyait `int` pour `additionner(2, 3)` : la docstring mentait."""
    assert type(resultat) is float


# --- Pour aller plus loin ---------------------------------------------------------------


def test_une_racine_cubique_de_negatif_n_a_pas_de_resultat_reel():
    """`(-8) ** (1/3)` renvoie un complexe en Python. Le code de départ le laissait passer."""
    with pytest.raises(HorsDomaine, match="pas de résultat réel"):
        puissance(-8, 1 / 3)
