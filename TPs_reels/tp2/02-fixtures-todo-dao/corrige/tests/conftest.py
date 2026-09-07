import pytest

from todoapp.todo import Todo
from todoapp.todo_dao import TodoDAO


@pytest.fixture(
    params=[
        pytest.param("memoire", id="memoire"),
        pytest.param("fichier", id="fichier", marks=pytest.mark.integration),
    ]
)
def dao(request, tmp_path):
    """Un DAO sur base vide, table créée. Chaque test tourne deux fois :
    en mémoire (rapide, non marqué) et sur un fichier dans tmp_path
    (marqué integration)."""
    chemin = ":memory:" if request.param == "memoire" else tmp_path / "todos.db"
    dao = TodoDAO(chemin)
    dao.creer_table()
    yield dao
    dao.fermer()  # teardown : exécuté après le test, même s'il a échoué


@pytest.fixture
def todos():
    """Trois todos non sauvés, dont un terminé."""
    return [
        Todo(title="Relire le rapport"),
        Todo(title="Envoyer le compte rendu", completed=True),
        Todo(title="Préparer la réunion"),
    ]


@pytest.fixture
def dao_rempli(dao, todos):
    """Fixture composée : le DAO avec les trois todos déjà sauvés."""
    for todo in todos:
        dao.save(todo)
    return dao
