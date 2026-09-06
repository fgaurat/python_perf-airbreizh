# Travaux pratiques

19 TPs **indépendants** : chacun a son propre petit programme — une todo-list,
une calculatrice, un *hello world*, un convertisseur — on peut les faire dans
n'importe quel ordre.

## Mise en place (une seule fois)

```bash
cd TPs
uv sync            # crée .venv (Python 3.12) et installe l'outillage
```

Sans `uv` :

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install "pytest>=8.2" pytest-cov ruff mypy
```

## Structure d'un TP

```
jN-XX-nom-du-tp/
  README.md     énoncé : contexte, objectif, étapes, critères de réussite
  depart/       le code sur lequel vous travaillez
  corrige/      une solution possible — à consulter après avoir cherché
```

## Lancer les tests

```bash
uv run pytest jN-XX-nom-du-tp/corrige       # les tests d'un corrigé
uv run pytest jN-XX-nom-du-tp/depart        # votre travail en cours
uv run pytest                               # tous les corrigés
```

Le dossier `depart/` est exclu de la collecte globale : `uv run pytest` sans
argument ne lance que les corrigés, et doit toujours être vert.

## Vérifier le style

```bash
uv run ruff check .
uv run ruff format .
uv run mypy jN-XX-nom-du-tp/corrige
```

## Table des TPs

| TP | Programme | Sujet | Durée |
|---|---|---|---|
| `j1-01-audit-code-difficile-a-tester` | todo-list | Analyser un script non testable | 45 min |
| `j1-02-decoupage-responsabilites` | hello world | Extraire une fonction pure, isoler les I/O | 45 min |
| `j1-03-exceptions-explicites` | calculatrice | Remplacer les erreurs silencieuses | 30 min |
| `j2-01-suite-pytest-de-zero` | todo-list | Construire une suite pytest de zéro | 45 min |
| `j2-02-parametrize-et-cas-limites` | calculatrice | Paramétrisation, cas limites, propriétés | 45 min |
| `j2-03-fixtures-et-fichiers-temporaires` | carnet d'adresses | Fixtures composées et `tmp_path` | 45 min |
| `j2-04-premier-cycle-tdd` | nombres romains | Un cycle TDD complet, de zéro | 60 min |
| `j2-05-test-de-non-regression` | durées | Transformer un bug en test | 30 min |
| `j3-01-mock-et-monkeypatch` | todo-list | `monkeypatch`, `patch`, injection : trois versions | 45 min |
| `j3-02-extraire-un-adapter` | devises | Isoler une API derrière un Adapter | 60 min |
| `j3-03-repository-et-fake` | todo-list | Repository, fake et test de contrat | 60 min |
| `j3-04-strategy` | todo-list | Cascade de `if` → Strategy | 45 min |
| `j4-01-tdd-nouvelle-fonctionnalite` | calculatrice | Ajouter une fonctionnalité par bourgeon | 60 min |
| `j4-02-mise-sous-test-methode-longue` | bulletin scolaire | Caractériser puis démonter 175 lignes | 90 min |
| `j4-03-introduire-un-pattern-en-refactoring` | rappels | Faire émerger un pattern en 4 étapes | 60 min |
| `j4-04-resoudre-une-dependance-circulaire` | todo-list | Casser un cycle, verrouiller l'architecture | 45 min |
| `j5-01-premier-pipeline` | calculatrice | Écrire une pipeline GitLab CI complète | 60 min |
| `j5-02-rapports-junit-et-couverture` | todo-list | Rapports JUnit, couverture, seuil en cliquet | 45 min |
| `j5-03-merge-request-cassee` | convertisseur | Diagnostiquer une pipeline rouge | 45 min |

## Les TPs du Jour 5

Les trois TPs du Jour 5 sont des **projets autonomes** : ils ont leur propre
`pyproject.toml`, leur `uv.lock` et un layout `src/`, parce que le packaging
fait partie du sujet.

```bash
cd TPs/j5-01-premier-pipeline/depart
uv lock                                            # une fois par TP
uv run --frozen pytest
uv run --frozen python outils/simuler_pipeline.py  # exécute les jobs du .gitlab-ci.yml
```

`outils/simuler_pipeline.py` n'est pas un runner GitLab : il ne gère ni les
images Docker, ni le cache, ni les artifacts, ni les matrices `parallel`. Il lit
le `.gitlab-ci.yml`, en extrait les stages et les jobs, et **exécute réellement
leurs commandes** en respectant les codes de retour — ce qui suffit à déboguer
une pipeline sans pousser un commit.
