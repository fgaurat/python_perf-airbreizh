import sqlite3
from collections.abc import Iterator
from datetime import date

import pytest
from fabrique_j3_03 import tache
from suivi.depot_memoire import DepotEnMemoire
from suivi.depot_sqlite import SCHEMA, DepotSqlite
from suivi.modele import Tache


@pytest.fixture
def taches() -> list[Tache]:
    return [
        tache(1, "Relire le rapport", echeance=date(2026, 9, 10)),
        tache(2, "Déployer", echeance=date(2026, 9, 20)),
        tache(3, "Corriger le CSS", echeance=date(2026, 9, 1), terminee=True),
        tache(4, "Appeler le client", projet="support", assignee="alan", echeance=date(2026, 9, 5)),
    ]


@pytest.fixture
def depot_memoire(taches) -> DepotEnMemoire:
    return DepotEnMemoire(taches)


@pytest.fixture
def depot_sqlite(taches) -> Iterator[DepotSqlite]:
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    depot = DepotSqlite(conn)
    for t in taches:
        depot.ajouter(t)
    yield depot
    conn.close()
