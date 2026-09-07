# TP 02 : fixtures, fichiers temporaires et TodoDAO

**Durée : 45 min**

## Contexte

`depart/todoapp/todo_dao.py` est le `TodoDAO` du tp1, avec une méthode
`creer_table()` en plus pour ne plus dépendre d'un fichier `todos.db` créé à la
main. Il écrit et lit des `Todo` dans une base sqlite.

Ce matin on l'a testé en lançant `main.py` et en regardant les `print`. Le
fichier `todos.db` s'est rempli à chaque lancement, et personne n'a vérifié ce
qui en revenait.

## Objectif

Écrire une suite de tests qui ne touche jamais au vrai fichier, en factorisant
la préparation dans des fixtures. En chemin, deux bugs du DAO vont apparaître.

## Étapes

### 1. Le premier test avec `tmp_path` (5 min)

Dans `depart/tests/test_todo_dao.py` :

```python
def test_save_puis_find_all(tmp_path):
    dao = TodoDAO(tmp_path / "todos.db")
    dao.creer_table()
    dao.save(Todo(title="Relire le rapport"))
    assert list(dao.find_all()) == [Todo(1, "Relire le rapport", False)]
```

`tmp_path` est un dossier vide, unique à ce test, fourni par pytest. Ajoutez
`print(tmp_path)` et lancez avec `-s` pour voir où il se trouve.

Pourquoi `list(...)` ? `find_all` est un générateur (revoir le tp1) : sans
`list`, la comparaison avec une liste est toujours fausse. Essayez.

### 2. Extraire des fixtures (10 min)

Écrivez deux tests de plus (par exemple : deux `save` donnent deux todos, un
todo `completed=True` revient bien terminé). Vous avez recopié trois fois les
deux mêmes lignes.

Créez `depart/tests/conftest.py` avec trois fixtures :

- `dao` : un DAO sur `tmp_path / "todos.db"`, table créée ;
- `todos` : une liste de trois `Todo`, dont un terminé ;
- `dao_rempli` : composée des deux précédentes, les trois todos déjà sauvés.

```python
@pytest.fixture
def dao(tmp_path):
    dao = TodoDAO(tmp_path / "todos.db")
    dao.creer_table()
    yield dao
    dao.fermer()          # tout ce qui suit le yield est le teardown
```

`fermer()` n'existe pas : ajoutez-la, et supprimez `__del__`. Un `__del__`
ferme la connexion « quand Python y pense », ce qui n'est jamais le bon moment
dans un test.

Vérifiez avec `python -m pytest --fixtures` que vos fixtures apparaissent avec
leur docstring.

### 3. Les cas limites, et les bugs qu'ils révèlent (15 min)

Un test par situation. Certains vont être rouges : c'est le but.

| Situation | Attendu |
|---|---|
| `find_all` sur une table vide | `[]` |
| `save(Todo(title="L'essentiel"))` | le titre revient intact |
| `save(Todo(title="Robert'); DROP TABLE todos_tbl; --"))` | le titre revient intact, la table existe toujours |
| un todo `completed=True` relu | `todo.completed is True` (pas `== True`, `is`) |
| `save` d'un todo | on aimerait connaître son `id` après coup |

Le deuxième et le troisième cas plantent : regardez comment `save` construit
sa requête. Corrigez avec des paramètres (`?`) et non en échappant l'apostrophe.

Le quatrième cas échoue parce que sqlite rend `1` et non `True`. Décidez :
convertir dans `find_all`, ou dans `Todo`. Le test documente le choix.

Pour le dernier, `cursor.lastrowid` existe. Faites en sorte que `save` renseigne
`todo.id` et le retourne.

### 4. Marqueurs et exécution ciblée (10 min)

Ces tests écrivent sur le disque. Ils sont rapides ici, mais ce sont des tests
d'intégration : ils vérifient le DAO contre un vrai sqlite. Marquez-les :

```python
pytestmark = pytest.mark.integration     # en tête de module : tout le fichier
```

Le marqueur est déclaré dans `pytest.ini`, regardez-le. Puis :

```bash
python -m pytest -m integration
python -m pytest -m "not integration"
python -m pytest --durations=3
```

sqlite sait travailler en mémoire : `TodoDAO(":memory:")`. Ajoutez une fixture
`dao_memoire` et un test qui l'utilise, non marqué. Relancez
`-m "not integration"`.

### 5. Bonus : une fixture paramétrée

Les tests sont les mêmes en mémoire et sur disque. Plutôt que de les dupliquer,
paramétrez la fixture :

```python
@pytest.fixture(params=[
    pytest.param("memoire", id="memoire"),
    pytest.param("fichier", id="fichier", marks=pytest.mark.integration),
])
def dao(request, tmp_path):
    ...
```

Chaque test tourne alors deux fois, et `-m "not integration"` ne garde que la
variante mémoire. Regardez le rendu avec `-v`.

## Critères de réussite

- Aucun test n'écrit ailleurs que dans `tmp_path`.
- `conftest.py` contient au moins trois fixtures, dont une composée et une avec teardown.
- `__del__` a disparu.
- Le titre `"L'essentiel"` est sauvé et relu, la requête utilise des paramètres.
- `completed` revient en `bool`.
- `python -m pytest -m "not integration"` exécute au moins un test.

## Discussion (5 min)

Ce que vous venez d'écrire teste le DAO contre un vrai sqlite. Au jour 3,
on testera le code *qui utilise* le DAO sans aucune base : c'est là qu'on
parlera de fake, de mock et de Repository. Où passe la frontière entre les
deux ?

## Corrigé

```bash
cd corrige
python -m pytest -v
python -m pytest -m "not integration" -v
```
