# TP j1-01 — Analyser un code difficile à tester

**Durée : 45 min — en binôme de préférence**

## Contexte

`depart/todo.py` est un script réel dans sa forme : 180 lignes, une liste de
tâches partagée par l'équipe. On ajoute des tâches avec une échéance et une
priorité, on les termine, et chaque matin on génère un rapport des retards qui
part par mail quand il y en a trop.

Le script fonctionne. Il est en production depuis 2021. Personne dans l'équipe
ne veut y toucher, et il n'a aucun test.

On vous demande une évolution simple : **ajouter une priorité `critique`, qui
déclenche l'alerte dès le premier jour de retard**, sans attendre le seuil.

## Objectif

Ne pas écrire une ligne de code. Produire un **diagnostic** : pourquoi ce
script est-il si difficile à faire évoluer, et par où commencer.

## Étapes

1. **Lisez le script en entier** (10 min), sans chercher à le corriger.

2. **La question du test** (10 min). Pour chacune de ces trois règles métier,
   écrivez ce dont vous auriez besoin pour vérifier qu'elle est correcte :

   - une tâche est en retard si son échéance est strictement antérieure au jour
     du rapport et qu'elle n'est pas terminée ;
   - le score d'une tâche en retard vaut `poids × (1 + jours de retard)` ;
   - une alerte est envoyée à partir de 3 tâches en retard.

3. **Repérez les symptômes** (15 min). Pour chacun des sept symptômes vus en
   cours, notez le ou les numéros de ligne où il apparaît :

   | Symptôme | Lignes |
   |---|---|
   | Méthode trop longue | |
   | Calcul et I/O mélangés | |
   | Accès direct à une ressource externe | |
   | Objet qui construit ses dépendances | |
   | État global mutable | |
   | Dépendance implicite (fichier, variable d'environnement, horloge) | |
   | Erreur silencieuse | |

4. **Proposez un découpage** (10 min). Listez les composants que vous
   extrairiez, avec pour chacun : son nom, sa responsabilité unique, et ce dont
   il aurait besoin pour être testé.

5. Écrivez le tout dans un fichier `depart/ANALYSE.md`.

## Critères de réussite

- Vous avez identifié **au moins un exemple de chacun des sept symptômes**.
- Votre découpage isole une fonction de calcul testable **sans base de données,
  sans serveur mail et sans fichier**.
- Vous savez dire quelle partie du script porte le **risque métier** le plus
  élevé, et donc laquelle mérite d'être testée en premier.

## Pour aller plus loin

Trouvez dans le script un bug qui produit un **résultat faux sans lever
d'exception**. Il y en a plusieurs. Le plus grave tient en une comparaison.

## Corrigé

`corrige/ANALYSE.md` — à lire après avoir fait le vôtre. Ce n'est pas la seule
analyse possible ; comparez-la à la vôtre plutôt que de la recopier.
