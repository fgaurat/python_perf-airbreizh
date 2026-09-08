# Aide-mémoire : pytest, doubles de test, design patterns

## 1. pytest en deux minutes

### Lancer

```bash
python -m pytest                 # tout le dossier courant
python -m pytest -v              # un nom de test par ligne
python -m pytest -x              # s'arrêter au premier échec
python -m pytest -k restantes    # tests dont le nom contient "restantes"
python -m pytest -m "not integration"   # par marqueur
python -m pytest --lf            # relancer seulement les derniers échecs
python -m pytest -s              # laisser passer les print
python -m pytest --fixtures      # lister les fixtures disponibles
python -m pytest --collect-only -q      # voir ce qui serait lancé, sans lancer
python -m pytest --durations=3   # les 3 tests les plus lents
python -m pytest tests/test_x.py::test_y   # un seul test
```

### Structure

```
mon_projet/
  conftest.py          vide : fait ajouter ce dossier à sys.path
  pytest.ini           options et marqueurs déclarés
  monpackage/
    __init__.py
    module.py
  tests/
    conftest.py        fixtures partagées par tous les tests du dossier
    test_module.py     fichiers test_*.py, fonctions test_*
```

Pas de `__init__.py` dans `tests/`. Un test = Arrange (préparer), Act (agir), Assert (vérifier).

### Écrire

```python
import pytest

def test_nominal():
    r = Rectangle(2, 3)              # Arrange
    s = r.surface                    # Act
    assert s == 6                    # Assert : un assert Python, pytest affiche le diff

def test_flottants():
    assert Cercle(2).surface == pytest.approx(4 * math.pi)

def test_erreur_attendue():
    with pytest.raises(DimensionInvalide, match="longueur"):
        Rectangle(2, 3).longueur = -1
    # Jamais pytest.raises(Exception) : il accepte n'importe quoi, même une faute de frappe.

@pytest.mark.parametrize(
    ("longueur", "largeur", "attendue"),
    [
        pytest.param(2, 3, 6, id="entiers"),
        pytest.param(0, 3, 0, id="largeur_nulle"),
        pytest.param(2.5, 2, 5.0, id="flottant"),
    ],
)
def test_surface(longueur, largeur, attendue):
    assert Rectangle(longueur, largeur).surface == attendue

pytestmark = pytest.mark.integration      # marque tout le module
```

```ini
# pytest.ini
[pytest]
markers =
    integration: touche une vraie ressource (fichier, base, réseau)
```

### Quoi tester en priorité

Règles métier, calculs, transformations de données, formats d'entrée et de
sortie, validations, bugs déjà rencontrés, code utilisé par d'autres packages.

Peu rentable : getters simples, `__str__`, détails d'implémentation,
tests qui répètent le code au lieu de décrire un comportement.

## 2. Fixtures

**Définition.** Une fixture est une fonction décorée `@pytest.fixture` qui
prépare ce dont un test a besoin (un objet, un fichier, une connexion) et,
si nécessaire, le nettoie après. Un test la reçoit en la nommant comme
paramètre. pytest l'exécute avant le test, et exécute ce qui suit le `yield`
après, même si le test a échoué.

```python
# tests/conftest.py
@pytest.fixture
def dao(tmp_path):                        # une fixture peut en demander une autre
    dao = TodoDAO(tmp_path / "todos.db")  # tmp_path : dossier vide, unique au test, fourni par pytest
    dao.creer_table()
    yield dao                             # avant le yield : setup
    dao.fermer()                          # après le yield : teardown

@pytest.fixture
def todos():
    return [Todo(title="a"), Todo(title="b", completed=True)]

@pytest.fixture
def dao_rempli(dao, todos):               # fixture composée
    for t in todos:
        dao.save(t)
    return dao

@pytest.fixture(autouse=True)             # appliquée à tous les tests sans la demander
def compteur_remis_a_zero():
    Rectangle._cpt = 0
    yield
    Rectangle._cpt = 0

@pytest.fixture(params=[                  # paramétrée : chaque test tourne une fois par valeur
    pytest.param("memoire", id="memoire"),
    pytest.param("sqlite", id="sqlite", marks=pytest.mark.integration),
])
def repo(request, tmp_path):
    ...
```

Fixtures fournies par pytest : `tmp_path`, `monkeypatch`, `capsys` (capturer
la sortie), `caplog` (capturer les logs), `request`.

Portée : `@pytest.fixture(scope="module")` pour ne la construire qu'une fois
par fichier. Par défaut `function`, une fois par test. Préférer `function`
tant que ce n'est pas lent : l'isolation d'abord.

## 3. Doubles de test

Un double de test remplace une dépendance réelle pendant un test. Cinq
sortes, du plus bête au plus bavard.

| Double | Définition | Vérifie | Exemple |
|---|---|---|---|
| **Dummy** | Objet passé pour remplir une signature, jamais utilisé. | rien | `TodoService(dao=None)` quand le test n'appelle pas le DAO |
| **Stub** | Renvoie des réponses préparées. Pas de logique, pas de mémoire. | un résultat | `HorlogeFixe(9)` dont `heure()` renvoie toujours 9 (TP 05) |
| **Fake** | Implémentation simplifiée mais fonctionnelle. A une logique réelle. | un résultat | `TodoRepositoryMemoire` : un vrai repository, en dict (TP 04) |
| **Spy** | Enregistre les appels qu'il reçoit, pour les inspecter après. | une interaction, après coup | `JournalEspion` qui garde les messages dans une liste (TP 08) |
| **Mock** | Programmé avec des attentes, et vérifie lui-même qu'elles ont été satisfaites. | une interaction | `patch("salut.horloges.urlopen")` puis `assert_called_once_with(...)` (TP 05) |

