# TP j2-04 — Un cycle TDD complet

**Durée : 60 min — le TP central de la journée**

## Contexte

L'équipe documentation a besoin de numéroter les chapitres et les annexes en
chiffres romains. Voici l'énoncé, tel qu'il vous a été transmis :

> « Il faut une fonction qui convertit un nombre en chiffres romains. Par
> exemple 4 donne IV, et 1994 donne MCMXCIV. »

C'est tout. Pas de spécification plus détaillée — c'est la situation habituelle.

`depart/nombres/romains.py` est **vide**. C'est voulu.

## Objectif

Écrire la fonction en TDD strict, et constater ce que le cycle Red / Green /
Refactor fait apparaître que l'énoncé ne dit pas.

## Règle du jeu

**Aucune ligne de code de production ne s'écrit sans un test rouge qui la
réclame.** Si vous vous surprenez à écrire une règle que personne ne demande,
supprimez-la et écrivez d'abord le test.

Notez chaque question soulevée dans `depart/tests_a_ecrire.md`. C'est le vrai
livrable du TP.

## Étapes

### Cycle 1 — le cas trivial (5 min)

Écrivez le test le plus simple imaginable, **avant** toute implémentation :

```python
def test_un():
    assert romain(1) == "I"
```

Lancez `pytest`. Vous devez voir une `ImportError`. **C'est un rouge valide.**

Trois décisions viennent d'être prises sans qu'aucun code n'existe. Lesquelles ?
Notez-les.

Implémentez le minimum — oui, `return "I"` est une implémentation valide à ce
stade — faites passer, passez au cycle suivant.

### Cycle 2 — la répétition (10 min)

```python
def test_deux():
    assert romain(2) == "II"
```

Rouge, puis vert. Puis 3, puis 10, 20, 30. À quel moment `return "I"` cesse
d'être tenable ? C'est le refactor qui fait apparaître la boucle.

### Cycle 3 — la notation soustractive (15 min)

```python
def test_quatre():
    assert romain(4) == ???
```

**Arrêtez-vous ici.** Regardez une horloge à chiffres romains : elle affiche
souvent `IIII`. L'énoncé dit `IV`. Deux questions qu'aucune ligne ne tranche :

1. Y a-t-il **une** forme correcte, ou plusieurs ? Laquelle produisez-vous ?
2. Une fois `IV` choisi : quelles autres paires suivent la même logique ?

Décidez, notez votre décision, puis écrivez les tests qui l'expriment — il y a
**six** formes soustractives. Faites-les passer une par une, puis vérifiez
`1994 → MCMXCIV`.

> Au refactor, la plupart des implémentations convergent vers une **table
> ordonnée** de treize paires (valeur, symbole) parcourue de la plus grande à
> la plus petite. Si la vôtre est une cascade de `if`, c'est le moment.

### Cycle 4 — les cas limites (10 min)

Un par un, en rouge d'abord. Que faire de `0` ? De `-1` ? De `4000` ? De `3.0` ?

Chaque réponse est une décision :

- les Romains n'avaient pas de zéro — exception, ou `""` ?
- au-delà de 3999, il faut une barre au-dessus des lettres — hors périmètre ?
- `3.0` n'est pas une donnée invalide, c'est une **erreur de programmation** de
  l'appelant : `TypeError` plutôt qu'une exception métier ?

Chaque exception métier dérive d'une racine commune.

### Cycle 5 — le sens inverse (10 min)

Personne ne l'a demandé. Mais un test d'**aller-retour** est la propriété la
plus forte que vous puissiez écrire, et il coûte une fonction `arabe`.

```python
def test_aller_retour():
    assert arabe("MCMXCIV") == 1994
```

Nouvelles questions : `arabe("IIII")` — accepté (4) ou refusé ? `arabe("xiv")` ?
`arabe("")` ? `arabe("MMMM")` ? Décidez, notez, testez.

### Cycle 6 — refactor et propriétés (10 min)

Relisez votre implémentation. Extrayez ce qui mérite un nom. Vos tests doivent
rester verts **sans être modifiés** — c'est ce qui prouve que le comportement
est préservé.

Terminez par des tests de propriété :

- `arabe(romain(n)) == n` pour **tout** `n` du domaine — une boucle dans un test ;
- seuls les sept symboles `MDCLXVI` apparaissent ;
- jamais quatre symboles identiques consécutifs ;
- `V`, `L` et `D` n'apparaissent jamais deux fois.

## Critères de réussite

- Chaque test a été vu **rouge** avant d'être vert.
- `depart/tests_a_ecrire.md` contient au moins **quatre questions** que l'énoncé
  ne tranchait pas.
- `arabe(romain(n)) == n` pour tout `n` de 1 à 3999.
- Le résultat est déterministe : relancer la suite donne le même résultat.

## Discussion (5 min, en groupe)

Comparez vos décisions. Combien de participants acceptent `IIII` en lecture ?
Combien ont choisi une exception pour `0`, combien une chaîne vide ? Quelle est
la plus grande valeur acceptée ?

Aucune de ces réponses n'est dans l'énoncé. Toutes ont dû être prises. **Le TDD
n'a pas inventé ces questions : il les a fait poser avant la mise en production,
plutôt qu'après.**

## Corrigé

`corrige/` — implémentation et tests organisés par cycle, plus de 250 cas dont
un aller-retour sur les 3999 valeurs. Lisez le fichier de tests dans l'ordre :
il raconte la conception.

```bash
uv run pytest j2-04-premier-cycle-tdd/corrige -v
```
