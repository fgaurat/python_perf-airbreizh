from salut.horloges import HorlogeSysteme
from salut.salutation import saluer

if __name__ == "__main__":
    # Remplacer par HorlogeTimeApi() pour passer par l'API.
    print(saluer("Ada", HorlogeSysteme()))
