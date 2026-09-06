"""Opérations élémentaires. Toutes retournent un float ou lèvent une ErreurCalcul."""

import math

from calculatrice.modele import DivisionParZero, HorsDomaine


def additionner(a: float, b: float) -> float:
    return float(a + b)


def soustraire(a: float, b: float) -> float:
    return float(a - b)


def multiplier(a: float, b: float) -> float:
    return float(a * b)


def diviser(a: float, b: float) -> float:
    if b == 0:
        raise DivisionParZero(f"{a} / 0")
    return a / b


def puissance(base: float, exposant: float) -> float:
    if base == 0 and exposant < 0:
        raise DivisionParZero(f"0 ** {exposant}")
    resultat = base**exposant
    if isinstance(resultat, complex):
        raise HorsDomaine(f"{base} ** {exposant} n'a pas de résultat réel")
    return float(resultat)


def racine(x: float) -> float:
    if x < 0:
        raise HorsDomaine(f"racine({x}) : argument négatif")
    return math.sqrt(x)
