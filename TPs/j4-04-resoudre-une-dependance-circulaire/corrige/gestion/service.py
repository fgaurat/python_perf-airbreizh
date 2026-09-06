"""La couche du dessus : combine projets et affichage. Seul module à importer les deux."""

from collections.abc import Iterable, Mapping
from datetime import date

from gestion import affichage, projets
from gestion.modele import Projet, ProjetInconnu, Tache


def resume(catalogue: Mapping[str, Projet], taches: Iterable[Tache], jour: date) -> list[str]:
    """Une ligne de titre par projet, suivie de ses tâches par échéance."""
    taches = list(taches)
    inconnus = sorted({t.projet for t in taches} - set(catalogue))
    if inconnus:
        raise ProjetInconnu(f"tâches rattachées à des projets inconnus : {inconnus}")
    lignes = []
    for nom in sorted(catalogue):
        lignes.append(affichage.en_titre(catalogue[nom]))
        lignes += [affichage.en_ligne(t, jour) for t in projets.taches_du_projet(taches, nom)]
    return lignes
