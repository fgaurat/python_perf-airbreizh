"""Le contrat d'un dépôt de tâches : deux méthodes, aucune règle métier."""

from typing import Protocol

from suivi.modele import Tache


class DepotTaches(Protocol):
    def toutes(self) -> list[Tache]:
        """Toutes les tâches, par identifiant croissant."""
        ...

    def par_id(self, identifiant: int) -> Tache:
        """La tâche portant cet identifiant, ou `TacheInconnue`."""
        ...
