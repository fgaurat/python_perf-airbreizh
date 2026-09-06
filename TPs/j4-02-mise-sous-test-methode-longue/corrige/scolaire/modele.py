"""Constantes, objets de valeur et exceptions du bulletin. N'importe rien du projet."""

from dataclasses import dataclass

NOTE_SUR = 20.0
COEFFICIENTS = {"maths": 4, "francais": 4, "histoire": 2, "anglais": 3, "sport": 1, "arts": 1}
OPTIONS = {"latin": 0.1, "grec": 0.1, "musique": 0.05}  # bonus par point au-dessus de 10
BONUS_MAX = 2.0
NIVEAUX = ("6e", "5e", "4e", "3e")
SEUIL_FELICITATIONS = 16.0
SEUIL_COMPLIMENTS = 14.0
SEUIL_ENCOURAGEMENTS = 12.0
SEUIL_AVERTISSEMENT = 8.0
SEUIL_ABSENCES = 10
ECART_PROGRESSION = 0.5
COEF_MATIERE_INCONNUE = 1


class ErreurBulletin(ValueError):
    """Racine des erreurs du bulletin. Dérive de ValueError pour les appelants historiques."""


@dataclass(frozen=True)
class Periode:
    annee: int
    numero: int


@dataclass(frozen=True)
class MoyenneMatiere:
    matiere: str
    moyenne: float
    nb_notes: int


@dataclass(frozen=True)
class Absences:
    demi_journees: int
    avertissement: bool
