---
marp: true
theme: your-theme
paginate: true
header: "Jour 5 — Rôle de la CI/CD dans la qualité logicielle"
---

<!-- _class: lead -->

# 1. Rôle de la CI/CD dans la qualité logicielle

*Ce qui change quand la machine exécute les tests*

---

# Ce que la CI change vraiment

Vos tests existent déjà. Ce que la pipeline ajoute n'est pas technique :

| Sans CI | Avec CI |
|---|---|
| « J'ai lancé les tests » | **On voit** qu'ils ont été lancés |
| Sur le poste de celui qui a écrit le code | Sur un environnement neutre et reproductible |
| Avec les dépendances installées il y a six mois | Avec celles déclarées dans `pyproject.toml` |
| Quand on y pense | À **chaque** poussée, sans exception |
| Le relecteur croit sur parole | Le relecteur voit un état vert ou rouge |

> La CI ne rend pas les tests meilleurs. Elle rend leur exécution **non
> négociable** — et transforme une intention d'équipe en fait vérifiable.

---

# Test local et test en pipeline : les écarts

Un test qui passe chez vous et échoue en CI révèle presque toujours une
**dépendance implicite** de votre poste :

| Écart | Ce qu'il révèle |
|---|---|
| Un paquet installé chez vous, absent du `pyproject.toml` | dépendance non déclarée — vos utilisateurs auront le même problème |
| Un fichier présent chez vous, absent du dépôt | donnée de test non versionnée |
| Une variable d'environnement locale | configuration non documentée |
| Un ordre d'exécution différent | **état partagé entre tests** |
| Un chemin absolu, un séparateur `\` ou `/` | code non portable |
| Un fuseau horaire ou une locale | calcul dépendant de l'environnement |

> **🎯 En pratique** : ces échecs sont désagréables et **précieux**. Chacun est
> un bug que vos consommateurs auraient rencontré à l'installation.

---

# Le coût du délai de détection

Le même défaut, selon le moment où il est trouvé :

```
   à l'écriture      →  30 secondes    le contexte est en tête
   en CI, sur la MR  →  10 minutes     il faut relire son diff
   en revue          →  1 heure        deux personnes mobilisées
   après fusion      →  1 demi-journée  bisect, correctif, nouvelle MR
   chez un consommateur → 1 semaine    diagnostic à distance, version à publier
   en production     →  ?              + le coût des résultats faux diffusés
```

Chaque ligne coûte environ **dix fois** la précédente. C'est tout l'argument
économique de la CI, et il ne dépend pas de la taille de l'équipe.

---

# Quand la pipeline doit bloquer

Bloquer trop peu ne sert à rien ; bloquer trop pousse l'équipe à contourner.

| Contrôle | Bloque ? | Pourquoi |
|---|---|---|
| Tests unitaires en échec | **oui** | c'est la raison d'être de la pipeline |
| Erreur de lint (`ruff check`) | **oui** | déterministe, corrigeable en une commande |
| Formatage non conforme | **oui** | zéro discussion possible en revue |
| Typage `mypy` sur du code neuf | oui, progressivement | commencez par les modules récents |
| Couverture du **diff** sous le seuil | oui | garde-fou sur le code neuf |
| Couverture **globale** sous un seuil | **non** | pousse à écrire des tests sans valeur |
| Tests d'intégration lents | selon | dans un stage séparé, non bloquant au début |
| Avertissements de sécurité | selon la criticité | à trier, pas à ignorer en bloc |

---

# Une politique qui tient dans le temps

Trois principes, à décider **en équipe** et à écrire quelque part :

> **1. Ce qui bloque doit être réparable en moins de dix minutes.**
> Sinon, l'équipe apprend à contourner — et vous perdez tout le bénéfice.

> **2. Un contrôle nouveau n'est jamais bloquant le premier jour.**
> On l'ajoute en avertissement, on résorbe le passif, puis on bloque.

> **3. Une pipeline rouge est traitée avant tout autre travail.**
> Une pipeline rouge tolérée pendant trois jours cesse d'être un signal.

Le troisième point est le plus difficile — et celui qui détermine si la CI sert
à quelque chose au bout de six mois.

---

# Tests rapides et tests lents

Une suite qui dure vingt minutes n'est plus lancée en local. C'est un problème
d'équipe avant d'être un problème technique.

```
   ┌─────────────────────────────────────────────────────────┐
   │  À chaque poussée      lint + format + unitaires   < 2 min│
   ├─────────────────────────────────────────────────────────┤
   │  Sur la merge request  + intégration + couverture  < 10 min│
   ├─────────────────────────────────────────────────────────┤
   │  Chaque nuit           + tests lents, matrice de   illimité│
   │                          versions, service réel           │
   └─────────────────────────────────────────────────────────┘
```

C'est le découpage préparé au Jour 2 avec les marqueurs :

```bash
pytest -m "not integration and not lent"     # boucle rapide
pytest                                        # tout, sur la MR
```

---

# Les pièges classiques

| Piège | Conséquence | Correctif |
|---|---|---|
| Tests instables (*flaky*) | l'équipe relance jusqu'au vert, puis ignore les rouges | traquer l'état partagé, jamais « relancer » |
| Pipeline de 40 minutes | plus personne n'attend, on fusionne à l'aveugle | découper en stages, mettre en cache |
| Seuil de couverture trop haut d'un coup | tests vides écrits pour la métrique | seuil sur le **diff**, relevé progressivement |
| Secrets en clair dans le `.gitlab-ci.yml` | fuite dans l'historique Git | variables masquées et protégées |
| Un seul job qui fait tout | on ne sait pas ce qui a échoué | un job par nature de contrôle |
| Job vert alors que la commande a échoué | fausse confiance | vérifier les codes de retour, pas les logs |

> **⚠️ Piège** : le dernier est le plus dangereux, parce qu'il est invisible.
> Nous en avons rencontré un exemple réel en préparant ce support.

---

# À retenir

> **1.** La CI ne rend pas les tests meilleurs : elle rend leur exécution
> **non négociable** et visible par toute l'équipe.

> **2.** Un test qui passe en local et casse en CI a trouvé une dépendance
> implicite de votre poste — c'est un bug de votre package, pas de la pipeline.

> **3.** Ce qui bloque doit être réparable en dix minutes, et une pipeline rouge
> se traite avant tout autre travail. Sinon la CI devient du bruit.
