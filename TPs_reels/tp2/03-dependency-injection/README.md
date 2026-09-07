# TP 03 : Dependency Injection

**Durée : 45 min**

## Contexte

`depart/todoapp/todo_service.py` ajoute des règles métier au-dessus du
`TodoDAO` du tp1 : lister les tâches restantes, produire un résumé. Le DAO est
celui du TP 02, corrigé (requêtes paramétrées, `fermer()`).

Le service marche : lancez `python main.py` deux fois.

## Objectif

Écrire un test unitaire du service qui ne touche à aucune base de données, et
découvrir ce qui l'empêche.

## Étapes

### 1. Le test impossible (10 min)

Lancez `python -m pytest`. Le test de `tests/test_todo_service.py` est rouge,
et un fichier `todos.db` vient d'apparaître dans `depart/`. Relancez : le
résultat change. Vous venez d'écrire un test qui pollue le disque et dont le
résultat dépend du lancement précédent.

Essayez de le rendre correct sans modifier `todo_service.py`. Quelles sont vos
options ? Supprimer `todos.db` avant chaque test ? Écrire dedans avec un second
DAO ? Aucune n'est un test unitaire : toutes passent par sqlite.

### 2. Nommer le problème (5 min)

Regardez `__init__`. Le service construit lui-même sa dépendance, avec un
chemin en dur. Personne de l'extérieur ne peut lui donner autre chose. C'est le
point 5 du jour 1 : « objets qui construisent eux-mêmes toutes leurs
dépendances ».

Un test unitaire du service a besoin de contrôler ce que `find_all` renvoie.
Il ne le peut pas.

### 3. Injecter la dépendance (10 min)

Le service reçoit son DAO au lieu de le créer :

```python
class TodoService:
    def __init__(self, dao):
        self._dao = dao
```

C'est tout le pattern. Mettez à jour `main.py`, qui devient le seul endroit
où `TodoDAO("todos.db")` est écrit. On appelle ça la *composition root* : le
point d'entrée assemble, le reste reçoit.

### 4. Le test devient simple (10 min)

Dans le test, donnez au service un objet qui ressemble à un DAO :

```python
class FauxDAO:
    def __init__(self, todos):
        self._todos = todos

    def find_all(self):
        return list(self._todos)
```

Aucune base, aucun fichier. Écrivez :

- `restantes` exclut les terminées ;
- `restantes` sur un DAO vide ;
- `resume` pour 0, 1 et 2 tâches. Le texte « 1 tâches restantes » est-il correct ?
  Corrigez le service, le test vous le permet maintenant.

Le service ne vérifie jamais le type de ce qu'il reçoit : c'est le duck typing
du tp1. Si vous voulez le rendre explicite, un `Protocol` avec `find_all` et
`save` suffit, sans héritage.

### 5. Et la valeur par défaut ? (5 min)

Certains voudront garder `TodoService()` sans argument, avec un DAO par défaut :

```python
def __init__(self, dao=None):
    self._dao = dao or TodoDAO("todos.db")
```

Discutez : le service connaît encore sqlite et le chemin. Que se passe-t-il le
jour où le DAO prend un paramètre de plus ? Le corrigé choisit de ne pas avoir
de défaut, et de laisser `main.py` assembler.

## Critères de réussite

- `python -m pytest` est vert et ne crée aucun fichier.
- `todo_service.py` n'importe plus `TodoDAO`.
- `TodoDAO("todos.db")` n'apparaît que dans `main.py`.
- Le faux DAO fait moins de dix lignes et vit dans le fichier de test.

## Discussion (5 min)

Le faux DAO ne sait faire que `find_all`. Le jour où le service appelle
`save`, le test cassera avec `AttributeError`, et le jour où le faux `save`
ne fait pas la même chose que le vrai, le test passera à tort. C'est le
sujet du TP 04.

## Corrigé

```bash
cd corrige
python -m pytest -v
python main.py
```
