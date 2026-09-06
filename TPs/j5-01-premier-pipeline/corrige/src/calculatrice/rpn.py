"""Évaluation d'expressions en notation polonaise inverse : « 3 4 + 2 * » vaut 14."""

from collections.abc import Callable

from calculatrice.modele import ExpressionInvalide
from calculatrice.operations import additionner, diviser, multiplier, puissance, soustraire

OPERATEURS: dict[str, Callable[[float, float], float]] = {
    "+": additionner,
    "-": soustraire,
    "*": multiplier,
    "/": diviser,
    "^": puissance,
}


def evaluer_rpn(expression: str) -> float:
    """Évalue une expression RPN. Les jetons sont séparés par des espaces."""
    pile: list[float] = []
    for position, jeton in enumerate(expression.split(), start=1):
        if jeton in OPERATEURS:
            if len(pile) < 2:
                raise ExpressionInvalide(f"jeton {position} : {jeton!r} attend deux opérandes")
            b, a = pile.pop(), pile.pop()
            pile.append(OPERATEURS[jeton](a, b))
        else:
            try:
                pile.append(float(jeton))
            except ValueError:
                raise ExpressionInvalide(f"jeton {position} : {jeton!r} inconnu") from None
    if len(pile) != 1:
        raise ExpressionInvalide(f"il reste {len(pile)} valeur(s) sur la pile, attendu 1")
    return pile[0]
