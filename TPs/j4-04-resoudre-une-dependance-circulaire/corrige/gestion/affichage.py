"""Mise en forme textuelle. Dépend du modèle, et de rien d'autre."""

from datetime import date

from gestion.modele import DELAI_ALERTE_JOURS, Projet, Tache


def en_ligne(tache: Tache, jour: date | None = None) -> str:
    """Ligne d'une tâche : case à cocher, titre, échéance, et un « ! » si elle est à surveiller."""
    case = "x" if tache.terminee else " "
    alerte = " !" if jour is not None and tache.est_a_surveiller(jour) else ""
    return f"[{case}] #{tache.id} {tache.titre} (pour le {tache.echeance.isoformat()}){alerte}"


def en_titre(projet: Projet) -> str:
    etat = "archivé" if projet.archive else "actif"
    return f"== {projet.nom} ({etat}, alerte à {DELAI_ALERTE_JOURS} j) =="
