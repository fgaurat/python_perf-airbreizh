---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — Prioriser ce qui doit être testé"
---

<!-- _class: lead -->

# 2. Prioriser ce qui doit être testé

*Un budget de test est fini — il faut le dépenser*

---

# On ne teste pas tout : on choisit

Personne n'a le temps de tester exhaustivement une librairie existante. La
question réaliste n'est donc pas *« faut-il tester ? »* mais :

> **Où placer les 20 premiers tests pour éliminer 80 % du risque ?**

Deux critères suffisent à décider :

| Critère | Question |
|---|---|
| **Risque** | Si c'est faux, combien de temps avant qu'on s'en aperçoive ? |
| **Volatilité** | À quelle fréquence ce code est-il modifié ? |

Un code risqué **et** souvent modifié est votre priorité absolue.
Un code stable et sans conséquence peut attendre indéfiniment.

---

# La grille de décision

|  | **Rarement modifié** | **Souvent modifié** |
|---|---|---|
| **Conséquence forte** | Tester — un jeu de cas de référence | **Tester en premier** — et densément |
| **Conséquence faible** | Laisser tel quel | Tester au fil de l'eau, quand on y touche |

Exemples typiques dans une librairie métier :

- *fort + volatile* → règles de gestion, grilles tarifaires, formules d'indice ;
- *fort + stable* → conversions d'unités, parsing d'un format figé ;
- *faible + volatile* → messages de log, mise en forme d'un affichage ;
- *faible + stable* → accesseurs, constantes, code de confort.

---

# Ce qui mérite un test en priorité

| Cible | Pourquoi |
|---|---|
| **Fonctions critiques métier** | Ce sont elles qui produisent les chiffres publiés |
| **Calculs sensibles** | Une erreur y est silencieuse par nature |
| **Transformations de données** | Un décalage de colonne ne lève aucune exception |
| **Formats d'entrée / sortie** | C'est le contrat avec les autres projets |
| **Règles de validation** | Elles décident ce qui entre dans le système |
| **Bugs déjà rencontrés** | Ils sont déjà revenus une fois ; ils reviendront |
| **Code utilisé par plusieurs packages** | Une régression y coûte N fois |

> **🎯 En pratique** : commencez par la dernière ligne du tableau. Le code
> partagé par plusieurs projets est celui dont la régression est la plus chère,
> et c'est souvent celui que personne n'ose modifier.

---

# Le bug déjà rencontré : le test le plus rentable

Un bug qui a été corrigé une fois a déjà prouvé trois choses :

1. le cas se produit **réellement** en production ;
2. le code ne le gérait pas — donc rien ne l'y empêche de revenir ;
3. quelqu'un a déjà passé du temps à le diagnostiquer.

Le test correspondant coûte cinq minutes, puisque le cas reproductible est déjà
identifié. C'est le meilleur rapport effort / valeur de toute la suite.

> Une politique d'équipe simple, applicable dès demain :
> **aucune correction de bug n'est fusionnée sans le test qui échouait avant.**

Nous verrons comment le formuler au chapitre 6 de cette journée.

---

# Ce qu'il est peu rentable de tester

| À éviter | Pourquoi |
|---|---|
| **Accesseurs simples** | `return self._x` — tester le langage, pas votre code |
| **Détails internes instables** | Le test cassera au premier refactoring légitime |
| **Duplication de tests** | Trois tests pour la même règle : trois à maintenir, un seul signal |
| **Tests couplés à l'implémentation** | Ils bloquent le refactoring (chapitre 1) |
| **Le code des bibliothèques tierces** | `pandas` et `numpy` ont leurs propres suites |
| **Le rendu exact d'un log** | Change souvent, ne casse jamais rien de fonctionnel |

> **⚠️ Piège** : un test inutile n'est pas neutre. Il coûte du temps
> d'exécution, du temps de maintenance, et il **dilue le signal** — dans une
> suite de 800 tests dont 300 sont sans valeur, plus personne ne lit les échecs.

---

# La couverture est un indicateur, pas un objectif

La couverture mesure **quelles lignes ont été exécutées**. Elle ne mesure ni la
pertinence des assertions, ni les cas absents.

```python
def diviser(a, b):
    return a / b

def test_diviser():
    diviser(10, 2)          # 100 % de couverture… et aucune assertion
```

Ce test couvre la fonction intégralement et ne vérifie rien — ni le résultat,
ni le comportement pour `b = 0`.

Ce que la couverture sait faire, en revanche, et qui est très utile :

> **Repérer le code que vous n'avez jamais exécuté.** Une fonction métier à
> 0 % est une information exploitable. La différence entre 82 % et 85 %, non.

Nous la brancherons dans la pipeline au Jour 5, avec un seuil — mais un seuil
choisi comme garde-fou, pas comme trophée.

---

# À retenir

> **1.** Priorisez sur deux axes : la **conséquence** d'une erreur et la
> **fréquence** de modification. Le croisement des deux donne l'ordre de travail.

> **2.** Le test le plus rentable de tous est celui qui reproduit un bug déjà
> rencontré : le cas est connu, l'écriture prend cinq minutes.

> **3.** Un test sans valeur n'est pas gratuit : il dilue le signal. Mieux vaut
> 60 tests qu'on lit que 600 qu'on ignore.
