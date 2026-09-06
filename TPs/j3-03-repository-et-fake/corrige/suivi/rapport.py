"""Rapport hebdomadaire : retards, avancement, charge, tâches dormantes.

Plus une ligne de SQL : les règles sont des compréhensions sur des `Tache`.
"""

from collections import Counter
from datetime import date

from suivi.modele import JOURS_AVANT_DORMANCE, ProjetInconnu
from suivi.ports import DepotTaches

SEUIL_SURCHARGE = 5


class Rapport:
    def __init__(self, depot: DepotTaches) -> None:
        self._depot = depot

    def en_retard(self, jour: date) -> list[str]:
        """Titres des tâches en retard, par échéance puis identifiant."""
        retards = [t for t in self._depot.toutes() if t.est_en_retard(jour)]
        return [t.titre for t in sorted(retards, key=lambda t: (t.echeance, t.id))]

    def avancement(self, projet: str) -> int:
        """Pourcentage de tâches terminées du projet, arrondi. Un projet inconnu est une erreur."""
        taches = [t for t in self._depot.toutes() if t.projet == projet]
        if not taches:
            raise ProjetInconnu(f"aucune tâche dans le projet {projet!r}")
        return round(100 * sum(t.terminee for t in taches) / len(taches))

    def surcharges(self, seuil: int = SEUIL_SURCHARGE) -> list[str]:
        """Personnes ayant strictement plus de `seuil` tâches non terminées, triées par nom."""
        charges = Counter(t.assignee for t in self._depot.toutes() if not t.terminee)
        return sorted(personne for personne, n in charges.items() if n > seuil)

    def dormantes(self, jour: date, jours: int = JOURS_AVANT_DORMANCE) -> list[str]:
        """Titres des tâches dormantes, par date de création puis identifiant."""
        vieilles = [t for t in self._depot.toutes() if t.est_dormante(jour, jours)]
        return [t.titre for t in sorted(vieilles, key=lambda t: (t.creee_le, t.id))]
