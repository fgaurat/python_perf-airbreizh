"""Fixtures du carnet : toutes construites à partir de `tmp_path`.

Rien n'est écrit ailleurs que dans le dossier temporaire du test en cours.
"""

from pathlib import Path

import pytest
from carnet.stockage import Contact, ecrire


@pytest.fixture
def carnet(tmp_path: Path) -> Path:
    """Le chemin du carnet — le fichier n'existe pas encore."""
    return tmp_path / "carnet.json"


@pytest.fixture
def contacts() -> list[Contact]:
    return [
        Contact("Ada Lovelace", "ada@exemple.org", "01 02 03 04 05"),
        Contact("Alan Turing", "alan@exemple.org"),
        Contact("Grace Hopper", "grace@exemple.org", "06 07 08 09 10"),
    ]


@pytest.fixture
def carnet_rempli(carnet: Path, contacts: list[Contact]) -> Path:
    """Composée : le carnet, déjà écrit sur disque avec les trois contacts."""
    ecrire(carnet, contacts)
    return carnet


@pytest.fixture
def sauvegardes_numerotees(carnet_rempli: Path) -> Path:
    """Le carnet accompagné de `.1`, `.2`, `.3` — chacune avec un contenu différent."""
    for numero in (1, 2, 3):
        carnet_rempli.with_name(f"carnet.json.{numero}").write_text(f"copie {numero}\n")
    return carnet_rempli
