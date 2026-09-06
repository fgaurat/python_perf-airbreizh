"""Un groupe de tests par couche. Chaque couche se teste sans celles du dessus."""

import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
from gestion import affichage, projets, service
from gestion.modele import Projet, ProjetInconnu, Tache

JOUR = date(2026, 9, 15)
CATALOGUE = {"site-web": Projet("site-web"), "archives": Projet("archives", archive=True)}
TACHES = [
    Tache(1, "Déployer", "site-web", date(2026, 9, 20)),
    Tache(2, "Relire", "site-web", date(2026, 9, 10)),
    Tache(3, "Trier", "archives", date(2026, 9, 1), terminee=True),
]

# --- modele : n'importe rien -------------------------------------------------------------


def test_le_modele_n_importe_rien_du_projet():
    import gestion.modele

    assert "import gestion" not in Path(gestion.modele.__file__).read_text(encoding="utf-8")


@pytest.mark.parametrize(("echeance", "attendu"), [(date(2026, 9, 14), True), (JOUR, False)])
def test_est_en_retard(echeance, attendu):
    assert Tache(1, "X", "p", echeance).est_en_retard(JOUR) is attendu


@pytest.mark.parametrize(
    ("echeance", "attendu"),
    [(date(2026, 9, 17), True), (date(2026, 9, 18), False), (date(2026, 9, 1), True)],
    ids=["dans_deux_jours", "dans_trois_jours", "deja_passee"],
)
def test_est_a_surveiller(echeance, attendu):
    assert Tache(1, "X", "p", echeance).est_a_surveiller(JOUR) is attendu


def test_une_tache_terminee_n_est_jamais_a_surveiller():
    assert Tache(1, "X", "p", date(2026, 9, 1), terminee=True).est_a_surveiller(JOUR) is False


# --- projets : sans affichage ------------------------------------------------------------


def test_est_actif():
    assert projets.est_actif(CATALOGUE, "site-web") is True
    assert projets.est_actif(CATALOGUE, "archives") is False
    assert projets.est_actif(CATALOGUE, "inconnu") is False


def test_projet_de_inconnu():
    with pytest.raises(ProjetInconnu, match=r"'inconnu' \(connus : \['archives', 'site-web'\]\)"):
        projets.projet_de(CATALOGUE, "inconnu")


def test_peut_etre_terminee():
    assert projets.peut_etre_terminee(TACHES[0], CATALOGUE) is True
    assert projets.peut_etre_terminee(TACHES[2], CATALOGUE) is False


def test_taches_du_projet_par_echeance():
    assert [t.id for t in projets.taches_du_projet(TACHES, "site-web")] == [2, 1]


def test_taches_du_projet_vide():
    assert projets.taches_du_projet(TACHES, "inconnu") == []


# --- affichage : sans projets --------------------------------------------------------------


def test_en_ligne():
    assert affichage.en_ligne(TACHES[0]) == "[ ] #1 Déployer (pour le 2026-09-20)"


def test_en_ligne_terminee():
    assert affichage.en_ligne(TACHES[2]).startswith("[x] #3 Trier")


def test_en_ligne_signale_les_taches_a_surveiller():
    assert affichage.en_ligne(TACHES[1], JOUR).endswith(" !")
    assert not affichage.en_ligne(TACHES[0], JOUR).endswith(" !")


def test_en_titre():
    assert affichage.en_titre(Projet("site-web")) == "== site-web (actif, alerte à 3 j) =="
    assert affichage.en_titre(Projet("archives", archive=True)).startswith("== archives (archivé")


# --- service : la couche du dessus ------------------------------------------------------------


def test_resume():
    assert service.resume(CATALOGUE, TACHES, JOUR) == [
        "== archives (archivé, alerte à 3 j) ==",
        "[x] #3 Trier (pour le 2026-09-01)",
        "== site-web (actif, alerte à 3 j) ==",
        "[ ] #2 Relire (pour le 2026-09-10) !",
        "[ ] #1 Déployer (pour le 2026-09-20)",
    ]


def test_resume_sans_tache():
    assert service.resume({"p": Projet("p")}, [], JOUR) == ["== p (actif, alerte à 3 j) =="]


def test_resume_refuse_les_projets_inconnus():
    """Pour aller plus loin : le code d'origine levait un KeyError brut."""
    with pytest.raises(ProjetInconnu, match=r"projets inconnus : \['fantome'\]"):
        service.resume(CATALOGUE, [Tache(9, "X", "fantome", JOUR)], JOUR)


# --- le package s'importe, et le contrat tient ---------------------------------------------------


def test_le_package_s_importe_dans_un_interpreteur_neuf():
    racine = Path(__file__).parents[1]
    resultat = subprocess.run(
        [sys.executable, "-c", "import gestion.service, gestion.projets, gestion.affichage"],
        cwd=racine,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultat.returncode == 0, resultat.stderr


def test_le_contrat_import_linter_est_respecte():
    racine = Path(__file__).parents[1]
    resultat = subprocess.run(
        [str(Path(sys.executable).with_name("lint-imports")), "--config", ".importlinter"],
        cwd=racine,
        capture_output=True,
        text=True,
        check=False,
    )
    assert "Contracts: 1 kept, 0 broken" in resultat.stdout, resultat.stdout + resultat.stderr
