"""Objets de valeur des rappels. N'importe rien du projet."""

from dataclasses import dataclass
from enum import Enum

SEUIL_URGENT_JOURS = 7


class EnvoiImpossible(Exception):
    """Le canal n'a pas pu délivrer le message."""


class Niveau(Enum):
    AUJOURD_HUI = "AUJOURD'HUI"
    RETARD = "RETARD"
    URGENT = "URGENT"


@dataclass(frozen=True)
class Rappel:
    titre: str
    assignee: str
    retard: int
    niveau: Niveau

    @property
    def message(self) -> str:
        quand = "à faire aujourd'hui" if self.retard == 0 else f"{self.retard} j de retard"
        return f"[{self.niveau.value}] {self.titre} — {self.assignee} — {quand}"
