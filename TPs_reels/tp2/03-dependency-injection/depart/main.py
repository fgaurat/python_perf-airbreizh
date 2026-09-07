from todoapp.todo_service import TodoService


def main():
    service = TodoService()
    service.ajouter("Relire le rapport")
    print(service.resume())


if __name__ == "__main__":
    main()
