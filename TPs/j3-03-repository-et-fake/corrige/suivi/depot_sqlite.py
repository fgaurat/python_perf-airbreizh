"""Le seul fichier qui contient du SQL. Il lit des lignes, il construit des `Tache`."""

import sqlite3
from datetime import date
from pathlib import Path

from suivi.modele import Tache, TacheInconnue

SCHEMA = (Path(__file__).parent / "schema.sql").read_text(encoding="utf-8")
COLONNES = "id, titre, projet, assignee, creee_le, echeance, terminee"


def _vers_tache(ligne: tuple) -> Tache:
    id_, titre, projet, assignee, creee_le, echeance, terminee = ligne
    return Tache(
        id_,
        titre,
        projet,
        assignee,
        date.fromisoformat(creee_le),
        date.fromisoformat(echeance),
        bool(terminee),
    )


class DepotSqlite:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def toutes(self) -> list[Tache]:
        lignes = self._conn.execute(f"SELECT {COLONNES} FROM taches ORDER BY id").fetchall()
        return [_vers_tache(ligne) for ligne in lignes]

    def par_id(self, identifiant: int) -> Tache:
        ligne = self._conn.execute(
            f"SELECT {COLONNES} FROM taches WHERE id = ?", (identifiant,)
        ).fetchone()
        if ligne is None:
            raise TacheInconnue(f"aucune tâche n°{identifiant}")
        return _vers_tache(ligne)

    def ajouter(self, tache: Tache) -> None:
        self._conn.execute(
            f"INSERT INTO taches ({COLONNES}) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                tache.id,
                tache.titre,
                tache.projet,
                tache.assignee,
                tache.creee_le.isoformat(),
                tache.echeance.isoformat(),
                int(tache.terminee),
            ),
        )
        self._conn.commit()
