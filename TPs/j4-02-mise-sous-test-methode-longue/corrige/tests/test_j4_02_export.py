"""L'export : sérialisation pure d'un côté, écriture de l'autre. L'orchestration n'écrit rien."""

import json
from pathlib import Path

import pytest
from fabrique_j4_02 import eleve
from scolaire.bulletin import generer_bulletin
from scolaire.export import en_csv, en_json, exporter
from scolaire.modele import ErreurBulletin

BULLETIN = {
    "id": "E1",
    "nom": "Ada",
    "moyenne_finale": 14.05,
    "matieres": [{"m": 1}],
    "mention": "",
}


def test_en_json_est_relisible():
    assert json.loads(en_json(BULLETIN)) == BULLETIN


def test_en_json_conserve_les_accents():
    assert "Félicitations" in en_json({"mention": "Félicitations"})


def test_en_csv_omet_les_listes_et_dicts():
    assert en_csv(BULLETIN).splitlines() == ["id,nom,moyenne_finale,mention", "E1,Ada,14.05,"]


def test_exporter_json(tmp_path: Path):
    chemin = exporter(BULLETIN, tmp_path / "b.json")
    assert json.loads(chemin.read_text(encoding="utf-8")) == BULLETIN


def test_exporter_csv(tmp_path: Path):
    chemin = exporter(BULLETIN, tmp_path / "b.csv", "csv")
    assert chemin.read_text(encoding="utf-8").startswith("id,nom,")


def test_format_inconnu(tmp_path: Path):
    with pytest.raises(ErreurBulletin, match="format inconnu : xml"):
        exporter(BULLETIN, tmp_path / "b.xml", "xml")


def test_generer_bulletin_n_ecrit_rien_sans_sortie(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    generer_bulletin(eleve(), "2026-T1")
    assert list(tmp_path.iterdir()) == []


def test_generer_bulletin_ecrit_quand_on_le_lui_demande(tmp_path: Path):
    bulletin = generer_bulletin(eleve(), "2026-T1", sortie=tmp_path / "ada.json")
    assert json.loads((tmp_path / "ada.json").read_text(encoding="utf-8")) == bulletin


def test_le_bulletin_de_reference():
    """Un test de caractérisation complet, pour lire d'un coup ce que produit la référence."""
    bulletin = generer_bulletin(eleve(), "2026-T1")
    assert bulletin["moyenne_generale"] == 13.69
    assert bulletin["mention"] == "Encouragements"
    assert bulletin["rang"] == 2
    assert bulletin["tendance"] == "en progrès"


def test_sans_moyenne_precedente_l_eleve_est_toujours_en_progres():
    """BUGS.md n° 1 — figé : la valeur par défaut 0.0 rend toute moyenne « en progrès »."""
    donnees = eleve()
    del donnees["moyenne_precedente"]
    assert generer_bulletin(donnees, "2026-T1")["tendance"] == "en progrès"
