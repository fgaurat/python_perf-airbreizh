"""Températures : Celsius, Fahrenheit, Kelvin."""

from convertisseur.modele import UniteInconnue

DECIMALES = 4
UNITES_TEMPERATURE = {"C", "F", "K"}


def _en_celsius(valeur: float, de: str) -> float:
    if de == "C":
        return valeur
    if de == "F":
        return (valeur - 32) * 5 / 9
    if de == "K":
        return valeur - 273.15
    raise UniteInconnue(f"unité de température inconnue : {de!r}")


def _depuis_celsius(celsius: float, vers: str) -> float:
    if vers == "C":
        return celsius
    if vers == "F":
        return celsius * 9 / 5 + 32
    if vers == "K":
        return celsius + 273.15
    raise UniteInconnue(f"unité de température inconnue : {vers!r}")


def convertir_temperature(valeur: float, de: str, vers: str) -> float:
    return round(_depuis_celsius(_en_celsius(valeur, de), vers), DECIMALES)
