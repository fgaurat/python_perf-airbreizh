"""Tests des chiffres romains, dans l'ordre où ils ont été écrits.

Chaque section correspond à un cycle Red / Green / Refactor. Lisez le fichier
de haut en bas : il raconte les décisions prises au fur et à mesure.
"""

import pytest
from nombres.romains import (
    MAXIMUM,
    MINIMUM,
    ErreurRomain,
    HorsBornes,
    RomainInvalide,
    arabe,
    romain,
)

# --- Cycle 1 — le cas trivial ---------------------------------------------------------
# Décisions : la fonction s'appelle `romain`, reçoit un int, retourne une str.


def test_un():
    assert romain(1) == "I"


# --- Cycle 2 — la répétition ----------------------------------------------------------


@pytest.mark.parametrize(
    ("n", "attendu"), [(2, "II"), (3, "III"), (10, "X"), (20, "XX"), (30, "XXX")]
)
def test_les_symboles_se_repetent(n, attendu):
    assert romain(n) == attendu


# --- Cycle 3 — la notation soustractive -----------------------------------------------
# Décision : forme canonique, 4 s'écrit IV et jamais IIII (même si les horloges disent IIII).


@pytest.mark.parametrize(
    ("n", "attendu"),
    [(4, "IV"), (9, "IX"), (40, "XL"), (90, "XC"), (400, "CD"), (900, "CM")],
)
def test_les_six_formes_soustractives(n, attendu):
    assert romain(n) == attendu


@pytest.mark.parametrize(
    ("n", "attendu"),
    [
        pytest.param(14, "XIV", id="dizaine_plus_soustractif"),
        pytest.param(1994, "MCMXCIV", id="l_exemple_de_l_enonce"),
        pytest.param(2024, "MMXXIV", id="une_annee"),
        pytest.param(1666, "MDCLXVI", id="tous_les_symboles_une_fois"),
        pytest.param(3888, "MMMDCCCLXXXVIII", id="le_plus_long"),
        pytest.param(3999, "MMMCMXCIX", id="le_plus_grand"),
    ],
)
def test_les_nombres_composes(n, attendu):
    assert romain(n) == attendu


# --- Cycle 4 — les cas limites ----------------------------------------------------------
# Décisions : pas de zéro (les Romains n'en avaient pas), pas de négatif, 3999 au plus.


def test_les_bornes_sont_incluses():
    assert romain(MINIMUM) == "I"
    assert romain(MAXIMUM) == "MMMCMXCIX"


@pytest.mark.parametrize(
    "n", [0, -1, -1994, 4000, 10_000], ids=["zero", "-1", "-1994", "4000", "10000"]
)
def test_hors_bornes(n):
    with pytest.raises(HorsBornes, match=f"{n} : attendu entre 1 et 3999"):
        romain(n)


@pytest.mark.parametrize("valeur", [3.0, "3", True, None], ids=["float", "str", "bool", "None"])
def test_un_non_entier_est_une_erreur_de_programmation(valeur):
    """`TypeError`, pas `ErreurRomain` : une donnée invalide, non — un bug de l'appelant."""
    with pytest.raises(TypeError):
        romain(valeur)


# --- Cycle 5 — le sens inverse ----------------------------------------------------------
# Décisions : `arabe` est strict sur la forme canonique, tolérant sur la casse et les espaces.


@pytest.mark.parametrize(
    ("texte", "attendu"),
    [("I", 1), ("IV", 4), ("IX", 9), ("XIV", 14), ("MCMXCIV", 1994), ("MMMCMXCIX", 3999)],
)
def test_arabe(texte, attendu):
    assert arabe(texte) == attendu


@pytest.mark.parametrize("texte", ["xiv", " XIV ", "Xiv\n"], ids=["minuscules", "espaces", "mixte"])
def test_arabe_tolere_la_casse_et_les_espaces(texte):
    assert arabe(texte) == 14


@pytest.mark.parametrize("texte", ["", "   "], ids=["vide", "blancs"])
def test_une_chaine_vide_est_refusee(texte):
    with pytest.raises(RomainInvalide, match="chaîne vide"):
        arabe(texte)


def test_un_symbole_inconnu_indique_sa_position():
    with pytest.raises(RomainInvalide, match="symbole inattendu 'A' en position 2"):
        arabe("XIA")


@pytest.mark.parametrize(
    "texte",
    [
        pytest.param("IIII", id="quatre_repetitions"),
        pytest.param("VV", id="cinq_repete"),
        pytest.param("IC", id="soustraction_interdite"),
        pytest.param("XCX", id="ordre_incoherent"),
        pytest.param("MMMM", id="au_dela_du_maximum"),
    ],
)
def test_une_forme_non_canonique_est_refusee(texte):
    with pytest.raises(RomainInvalide):
        arabe(texte)


def test_le_message_donne_la_forme_canonique():
    with pytest.raises(RomainInvalide, match=r"'IIII' n'est pas la forme canonique de 4 \(IV\)"):
        arabe("IIII")


def test_toutes_les_erreurs_derivent_d_une_racine_commune():
    for exc in (HorsBornes, RomainInvalide):
        assert issubclass(exc, ErreurRomain)


# --- Cycle 6 — refactor et propriétés -----------------------------------------------------
# Le refactor a fait émerger `TABLE` ; les tests ci-dessus n'ont pas bougé.


def test_aller_retour_sur_tout_le_domaine():
    for n in range(MINIMUM, MAXIMUM + 1):
        assert arabe(romain(n)) == n


@pytest.mark.parametrize("n", [1, 49, 444, 999, 1494, 2999, 3888])
def test_seuls_les_sept_symboles_apparaissent(n):
    assert set(romain(n)) <= set("MDCLXVI")


@pytest.mark.parametrize("n", range(1, 4000, 37))
def test_jamais_quatre_symboles_identiques_consecutifs(n):
    texte = romain(n)
    assert all(symbole * 4 not in texte for symbole in "MDCLXVI")


@pytest.mark.parametrize("n", range(1, 4000, 41))
def test_v_l_et_d_ne_se_repetent_jamais(n):
    texte = romain(n)
    assert all(texte.count(symbole) <= 1 for symbole in "VLD")


def test_la_longueur_maximale_est_quinze():
    assert max(len(romain(n)) for n in range(MINIMUM, MAXIMUM + 1)) == 15


def test_le_resultat_est_deterministe():
    assert romain(1994) == romain(1994) == "MCMXCIV"
