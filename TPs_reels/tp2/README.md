# Jour 2 : design patterns comme outils de testabilité, avec ce qu'il faut de pytest

Neuf TP indépendants, dans le prolongement de ce qui a été codé au tp1
(Rectangle, Cercle, Carre, Todo, TodoDAO, ABC, Protocol). Chacun a son propre
code, on peut les faire dans n'importe quel ordre.

Les TP 03 à 09 suivent tous la même trame : un code qui marche mais qui est
mal conçu, un test qu'on essaie d'écrire et qui fait mal, le problème nommé,
le pattern comme réponse, et le test qui devient simple. Le pattern n'est
jamais présenté avant le problème.

| TP | Sujet | Pattern | Le test qui fait mal | Durée |
|---|---|---|---|---|
| `01-premiers-tests-geometrie` | Rectangle, Cercle, Carre | (pytest : structure, paramétrisation, exceptions, cas limites) | | 45 min |
| `02-fixtures-todo-dao` | TodoDAO sqlite | (pytest : fixtures, `tmp_path`, marqueurs) | | 45 min |
| `03-dependency-injection` | TodoService qui crée son DAO | Dependency Injection | impossible sans `todos.db` | 45 min |
| `04-repository` | faux DAO qui ne fait pas comme le vrai | Repository + test de contrat | vert en test, doublon en prod | 60 min |
| `05-adapter` | hello world qui lit l'heure sur une API | Adapter | dépend du réseau et de l'heure | 45 min |
| `06-strategy` | `lister(tri="...")` en cascade de `if` | Strategy | un tri de plus = rouvrir la classe | 45 min |
| `07-factory` | `if type_ == "cercle"` recopié partout | Factory | la forme inconnue disparaît en silence | 45 min |
| `08-facade` | cinq modules à enchaîner soi-même | Facade | le test recopie l'orchestration | 45 min |
| `09-template-method` | rapport texte et HTML dupliqués | Template Method | bug corrigé d'un côté seulement | 45 min |

## Déroulé suggéré pour une journée

Sept patterns en un jour ne tiennent pas. Cinq TP, plus un en réserve :

| Heure | Séquence |
|---|---|
| 9h00 | Ouverture : le bug `x + yx` de `main_prot.py` du tp1, mypy dit OK. Pourquoi tester, quoi tester. |
| 9h20 | Démo : étape 1 du TP 01 en direct (structure, premier test, `pytest -v`, un test cassé). |
| 9h40 | TP 01, étapes 2 à 3 seulement : paramétrisation, `approx`, exceptions métier. |
| 10h20 | Débrief, puis démo fixtures et `tmp_path` en dix minutes (le TP 02 n'est pas fait, il est en réserve). |
| 10h45 | Pause |
| 11h00 | TP 03 Dependency Injection. |
| 11h45 | TP 04 Repository, qui enchaîne directement. |
| 12h45 | Déjeuner |
| 13h45 | Débrief 03 et 04 : DAO contre Repository, ce que prouve un test de contrat. |
| 14h00 | TP 06 Strategy. |
| 14h45 | TP 07 Factory. |
| 15h30 | Pause |
| 15h45 | TP 09 Template Method, puis comparaison Strategy contre Template Method. |
| 16h30 | Bilan : pour chaque pattern, le problème qu'il résout et le cas où il est de trop. |

En réserve, ou pour un groupe rapide : TP 05 Adapter (introduit `unittest.mock.patch`)
et TP 08 Facade. Le TP 02 sert si le groupe a besoin de plus de pytest avant
d'attaquer les patterns.

## Mise en place (une seule fois)

Python 3.10 ou plus.

```bash
cd TPs_reels/tp2
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install pytest
```

## Structure d'un TP

```
0N-nom-du-tp/
  README.md      énoncé : contexte, étapes, critères de réussite, discussion
  depart/        le code sur lequel vous travaillez, avec son main.py
  corrige/       une solution possible, commentée aux endroits de décision
```

Chaque `depart/` et `corrige/` contient un `conftest.py` vide à la racine :
c'est lui qui permet à pytest d'importer les packages (`from geo.rectangle import ...`)
sans rien installer.

## Lancer les tests

```bash
cd 03-dependency-injection/depart
python -m pytest              # tous les tests du dossier
python -m pytest -v           # un nom par ligne
python -m pytest -x           # s'arrêter au premier échec
python -m pytest -k restantes # seulement les tests dont le nom contient "restantes"
python -m pytest --lf         # seulement ceux qui ont échoué la dernière fois
python -m pytest tests/test_todo_service.py::test_resume   # un seul test
python main.py                # le programme lui-même
```

Pour tout vérifier d'un coup depuis `tp2/` :

```bash
for d in */corrige; do (cd "$d" && python -m pytest -q); done
```
