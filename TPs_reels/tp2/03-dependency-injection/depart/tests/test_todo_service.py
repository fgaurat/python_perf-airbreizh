from todoapp.todo_service import TodoService


def test_restantes_exclut_les_terminees():
    service = TodoService()
    # Comment mettre un todo terminé et un todo non terminé dans le service,
    # sans passer par le fichier todos.db ?
    assert service.resume() == "1 tâches restantes"
