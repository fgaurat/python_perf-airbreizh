"""Projets et règles de rattachement."""

from gestion.affichage import en_titre  # ← importe affichage
from gestion.taches import Tache  # ← importe taches

DELAI_ALERTE_JOURS = 3


class ProjetInconnu(Exception):
    """Aucun projet ne porte ce nom."""


def est_actif(projets: dict, nom: str) -> bool:
    """Vrai si le projet existe et n'est pas archivé."""
    return nom in projets and not projets[nom]["archive"]


def taches_du_projet(taches: list[Tache], nom: str) -> list[Tache]:
    return [t for t in taches if t.projet == nom]


def resume(projets: dict, taches: list[Tache]) -> list[str]:
    """Une ligne de titre par projet, suivie de ses tâches."""
    lignes = []
    for nom in sorted(projets):
        lignes.append(en_titre(nom, projets[nom]))
        lignes += [t.ligne() for t in taches_du_projet(taches, nom)]
    return lignes
