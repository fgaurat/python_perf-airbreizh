"""Le fake : un dictionnaire. Même contrat que `DepotSqlite`, sans base."""

from collections.abc import Iterable

from suivi.modele import Tache, TacheInconnue


class DepotEnMemoire:
    def __init__(self, taches: Iterable[Tache] = ()) -> None:
        self._taches = {t.id: t for t in taches}

    def toutes(self) -> list[Tache]:
        return [self._taches[i] for i in sorted(self._taches)]

    def par_id(self, identifiant: int) -> Tache:
        try:
            return self._taches[identifiant]
        except KeyError:
            raise TacheInconnue(f"aucune tâche n°{identifiant}") from None

    def ajouter(self, tache: Tache) -> None:
        self._taches[tache.id] = tache
