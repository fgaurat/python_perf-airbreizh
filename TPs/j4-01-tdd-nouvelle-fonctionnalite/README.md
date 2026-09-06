# TP j4-01 — Ajouter une fonctionnalité par bourgeon

**Durée : 60 min**

## Contexte

`depart/bureau/moteur.py` est le moteur de la calculatrice de bureau :
évaluation d'expressions, fonctions, mémoire (M+, MR, MC), pourcentage, degrés
ou radians, précision d'affichage, journal sur disque. Cent quinze lignes, six
ans d'histoire, neuf auteurs, un `eval` bien caché, **aucun test**.

## La demande

Les utilisateurs veulent un historique :

> « On veut revoir les dix derniers calculs, annuler le dernier pour revenir au
> résultat précédent, et pouvoir rétablir ce qu'on vient d'annuler. Les calculs
> en erreur ne doivent pas apparaître. »

## Objectif

Ajouter la fonctionnalité **en TDD, dans un module neuf**, et ne toucher au
code historique que pour quelques lignes de greffe.

## La tentation, et pourquoi y résister

La tentation est d'ouvrir `moteur.py`, d'ajouter une liste dans `__init__`,
un `append` dans `calculer`, et de bricoler `annuler` à côté de `memoire_plus`.

Vous auriez alors : une logique neuve **noyée** dans cent lignes non testées,
testable seulement en passant par `eval`, la mémoire et le journal — et un
risque de régression sur tout le moteur.

La technique du **bourgeon** consiste à écrire le neuf **à côté**, en TDD, et à
ne toucher à l'existant que pour le brancher.

## Étapes

### 1. Le module neuf, en TDD strict (35 min)

Créez `bureau/historique.py` — **sans ouvrir `moteur.py`**.

Commencez par le test :

```python
def test_enregistrer_retourne_l_entree():
    assert Historique().enregistrer("2 + 2", 4.0) == Entree("2 + 2", 4.0)
```

Trois décisions sont déjà prises : le nom, le fait de stocker une **entrée**
(expression + résultat) plutôt qu'un simple nombre, et le fait que
l'historique ne connaît pas le moteur.

> **Pourquoi `Historique` ne reçoit-il pas la `Calculatrice` ?** Parce qu'il
> n'a besoin ni de `eval`, ni de la mémoire, ni du journal. Plus l'entrée est
> étroite, plus le test est simple — c'est le principe ISP.

Poursuivez par cycles, un cas à la fois :

| Cycle | Cas | Question soulevée |
|---|---|---|
| 1 | enregistrer, relire | le nominal — dans quel ordre `derniers()` rend-il les entrées ? |
| 2 | **onze** calculs pour une capacité de dix | « les dix derniers » : la onzième évince la première ? |
| 3 | annuler, annuler à vide | à vide : `None`, ou une erreur ? |
| 4 | rétablir, puis calculer après une annulation | undo/redo classique — l'énoncé ne le dit pas |
| 5 | `derniers(n)` avec `n` trop grand, nul, négatif | cas dégénérés |

Notez les questions des cycles 1, 3 et 4 : ce sont trois ambiguïtés réelles de
l'énoncé, que le TDD fait apparaître avant la production.

### 2. La greffe (15 min)

Maintenant, ouvrez `moteur.py`. Trois points de contact, et pas un de plus :

1. `__init__` construit un `Historique` — avec une capacité paramétrable ;
2. `calculer` enregistre le résultat, **après** l'arrondi et **après** que les
   erreurs ont été levées — c'est ce qui garantit qu'un calcul en erreur
   n'apparaît pas ;
3. une méthode `annuler()` de quatre lignes, qui remet `derniere_valeur` au
   résultat précédent — pour que `ans` reste cohérent.

> **Question métier à trancher** : après avoir tout annulé, que vaut `ans` ?
> Zéro, comme au démarrage ? Décidez, écrivez-le dans un test, et mentionnez-le
> en fin de séance.

### 3. Les tests d'intégration (10 min)

Six tests suffisent — la règle est déjà couverte par vos tests unitaires.
Vérifiez seulement que le branchement fonctionne : enregistrement, erreur non
enregistrée, `annuler` et `ans`, tout annuler, capacité.

Ajoutez deux tests de non-régression sur ce que le moteur faisait déjà
(mémoire, mode angulaire, précision). Ils vous protégeront si quelqu'un touche
à ce module demain.

## Critères de réussite

- `historique.py` n'importe rien de `moteur.py`.
- Ses tests s'écrivent sans construire de `Calculatrice`.
- La modification de `moteur.py` tient en **moins de dix lignes**.
- Un test prouve qu'un calcul en erreur n'entre pas dans l'historique.
- Vous avez identifié au moins **deux ambiguïtés** dans l'énoncé.

## Discussion (5 min)

Le module historique n'a pas été amélioré. `eval` est toujours là. Est-ce un
échec ?

> Il n'a pas empiré, la partie neuve est correcte et testée, et le travail a
> pris une heure. Un refactoring complet aurait pris trois jours — pour un
> bénéfice que personne n'aurait su chiffrer. Le bourgeon est une technique de
> **survie**, à assumer comme telle : notez la dette, ne la cachez pas.

## Corrigé

`corrige/` — 28 tests (20 unitaires sur l'historique, 8 d'intégration).

```bash
uv run pytest j4-01-tdd-nouvelle-fonctionnalite/corrige -v
```
