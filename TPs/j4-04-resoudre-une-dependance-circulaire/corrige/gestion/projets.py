"""Projets et règles de rattachement. Dépend du modèle, et de rien d'autre."""

from collections.abc import Iterable, Mapping

from gestion.modele import Projet, ProjetInconnu, Tache


def projet_de(projets: Mapping[str, Projet], nom: str) -> Projet:
    try:
        return projets[nom]
    except KeyError:
        raise ProjetInconnu(f"projet inconnu : {nom!r} (connus : {sorted(projets)})") from None


def est_actif(projets: Mapping[str, Projet], nom: str) -> bool:
    """Vrai si le projet existe et n'est pas archivé."""
    return nom in projets and not projets[nom].archive


def peut_etre_terminee(tache: Tache, projets: Mapping[str, Projet]) -> bool:
    return not tache.terminee and est_actif(projets, tache.projet)


def taches_du_projet(taches: Iterable[Tache], nom: str) -> list[Tache]:
    return sorted((t for t in taches if t.projet == nom), key=lambda t: (t.echeance, t.id))
