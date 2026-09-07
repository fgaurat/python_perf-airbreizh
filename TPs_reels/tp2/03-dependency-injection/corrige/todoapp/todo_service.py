from typing import Iterable, Protocol

from todoapp.todo import Todo


class SourceTodos(Protocol):
    """Ce dont le service a besoin, et rien de plus.

    Un Protocol (tp1) : pas d'héritage, n'importe quel objet qui a ces deux
    méthodes convient. Le vrai TodoDAO comme le faux des tests.
    """

    def save(self, todo: Todo) -> Todo: ...
    def find_all(self) -> Iterable[Todo]: ...


class TodoService:
    """Règles métier au-dessus d'une source de todos, reçue à la construction."""

    def __init__(self, dao: SourceTodos):
        self._dao = dao

    def ajouter(self, titre: str) -> Todo:
        return self._dao.save(Todo(title=titre))

    def restantes(self) -> list[Todo]:
        return [t for t in self._dao.find_all() if not t.completed]

    def resume(self) -> str:
        n = len(self.restantes())
        if n == 0:
            return "aucune tâche restante"
        if n == 1:
            return "1 tâche restante"
        return f"{n} tâches restantes"
