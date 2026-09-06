"""Transformation 3 : le Rappeleur reçoit son canal, il ne construit plus rien."""

from collections.abc import Iterable, Mapping
from datetime import date

from rappels.canaux import Canal
from rappels.regles import detecter


class Rappeleur:
    def __init__(self, canal: Canal) -> None:
        self._canal = canal
        self.envoyes: list[str] = []

    def rappeler(self, taches: Iterable[Mapping], jour: date) -> int:
        rappels = detecter(taches, jour)
        for rappel in rappels:
            self._canal.envoyer(rappel)
            self.envoyes.append(rappel.message)
        return len(rappels)
