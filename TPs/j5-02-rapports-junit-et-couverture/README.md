# TP j5-02 — Rapports JUnit et couverture

**Durée : 45 min**

## Contexte

`depart/` contient `todolist`, un petit package de planification : chaque
tâche reçoit un **score** — poids de la priorité, bonus d'étiquette (`URGENT`,
`CLIENT`), un point par jour de retard, plafond à 10 — et la liste est triée
par score décroissant.

Six tests. Ils passent tous.

## Objectif

Produire les rapports que GitLab sait exploiter, se servir de la couverture
comme d'un **outil de diagnostic**, et poser un seuil qui protège sans nuire.

## Étapes

### 1. Mesurer (5 min)

```bash
cd j5-02-rapports-junit-et-couverture/depart
uv lock
uv run --frozen pytest --cov=src --cov-report=term-missing
```

```
Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
src/todolist/planning.py       48     12     10      2    72%   45, 59-62, 69, 81-86
```

72 %. Beaucoup d'équipes trouveraient cela acceptable.

> **La colonne qui compte est `Missing`**, pas le pourcentage. Elle nomme les
> lignes et les branches que vos tests n'atteignent jamais. Ouvrez le fichier
> et regardez ces douze lignes.

### 2. Écrire les tests manquants (20 min)

Prenez la colonne `Missing` ligne par ligne.

**Lignes 59-62** — `bonus_etiquette`. Trois étiquettes au barème, un cas
d'erreur, une histoire de casse. Trois tests.

**Ligne 69** — le cumul de l'étiquette dans `score`. Écrivez le test le plus
naturel :

```python
def test_l_etiquette_s_ajoute_a_la_priorite():
    tache = Tache(1, "X", JOUR, priorite="haute", etiquette="client")
    assert score(tache, JOUR) == 3 + 2
```

**Arrêtez-vous.** Que renvoie réellement l'appel ?

**Lignes 81-86** — `resume`. Un test avec deux tâches suffit.

### 3. Ce que vous venez de découvrir (5 min)

Le test de la ligne 69 échoue. En production, une tâche **haute** étiquetée
**client** score 2 au lieu de 5 : l'étiquette **écrase** la priorité au lieu
de s'y ajouter. Les tâches urgentes des clients passent derrière les tâches
internes basses en retard d'un jour.

Le code fautif tient en un caractère : `=` au lieu de `+=`.

> Les six tests d'origine passaient. La couverture affichait 72 %, ce qui
> paraissait honnête. Le bug vivait dans les 28 % restants — et personne ne
> lisait la liste triée d'assez près pour s'en apercevoir.
>
> **C'est l'usage utile de la couverture** : elle ne juge pas la qualité de vos
> tests, elle vous montre où vous n'avez jamais regardé.

Corrigez, documentez le bug dans la docstring du test, puis élargissez : le
plafond à 10 (exactement 10, et au-delà), le cumul des trois sources, le tri à
score égal.

### 4. La ligne qui restera non couverte (5 min)

Après vos tests, la couverture atteint 97 %. La ligne 45 résiste :

```python
for nom, poids in POIDS_PRIORITE:
    if priorite == nom:
        return poids
return 0  # ← ligne 45
```

Essayez d'écrire un test qui l'atteint. Vous n'y arriverez pas : la priorité
est validée à la construction de `Tache`, et `poids_priorite` n'est appelée
qu'avec une priorité connue. **C'est du code mort.**

> Chercher les 3 % manquants vous a appris quelque chose sur le code. Les
> atteindre à tout prix vous ferait écrire un test absurde. Supprimez la ligne,
> ou laissez-la — mais ne truquez pas la métrique.

### 5. La pipeline (10 min)

Écrivez `.gitlab-ci.yml` avec les deux rapports :

```yaml
tests:
  script:
    - uv run pytest --junitxml=rapport.xml --cov=src --cov-report=xml
      --cov-report=term-missing --cov-fail-under=90
  coverage: '/TOTAL.*\s+(\d+%)$/'
  artifacts:
    when: always
    reports:
      junit: rapport.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

```bash
uv run --frozen python outils/simuler_pipeline.py
```

Deux points à comprendre :

- **`when: always`** — sans cette ligne, GitLab ne récupère les artifacts que si
  le job réussit. Testez-le : cassez un test, relancez, et constatez.
- **`--cov-fail-under=90`** — la couverture est à 97 %. Le seuil est réglé
  **en dessous**. C'est un **cliquet** : il n'impose pas de progresser, il
  empêche de régresser. Un seuil à 100 % produirait des tests sans assertion.

## Critères de réussite

- Couverture à 97 %, et vous savez expliquer pourquoi pas 100 %.
- Le bug du cumul est corrigé, avec un test dont la docstring en garde la trace.
- `rapport.xml` et `coverage.xml` sont produits.
- `when: always` figure dans les artifacts.
- Le seuil est réglé sous la valeur actuelle, pas au-dessus.

## Discussion (5 min)

Si l'équipe s'était fixé « 80 % de couverture » comme objectif, aurait-elle
trouvé ce bug ?

> Le paquet était à 72 %. Atteindre 80 % demandait deux ou trois tests. Les
> plus faciles à écrire étaient ceux de `bonus_etiquette` — lignes 59-62, sans
> bug. L'objectif aurait été atteint, le badge serait passé au vert, et le bug
> serait resté.

## Corrigé

`corrige/` — 29 tests, 97 % de couverture, pipeline avec les deux rapports.

```bash
cd j5-02-rapports-junit-et-couverture/corrige
uv lock && uv run --frozen pytest --cov=src --cov-report=term-missing
```
