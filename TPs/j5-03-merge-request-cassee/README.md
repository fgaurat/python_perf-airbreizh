# TP j5-03 — Une merge request avec une pipeline rouge

**Durée : 45 min**

## Contexte

Vous êtes de garde sur les merge requests du package `convertisseur`, qui
convertit des longueurs et des températures. Il est consommé par le module
d'import des fiches produit et par l'export vers le catalogue anglophone.

Une MR vient d'arriver :

> **MR !418 — Ajout du mille nautique**
>
> *L'équipe logistique maritime a besoin du mille nautique. J'ai ajouté l'unité
> et factorisé au passage : les conversions de longueur étaient une cascade de
> `if`, elles passent maintenant toutes par une table de facteurs vers le
> kilomètre, avec le même arrondi à quatre décimales qu'avant.*
>
> ❌ **Pipeline en échec** — job `tests`

## Objectif

Diagnostiquer, corriger, valider. Et surtout : **dans le bon ordre**.

## La règle du TP

> **N'ouvrez pas `src/` avant l'étape 3.**

Le réflexe est de lire le code source. Le TP fait travailler la compétence
inverse : partir du rapport, laisser les tests vous conduire au défaut.

## Étapes

### 1. Lire le rapport de la pipeline (10 min)

Le job a produit son artifact — c'est le fichier `rapport_pipeline_418.xml`,
que vous téléchargeriez depuis GitLab.

```bash
cd j5-03-merge-request-cassee/depart
uv lock
uv run --frozen python outils/lire_rapport.py rapport_pipeline_418.xml
```

Répondez, **sans ouvrir le code** :

| Question | Votre réponse |
|---|---|
| Combien de tests au total ? | |
| Combien en échec ? | |
| Quelles unités sont concernées ? | |
| Quelles unités **ne** le sont **pas** ? | |
| Les valeurs obtenues sont-elles trop grandes ou trop petites ? | |

> La quatrième ligne est la plus instructive. Kilomètres, miles, milles
> nautiques et températures passent. Qu'ont en commun les quatre tests rouges,
> et que n'ont pas les autres ?

### 2. Formuler une hypothèse (10 min)

Regardez les écarts, toujours sans ouvrir `src/` :

```
test_pouce_vers_centimetre     obtenu 0.0    attendu 2.54
test_pied_vers_metre           obtenu 0.3    attendu 0.3048
test_millimetre_vers_metre     obtenu 0.0    attendu 0.001
```

Un pouce donne zéro centimètre, et un pied donne 0,3 mètre tout rond. Que
peut-on en déduire sur le moment où l'arrondi est appliqué — et sur l'unité
dans laquelle il l'est ?

Écrivez votre hypothèse en une phrase avant de continuer.

### 3. Vérifier dans le code (10 min)

Ouvrez maintenant `src/convertisseur/longueurs.py`. Regardez la fonction
ajoutée par la MR :

```python
def _via_base(valeur, de, vers, facteurs):
    base = round(valeur * facteurs[de], DECIMALES)
    return round(base / facteurs[vers], DECIMALES)
```

Votre hypothèse était-elle juste ?

> La factorisation était une bonne idée — les conversions partageaient
> réellement le même schéma. Mais elle a introduit un **arrondi intermédiaire**
> sur la valeur en kilomètres. Un pouce vaut 0,0000254 km : à quatre décimales,
> c'est zéro. Les grandes unités n'y voient rien, les petites sont écrasées.

### 4. Corriger (5 min)

Corrigez `_via_base` — **sans révoquer la factorisation**, qui reste
justifiée. Une MR qui casse quelque chose se corrige ; on ne l'annule que si
son intention était mauvaise.

Ajoutez un commentaire qui explique **pourquoi** l'arrondi ne doit porter que
sur le résultat final : c'est exactement le genre d'erreur qui se reproduira.

### 5. Ajouter le test de non-régression (5 min)

Les quatre tests rouges existaient déjà — c'est ce qui a sauvé la MR. Mais rien
ne dit explicitement que **l'arrondi unique** est la règle.

Ajoutez un test paramétré qui l'énonce, avec le numéro de MR dans sa docstring :

```python
def test_l_arrondi_ne_porte_que_sur_le_resultat_final(valeur, de, vers, attendu):
    """Non-régression MR !418 — un arrondi intermédiaire en km écrasait les petites unités."""
```

> Choisissez vos cas avec soin : `1 mm → km` vaut 0,000001, ce qu'aucun arrondi
> à quatre décimales ne peut représenter, même correct. Un test de non-régression
> doit être rouge avec le bug **et** vert sans lui. `12 in → ft` fait 1,0 :
> voilà un bon cas.

### 6. Valider la pipeline (5 min)

```bash
uv run --frozen python outils/simuler_pipeline.py
```

Les deux stages doivent passer. Régénérez le rapport et relisez-le :

```bash
uv run --frozen pytest --junitxml=rapport.xml -q
uv run --frozen python outils/lire_rapport.py rapport.xml
```

## Critères de réussite

- Vous avez formulé votre hypothèse **avant** d'ouvrir `src/`.
- La factorisation est conservée, et corrigée.
- Un test de non-régression porte le numéro de la MR.
- `simuler_pipeline.py` affiche `✓ PIPELINE VERTE`.

## Discussion (10 min)

**Première question.** Cette MR aurait-elle pu être fusionnée si le projet
n'avait pas eu ces quatre tests ? Combien de temps avant que quelqu'un s'en
aperçoive — sachant que les fiches produit importées en pouces auraient toutes
affiché une dimension de 0 cm, et que le catalogue anglophone ne concerne que
quelques références ?

**Deuxième question.** Que répondez-vous à l'auteur de la MR ? Rédigez le
commentaire de revue en trois lignes.

> Piste : la factorisation était pertinente. Le défaut n'est pas d'avoir
> refactorisé, c'est d'avoir refactorisé **et** ajouté une fonctionnalité dans
> la même MR — précisément ce que le Jour 4 recommandait d'éviter. Deux MR
> séparées auraient rendu l'arrondi intermédiaire évident.

## Corrigé

`corrige/` — 29 tests, dont 4 de non-régression sur la MR !418.

```bash
cd j5-03-merge-request-cassee/corrige
uv lock && uv run --frozen python outils/simuler_pipeline.py
```
