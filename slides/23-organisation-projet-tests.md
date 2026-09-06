---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — Organisation d'un projet de tests"
---

<!-- _class: lead -->

# 3. Organisation d'un projet de tests

*Où poser les fichiers, et pourquoi ça compte*

---

# Structure recommandée d'un package Python

```
mesures/
├── pyproject.toml
├── src/
│   └── mesures/
│       ├── __init__.py
│       ├── modele.py          # objets métier
│       ├── calculs.py         # fonctions pures
│       ├── lecture.py         # I/O
│       └── sources/
│           ├── __init__.py
│           └── api.py
└── tests/
    ├── conftest.py            # fixtures partagées
    ├── donnees/               # jeux de test versionnés
    │   └── releve_minimal.csv
    ├── unitaires/
    │   ├── test_calculs.py
    │   └── test_modele.py
    └── integration/
        └── test_api.py
```

---

# Pourquoi `src/` — ce n'est pas cosmétique

Sans `src/`, le package est **au même niveau** que le dossier de tests. Python
ajoute le répertoire courant à `sys.path`, donc `import mesures` trouve le code
source local, **même s'il n'est pas installé**.

Conséquence : vous testez vos fichiers, pas votre package.

| Ce qui casse en silence sans `src/` | Détecté avec `src/` |
|---|---|
| Un fichier oublié dans le paquet distribué | ✓ à l'import |
| Un `package_data` manquant (fichiers de données) | ✓ à l'exécution |
| Un sous-package sans `__init__.py` | ✓ à l'import |

Avec `src/`, la seule façon d'importer `mesures` est de l'**installer** :

```bash
uv pip install -e .        # ou : pip install -e .
```

Vos tests s'exécutent alors contre le package tel que vos consommateurs le recevront.

---

# Le dossier `tests/` en miroir du package

La règle la plus économique : **un fichier de test par module**, au même
emplacement relatif.

| Module | Test |
|---|---|
| `src/mesures/calculs.py` | `tests/unitaires/test_calculs.py` |
| `src/mesures/sources/api.py` | `tests/integration/test_api.py` |

Vous savez ainsi immédiatement :

- où ajouter un test quand vous modifiez un module ;
- quel module n'a **aucun** test — le fichier correspondant est absent.

> **⚠️ Piège** : ne mettez pas de `__init__.py` dans `tests/`. Le dossier de
> tests n'est pas un package importable, et pytest s'en passe très bien.

---

# `conftest.py` : le fichier que pytest découvre tout seul

`conftest.py` contient les fixtures et la configuration **partagées par tous les
tests du dossier et de ses sous-dossiers**. Vous ne l'importez jamais.

```
tests/
├── conftest.py               # fixtures pour tous les tests
├── unitaires/
│   └── conftest.py           # fixtures propres aux tests unitaires
└── integration/
    └── conftest.py           # ex. : une base temporaire
```

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def dossier_donnees() -> Path:
    """Racine des jeux de données de test."""
    return Path(__file__).parent / "donnees"
```

Toute fonction de test peut désormais recevoir `dossier_donnees` en paramètre.

---

# Conventions de nommage

pytest découvre les tests par convention. Il n'y a rien à déclarer.

| Élément | Convention | Exemple |
|---|---|---|
| Fichier | `test_*.py` | `test_calculs.py` |
| Fonction | `test_*` | `test_moyenne_sur_serie_vide` |
| Classe (optionnelle) | `Test*`, sans `__init__` | `TestGrilleTarifaire` |

Pour les **noms de tests**, une seule règle utile :

> Le nom décrit le **comportement attendu**, pas l'appel technique.

<div class="cols">
<div>

❌ `test_calculer_indice_1`
❌ `test_calculer_indice_ko`
❌ `test_bug_4231`

</div>
<div>

✓ `test_indice_plafonne_a_100`
✓ `test_indice_none_sans_mesure`
✓ `test_seuil_inclusif_a_la_borne`

</div>
</div>

Quand un test rougit en CI, son nom est souvent la seule chose que le relecteur lira.

---

# Arrange / Act / Assert

Trois blocs, dans cet ordre, séparés par une ligne vide. C'est tout.

```python
def test_avancement_complet_vaut_100():
    # Arrange — préparer les données
    taches = [Tache("A", terminee=True), Tache("B", terminee=True)]

    # Act — une seule action, celle qu'on teste
    avancement = calculer_avancement(taches)

    # Assert — vérifier le résultat observable
    assert avancement == 100.0
```

Bénéfices concrets :

- si le bloc **Act** contient plus d'une ligne, le test vérifie plusieurs choses ;
- si le bloc **Arrange** fait 30 lignes, le code testé a trop de dépendances ;
- le lecteur trouve l'entrée et la sortie attendue sans lire le corps.

Les commentaires sont facultatifs — la structure en trois paragraphes suffit.

---

# Séparer les tests unitaires des tests d'intégration

Deux moyens, complémentaires : les **dossiers** et les **marqueurs**.

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "integration: nécessite une ressource externe (base, réseau, fichier volumineux)",
    "lent: dépasse une seconde",
]
```

```python
@pytest.mark.integration
def test_lecture_depuis_la_base(base_temporaire):
    ...
```

L'intérêt apparaît au quotidien :

```bash
pytest -m "not integration"     # boucle de développement : quelques secondes
pytest                          # avant de pousser : tout
```

C'est ce découpage que nous exploiterons au Jour 5 pour tenir des pipelines rapides.

---

# Les données de test

| Type de donnée | Où la mettre |
|---|---|
| Deux ou trois valeurs | **en dur dans le test** — c'est le plus lisible |
| Un objet métier récurrent | une fixture dans `conftest.py` |
| Un fichier d'entrée réaliste | `tests/donnees/`, **versionné**, réduit au minimum |
| Un fichier produit par le test | `tmp_path` — jamais le dossier du projet |

> **🎯 En pratique** : un fichier de test de 200 Mo extrait de la production est
> presque toujours une erreur. Réduisez-le à 5 lignes qui contiennent le cas
> intéressant, et documentez en commentaire ce qu'elles représentent.

Un jeu de données de test doit tenir dans un dépôt Git **et** dans la tête du
relecteur.

---

# À retenir

> **1.** `src/` + installation en mode éditable : vos tests s'exécutent contre
> le package tel qu'il sera livré, pas contre vos fichiers locaux.

> **2.** `tests/` en miroir du package, sans `__init__.py`, avec un
> `conftest.py` pour les fixtures partagées.

> **3.** Arrange / Act / Assert. Si l'un des trois blocs devient long, c'est le
> **code testé** qui a un problème, pas le test.
