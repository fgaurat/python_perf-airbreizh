# TP 06 : Strategy

**Durée : 45 min**

## Contexte

`depart/todoapp/todolist.py` est une liste de tâches en mémoire. Sa méthode
`lister(tri=...)` sait trier par ordre d'ajout, par titre, par priorité, ou
restantes d'abord. Le choix se fait par une chaîne, dans une cascade de `if`.

```bash
cd depart
python main.py
python -m pytest -v
```

Deux tests, verts.

## Objectif

Sortir les algorithmes de tri de la classe, pour pouvoir en ajouter sans la
modifier et les tester sans elle.

## Étapes

### 1. La demande qui fait mal (10 min)

On vous demande un cinquième tri : par priorité décroissante, puis par titre à
priorité égale. Faites-le : test d'abord, puis le `elif`.

Notez ce que ça a coûté :

- un `elif` de plus dans `TodoList`, qui n'a rien à voir avec le tri ;
- un test qui a dû construire une `TodoList` et trois tâches pour vérifier
  une seule fonction de tri ;
- et si vous écrivez `liste.lister("priorit")`, rien ne vous le dit avant
  l'exécution.

Regardez aussi les deux tests existants : les mêmes trois lignes d'`ajouter`
sont recopiées partout.

### 2. Nommer le problème (5 min)

`TodoList` a deux raisons de changer : les règles de la liste, et les façons
de la trier. C'est le principe ouvert / fermé du jour 1 : on voudrait pouvoir
ajouter un tri sans rouvrir la classe.

L'algorithme est choisi *dans* la classe. Il devrait lui être *donné*.

### 3. Le tri devient un objet (10 min)

Un tri, c'est une fonction qui prend une liste de todos et en rend une autre.
En Python, une fonction est un objet : pas besoin de classe.

Créez `todoapp/tris.py` :

```python
def par_titre(todos: list[Todo]) -> list[Todo]:
    return sorted(todos, key=lambda t: t.title.lower())
```

Une fonction par tri. Puis `lister` devient :

```python
def lister(self, tri=par_ajout) -> list[Todo]:
    return tri(list(self._todos))
```

Le `ValueError` disparaît : un nom faux est un `NameError` à l'import, avant
tout test.

### 4. Tester séparément (10 min)

Chaque tri se teste sur une liste de `Todo` construite en une ligne, sans
`TodoList`. Réécrivez les tests de tri ainsi, avec une fixture `todos` pour
les trois tâches.

`TodoList.lister` se teste une seule fois : « elle applique le tri reçu ».
Donnez-lui un tri bidon, `reversed` par exemple, ou une fonction qui renvoie
une liste vide.

### 5. Quand une classe devient utile (5 min)

Un tri « restantes d'abord, mais seulement celles de priorité au moins N » a
besoin d'un paramètre. Une fonction avec `functools.partial` marche. Une
classe avec `__init__(self, seuil)` et `__call__(self, todos)` se lit mieux.
Écrivez-en une, et son test.

C'est la forme classique du pattern. En Python, on ne l'utilise que quand la
stratégie a un état.

## Critères de réussite

- `todolist.py` ne contient plus aucun `if` sur le tri, ni le mot `sorted`.
- Ajouter un tri ne modifie que `tris.py` et son test.
- Les tests de tri ne construisent pas de `TodoList`.
- `TodoList.lister` a exactement un test, avec un tri factice.

## Discussion (5 min)

`main.py` affichait les tris par leur nom en chaîne. Où va la table
`{"titre": par_titre, ...}` maintenant ? À la frontière, dans `main.py` ou la
ligne de commande, jamais dans `TodoList`. Choisir un objet à partir d'un nom,
c'est le TP 07.

Sur-design : deux tris qui n'ont pas bougé depuis un an, un `if` de trois
lignes. Laissez-le.

## Corrigé

```bash
cd corrige
python -m pytest -v
python main.py
```
