"""Opérations de la calculatrice.

Contrat commun à toutes les fonctions :

- les arguments sont des nombres (`int` ou `float`) ;
- **le résultat est toujours un `float`** ;
- toute opération sans résultat lève une `ErreurCalcul`, jamais `None`.

`arrondir` applique l'arrondi commercial (« au plus proche, le demi vers le
haut ») : 2,675 → 2,68 et 2,5 → 3.
"""

import math


class ErreurCalcul(Exception):
    """Racine des erreurs de la calculatrice."""


class DivisionParZero(ErreurCalcul):
    pass


class HorsDomaine(ErreurCalcul):
    """Argument hors du domaine de définition de l'opération."""


class SerieVide(ErreurCalcul):
    """La moyenne d'une série vide n'existe pas."""


def additionner(a: float, b: float) -> float:
    return a + b


def soustraire(a: float, b: float) -> float:
    return a - b


def multiplier(a: float, b: float) -> float:
    return a * b


def diviser(a: float, b: float) -> float:
    if b == 0:
        raise DivisionParZero(f"{a} / 0")
    return a / b


def puissance(base: float, exposant: float) -> float:
    return base**exposant


def racine(x: float) -> float:
    if x < 0:
        raise HorsDomaine(f"racine({x}) : argument négatif")
    return math.sqrt(x)


def pourcentage(valeur: float, taux: float) -> float:
    """`taux` % de `valeur` : pourcentage(200, 15) == 30."""
    return valeur * taux / 100


def arrondir(x: float, decimales: int = 2) -> float:
    """Arrondi commercial à `decimales` chiffres après la virgule."""
    return round(x, decimales)


def moyenne(valeurs: list[float]) -> float:
    if not valeurs:
        raise SerieVide("moyenne d'une série vide")
    return sum(valeurs) / len(valeurs)
