from todoapp.todolist import TodoList


def main():
    liste = TodoList()
    liste.ajouter("relire le rapport", priorite=1)
    liste.ajouter("Envoyer le compte rendu")
    liste.ajouter("appeler le client", priorite=2)
    liste.terminer(2)
    for tri in ("ajout", "titre", "priorite", "restantes"):
        print(f"--- {tri}")
        for todo in liste.lister(tri):
            print(f"  [{'x' if todo.completed else ' '}] p{todo.priorite} {todo.title}")


if __name__ == "__main__":
    main()
