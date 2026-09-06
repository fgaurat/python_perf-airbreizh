"""Transformation 1 : la règle pure, extraite avant de toucher aux connexions."""

from collections.abc import Iterable, Mapping
from datetime import date

from rappels.modele import SEUIL_URGENT_JOURS, Niveau, Rappel


def niveau_pour(retard: int) -> Niveau | None:
    """Le niveau d'un retard en jours, ou None s'il n'y a rien à rappeler."""
    if retard >= SEUIL_URGENT_JOURS:
        return Niveau.URGENT
    if retard >= 1:
        return Niveau.RETARD
    if retard == 0:
        return Niveau.AUJOURD_HUI
    return None


def detecter(taches: Iterable[Mapping], jour: date) -> list[Rappel]:
    """Les rappels à envoyer, du plus en retard au moins en retard, puis par titre."""
    rappels = []
    for tache in taches:
        if tache.get("terminee"):
            continue
        retard = (jour - tache["echeance"]).days
        niveau = niveau_pour(retard)
        if niveau is not None:
            rappels.append(Rappel(tache["titre"], tache.get("assignee", "?"), retard, niveau))
    return sorted(rappels, key=lambda r: (-r.retard, r.titre))
