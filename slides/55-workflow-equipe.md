---
marp: true
theme: your-theme
paginate: true
header: "Jour 5 — Tests et workflow d'équipe"
---

<!-- _class: lead -->

# 5. Tests et workflow d'équipe

*Les règles qui survivent à la formation*

---

# Quand écrire un test

| Situation | Test à écrire | Quand |
|---|---|---|
| Nouvelle règle métier | unitaire, en TDD | **avant** le code |
| Correction de bug | non-régression | **avant** la correction |
| Refactoring | caractérisation | **avant** de toucher au code |
| Nouvelle intégration externe | test d'intégration | pendant, pour apprendre le comportement réel |
| Code lu et compris difficilement | un test qui documente | pendant la lecture |
| Fonction d'affichage, log, confort | aucun | — |

> Les trois premières lignes disent **avant**. Ce n'est pas une préférence
> méthodologique : un test écrit après n'a jamais été vu rouge, donc rien ne
> prouve qu'il détecte quoi que ce soit.

---

# Ajouter un test lors d'une correction de bug

La séquence, telle qu'elle devrait figurer dans le guide de contribution :

```
  1. Reproduire le bug par un test           → rouge
  2. Committer le test seul                  → « test: reproduit #4231 »
  3. Corriger                                → vert
  4. Committer la correction                 → « fix: corrige #4231 »
  5. Élargir aux cas voisins                 → la famille du bug
```

L'étape 2 est celle qu'on saute. Elle a pourtant deux vertus :

- le relecteur voit **la reproduction** séparée de **la correction** ;
- l'historique contient un commit où le test échoue — la preuve définitive
  qu'il détecte bien le bug.

> **🎯 En pratique** : sur une base sans tests, c'est la règle la plus rentable
> à instaurer. Elle ne demande aucun budget dédié et concentre l'effort
> exactement là où le code casse déjà.

---

# Relire une merge request sous l'angle qualité

Questions à poser, dans cet ordre — les trois premières prennent deux minutes :

| # | Question | Signal |
|---|---|---|
| 1 | La pipeline est-elle verte ? | sinon, on ne relit pas encore |
| 2 | Y a-t-il un test pour ce qui change ? | sinon, pourquoi ? |
| 3 | Les noms de tests décrivent-ils un comportement ? | `test_cas_2` → à renommer |
| 4 | Les cas limites sont-ils couverts ? | vide, borne, erreur attendue |
| 5 | Le test casserait-il si le bug revenait ? | le test décisif |
| 6 | Le contrat public change-t-il ? | signature, exception, valeur de retour |
| 7 | Y a-t-il des mocks superflus ? | signe de couplage non traité |

> **La question 5 est la plus utile et la moins posée.** Un test qui reste vert
> quand on réintroduit le bug ne protège rien. En cas de doute, demandez à
> l'auteur de le montrer.

---

# Ne pas casser une librairie utilisée par d'autres

Une modification est **cassante** dès qu'un projet consommateur doit changer son
code pour continuer à fonctionner :

| Changement | Cassant ? |
|---|---|
| Ajouter une fonction | non |
| Ajouter un paramètre **avec** valeur par défaut | non |
| Ajouter un paramètre **sans** valeur par défaut | **oui** |
| Renommer une fonction, un paramètre, une classe publique | **oui** |
| Changer le type de retour | **oui** |
| Lever une nouvelle exception dans un cas qui marchait | **oui** |
| Cesser de lever une exception | non, mais à signaler |
| Corriger un calcul faux | **oui, en pratique** — les résultats changent |

> **⚠️ La dernière ligne** est la plus délicate dans une librairie
> scientifique : une correction légitime modifie des résultats déjà publiés.
> Elle se traite comme une rupture — annonce, version majeure, note explicite.

---

# Déprécier plutôt que supprimer

```python
import warnings

def calculer_indice_v1(mesures):
    """Ancienne formule d'indice.

    .. deprecated:: 2.3
        Utiliser :func:`calculer_indice`. Suppression prévue en 3.0.
    """
    warnings.warn(
        "calculer_indice_v1 est déprécié depuis la 2.3, "
        "utiliser calculer_indice ; suppression en 3.0",
        DeprecationWarning,
        stacklevel=2,
    )
    return calculer_indice(mesures, formule="v1")
```

Et le test qui garantit que l'avertissement est bien émis :

```python
def test_l_ancienne_api_avertit():
    with pytest.warns(DeprecationWarning, match="3.0"):
        calculer_indice_v1(MESURES)
```

> Trois éléments obligatoires dans le message : **depuis quand**, **par quoi
> remplacer**, **quand ce sera supprimé**.

---

# Documentation minimale des tests

Ce qui mérite d'être écrit, et ce qui ne le mérite pas :

| À documenter | Où |
|---|---|
| Pourquoi ce cas limite existe | docstring du test |
| Le numéro de ticket d'un bug | docstring du test de non-régression |
| Qu'un test est de **caractérisation** | docstring, en toutes lettres, avec la date |
| Comment lancer la suite | `README` du projet, cinq lignes |
| Ce que fait une fixture | docstring de la fixture |

| À ne pas documenter |
|---|
| Ce que fait le test — son **nom** doit suffire |
| Chaque assertion, commentée ligne à ligne |
| Un fichier `TESTS.md` séparé, qui se périmera |

> **La règle** : un commentaire dans un test explique un **pourquoi**. Si vous
> devez expliquer le **quoi**, renommez le test.

---

# Les standards d'équipe qui tiennent

Cinq règles, tenant sur une page du guide de contribution :

> **1.** Aucune correction de bug sans le test qui échouait avant.

> **2.** Le code neuf est testé — vérifié par la couverture du diff.

> **3.** Une pipeline rouge se traite avant tout autre travail.

> **4.** Un test instable est supprimé ou réparé dans la semaine — jamais relancé.

> **5.** Une rupture d'API publique s'annonce et se déprécie avant de se supprimer.

Ce qui rend ces règles applicables : **quatre sur cinq sont vérifiables
automatiquement**. La seule qui repose sur la discipline est la troisième — et
c'est celle qui déterminera si tout le reste sert à quelque chose.

---

# À retenir

> **1.** Le test s'écrit **avant** dans les trois cas qui comptent : nouvelle
> règle, correction de bug, refactoring. Sinon il n'a jamais été vu rouge.

> **2.** En revue, la question décisive est : *ce test casserait-il si le bug
> revenait ?*

> **3.** Dans une librairie partagée, corriger un calcul faux est une rupture
> pour vos consommateurs. Elle s'annonce.
