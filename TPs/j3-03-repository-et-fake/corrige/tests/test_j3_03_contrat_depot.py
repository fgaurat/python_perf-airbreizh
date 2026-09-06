"""Le test de contrat : écrit une fois, exécuté sur les deux implémentations.

Si le fake dérive de la vraie base, l'une des deux classes rougit.
"""

from datetime import date

import pytest
from fabrique_j3_03 import tache
from suivi.modele import TacheInconnue


class ContratDepotTaches:
    def test_toutes_retourne_les_taches_par_id_croissant(self, depot):
        assert [t.id for t in depot.toutes()] == [1, 2, 3, 4]

    def test_toutes_conserve_chaque_champ(self, depot):
        t = depot.toutes()[3]
        assert (t.titre, t.projet, t.assignee) == ("Appeler le client", "support", "alan")
        assert (t.creee_le, t.echeance, t.terminee) == (date(2026, 9, 1), date(2026, 9, 5), False)

    def test_les_dates_sont_des_dates_pas_des_chaines(self, depot):
        assert isinstance(depot.par_id(1).echeance, date)

    def test_terminee_est_un_booleen(self, depot):
        assert depot.par_id(3).terminee is True
        assert depot.par_id(1).terminee is False

    def test_par_id_retrouve_une_tache(self, depot):
        assert depot.par_id(2).titre == "Déployer"

    def test_par_id_inconnu(self, depot):
        with pytest.raises(TacheInconnue, match="aucune tâche n°42"):
            depot.par_id(42)

    def test_ajouter_puis_relire(self, depot):
        depot.ajouter(tache(5, "Nouvelle", echeance=date(2026, 10, 1)))
        assert depot.par_id(5).titre == "Nouvelle"
        assert len(depot.toutes()) == 5


class TestDepotEnMemoire(ContratDepotTaches):
    @pytest.fixture
    def depot(self, depot_memoire):
        return depot_memoire


class TestDepotSqlite(ContratDepotTaches):
    @pytest.fixture
    def depot(self, depot_sqlite):
        return depot_sqlite
