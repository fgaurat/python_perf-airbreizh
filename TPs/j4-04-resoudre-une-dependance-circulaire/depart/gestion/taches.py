"""Tâches de la todo-list."""

from dataclasses import dataclass
from datetime import date

from gestion.affichage import en_ligne  # ← importe affichage
from gestion.projets import est_actif  # ← importe projets


@dataclass
class Tache:
    """Une tâche rattachée à un projet."""

    id: int
    titre: str
    projet: str
    echeance: date
    terminee: bool = False

    def peut_etre_terminee(self, projets: dict) -> bool:
        """Vrai si le projet de la tâche est encore actif."""
        return not self.terminee and est_actif(projets, self.projet)

    def ligne(self) -> str:
        """Représentation textuelle de la tâche."""
        return en_ligne(self)
