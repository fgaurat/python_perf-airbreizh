"""Conversion d'unités : longueurs et températures."""

from convertisseur.longueurs import UNITES_LONGUEUR, convertir_longueur
from convertisseur.modele import ConversionImpossible, ErreurConversion, UniteInconnue
from convertisseur.temperatures import UNITES_TEMPERATURE, convertir_temperature

__all__ = [
    "ConversionImpossible",
    "ErreurConversion",
    "UniteInconnue",
    "convertir",
    "convertir_longueur",
    "convertir_temperature",
]


def convertir(valeur: float, de: str, vers: str) -> float:
    """Convertit `valeur` de l'unité `de` vers l'unité `vers`, quelle que soit la famille."""
    if de in UNITES_LONGUEUR and vers in UNITES_LONGUEUR:
        return convertir_longueur(valeur, de, vers)
    if de in UNITES_TEMPERATURE and vers in UNITES_TEMPERATURE:
        return convertir_temperature(valeur, de, vers)
    for unite in (de, vers):
        if unite not in UNITES_LONGUEUR | UNITES_TEMPERATURE:
            raise UniteInconnue(f"unité inconnue : {unite!r}")
    raise ConversionImpossible(f"{de} et {vers} ne sont pas de la même famille")
