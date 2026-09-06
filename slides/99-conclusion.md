---
marp: true
theme: your-theme
paginate: true
header: "Conclusion"
---

<!-- _class: lead -->

# Conclusion

*Ce qu'on emporte, et par quoi commencer*

---

# Le fil des cinq jours

| Jour | La question | La réponse retenue |
|---|---|---|
| **1** | Pourquoi ce code est-il dur à tester ? | il construit ses dépendances et mélange calcul et I/O |
| **2** | Que tester, et comment ? | le comportement, en priorité là où l'erreur est silencieuse |
| **3** | Comment tester ce qui dépend de l'extérieur ? | déplacer la frontière avant de sortir un mock |
| **4** | Comment améliorer sans casser ? | petits pas, sous filet, sans corriger de bug en même temps |
| **5** | Comment rendre tout cela systématique ? | une pipeline qui rend l'exécution non négociable |

Une seule idée les traverse :

> **Un code difficile à tester n'a pas un problème de tests.
> Il a un problème de conception — et le test est ce qui le révèle.**

---

# Les cinq gestes les plus rentables

Par ordre de rapport bénéfice / effort, tels qu'observés sur les TPs :

> **1.** Remplacer une dépendance construite par une dépendance **reçue**.
> Une ligne. Transforme un module intestable en module testable.

> **2.** Extraire la **fonction pure** au cœur d'un traitement.
> Elle porte le risque métier et se teste sans rien monter.

> **3.** Transformer chaque bug corrigé en **test de non-régression**.
> Cinq minutes, et le cas est déjà connu.

> **4.** Remplacer un `return None` silencieux par une **exception métier**.
> Fait échouer bruyamment ce qui produisait des résultats faux.

> **5.** Mettre en place une **pipeline de six lignes**.
> Rend visible ce que l'équipe fait déjà.

---

# Un plan à trente jours pour l'équipe

| Semaine | Action | Effort |
|---|---|---|
| **1** | Pipeline minimale : `pytest` à chaque poussée, même sur trois tests | ½ j |
| **1** | `ruff format` + `ruff check` en CI, non bloquants d'abord | ½ j |
| **2** | Cartographier les zones critiques (`git log` + incidents + consommateurs) | ½ j |
| **2** | Règle d'équipe : aucune correction de bug sans son test | 0 j |
| **3** | Test de bout en bout sur les deux traitements les plus critiques | 2 j |
| **4** | Extraire et tester les règles métier de la zone la plus risquée | 2 j |
| **4** | Rapport JUnit et couverture du diff dans les merge requests | ½ j |

Ce plan ne demande **jamais** d'arrêter les évolutions fonctionnelles, et ne
fixe **aucun objectif de couverture globale**.

---

# Trois pièges à éviter en rentrant

> **⚠️ Appliquer les patterns partout.** Un pattern qui ne rend aucun test
> possible n'apporte rien. Le critère est là, et nulle part ailleurs.

> **⚠️ Viser un pourcentage de couverture.** Vous l'atteindrez, et vous n'aurez
> rien gagné. Visez la couverture du **code neuf**.

> **⚠️ Vouloir tout reprendre d'un coup.** Testez ce que vous vous apprêtez à
> modifier. Le reste attendra son tour, légitimement.

Et une chose à faire dès lundi : reprenez **le code de votre équipe** auquel
vous pensiez au premier jour. Posez-lui la question du chapitre 5 du Jour 1 —
*de quoi ai-je besoin pour tester ceci ?* — et écrivez le premier test.

---

# Pour aller plus loin

| Sujet | Référence |
|---|---|
| Refactoring et catalogue de transformations | *Refactoring*, Martin Fowler |
| Code legacy, coutures, caractérisation | *Working Effectively with Legacy Code*, Michael Feathers |
| Doubles de test, état vs interaction | *Growing Object-Oriented Software, Guided by Tests*, Freeman & Pryce |
| Frontières et architecture testable | *Clean Architecture*, Robert C. Martin |
| Outillage Python | documentation de `pytest`, `ruff`, `uv`, `import-linter` |

Le support complet, les 19 TPs et leurs corrigés restent à votre disposition.

---

<!-- _class: lead -->

# Merci

*Questions, retours, et bon courage pour lundi*
