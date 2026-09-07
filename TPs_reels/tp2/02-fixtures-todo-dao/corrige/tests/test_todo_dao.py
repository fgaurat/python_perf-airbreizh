import pytest

from todoapp.todo import Todo

# ---------------------------------------------------------------- nominal


def test_save_puis_find_all(dao):
    dao.save(Todo(title="Relire le rapport"))
    assert list(dao.find_all()) == [Todo(1, "Relire le rapport", False)]


def test_find_all_est_un_generateur(dao):
    # Sans list(), la comparaison est toujours fausse : un générateur n'est pas une liste.
    dao.save(Todo(title="Relire le rapport"))
    assert dao.find_all() != [Todo(1, "Relire le rapport", False)]


def test_deux_save_donnent_deux_ids(dao):
    dao.save(Todo(title="a"))
    dao.save(Todo(title="b"))
    assert [t.id for t in dao.find_all()] == [1, 2]


def test_dao_rempli_contient_les_trois_todos(dao_rempli, todos):
    relus = list(dao_rempli.find_all())
    assert [t.title for t in relus] == [t.title for t in todos]


def test_save_renseigne_et_retourne_l_id(dao):
    todo = Todo(title="a")
    retour = dao.save(todo)
    assert todo.id == 1
    assert retour is todo


# ---------------------------------------------------------------- cas limites


def test_table_vide(dao):
    assert list(dao.find_all()) == []


def test_apostrophe_dans_le_titre(dao):
    # Rouge avec la version f-string du tp1 : sqlite3.OperationalError.
    dao.save(Todo(title="L'essentiel"))
    assert list(dao.find_all())[0].title == "L'essentiel"


def test_injection_sql_sans_effet(dao):
    titre = "Robert'); DROP TABLE todos_tbl; --"
    dao.save(Todo(title=titre))
    assert list(dao.find_all())[0].title == titre


def test_titre_vide_accepte(dao):
    # Décision : le DAO ne valide pas, il stocke. La validation est du ressort
    # de la couche métier (voir TP 03).
    dao.save(Todo(title=""))
    assert list(dao.find_all())[0].title == ""


def test_completed_revient_en_booleen(dao):
    dao.save(Todo(title="a", completed=True))
    relu = list(dao.find_all())[0]
    assert relu.completed is True  # 1 == True passerait, 1 is True non


def test_non_completed_revient_en_booleen(dao):
    dao.save(Todo(title="a"))
    assert list(dao.find_all())[0].completed is False


# ---------------------------------------------------------------- isolation


@pytest.mark.integration
def test_chaque_test_a_sa_propre_base(tmp_path):
    # tmp_path est unique par test : deux DAO créés dans deux tests différents
    # ne se voient jamais. Ici on le vérifie à l'intérieur d'un seul test.
    from todoapp.todo_dao import TodoDAO

    chemin = tmp_path / "todos.db"
    assert not chemin.exists()
    dao = TodoDAO(chemin)
    dao.creer_table()
    dao.fermer()
    assert chemin.exists()
