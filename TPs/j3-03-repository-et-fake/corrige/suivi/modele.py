"""Une tâche, et les règles élémentaires qui ne dépendent que d'elle."""

from dataclasses import dataclass
from datetime import date

JOURS_AVANT_DORMANCE = 30


class ErreurTodo(Exception):
    """Racine des erreurs du module."""


class TacheInconnue(ErreurTodo):
    pass


class ProjetInconnu(ErreurTodo):
    pass


@dataclass(frozen=True)
class Tache:
    id: int
    titre: str
    projet: str
    assignee: str
    creee_le: date
    echeance: date
    terminee: bool = False

    def est_en_retard(self, jour: date) -> bool:
        """Strictement après l'échéance : une tâche due aujourd'hui n'est pas en retard."""
        return not self.terminee and self.echeance < jour

    def age(self, jour: date) -> int:
        return (jour - self.creee_le).days

    def est_dormante(self, jour: date, jours: int = JOURS_AVANT_DORMANCE) -> bool:
        """Strictement plus de `jours` jours : à exactement `jours`, pas encore."""
        return not self.terminee and self.age(jour) > jours
