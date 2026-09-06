"""Mise en forme textuelle."""

from gestion.projets import DELAI_ALERTE_JOURS  # ← importe projets
from gestion.taches import Tache  # ← importe taches


def en_ligne(tache: Tache) -> str:
    """Ligne d'une tâche : case à cocher, titre, échéance."""
    case = "x" if tache.terminee else " "
    return f"[{case}] #{tache.id} {tache.titre} (pour le {tache.echeance.isoformat()})"


def en_titre(nom: str, projet: dict) -> str:
    """Titre d'un projet : nom, état, délai d'alerte."""
    etat = "archivé" if projet["archive"] else "actif"
    return f"== {nom} ({etat}, alerte à {DELAI_ALERTE_JOURS} j) =="
