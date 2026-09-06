---
marp: true
theme: your-theme
paginate: true
header: "Jour 4 — Stratégie de reprise d'une base existante"
---

<!-- _class: lead -->

# 6. Stratégie de reprise d'une base existante

*Par où commencer quand tout est à faire*

---

# La question de lundi matin

Vous héritez d'une librairie de 12 000 lignes, sans tests, utilisée par quatre
projets. Vous avez, disons, deux jours par mois à y consacrer.

Les deux réponses qui échouent :

| Réponse | Pourquoi elle échoue |
|---|---|
| « On réécrit tout proprement » | 18 mois, aucun livrable, et les projets consommateurs continuent d'évoluer pendant ce temps |
| « On vise 80 % de couverture » | 6 semaines de tests sur le code facile — c'est-à-dire celui qui ne cassait jamais |

La réponse qui fonctionne tient en une phrase :

> **Testez ce que vous vous apprêtez à modifier, et rien d'autre.**

Le reste viendra quand il faudra y toucher — et pas avant.

---

# Cartographier les zones critiques

Une demi-journée, en équipe, sur trois sources d'information :

| Source | Question | Où la trouver |
|---|---|---|
| **L'historique Git** | quels fichiers changent le plus ? | `git log` |
| **Les incidents** | où sont apparus les bugs ? | tickets, mails, mémoire de l'équipe |
| **Les consommateurs** | quelles fonctions sont appelées par d'autres projets ? | `grep` dans les projets clients |

```bash
# Les 15 fichiers les plus modifiés sur deux ans
git log --since="2 years ago" --name-only --pretty=format: \
  | grep '\.py$' | sort | uniq -c | sort -rn | head -15
```

> Un fichier souvent modifié **et** cité dans les incidents **et** appelé par
> trois projets : c'est là que vous commencez. Pas ailleurs.

---

# La matrice de priorité

|  | **Rarement modifié** | **Souvent modifié** |
|---|---|---|
| **Conséquence forte** | ② tests de caractérisation, sans refactoring | ① **commencer ici** |
| **Conséquence faible** | ④ ne rien faire | ③ tester au fil de l'eau |

Ce que chaque case veut dire concrètement :

- **①** filet complet, puis refactoring, puis tests unitaires sur les règles ;
- **②** quelques tests de caractérisation, pour la seule non-régression ;
- **③** règle d'équipe : on ajoute les tests quand on touche au fichier ;
- **④** rien. Ce code coûte moins cher à ignorer qu'à tester.

> **⚠️ Piège** : la case ④ met mal à l'aise. Elle est pourtant ce qui rend le
> plan réaliste — et donc ce qui permet aux cases ① et ② d'aboutir.

---

# La règle du boy-scout, en version testable

> **Vous laissez le code un peu plus propre que vous ne l'avez trouvé.**

Traduite en règle d'équipe applicable :

| Quand vous… | Vous ajoutez… |
|---|---|
| corrigez un bug | le test qui échouait avant la correction |
| ajoutez une fonctionnalité | ses tests, écrits avant (bourgeon) |
| lisez du code pour le comprendre | le test qui documente ce que vous venez de comprendre |
| touchez une fonction non testée | un test de caractérisation, même minimal |

L'effet est cumulatif et se concentre **naturellement** sur le code qui bouge —
c'est-à-dire exactement celui qui casse.

> Aucune de ces quatre lignes ne demande de budget dédié. Elles s'appliquent
> pendant le travail déjà planifié.

---

# La couverture : ce qu'elle sait et ne sait pas

| Elle sait | Elle ne sait pas |
|---|---|
| quelles lignes n'ont **jamais** été exécutées | si les assertions vérifient quoi que ce soit |
| si un module entier est à 0 % | si les cas limites sont couverts |
| si votre nouveau code est testé (couverture du **diff**) | si les tests sont justes |

```python
def diviser(a, b):
    return a / b

def test_diviser():
    diviser(10, 2)      # 100 % de couverture, zéro assertion
```

> **🎯 En pratique** : sur du legacy, l'indicateur utile n'est pas la couverture
> globale — elle démarrera à 4 % et humiliera tout le monde. C'est la
> **couverture des lignes modifiées** dans la merge request. Nous la mettrons en
> place demain.

---

# Un plan réaliste sur six mois

| Mois | Objectif | Effort |
|---|---|---|
| **1** | Cartographie, pipeline CI qui lance `pytest`, même sur 3 tests | 2 j |
| **1-2** | Test de bout en bout sur les 2 traitements les plus critiques | 3 j |
| **2-3** | Caractérisation + extraction des règles métier de la zone ① | 5 j |
| **3-4** | Règle d'équipe : aucun correctif sans test de non-régression | 0 j |
| **4-6** | Seuil de couverture **sur le diff** en merge request | 1 j |

Ce qui rend ce plan tenable :

- il produit un résultat visible dès le premier mois ;
- il ne demande jamais d'arrêter les évolutions fonctionnelles ;
- il ne fixe **aucun objectif de couverture globale**.

---

# Les indicateurs qui valent la peine d'être suivis

| Indicateur | Ce qu'il dit | Piège s'il devient un objectif |
|---|---|---|
| **Couverture du diff** | le code neuf est-il testé ? | peut se contourner par des tests vides |
| **Nombre de bugs revenus** | les non-régressions font-elles leur travail ? | — |
| **Durée de la suite** | reste-t-elle lançable en local ? | — |
| **Tests instables** (*flaky*) | y a-t-il de l'état partagé ? | — |
| Couverture globale | peu de choses sur du legacy | **beaucoup** de tests sans valeur |

> **La loi de Goodhart, version test** : dès qu'une métrique devient un
> objectif, elle cesse d'être une bonne métrique. Une équipe à qui l'on impose
> 80 % de couverture atteindra 80 % — et vous n'aurez rien gagné.

---

# À retenir

> **1.** Ne testez pas la base existante « en général ». Testez **ce que vous
> vous apprêtez à modifier** — le reste attendra son tour légitimement.

> **2.** La matrice conséquence × fréquence donne l'ordre de travail, et le
> quadrant « ne rien faire » est ce qui rend le plan réaliste.

> **3.** Sur du legacy, l'indicateur utile est la couverture du **diff**, pas la
> couverture globale.
