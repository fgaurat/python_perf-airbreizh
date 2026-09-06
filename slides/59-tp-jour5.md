---
marp: true
theme: your-theme
paginate: true
header: "Jour 5 — Travaux pratiques"
---

<!-- _class: lead -->

# Travaux pratiques du Jour 5

*Trois exercices et un bilan — 3 h*

---

# Le programme

| TP | Ce que vous allez faire | Durée |
|---|---|---|
| **j5-01** | Écrire un `.gitlab-ci.yml` complet pour un vrai package, `calculatrice` : stages, cache `uv`, matrice de versions. Validé par un simulateur local qui exécute réellement les jobs. | 60 min |
| **j5-02** | Sur le package `todolist`, produire un rapport JUnit et un rapport de couverture, trouver le bug que cachent les 28 % non couverts, et régler le seuil en cliquet plutôt qu'en objectif. | 45 min |
| **j5-03** | Recevoir une merge request rouge sur le package `convertisseur` : lire le rapport, diagnostiquer, corriger, valider. | 45 min |
| **Bilan** | En groupe : chacun repart avec **trois règles** applicables à sa librairie dès lundi, et une zone de code par laquelle commencer. | 30 min |

---

# Une pipeline s'exécute sans GitLab

Vous n'avez pas de runner sous la main. Ce n'est pas un obstacle :

```bash
uv run python outils/simuler_pipeline.py
```

Ce simulateur lit votre `.gitlab-ci.yml`, en extrait les stages et les jobs,
et **exécute réellement leurs commandes** dans l'ordre, en respectant les
codes de retour.

> **🎯 Le principe qui compte** : toute commande de votre pipeline doit être
> exécutable sur votre poste. Si le simulateur ne peut pas la lancer, votre
> collègue ne pourra pas la déboguer non plus.

Sur `j5-03`, résistez à l'envie d'ouvrir le code source en premier. Commencez
par le rapport de tests — c'est la compétence que le TP fait travailler.
