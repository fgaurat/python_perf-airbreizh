"""Rapport hebdomadaire de la todo-list d'équipe : retards, avancement, charge, tâches dormantes.

Les quatre règles sont écrites en SQL, directement dans le métier.
"""

import sqlite3
from datetime import date

JOURS_AVANT_DORMANCE = 30
SEUIL_SURCHARGE = 5


class Rapport:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def en_retard(self, jour: date) -> list[str]:
        """Titres des tâches non terminées dont l'échéance est passée."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT titre FROM taches WHERE terminee = 0 AND echeance < ? ORDER BY echeance, id",
            (jour.isoformat(),),
        )
        return [ligne[0] for ligne in cur.fetchall()]

    def avancement(self, projet: str) -> int:
        """Pourcentage de tâches terminées du projet, arrondi."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*), SUM(terminee) FROM taches WHERE projet = ?", (projet,))
        total, terminees = cur.fetchone()
        if not total:
            return 0
        return round(100 * (terminees or 0) / total)

    def surcharges(self, seuil: int = SEUIL_SURCHARGE) -> list[str]:
        """Personnes ayant strictement plus de `seuil` tâches non terminées."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT assignee FROM taches WHERE terminee = 0 "
            "GROUP BY assignee HAVING COUNT(*) > ? ORDER BY assignee",
            (seuil,),
        )
        return [ligne[0] for ligne in cur.fetchall()]

    def dormantes(self, jour: date, jours: int = JOURS_AVANT_DORMANCE) -> list[str]:
        """Titres des tâches non terminées créées il y a strictement plus de `jours` jours."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT titre FROM taches WHERE terminee = 0 "
            "AND julianday(?) - julianday(creee_le) > ? ORDER BY creee_le, id",
            (jour.isoformat(), jours),
        )
        return [ligne[0] for ligne in cur.fetchall()]
