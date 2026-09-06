"""La greffe : cinq tests de branchement, deux de non-régression. La règle est couverte ailleurs."""

import pytest
from bureau.historique import Entree, HistoriqueVide
from bureau.moteur import Calculatrice, ErreurCalcul

# --- Le branchement ---------------------------------------------------------------------


def test_chaque_calcul_est_enregistre():
    c = Calculatrice()
    c.calculer("2 + 2")
    c.calculer("ans * 3")
    assert c.historique.derniers() == [Entree("2 + 2", 4.0), Entree("ans * 3", 12.0)]


def test_un_calcul_en_erreur_n_est_pas_enregistre():
    c = Calculatrice()
    with pytest.raises(ErreurCalcul):
        c.calculer("1 / 0")
    assert len(c.historique) == 0


def test_annuler_revient_a_la_valeur_precedente():
    c = Calculatrice()
    c.calculer("10")
    c.calculer("20")
    assert c.annuler() == 10.0
    assert c.calculer("ans + 1") == 11.0


def test_annuler_le_seul_calcul_ramene_a_zero():
    c = Calculatrice()
    c.calculer("10")
    assert c.annuler() == 0.0
    assert c.calculer("ans") == 0.0


def test_annuler_sans_calcul_est_une_erreur():
    with pytest.raises(HistoriqueVide):
        Calculatrice().annuler()


def test_la_capacite_est_configurable():
    c = Calculatrice(capacite=2)
    for e in ["1", "2", "3"]:
        c.calculer(e)
    assert [e.expression for e in c.historique.derniers()] == ["2", "3"]


# --- Non-régression sur ce que le moteur faisait déjà ---------------------------------------


def test_la_memoire_fonctionne_toujours():
    c = Calculatrice()
    c.calculer("7")
    c.memoire_plus()
    assert c.calculer("MR * 2") == 14.0


def test_la_precision_et_le_mode_fonctionnent_toujours():
    assert Calculatrice(precision=2).calculer("cos(60)") == 0.5
    assert Calculatrice(mode="radians", precision=3).calculer("sin(pi / 2)") == 1.0
