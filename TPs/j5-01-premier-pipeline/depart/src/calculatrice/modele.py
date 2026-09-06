"""Exceptions de la calculatrice."""


class ErreurCalcul(Exception):
    """Racine des erreurs de la calculatrice."""


class DivisionParZero(ErreurCalcul):
    pass


class HorsDomaine(ErreurCalcul):
    """Argument hors du domaine de définition de l'opération."""


class ExpressionInvalide(ErreurCalcul):
    """Expression RPN mal formée."""
