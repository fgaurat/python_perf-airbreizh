"""Tests de la calculatrice.

La moitié de ces tests vérifient des **erreurs attendues**. C'est normal : un
module qui refuse proprement les entrées invalides a autant de comportements à
protéger côté échec que côté succès.
"""

import pytest
from calculatrice import (
    DivisionParZero,
    ErreurCalcul,
    ExpressionInvalide,
    FonctionInconnue,
    HorsDomaine,
    OperationImpossible,
    calculer,
)

# --- Le cas nominal ------------------------------------------------------------


@pytest.mark.parametrize(
    ("expression", "attendu"),
    [
        ("3 + 4 * 2", 11.0),
        ("(3 + 4) * 2", 14.0),
        ("10 / 4", 2.5),
        ("-(2 + 3) * 2", -10.0),
        ("2 * -3", -6.0),
        ("racine(16) / (1 + 1)", 2.0),
        ("log(1)", 0.0),
        ("1.5 + .5", 2.0),
        ("42", 42.0),
    ],
)
def test_calculs_valides(expression, attendu):
    assert calculer(expression) == pytest.approx(attendu)


# --- Les neuf situations, une exception chacune ---------------------------------


@pytest.mark.parametrize("expression", ["", "   ", "\t\n"])
def test_expression_vide(expression):
    with pytest.raises(ExpressionInvalide, match="expression vide"):
        calculer(expression)


def test_caractere_inconnu_indique_la_position():
    with pytest.raises(ExpressionInvalide, match=r"position 2 : caractère inattendu '\$'"):
        calculer("3 $ 4")


def test_nombre_malforme():
    with pytest.raises(ExpressionInvalide, match="nombre malformé '3.4.5'"):
        calculer("3.4.5")


def test_parenthese_non_fermee():
    with pytest.raises(ExpressionInvalide, match=r"attendu '\)', trouvé \"fin de l'expression\""):
        calculer("(3 + 4")


def test_operateur_sans_operande():
    with pytest.raises(ExpressionInvalide, match="fin de l'expression : attendu un nombre"):
        calculer("3 +")


def test_deux_operateurs_consecutifs():
    with pytest.raises(ExpressionInvalide, match=r"opérande attendu, trouvé '\*'"):
        calculer("3 * * 4")


def test_jetons_en_trop():
    with pytest.raises(ExpressionInvalide, match="'4' inattendu après la fin"):
        calculer("3 4")


def test_division_par_zero():
    with pytest.raises(DivisionParZero, match="10 / 0"):
        calculer("10 / 0")


@pytest.mark.parametrize("expression", ["racine(-4)", "log(0)", "log(-1)"])
def test_hors_domaine(expression):
    with pytest.raises(HorsDomaine, match="n'est pas défini"):
        calculer(expression)


def test_fonction_inconnue_liste_les_fonctions_disponibles():
    with pytest.raises(FonctionInconnue, match=r"'sinus' \(disponibles : \['log', 'racine'\]\)"):
        calculer("sinus(1)")


# --- Ce que les sentinelles faisaient passer -----------------------------------


@pytest.mark.parametrize("expression", ["10 / 0 + 5", "racine(-4) + 10", "sinus(1) + 3"])
def test_une_erreur_au_milieu_d_une_expression_ne_produit_pas_de_resultat(expression):
    """Le code de départ renvoyait 5.0, 9.0 et 3.0 : les sentinelles participaient au calcul."""
    with pytest.raises(ErreurCalcul):
        calculer(expression)


# --- La hiérarchie -------------------------------------------------------------


def test_un_seul_except_attrape_tout():
    for expression in ["", "3 $", "10 / 0", "racine(-1)", "sinus(1)"]:
        with pytest.raises(ErreurCalcul):
            calculer(expression)


def test_les_erreurs_de_calcul_se_distinguent_des_erreurs_de_syntaxe():
    with pytest.raises(OperationImpossible):
        calculer("1 / 0")
    with pytest.raises(ExpressionInvalide):
        calculer("1 /")


def test_la_cause_d_origine_est_conservee():
    with pytest.raises(DivisionParZero) as info:
        calculer("1 / 0")
    assert isinstance(info.value.__cause__, ZeroDivisionError)

    with pytest.raises(HorsDomaine) as info:
        calculer("racine(-1)")
    assert isinstance(info.value.__cause__, ValueError)


def test_la_signature_est_honnete():
    """`calculer` renvoie toujours un float : plus de None, de 0.0, de -1 ni de False."""
    assert isinstance(calculer("2 + 2"), float)
