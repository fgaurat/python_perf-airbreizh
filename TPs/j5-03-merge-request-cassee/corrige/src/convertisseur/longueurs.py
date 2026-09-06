"""Longueurs : métriques, impériales et marines.

Toutes les conversions passent par une table de facteurs vers le kilomètre.
"""

from convertisseur.modele import UniteInconnue

DECIMALES = 4
FACTEURS_KM = {
    "km": 1.0,
    "m": 0.001,
    "cm": 0.00001,
    "mm": 0.000001,
    "mi": 1.609344,
    "nmi": 1.852,  # mille nautique — MR !418
    "ft": 0.0003048,
    "in": 0.0000254,
}
UNITES_LONGUEUR = set(FACTEURS_KM)


def _via_base(valeur: float, de: str, vers: str, facteurs: dict[str, float]) -> float:
    """Convertit en passant par l'unité de base de la table.

    L'arrondi est appliqué UNE SEULE FOIS, sur le résultat final. Un arrondi
    intermédiaire sur la valeur en kilomètres écraserait les petites unités :
    1 pouce = 0,0000254 km, qui vaut 0 à quatre décimales. (MR !418)
    """
    return round(valeur * facteurs[de] / facteurs[vers], DECIMALES)


def convertir_longueur(valeur: float, de: str, vers: str) -> float:
    for unite in (de, vers):
        if unite not in FACTEURS_KM:
            raise UniteInconnue(f"unité de longueur inconnue : {unite!r}")
    return _via_base(valeur, de, vers, FACTEURS_KM)
