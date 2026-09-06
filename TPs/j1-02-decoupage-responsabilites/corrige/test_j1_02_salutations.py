"""Tests du message d'accueil.

Remarquez ce que ces tests n'ont pas besoin de faire : figer l'horloge, changer
d'utilisateur système, créer un fichier de configuration. C'est le bénéfice
direct de la séparation entre calcul et I/O — seuls les deux derniers tests,
qui visent précisément les I/O, touchent un fichier.
"""

from datetime import datetime
from pathlib import Path

import pytest
from salutations import (
    Config,
    Moment,
    formuler,
    journaliser,
    lire_config,
    moment_de_la_journee,
    saluer,
)

# --- moment_de_la_journee ----------------------------------------------------


@pytest.mark.parametrize("heure", [0, 3, 5])
def test_la_nuit(heure):
    assert moment_de_la_journee(heure) is Moment.NUIT


@pytest.mark.parametrize("heure", [6, 12, 17])
def test_le_jour(heure):
    assert moment_de_la_journee(heure) is Moment.JOUR


@pytest.mark.parametrize("heure", [18, 21, 23])
def test_le_soir(heure):
    assert moment_de_la_journee(heure) is Moment.SOIR


def test_les_bornes_du_soir():
    """Le bug du code de départ : le soir commençait à 19 h au lieu de 18 h."""
    assert moment_de_la_journee(17) is Moment.JOUR
    assert moment_de_la_journee(18) is Moment.SOIR


def test_les_bornes_du_matin():
    assert moment_de_la_journee(5) is Moment.NUIT
    assert moment_de_la_journee(6) is Moment.JOUR


@pytest.mark.parametrize("heure", [-1, 24, 25])
def test_une_heure_impossible_est_refusee(heure):
    with pytest.raises(ValueError, match="hors de"):
        moment_de_la_journee(heure)


# --- formuler -----------------------------------------------------------------


def test_formule_informelle_en_francais():
    assert formuler("Ada", Moment.JOUR) == "Bonjour Ada !"


def test_formule_formelle_en_francais():
    assert formuler("Ada", Moment.SOIR, formel=True) == "Bonsoir, Ada. Bienvenue."


def test_formule_informelle_en_anglais():
    assert formuler("Ada", Moment.NUIT, langue="en") == "Good night Ada !"


def test_formule_formelle_en_anglais():
    assert formuler("Ada", Moment.JOUR, langue="en", formel=True) == "Hello, Ada. Welcome."


@pytest.mark.parametrize(
    ("langue", "attendu"),
    [("fr", "Bonjour Ada ! Bon week-end !"), ("en", "Hello Ada ! Have a nice weekend!")],
)
def test_le_vendredi_on_souhaite_un_bon_weekend(langue, attendu):
    assert formuler("Ada", Moment.JOUR, langue=langue, veille_de_weekend=True) == attendu


def test_pas_de_bon_weekend_la_nuit():
    assert formuler("Ada", Moment.NUIT, veille_de_weekend=True) == "Bonne nuit Ada !"


def test_une_langue_inconnue_est_refusee():
    with pytest.raises(ValueError, match="langue inconnue"):
        formuler("Ada", Moment.JOUR, langue="klingon")


# --- I/O ----------------------------------------------------------------------


def test_lire_config(tmp_path: Path):
    chemin = tmp_path / "config.json"
    chemin.write_text('{"langue": "en", "formel": true, "journal": "x.log"}', encoding="utf-8")
    assert lire_config(chemin) == Config(langue="en", formel=True, journal="x.log")


def test_lire_config_applique_les_valeurs_par_defaut(tmp_path: Path):
    chemin = tmp_path / "config.json"
    chemin.write_text("{}", encoding="utf-8")
    assert lire_config(chemin) == Config()


def test_journaliser_ajoute_une_ligne(tmp_path: Path):
    chemin = tmp_path / "accueil.log"
    quand = datetime(2026, 9, 4, 8, 30)
    journaliser(chemin, quand, "ada", "fr", Moment.JOUR)
    journaliser(chemin, quand, "ada", "fr", Moment.JOUR)
    assert chemin.read_text(encoding="utf-8").splitlines() == ["2026-09-04 08:30 ada fr jour"] * 2


# --- Orchestration ------------------------------------------------------------


def test_saluer_de_bout_en_bout(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Un seul test de bout en bout suffit : la logique est déjà couverte au-dessus."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("salutations.getpass.getuser", lambda: "ada")
    Path("config.json").write_text('{"langue": "fr", "formel": true}', encoding="utf-8")

    texte = saluer(maintenant=datetime(2026, 9, 4, 18, 0))  # un vendredi, 18 h

    assert texte == "Bonsoir, ada. Bienvenue. Bon week-end !"
    assert Path("accueil.log").read_text(encoding="utf-8") == "2026-09-04 18:00 ada fr soir\n"
