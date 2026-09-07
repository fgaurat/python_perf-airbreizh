from todoapp.todo_dao import TodoDAO
from todoapp.todo_service import TodoService


def main():
    # Composition root : le seul endroit qui connaît sqlite et le chemin.
    dao = TodoDAO("todos.db")
    dao.creer_table()
    service = TodoService(dao)
    service.ajouter("Relire le rapport")
    print(service.resume())
    dao.fermer()


if __name__ == "__main__":
    main()
