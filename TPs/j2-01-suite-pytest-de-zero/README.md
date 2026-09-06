# TP j2-01 — Mettre en place une suite pytest de zéro

**Durée : 45 min**

## Contexte

`depart/todolist/taches.py` est une liste de tâches en mémoire : on ajoute un
titre avec une priorité, on termine, on liste (priorité haute d'abord), on
filtre. Il est utilisé par la ligne de commande `todo`, le widget du tableau de
bord et l'export hebdomadaire.

Le module est propre : responsabilités séparées, exceptions explicites,
docstrings à jour. Il lui manque une seule chose — **aucun test**.

Personne ne sait donc si `"  relire   le rapport "` devient bien
`"Relire le rapport"`, ce qui se passe quand on termine deux fois la même
tâche, ni si l'ordre de `lister()` est vraiment celui que la docstring annonce.

## Objectif

Construire la structure de tests, puis écrire une suite qui documente le
comportement réel du module.

## Étapes

1. **Créer la structure** (5 min), dans `depart/` :

   ```
   depart/
   ├── conftest.py           ← déjà présent : met `depart/` sur sys.path
   ├── todolist/
   │   └── taches.py
   └── tests/
       ├── conftest.py       ← à créer
       ├── donnees/          ← à créer
       └── unitaires/
           └── test_taches.py
   ```

   > Pas de `__init__.py` dans `tests/`. Vérifiez que `pytest` collecte bien
   > zéro test avant de commencer : `uv run pytest j2-01-*/depart`

2. **Le cas nominal** (5 min). Un seul test, pour valider la mécanique :

   ```python
   def test_ajouter_retourne_la_tache_creee():
       liste = TodoList()
       assert liste.ajouter("Relire le rapport") == Tache(1, "Relire le rapport")
   ```

   > `Tache` est une `dataclass` : deux instances aux mêmes champs sont égales.
   > C'est ce qui rend l'assertion lisible en une ligne.

3. **La normalisation** (10 min). La docstring du module annonce trois
   tolérances de saisie. Écrivez un cas paramétré pour chacune, avec des `id=`
   lisibles, puis un cas qui les cumule.

   Ajoutez un test d'**idempotence** : normaliser deux fois donne le même
   résultat qu'une fois.

4. **L'ordre et les filtres** (10 min). Créez dans `tests/conftest.py` une
   fixture `liste_garnie` : trois tâches de priorités différentes, ajoutées
   **dans le désordre**. Vérifiez que `lister()` les remet dans l'ordre, puis
   qu'à priorité égale l'ordre d'ajout est conservé.

   Paramétrez `filtrer(priorite=...)` sur les trois priorités.

5. **Les erreurs attendues** (10 min). Le module déclare trois exceptions.
   Couvrez-les toutes avec `pytest.raises`, et vérifiez au moins un **message**
   avec `match=`.

   Vérifiez aussi qu'un ajout refusé **ne laisse aucune trace** dans la liste.

6. **Un jeu de données** (5 min). Créez `tests/donnees/titres_valides.txt`
   avec quelques titres déjà normalisés, une fixture dans `tests/conftest.py`
   pour le charger, et un test qui vérifie qu'ils sont tous acceptés tels quels.

## Critères de réussite

- `uv run pytest j2-01-suite-pytest-de-zero/depart` est vert.
- Les trois exceptions du module sont couvertes.
- Au moins un test vérifie un **message** d'erreur, pas seulement son type.
- Vos tests ne créent aucun fichier en dehors de `tests/donnees/`.
- Chaque nom de test décrit un comportement : un lecteur qui ne connaît pas le
  module comprend la règle métier rien qu'en lisant la liste des tests
  (`uv run pytest --collect-only -q`).

## Pour aller plus loin

`TITRE_MAX` vaut 80. Un titre de 121 caractères **saisis**, dont beaucoup
d'espaces, est-il refusé ? La longueur est-elle vérifiée avant ou après la
normalisation ? Lisez le code, tranchez, puis écrivez le test qui documente la
réponse actuelle — et demandez-vous si c'est celle que vous auriez choisie.

## Corrigé

`corrige/` — 36 tests.

```bash
uv run pytest j2-01-suite-pytest-de-zero/corrige -v
```