En pratique, `unittest.mock.MagicMock` sert pour les quatre derniers selon
ce qu'on en fait. Le nom décrit l'usage, pas la classe.

```python
# Stub et fake : écrits à la main, quelques lignes, dans le fichier de test
class HorlogeFixe:
    def __init__(self, heure): self._heure = heure
    def heure(self): return self._heure

# Spy : un faux qui retient
class JournalEspion:
    def __init__(self): self.messages = []
    def noter(self, m): self.messages.append(m)

# Mock avec unittest.mock
from unittest.mock import MagicMock, patch
reponse = MagicMock()
reponse.read.return_value = b'{"hour": 14}'
reponse.__enter__.return_value = reponse
with patch("salut.horloges.urlopen", return_value=reponse) as urlopen:
    assert HorlogeTimeApi().heure() == 14
urlopen.assert_called_once_with(HorlogeTimeApi.URL, timeout=5)

with patch("salut.horloges.urlopen", side_effect=OSError("pas de réseau")):
    ...   # simuler une erreur

# monkeypatch (fixture pytest) : remplacer temporairement, remis en place après le test
def test_env(monkeypatch):
    monkeypatch.setenv("TODO_FILE", "/tmp/x.csv")
    monkeypatch.setattr(module, "fonction", lambda: 42)
```

**Règles**

- Patcher là où le nom est *utilisé* (`salut.horloges.urlopen`), pas là où il est défini (`urllib.request.urlopen`).
- Résultat plutôt qu'interaction : vérifier ce que la fonction rend, pas comment elle s'y est prise. Un test qui vérifie des appels casse au premier refactoring.
- Un fake écrit à la main vaut mieux qu'un mock configuré, dès que la dépendance a un comportement (TP 04). Et un fake doit être confronté au vrai par un **test de contrat**.
- Beaucoup de mocks dans un test = le code testé a trop de dépendances. C'est un signal de conception, pas un problème de test.
- Tester les frontières du système (l'adaptateur HTTP, le repository sqlite) une fois, avec un mock ou une vraie ressource marquée `integration`. Tester le reste avec des fakes et des stubs.

## 4. Design patterns vus en TP

Le pattern est une réponse à un problème. Sans le problème, il est de trop.

| Pattern | Le problème | La réponse | Le test devient | Sur-design quand |
|---|---|---|---|---|
| **Dependency Injection** (TP 03) | l'objet construit lui-même ses dépendances, le test ne peut rien remplacer | la dépendance est passée au constructeur, `main.py` assemble | un faux de huit lignes suffit | jamais, ou presque |
| **Repository** (TP 04) | le stockage est exposé par des méthodes techniques, le faux et le vrai divergent | une interface métier (`ajouter`, `obtenir`, `lister`), deux implémentations, un test de contrat sur les deux | rapide avec l'implémentation mémoire, le contrat garantit le reste | une seule implémentation, pour toujours |
| **Adapter** (TP 05) | le format d'une source externe est écrit dans le code métier | une interface qui dit ce dont le métier a besoin, un adaptateur par source | un stub pour le métier, un mock pour l'adaptateur, une fois | une seule source, jamais de test |
| **Strategy** (TP 06) | une cascade de `if` choisit l'algorithme dans la classe | l'algorithme est un objet (souvent une fonction) donné à la classe | chaque stratégie testée seule, la classe testée une fois avec une stratégie bidon | deux branches stables |
| **Factory** (TP 07) | la logique « quel nom donne quelle classe » est recopiée partout, l'inconnu passe en silence | une table nom → constructeur, écrite une fois, qui refuse clairement | on enregistre une classe de test sans toucher au package | un ou deux types figés : un `dict` suffit |
| **Facade** (TP 08) | chaque appelant ré-orchestre les mêmes cinq appels, avec ses propres erreurs | une classe qui nomme le cas d'usage et l'enchaîne une fois | un test de bout en bout en deux lignes, un espion pour le journal | un seul appelant, deux lignes |
| **Template Method** (TP 09) | le même déroulé recopié dans plusieurs classes, les corrections ne se propagent pas | une classe abstraite fixe le déroulé, les sous-classes remplissent les trous | le squelette testé une fois avec une sous-classe espionne | un seul format ; trous trop nombreux : passer à Strategy |

**Héritage ou composition.** Template Method : le parent appelle les enfants.
Strategy : l'objet appelle ce qu'on lui donne. Quand les trous se
multiplient ou qu'une variante a besoin d'un état, la composition est plus
simple.

**Les principes derrière**

- *Single Responsibility* : une classe, une raison de changer (TP 06).
- *Open / Closed* : ajouter sans modifier (TP 06, 07, 09).
- *Dependency Inversion* : dépendre d'une interface, pas d'une implémentation (TP 03, 04, 05).
- *Interface Segregation* : un `Protocol` ne déclare que ce dont le client a besoin (TP 03).

En Python, l'interface est souvent implicite (duck typing). `typing.Protocol`
la rend explicite sans héritage. `abc.ABC` l'impose, avec une erreur à
l'instanciation si une méthode manque (TP 09).
