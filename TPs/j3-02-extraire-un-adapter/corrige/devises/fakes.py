"""Des sources de taux qui fonctionnent vraiment — sans réseau.

Ce sont des fakes, pas des mocks : on peut les interroger autant de fois qu'on
veut, elles se comportent comme une vraie source.
"""

from devises.modele import DeviseInconnue, SourceIndisponible


class SourceEnMemoire:
    def __init__(self, taux_par_base: dict[str, dict[str, float]]) -> None:
        self._taux = taux_par_base
        self.appels = 0

    def taux(self, base: str) -> dict[str, float]:
        self.appels += 1
        if base not in self._taux:
            raise DeviseInconnue(f"aucun taux depuis {base}")
        return dict(self._taux[base])


class SourceEnPanne:
    def taux(self, base: str) -> dict[str, float]:
        raise SourceIndisponible(f"base {base} : source en panne")
