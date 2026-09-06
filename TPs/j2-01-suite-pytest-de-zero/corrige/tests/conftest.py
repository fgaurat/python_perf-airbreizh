from pathlib import Path

import pytest
from todolist.taches import Priorite, TodoList

DONNEES = Path(__file__).parent / "donnees"


@pytest.fixture
def titres_valides() -> list[str]:
    return (DONNEES / "titres_valides.txt").read_text(encoding="utf-8").splitlines()


@pytest.fixture
def liste_garnie() -> TodoList:
    """Trois tâches : une haute, une normale, une basse — ajoutées dans le désordre."""
    liste = TodoList()
    liste.ajouter("Ranger le bureau", Priorite.BASSE)
    liste.ajouter("Relire le rapport", Priorite.HAUTE)
    liste.ajouter("Appeler le fournisseur")
    return liste
