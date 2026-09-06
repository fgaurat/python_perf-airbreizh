"""Jeux de données : un élève de référence, on ne surcharge que ce qu'on teste."""


def eleve(**surcharges) -> dict:
    defauts = {
        "id": "E001",
        "nom": "Ada",
        "classe": "5e",
        "notes": {
            "maths": [{"valeur": 14}, {"valeur": 16, "coef": 2}],
            "francais": [{"valeur": 12}],
            "histoire": [{"valeur": 10}],
            "anglais": [{"valeur": 15}],
            "sport": [{"valeur": 18}],
            "arts": [{"valeur": 13}],
        },
        "absences": [],
        "moyennes_classe": [11.5, 13.0, 15.5],
        "moyenne_precedente": 13.0,
    }
    return {**defauts, **surcharges}
