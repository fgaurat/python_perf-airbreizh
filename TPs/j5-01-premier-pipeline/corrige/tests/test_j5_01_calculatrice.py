"""Tests du package calculatrice."""

import pytest

from calculatrice import (
    DivisionParZero,
    ErreurCalcul,
    ExpressionInvalide,
    HorsDomaine,
    additionner,
    diviser,
    evaluer_rpn,
    multiplier,
    puissance,
    racine,
    soustraire,
)


@pytest.mark.parametrize(("a", "b", "attendu"), [(2, 3, 5.0), (-2, 3, 1.0), (0.1, 0.2, 0.3)])
def test_additionner(a, b, attendu):
    assert additionner(a, b) == pytest.approx(attendu)


def test_soustraire():
    assert soustraire(5, 7) == -2.0


def test_multiplier():
    assert multiplier(1.5, 4) == 6.0


@pytest.mark.parametrize(("a", "b", "attendu"), [(10, 4, 2.5), (1, 3, 0.3333333333)])
def test_diviser(a, b, attendu):
    assert diviser(a, b) == pytest.approx(attendu)


def test_division_par_zero():
    with pytest.raises(DivisionParZero, match="10 / 0"):
        diviser(10, 0)


@pytest.mark.parametrize(
    ("base", "exposant", "attendu"), [(2, 10, 1024.0), (9, 0.5, 3.0), (5, 0, 1.0)]
)
def test_puissance(base, exposant, attendu):
    assert puissance(base, exposant) == pytest.approx(attendu)


def test_zero_puissance_negative():
    with pytest.raises(DivisionParZero):
        puissance(0, -1)


def test_puissance_complexe():
    with pytest.raises(HorsDomaine, match="pas de résultat réel"):
        puissance(-8, 1 / 3)


@pytest.mark.parametrize(("x", "attendu"), [(16, 4.0), (0, 0.0), (2, 1.4142135624)])
def test_racine(x, attendu):
    assert racine(x) == pytest.approx(attendu)


def test_racine_negative():
    with pytest.raises(HorsDomaine, match="argument négatif"):
        racine(-1)


@pytest.mark.parametrize(
    ("expression", "attendu"),
    [
        ("42", 42.0),
        ("3 4 +", 7.0),
        ("3 4 + 2 *", 14.0),
        ("5 1 2 + 4 * + 3 -", 14.0),
        ("2 3 ^", 8.0),
        ("10 4 /", 2.5),
        ("  3   4 +  ", 7.0),
    ],
)
def test_evaluer_rpn(expression, attendu):
    assert evaluer_rpn(expression) == pytest.approx(attendu)


@pytest.mark.parametrize(
    ("expression", "message"),
    [
        ("", "il reste 0 valeur"),
        ("3 +", "jeton 2 : '\\+' attend deux opérandes"),
        ("3 4", "il reste 2 valeur"),
        ("3 x +", "jeton 2 : 'x' inconnu"),
    ],
)
def test_expression_invalide(expression, message):
    with pytest.raises(ExpressionInvalide, match=message):
        evaluer_rpn(expression)


def test_division_par_zero_en_rpn():
    with pytest.raises(DivisionParZero):
        evaluer_rpn("1 0 /")


def test_toutes_les_erreurs_derivent_d_une_racine_commune():
    for exc in (DivisionParZero, HorsDomaine, ExpressionInvalide):
        assert issubclass(exc, ErreurCalcul)
