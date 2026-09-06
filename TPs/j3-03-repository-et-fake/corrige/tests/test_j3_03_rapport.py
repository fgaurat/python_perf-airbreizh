"""Les règles métier, testées sur le fake — et en particulier leurs bornes."""

from datetime import date

import pytest
from fabrique_j3_03 import JOUR, tache
from suivi.depot_memoire import DepotEnMemoire
from suivi.modele import ProjetInconnu
from suivi.rapport import Rapport


@pytest.fixture
def rapport(depot_memoire) -> Rapport:
    return Rapport(depot_memoire)


# --- en_retard ---------------------------------------------------------------------


def test_en_retard(rapport):
    assert rapport.en_retard(JOUR) == ["Appeler le client", "Relire le rapport"]


def test_une_tache_terminee_n_est_jamais_en_retard(rapport):
    assert "Corriger le CSS" not in rapport.en_retard(date(2030, 1, 1))


def test_une_echeance_au_jour_meme_n_est_pas_en_retard():
    depot = DepotEnMemoire([tache(1, "Aujourd'hui", echeance=JOUR)])
    assert Rapport(depot).en_retard(JOUR) == []
    assert Rapport(depot).en_retard(date(2026, 9, 16)) == ["Aujourd'hui"]


def test_en_retard_sur_un_depot_vide():
    assert Rapport(DepotEnMemoire()).en_retard(JOUR) == []


# --- avancement ---------------------------------------------------------------------


def test_avancement(rapport):
    assert rapport.avancement("site-web") == 33


def test_avancement_complet():
    depot = DepotEnMemoire([tache(1, "A", terminee=True), tache(2, "B", terminee=True)])
    assert Rapport(depot).avancement("site-web") == 100


def test_avancement_nul(rapport):
    assert rapport.avancement("support") == 0


def test_un_projet_inconnu_est_une_erreur_pas_zero(rapport):
    """Le code de départ renvoyait 0 : indiscernable d'un projet où rien n'est fait."""
    with pytest.raises(ProjetInconnu, match="aucune tâche dans le projet 'inexistant'"):
        rapport.avancement("inexistant")


# --- surcharges ---------------------------------------------------------------------------


def test_personne_n_est_surcharge_par_defaut(rapport):
    assert rapport.surcharges() == []


def test_surcharges_au_dessus_du_seuil():
    depot = DepotEnMemoire([tache(i, f"T{i}", assignee="ada") for i in range(1, 7)])
    assert Rapport(depot).surcharges(seuil=5) == ["ada"]


def test_exactement_au_seuil_n_est_pas_surcharge():
    depot = DepotEnMemoire([tache(i, f"T{i}", assignee="ada") for i in range(1, 6)])
    assert Rapport(depot).surcharges(seuil=5) == []


def test_les_taches_terminees_ne_comptent_pas_dans_la_charge():
    taches = [tache(i, f"T{i}", assignee="ada", terminee=(i > 3)) for i in range(1, 10)]
    assert Rapport(DepotEnMemoire(taches)).surcharges(seuil=3) == []


def test_surcharges_est_trie_par_nom():
    taches = [tache(i, f"T{i}", assignee="zoe") for i in range(1, 4)]
    taches += [tache(i, f"T{i}", assignee="ada") for i in range(4, 7)]
    assert Rapport(DepotEnMemoire(taches)).surcharges(seuil=2) == ["ada", "zoe"]


# --- dormantes -------------------------------------------------------------------------------


def test_dormantes():
    depot = DepotEnMemoire(
        [
            tache(1, "Vieille", creee_le=date(2026, 7, 1)),
            tache(2, "Récente", creee_le=date(2026, 9, 10)),
            tache(3, "Vieille mais finie", creee_le=date(2026, 7, 1), terminee=True),
        ]
    )
    assert Rapport(depot).dormantes(JOUR) == ["Vieille"]


def test_exactement_trente_jours_n_est_pas_dormante():
    depot = DepotEnMemoire([tache(1, "Pile", creee_le=date(2026, 8, 16))])
    assert Rapport(depot).dormantes(JOUR) == []
    assert Rapport(depot).dormantes(date(2026, 9, 16)) == ["Pile"]


def test_dormantes_triees_par_date_de_creation():
    depot = DepotEnMemoire(
        [tache(1, "B", creee_le=date(2026, 6, 1)), tache(2, "A", creee_le=date(2026, 5, 1))]
    )
    assert Rapport(depot).dormantes(JOUR) == ["A", "B"]


# --- Le métier ne connaît pas la base --------------------------------------------------------


def test_le_mot_select_n_apparait_que_dans_le_depot_sqlite():
    from pathlib import Path

    import suivi.rapport

    assert "SELECT" not in Path(suivi.rapport.__file__).read_text(encoding="utf-8")
