---
marp: true
theme: your-theme
paginate: true
header: "Jour 1 — Travaux pratiques"
---

<!-- _class: lead -->

# Travaux pratiques du Jour 1

*Trois exercices indépendants — 2 h*

---

# Mise en place

```bash
cd TPs
uv sync                                    # une seule fois
uv run pytest j1-02-decoupage-responsabilites/corrige
```

Chaque TP suit la même structure :

| | |
|---|---|
| `README.md` | contexte, objectif, étapes, critères de réussite |
| `depart/` | le code sur lequel vous travaillez |
| `corrige/` | une solution possible — **après** avoir cherché |

Les trois TPs sont **indépendants** : chacun a son propre petit programme.

---

# Le programme

| TP | Ce que vous allez faire | Durée |
|---|---|---|
| **j1-01** | Auditer un script todo-list de 180 lignes que personne n'ose modifier. Aucun code : un diagnostic, sept symptômes à localiser, un découpage à proposer. | 45 min |
| **j1-02** | Extraire des fonctions pures d'un *hello world* qui mêle heure, langue, configuration et `print`. Isoler les I/O, écrire les premiers tests — sans changer un seul message. | 45 min |
| **j1-03** | Remplacer neuf comportements silencieux d'une calculatrice (`10 / 0` → `0.0`) par des exceptions métier explicites, sans jamais perdre la cause d'origine. | 30 min |

> **🎯 Consigne commune** : à chaque étape, posez-vous la question du chapitre 5 —
> *de quoi aurais-je besoin pour tester ceci ?* C'est elle qui guide le découpage.

Le TP j1-01 se fait de préférence **en binôme** : le diagnostic gagne beaucoup
à être discuté à voix haute.
