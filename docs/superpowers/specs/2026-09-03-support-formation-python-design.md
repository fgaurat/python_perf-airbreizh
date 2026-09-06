# Support de formation — Python avancé : qualité logicielle, TDD, design patterns et CI/CD

Document de conception — 2026-09-03

## 1. Périmètre

Produire le support complet d'une formation de 5 jours (35 h) destinée à des
ingénieurs et profils scientifiques qui développent ou maintiennent des
librairies Python internes.

Deux livrables :

- **Slides** — Marp, dans `slides/`, assemblées et exportées en PDF par `build.py`.
- **TPs** — 19 travaux pratiques **indépendants** dans `TPs/`, chacun avec
  énoncé, code de départ et corrigé exécutable.

Décisions structurantes actées avec le formateur :

| Décision | Choix |
|---|---|
| Fil rouge | **Aucun.** Chaque TP est autonome, avec son propre contexte métier. |
| Outillage | Python 3.12, `uv`, `pytest` + `pytest-cov`, `ruff` (lint + format), `mypy` |
| Densité | ~60-70 slides par jour, une idée par slide (~340 slides au total) |
| Découpage | Un fichier de slides par section du programme |
| Ordre de production | Jour par jour, validation après le Jour 1 |

## 2. Architecture du support

### 2.1 Nommage des fichiers de slides

`build.py` assemble les fichiers `slides/[0-9][0-9]-*.md` par ordre
alphabétique. On exploite ce tri : **premier chiffre = jour, second chiffre =
section**.

```
slides/
  00-intro.md
  11-qualite-librairies.md            21-role-des-tests.md
  12-demarche-guidee-par-les-tests.md 22-prioriser-les-tests.md
  13-poo-testabilite.md               23-organisation-projet-tests.md
  14-patterns-introduction.md         24-pytest-en-pratique.md
  15-code-difficile-a-tester.md       25-premiers-cycles-tdd.md
  16-solid-pragmatique.md             26-tests-non-regression.md
  19-tp-jour1.md                      29-tp-jour2.md

  31-doubles-de-test.md               41-tdd-sur-code-existant.md
  32-mocking-python.md                42-ecrire-le-test-avant.md
  33-monkeypatch.md                   43-refactoring-securise.md
  34-tester-les-acces-externes.md     44-methodes-longues.md
  35-patterns-testabilite.md          45-dependances-circulaires.md
  36-patterns-solid-mocking.md        46-strategie-reprise-legacy.md
  39-tp-jour3.md                      49-tp-jour4.md

  51-cicd-et-qualite.md               55-workflow-equipe.md
  52-gitlab-ci-python.md              59-tp-jour5.md
  53-rapports-de-tests.md             99-conclusion.md
  54-controles-complementaires.md
```

Un fichier = 8 à 20 slides. Objectif : pouvoir corriger, réordonner ou
remplacer une section sans toucher au reste.

Chaque fichier porte le frontmatter complet — `build.py` n'en retient que
`header:`, mais `theme` et `paginate` permettent de **prévisualiser un chapitre
seul** dans VS Code sans passer par la concaténation :

```markdown
---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — Pytest en pratique"
---
```

### 2.2 Conventions rédactionnelles

- **Une idée par slide.** Titre formulé comme une affirmation
  (« Un mock vérifie une interaction, pas un résultat ») plutôt qu'un
  substantif (« Les mocks »).
- **Code avant / code après** en deux colonnes pour tout ce qui touche au
  refactoring et aux patterns. Nécessite une classe CSS `.cols` (§2.4).
- **Slides récurrentes** :
  - `⚠️ Piège` — l'erreur classique sur le sujet qui vient d'être vu.
  - `🎯 En pratique` — la règle de décision applicable en sortie de formation.
  - `À retenir` — clôture chaque section, 3 puces maximum.
- Exemples de code : **15 lignes maximum**, autonomes, exécutables mentalement.
  Chaque exemple de mauvais code est suivi de sa version corrigée.
- Le ton est **pragmatique et non dogmatique**, conformément au positionnement
  du programme : chaque principe (SOLID, TDD, patterns, couverture) est
  accompagné explicitement de ses limites et des cas où il ne s'applique pas.
- `<!-- _class: dense -->` réservé aux slides de code longues. Le contrôle
  `python3 build.py --check` doit passer sans débordement avant chaque export PDF.

