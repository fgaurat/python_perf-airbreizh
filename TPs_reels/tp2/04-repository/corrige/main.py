import os

from todoapp.repository_sqlite import SqliteTodoRepository
from todoapp.todo_service import TodoService


def main():
    if os.path.exists("todos.db"):
        os.remove("todos.db")
    repo = SqliteTodoRepository("todos.db")
    service = TodoService(repo)

    todo = service.ajouter("Relire le rapport")
    print("après ajout   :", service.resume())
    service.terminer(todo.id)
    print("après terminer:", service.resume())
    print("en base       :", repo.lister())
    repo.fermer()


if __name__ == "__main__":
    main()
