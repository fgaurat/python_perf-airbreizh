---
marp: true
theme: your-theme
paginate: true
header: "Jour 3 — Travaux pratiques"
---

<!-- _class: lead -->

# Travaux pratiques du Jour 3

*Quatre exercices indépendants — 3 h 30*

---

# Le programme

| TP | Ce que vous allez faire | Durée |
|---|---|---|
| **j3-01** | Tester « les tâches en retard d'un projet » : la fonction lit l'environnement, appelle un service et consulte l'horloge. Trois versions du même test : `monkeypatch`, `patch` + autospec, puis injection — et comparaison. | 45 min |
| **j3-02** | Extraire un **Adapter** autour d'une API de taux de change, écrire un fake, et faire remonter la panne qu'un `except: return 0.0` masquait. | 60 min |
| **j3-03** | Introduire un **Repository** pour remonter les règles du rapport de la todo-list hors du SQL, puis écrire le **test de contrat** qui garde le fake aligné sur SQLite. | 60 min |
| **j3-04** | Remplacer la cascade de `if` d'un export texte / CSV / JSON / Markdown par une **Strategy**, et rendre chaque format testable seul. | 45 min |

---

# La question à garder en tête

Pour chaque TP, avant d'écrire le test, demandez-vous :

> **Est-ce que je vérifie un résultat, ou une interaction ?**

Et à la fin de chaque TP :

> **Combien de tests étaient impossibles avant ce refactoring ?**

C'est le seul critère qui justifie d'avoir introduit un pattern. Si la réponse
est « zéro », le pattern était de trop — et c'est une réponse acceptable, que
nous discuterons.

La *suppression d'une dépendance circulaire*, listée au programme de ce jour,
est traitée demain en **j4-04** — une fois vus les outils de résolution.

Le TP **j3-01** est le plus court à comprendre mais le plus riche en discussion :
gardez vos trois versions du test côte à côte pour la mise en commun.