### 2.3 Structure des TPs

```
TPs/
  pyproject.toml          # environnement uv unique : pytest, pytest-cov, ruff, mypy
  README.md               # comment lancer les TPs
  j2-01-suite-pytest-de-zero/
    README.md             # contexte, objectif, étapes, critères de réussite, durée
    depart/               # code de départ (à trous, tests rouges ou absents)
    corrige/              # solution complète, `pytest` vert
```

- **Structure plate par défaut** (modules et `test_*.py` côte à côte) — pas de
  packaging là où ce n'est pas le sujet.
- **Layout `src/` + `pyproject.toml` par TP** uniquement quand le packaging
  fait partie de l'exercice : `j4-04` (dépendances circulaires) et les TPs du
  Jour 5 (CI/CD).
- Chaque `README.md` de TP indique une **durée cible** et des **critères de
  réussite vérifiables** (« `pytest` passe au vert », « `ruff check` ne remonte
  rien », « la fonction `calculer_indice` n'ouvre plus aucun fichier »).
- **Tout corrigé est exécuté et vérifié vert** avant livraison.

### 2.4 Modifications de l'outillage existant

Deux retouches à `build.py` :

1. `GLOBAL_FRONTMATTER` : titre et en-tête « Formation Python Perfectionnement »
   → « Python avancé — Qualité, TDD, Design patterns, CI/CD ».
2. `OUTPUT_MD` : `python-perfectionnement-complet.md` → `python-avance-complet.md`.

Un ajout à `your-theme.css` :

```css
section .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2em; }
section .cols pre { font-size: 0.38em; }
```

(`build.py` passe déjà `--html` à Marp, les `<div>` sont donc autorisés.)

## 3. Contenu détaillé

### Jour 1 — Qualité, architecture testable, POO et SOLID (75 slides — produit)

| Fichier | Contenu | ~Slides |
|---|---|---|
| `00-intro.md` | Objectifs, positionnement (ce n'est pas du « Python perfectionnement »), déroulé, prérequis, outillage, conventions du support | 6 |
| `11-qualite-librairies.md` | Script / notebook / module / librairie ; coût du changement ; les 7 problèmes classiques des librairies internes ; ce qu'on cherche à sécuriser ; notion de contrat | 10 |
| `12-demarche-guidee-par-les-tests.md` | Tester après vs concevoir testable ; le TDD comme outil d'analyse ; cycle Red/Green/Refactor ; où le TDD est pertinent dans une lib métier, où il ne l'est pas (exploration, calcul numérique) | 10 |
| `13-poo-testabilite.md` | Responsabilités ; agrégation vs composition ; couplage et loi de Déméter ; encapsulation pragmatique (`_`, `@property`, pas de getters/setters) ; duck typing ; `ABC` vs `typing.Protocol` ; `dataclass(frozen=True)` ; exceptions métier, hiérarchie, `raise … from` | 12 |
| `14-patterns-introduction.md` | Les patterns ne sont pas des recettes ; reconnaître le problème avant de nommer le pattern ; tableau problème → pattern ; en Python, la fonction et le `dict` remplacent souvent le pattern ; catalogue de la formation | 9 |
| `15-code-difficile-a-tester.md` | Les 7 symptômes, chacun illustré par un extrait réel ; heuristique « si je dois lancer une base pour tester une formule, le problème est dans le code » | 10 |
| `16-solid-pragmatique.md` | SRP (axe de changement) ; OCP (registry/injection plutôt que hiérarchies) ; DIP (« l'abstraction, c'est souvent juste un paramètre ») ; ISP (`Protocol` étroits) ; LSP en survol ; limites d'une application rigide en Python | 11 |
| `19-tp-jour1.md` | Annonce et cadrage des 3 TPs | 3 |

**TPs du Jour 1**

1. `j1-01-audit-code-difficile-a-tester` — analyser un module de ~180 lignes
   mêlant lecture de fichier, calcul et écriture. Livrable : carte des
   responsabilités + plan de découpage. (45 min)
2. `j1-02-decoupage-responsabilites` — extraire une fonction de calcul pure,
   séparer les I/O, rendre la fonction testable sans fichier. (45 min)
3. `j1-03-exceptions-explicites` — remplacer les `return None`, les codes
   d'erreur et les `except: pass` par des exceptions métier ; premiers tests
   d'erreurs attendues. (30 min)

### Jour 2 — Pytest, stratégie de test et premiers cycles TDD (~70 slides)

| Fichier | Contenu | ~Slides |
|---|---|---|
| `21-role-des-tests.md` | Bug visible / bug silencieux / régression ; unitaire, intégration, fonctionnel ; tester le comportement et non l'implémentation ; contrat logiciel | 11 |
| `22-prioriser-les-tests.md` | Ce qui mérite un test (calculs sensibles, transformations, validations, bugs passés, code partagé) ; ce qui n'en mérite pas (getters, détails instables, duplication) | 8 |
| `23-organisation-projet-tests.md` | Layout `src/` ; dossier `tests/` ; `conftest.py` ; nommage ; séparation unitaires/intégration ; données de test ; Arrange / Act / Assert | 10 |
| `24-pytest-en-pratique.md` | Assertions et introspection ; `pytest.raises` (+ `match`) ; fixtures et scopes ; fixtures partagées ; `parametrize` et `ids` ; `tmp_path` ; `pytest.approx` ; marqueurs ; `-k` / `-m` / `--lf` ; options utiles ; bonnes pratiques | 18 |
| `25-premiers-cycles-tdd.md` | Écrire le test d'abord ; voir le rouge ; implémentation minimale ; refactor ; ajout progressif des cas limites ; le test fait émerger l'interface ; TDD strict vs pragmatique | 11 |
| `26-tests-non-regression.md` | Transformer un bug en test ; tests de caractérisation ; filet de sécurité avant refactoring ; golden/approval tests et leurs limites | 9 |
| `29-tp-jour2.md` | Annonce des 5 TPs | 3 |

**TPs du Jour 2**

4. `j2-01-suite-pytest-de-zero` — mettre en place `tests/`, `conftest.py`,
   premiers tests d'une fonction métier. (45 min)
5. `j2-02-parametrize-et-cas-limites` — paramétrer des cas de calcul, tester
   les erreurs attendues, comparer des flottants. (45 min)
6. `j2-03-fixtures-et-fichiers-temporaires` — fixtures partagées, `tmp_path`,
   jeu de données de test. (45 min)
7. `j2-04-premier-cycle-tdd` — Red/Green/Refactor complet sur une fonction
   métier simple, cas limites ajoutés un par un. (60 min)
8. `j2-05-test-de-non-regression` — un bug est fourni : le reproduire par un
   test, corriger, vérifier. (30 min)

### Jour 3 — Mocking, dépendances externes et patterns (~70 slides)

| Fichier | Contenu | ~Slides |
|---|---|---|
| `31-doubles-de-test.md` | Dummy, stub, fake, mock, spy (tableau comparatif) ; vérifier un résultat vs vérifier une interaction ; quand mocker, quand s'abstenir ; risques des tests sur-mockés ; tester les frontières | 11 |
| `32-mocking-python.md` | `unittest.mock` ; `Mock` vs `MagicMock` ; `return_value`, `side_effect`, exceptions ; `assert_called_with` et consorts ; `patch` (décorateur / contexte) et la règle **« patcher là où c'est utilisé »** ; `patch.object`, `autospec`, `PropertyMock` | 16 |
| `33-monkeypatch.md` | `setattr`, `setenv`/`delenv`, `chdir`, `syspath_prepend` ; remplacer un module ; tableau comparatif `patch` vs `monkeypatch` | 8 |
| `34-tester-les-acces-externes.md` | Bases de données, fichiers, APIs HTTP, flux ; stratégies : adapter, repository, service, fake en mémoire, fichier de test, injection de dépendance, séparation logique/IO | 11 |
| `35-patterns-testabilite.md` | Adapter, Strategy, Factory, Repository, Facade, Dependency Injection, Template Method — pour chacun : le problème, avant/après, le test que cela rend possible, et quand ne **pas** l'utiliser | 15 |
| `36-patterns-solid-mocking.md` | Une meilleure conception réduit le besoin de mocks ; reconnaître le sur-design ; relier patterns, SOLID et doubles de test | 6 |
| `39-tp-jour3.md` | Annonce des 4 TPs | 3 |

**TPs du Jour 3**

9. `j3-01-mock-et-monkeypatch` — tester une fonction lisant une variable
   d'environnement et appelant un service ; comparer les deux approches. (45 min)
10. `j3-02-extraire-un-adapter` — isoler un client HTTP derrière un `Protocol`,
    écrire un fake en mémoire, simuler une erreur réseau. (60 min)
11. `j3-03-repository-et-fake` — isoler l'accès à une base SQLite derrière un
    Repository, tester la logique métier sans base. (60 min)
12. `j3-04-strategy` — rendre un algorithme de calcul interchangeable et
    testable, remplacer une cascade de `if` par une stratégie injectée. (45 min)

### Jour 4 — TDD avancé, refactoring sécurisé et code legacy (~66 slides)

| Fichier | Contenu | ~Slides |
|---|---|---|
| `41-tdd-sur-code-existant.md` | Ajouter une fonctionnalité en TDD sur une base existante ; caractérisation avant modification ; bug → test de non-régression ; zones où le TDD s'applique mal (calcul scientifique, traitements de masse) et comment adapter | 11 |
| `42-ecrire-le-test-avant.md` | Définir le comportement attendu ; commencer simple ; faire émerger l'interface ; garder les tests lisibles ; ne pas tester l'implémentation | 7 |
| `43-refactoring-securise.md` | Refactoring vs réécriture ; petits pas ; catalogue : extraire fonction, extraire classe, objet paramètre, remplacer conditionnelle par dispatch, supprimer la duplication, réduire les effets de bord ; introduire un pattern **pendant** un refactoring | 13 |
| `44-methodes-longues.md` | Pourquoi une méthode de 300 lignes coûte cher ; identifier les blocs cohérents ; séparer calcul / validation / accès données / écriture ; extraire des fonctions pures ; objet de configuration ; démonstration pas à pas sous caractérisation | 12 |
| `45-dependances-circulaires.md` | Causes fréquentes ; détection (`ruff`, `import-linter`, `pydeps`) ; résolution : extraction d'interface, inversion de dépendance, module commun, événements, services applicatifs, passage explicite | 11 |
| `46-strategie-reprise-legacy.md` | Cartographier les zones critiques ; prioriser par le risque ; construire une couverture utile ; pourquoi viser 100 % est contre-productif ; politique d'amélioration continue | 9 |
| `49-tp-jour4.md` | Annonce des 4 TPs | 3 |

**TPs du Jour 4**

13. `j4-01-tdd-nouvelle-fonctionnalite` — ajouter une fonctionnalité à une base
    existante en écrivant le test d'abord. (60 min)
14. `j4-02-mise-sous-test-methode-longue` — tests de caractérisation sur une
    méthode de ~200 lignes, puis extraction progressive. (75 min)
15. `j4-03-introduire-un-pattern-en-refactoring` — réduire le couplage d'un
    composant en introduisant un pattern, sous couverture de tests. (60 min)
16. `j4-04-resoudre-une-dependance-circulaire` — mini-package avec imports
    croisés : diagnostic puis résolution par inversion de dépendance. (45 min)

### Jour 5 — GitLab CI/CD, qualité automatisée et synthèse (~63 slides)

| Fichier | Contenu | ~Slides |
|---|---|---|
| `51-cicd-et-qualite.md` | Pourquoi automatiser ; détection précoce des régressions ; test local vs test en pipeline ; quand la pipeline doit bloquer ; tests rapides vs tests lents | 9 |
| `52-gitlab-ci-python.md` | Anatomie d'un `.gitlab-ci.yml` ; image Docker Python ; installation avec `uv` ; stages installation / qualité / tests / rapport / packaging ; cache ; artifacts ; variables ; `rules` ; matrice de versions Python | 17 |
| `53-rapports-de-tests.md` | JUnit XML et son affichage dans la merge request ; couverture au format Cobertura et annotations dans le diff ; conservation des artifacts ; logs bruts vs rapport structuré | 9 |
| `54-controles-complementaires.md` | `ruff format` et `ruff check` ; `mypy` (adoption progressive, `strict` par module) ; `pytest-cov` et seuils ; `pre-commit` ; choisir des indicateurs utiles plutôt que des métriques cosmétiques | 11 |
| `55-workflow-equipe.md` | Quand écrire un test ; ajouter un test lors d'une correction de bug ; relire une merge request sous l'angle qualité ; ne pas casser une librairie consommée par d'autres packages ; versionnement et dépréciation ; standards d'équipe | 9 |
| `59-tp-jour5.md` | Annonce des 3 TPs | 3 |
| `99-conclusion.md` | Synthèse des 5 jours ; plan d'action à 30 jours pour l'équipe ; ressources | 5 |

**TPs du Jour 5**

17. `j5-01-premier-pipeline` — écrire un `.gitlab-ci.yml` exécutant `pytest` sur
    un petit package, avec cache des dépendances. (60 min)
18. `j5-02-rapports-junit-et-couverture` — produire un rapport JUnit et un
    rapport de couverture exploités dans la merge request. (45 min)
19. `j5-03-merge-request-cassee` — simuler une MR dont un test échoue, lire le
    rapport, corriger, valider. (45 min)

## 4. Ordre de production et vérification

1. Retouches `build.py` + `your-theme.css` (§2.4).
2. `00-intro.md` et les slides du Jour 1, puis ses 3 TPs.
3. **Point de validation avec le formateur** : ton, niveau, densité, format des TPs.
4. Jours 2 à 5, un jour à la fois, dans l'ordre.
5. `99-conclusion.md`.

Contrôles avant chaque livraison de jour :

- `python3 build.py --check` — aucune slide en débordement.
- `uv run pytest` — tous les corrigés au vert.
- `uv run ruff check` — les corrigés respectent ce qu'ils enseignent.
- Relecture orthographique française (accents inclus).

## 5. Points hors périmètre

- Rappels sur les bases de Python, de Git ou de GitLab (prérequis annoncés).
- Django, Flask, FastAPI, asyncio, performance et optimisation.
- Installation d'un runner GitLab : les TPs du Jour 5 fournissent le
  `.gitlab-ci.yml` et sa validation locale, l'exécution sur une instance
  GitLab réelle dépend de l'environnement du client.

## 6. Révision du 6 septembre 2026 — thèmes génériques

Les 19 TPs de la première version s'appuyaient sur des contextes proches du
métier des participants (qualité de l'air, stations de mesure, référentiels
géographiques). Décision : **tout refaire avec des exemples génériques**
(hello world, calculatrice, todo-list, katas classiques), sans rien changer aux
objectifs pédagogiques, aux durées, ni au squelette (`README / depart /
corrige`, outillage uv + pytest + ruff + mypy).

La première version est conservée hors dépôt dans `AirBreizhTPs/` (archive).
Les slides « Travaux pratiques » (`19`, `29`, `39`, `49`, `59`) et
`TPs/README.md` sont réécrites en conséquence ; les quelques mentions du
domaine dans les slides de cours (chapitres 13, 14, 34, 42) sont neutralisées.

| TP | Thème générique |
|---|---|
| j1-01 audit | `todo.py`, script todo-list monolithique de ~160 lignes à diagnostiquer |
| j1-02 découpage | hello world : `saluer()` mêle heure, langue, config et `print` |
| j1-03 exceptions | calculatrice : `calculer("10 / 0")` renvoie `None` |
| j2-01 suite de zéro | todo-list : `ajouter / terminer / lister / filtrer` |
| j2-02 parametrize | calculatrice : opérations, priorités, `approx`, cas limites |
| j2-03 fixtures + `tmp_path` | carnet d'adresses JSON avec sauvegarde tournante |
| j2-04 TDD de zéro | kata nombres romains |
| j2-05 non-régression | `formater_duree(3600)` affiche `0 h` |
| j3-01 mock / monkeypatch | todo-list : tâches en retard, `date.today()` et variable d'environnement |
| j3-02 Adapter | convertisseur de devises derrière une API de taux |
| j3-03 Repository + fake | todo-list : SQLite vs mémoire, test de contrat |
| j3-04 Strategy | export de la todo-list texte / CSV / JSON / Markdown |
| j4-01 bourgeon | calculatrice : historique et `annuler()` |
| j4-02 méthode longue | bulletin scolaire : `generer_bulletin()` 175 lignes |
| j4-03 pattern émergent | rappels de la todo-list console / mail / fichier |
| j4-04 cycle d'imports | todo-list : `taches ↔ projets ↔ affichage` |
| j5-01 pipeline | paquet `calculatrice` |
| j5-02 JUnit + couverture | paquet `todolist` |
| j5-03 MR cassée | paquet `convertisseur` d'unités |
