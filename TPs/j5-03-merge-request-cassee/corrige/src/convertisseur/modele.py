"""Exceptions du convertisseur."""


class ErreurConversion(Exception):
    """Racine des erreurs de conversion."""


class UniteInconnue(ErreurConversion):
    pass


class ConversionImpossible(ErreurConversion):
    """Les deux unités n'appartiennent pas à la même famille."""
