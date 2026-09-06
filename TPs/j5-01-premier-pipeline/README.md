# TP j5-01 — Écrire une pipeline GitLab CI complète

**Durée : 60 min**

## Contexte

`depart/` contient un vrai package : `calculatrice`, des opérations
élémentaires et un évaluateur d'expressions en notation polonaise inverse
(`3 4 + 2 *` vaut 14). Layout `src/`, `pyproject.toml`, 30 tests qui passent.

Il n'a **aucune pipeline**. Chacun lance les tests quand il y pense.

## Objectif

Écrire un `.gitlab-ci.yml` complet — stages, cache, rapports, matrice de
versions — et le **vérifier localement** avant toute poussée.

## Le simulateur

Vous n'avez pas de runner GitLab. `outils/simuler_pipeline.py` lit votre
`.gitlab-ci.yml`, en extrait les stages et les jobs, et **exécute réellement
leurs commandes**, dans l'ordre, en respectant les codes de retour.

```bash
cd j5-01-premier-pipeline/depart
uv lock                                        # une fois
uv run --frozen python outils/simuler_pipeline.py
```

Ce qu'il ne fait pas : les images Docker, le cache, les artifacts, la matrice
de versions (il n'exécute qu'une fois les jobs `parallel`). Ce qu'il fait, et
qui est l'essentiel : vous dire si vos commandes marchent.

> Si Docker est installé sur votre poste, `gitlab-ci-local` fait tout cela
> fidèlement, conteneurs compris : `brew install gitlab-ci-local`, puis
> `gitlab-ci-local` dans le dossier. Le simulateur reste le repli sans Docker.

## Étapes

### 1. La pipeline minimale (10 min)

Créez `depart/.gitlab-ci.yml` :

```yaml
image: python:3.12-slim

test:
  script:
    - pip install --no-cache-dir uv
    - uv sync --frozen
    - uv run pytest
```

Lancez le simulateur. Vert ? Vous avez une pipeline. Tout le reste n'est
qu'amélioration.

### 2. Les stages (15 min)

Découpez en trois : `qualite`, `test`, `packaging`. Ajoutez trois jobs de
qualité qui tournent **en parallèle** :

| Job | Commande |
|---|---|
| `format` | `uv run ruff format --check .` |
| `lint` | `uv run ruff check .` |
| `types` | `uv run mypy src` |

> Lancez le simulateur. **Deux de ces jobs vont échouer** — le package de départ
> n'est pas propre : des imports en désordre, un import inutile, du code
> formaté à la main. C'est volontaire : corrigez-le avec `ruff format .` et
> `ruff check --fix .`, exactement comme vous le feriez sur une vraie MR.

### 3. Factoriser avec `default` (10 min)

Les trois jobs répètent les deux mêmes lignes d'installation. Remontez-les :

```yaml
default:
  before_script:
    - pip install --no-cache-dir uv
    - uv sync --frozen
  cache:
    key:
      files: [uv.lock]
    paths: [.uv-cache]
```

Ajoutez les variables `UV_CACHE_DIR` et `UV_LINK_MODE: copy`.

> **Pourquoi `--frozen` ?** Sans lui, `uv sync` peut mettre à jour `uv.lock` et
> installer des versions différentes des vôtres. Avec, la CI échoue si le verrou
> n'est plus cohérent avec `pyproject.toml` — ce qui est le comportement voulu.

### 4. Les rapports (10 min)

```yaml
tests:
  stage: test
  script:
    - uv run pytest --junitxml=rapport.xml --cov=src --cov-report=xml
  artifacts:
    when: always
    reports:
      junit: rapport.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

> **`when: always` est la ligne à ne pas oublier.** Sans elle, GitLab ne
> récupère les artifacts que si le job réussit — donc jamais quand vous en avez
> besoin.

### 5. La matrice de versions (10 min)

`calculatrice` déclare `requires-python = ">=3.10"`. Cette promesse est-elle
tenue ?

```yaml
tests_multi_versions:
  stage: test
  image: python:$VERSION_PYTHON-slim
  parallel:
    matrix:
      - VERSION_PYTHON: ["3.10", "3.11", "3.12", "3.13"]
  script:
    - uv run pytest -q
```

> Le simulateur n'exécutera ce job qu'une fois, avec votre Python local. Pour
> vraiment vérifier les quatre versions : `uv run --python 3.10 pytest`.
> Essayez — le package passe-t-il en 3.10 ?

### 6. Le packaging (5 min)

```yaml
build:
  stage: packaging
  script:
    - uv build
    - ls -l dist/
  artifacts:
    paths: [dist/]
  rules:
    - if: $CI_COMMIT_TAG
```

Ce job vérifie une chose que les tests ne voient pas : **le paquet se
construit**. C'est ici qu'on découvre un `pyproject.toml` cassé ou un fichier
de données oublié.

## Critères de réussite

- `uv run --frozen python outils/simuler_pipeline.py` affiche `✓ PIPELINE VERTE`.
- Les trois jobs de qualité sont dans le même stage.
- L'installation n'est écrite qu'**une seule fois**, dans `default`.
- `when: always` figure sur les artifacts du job de tests.
- Vous pouvez lancer **chaque commande** de votre pipeline à la main.

## Pour aller plus loin

Cassez volontairement un test, relancez le simulateur, et vérifiez que le stage
`packaging` **n'est pas exécuté**. Puis remettez le test en état.

## Corrigé

`corrige/.gitlab-ci.yml` — 3 stages, 6 jobs, commenté.

```bash
cd j5-01-premier-pipeline/corrige
uv lock && uv run --frozen python outils/simuler_pipeline.py
```
