---
marp: true
theme: your-theme
paginate: true
header: "Jour 5 — GitLab CI/CD pour un projet Python"
---

<!-- _class: lead -->

# 2. GitLab CI/CD pour un projet Python

*Du `.gitlab-ci.yml` minimal à la pipeline complète*

---

# Le vocabulaire, en une slide

| Terme | Ce que c'est |
|---|---|
| **Pipeline** | l'ensemble déclenché par une poussée ou une merge request |
| **Stage** | une étape ; les stages s'exécutent **en séquence** |
| **Job** | une unité de travail ; les jobs d'un même stage s'exécutent **en parallèle** |
| **Runner** | la machine qui exécute les jobs |
| **Image** | le conteneur Docker dans lequel le job tourne |
| **Artifact** | un fichier produit par un job, conservé et transmis |
| **Cache** | des fichiers réutilisés d'une pipeline à l'autre, pour la vitesse |

> **Artifact ou cache ?** L'artifact est un **résultat** qu'on veut consulter
> (rapport de tests, paquet). Le cache est un **moyen** d'aller plus vite
> (dépendances). Perdre un cache est sans conséquence ; perdre un artifact, non.

---

# La pipeline minimale qui marche

```yaml
# .gitlab-ci.yml
image: python:3.12-slim

test:
  script:
    - pip install -e ".[dev]"
    - pytest
```

Six lignes. C'est déjà mieux que rien, et c'est le bon point de départ pour une
équipe qui n'a pas encore de CI.

> **🎯 En pratique** : mettez ceci en place **cette semaine**, même si votre
> suite ne compte que trois tests. Une pipeline qui existe s'améliore ; une
> pipeline parfaite qu'on prévoit d'écrire n'existe jamais.

Les slides suivantes ajoutent, dans l'ordre : les stages, le cache, les
rapports, la matrice de versions.

---

# Structurer en stages

```yaml
stages:
  - qualite
  - test
  - packaging

format:
  stage: qualite
  script:
    - ruff format --check .

lint:
  stage: qualite
  script:
    - ruff check .

types:
  stage: qualite
  script:
    - mypy src

tests:
  stage: test
  script:
    - pytest -m "not lent"
```

Les trois jobs de `qualite` tournent **en parallèle** ; `test` ne démarre que
s'ils sont tous verts. Un échec de lint n'attend pas 4 minutes de tests.

> On voit parfois un stage `installation` séparé. Avec `uv sync --frozen` en
> `before_script` et un cache, l'installation est refaite dans chaque job en
> quelques secondes — plus simple qu'un stage qui devrait transmettre un
> environnement complet par artifact.

---

# `uv` dans la pipeline

```yaml
image: python:3.12-slim

variables:
  UV_CACHE_DIR: .uv-cache
  UV_LINK_MODE: copy          # évite les avertissements de lien dur en conteneur

.avec_uv: &avec_uv
  before_script:
    - pip install --no-cache-dir uv
    - uv sync --frozen        # installe EXACTEMENT le uv.lock du dépôt
  cache:
    key:
      files: [uv.lock]        # nouvelle clé quand les dépendances changent
    paths: [.uv-cache]

tests:
  <<: *avec_uv
  stage: test
  script:
    - uv run pytest
```

> **`--frozen` est le point important** : il échoue si `uv.lock` ne correspond
> plus à `pyproject.toml`. Sans lui, la CI peut installer des versions
> différentes des vôtres — et vous ne testez plus la même chose.

---

# Le cache des dépendances

Sans cache, chaque job réinstalle tout. Sur un projet avec `numpy`, `pandas` et
`scipy`, cela représente **deux à trois minutes par job**.

```yaml
cache:
  key:
    files:
      - uv.lock             # la clé change quand le verrou change
  paths:
    - .uv-cache
  policy: pull-push         # pull seul pour les jobs qui n'installent rien
```

| Situation | Effet |
|---|---|
| `uv.lock` inchangé | cache réutilisé — installation en quelques secondes |
| `uv.lock` modifié | nouvelle clé, cache reconstruit une fois |
| Cache absent ou corrompu | le job réinstalle, sans échouer |

> **⚠️ Piège** : ne mettez **jamais** le `.venv` en cache entre des images
> différentes. Les chemins absolus et les binaires compilés ne sont pas
> portables. Mettez en cache le **répertoire de téléchargement**, pas
> l'environnement.

---

# Variables et secrets

```yaml
variables:
  PYTHONDONTWRITEBYTECODE: "1"
  PIP_DISABLE_PIP_VERSION_CHECK: "1"
  UV_CACHE_DIR: .uv-cache
```

Ce sont des variables **de configuration**, versionnées : aucun secret ici.

Les secrets se déclarent dans l'interface GitLab
(*Settings → CI/CD → Variables*), avec deux options qui comptent :

| Option | Effet |
|---|---|
| **Masked** | la valeur est remplacée par `[MASKED]` dans les journaux |
| **Protected** | la variable n'est exposée qu'aux branches protégées |

> **⚠️ Piège** : un secret écrit dans le `.gitlab-ci.yml` reste dans
> l'historique Git **même après suppression**. Le retirer du fichier ne suffit
> pas : il faut le révoquer.

---

# Contrôler ce qui déclenche quoi avec `rules`

```yaml
tests:
  stage: test
  script: [uv run pytest -m "not lent"]
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

tests_lents:
  stage: test
  script: [uv run pytest -m lent]
  rules:
    - if: $CI_PIPELINE_SOURCE == "schedule"      # la nuit
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
      when: manual                                # ou à la demande
      allow_failure: true
```

| Variable GitLab | Contient |
|---|---|
| `$CI_PIPELINE_SOURCE` | `push`, `merge_request_event`, `schedule`, `web` |
| `$CI_COMMIT_BRANCH` | la branche courante |
| `$CI_DEFAULT_BRANCH` | `main`, en général |
| `$CI_MERGE_REQUEST_IID` | le numéro de la MR |

---

# Tester plusieurs versions de Python

Pour une librairie interne consommée par des projets qui n'ont pas tous la même
version de Python, c'est le contrôle le plus utile de toute la pipeline.

```yaml
tests:
  stage: test
  image: python:$VERSION_PYTHON-slim
  parallel:
    matrix:
      - VERSION_PYTHON: ["3.10", "3.11", "3.12", "3.13"]
  script:
    - pip install --no-cache-dir uv
    - uv sync --frozen
    - uv run pytest
```

Quatre jobs en parallèle, un par version. Vous découvrez immédiatement qu'une
syntaxe `match` ne passe pas en 3.9, ou qu'un `StrEnum` exige 3.11.

> **🎯 En pratique** : la matrice doit refléter les versions **réellement
> utilisées** par vos consommateurs — pas les versions supportées en amont.

---

# Le stage `packaging`

```yaml
build:
  stage: packaging
  script:
    - uv build                       # produit dist/*.whl et dist/*.tar.gz
    - uv run twine check dist/*      # vérifie les métadonnées
  artifacts:
    paths: [dist/]
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_TAG             # uniquement sur une version taguée
```

Deux contrôles que ce job apporte, et que les tests ne donnent pas :

- le paquet **se construit** — un `pyproject.toml` cassé est détecté ;
- le paquet **contient ce qu'il faut** — c'est ici qu'on découvre un fichier de
  données oublié, grâce au layout `src/` vu au Jour 2.

---

# Une pipeline complète, commentée

```yaml
stages: [qualite, test, rapport]

image: python:3.12-slim
variables:
  UV_CACHE_DIR: .uv-cache
  UV_LINK_MODE: copy

default:
  before_script:
    - pip install --no-cache-dir uv
    - uv sync --frozen
  cache:
    key: {files: [uv.lock]}
    paths: [.uv-cache]

format:      {stage: qualite, script: [uv run ruff format --check .]}
lint:        {stage: qualite, script: [uv run ruff check .]}
types:       {stage: qualite, script: [uv run mypy src]}
architecture: {stage: qualite, script: [uv run lint-imports]}

tests:
  stage: test
  script:
    - uv run pytest --junitxml=rapport.xml --cov=src --cov-report=xml
  artifacts:
    when: always
    reports:
      junit: rapport.xml
      coverage_report: {coverage_format: cobertura, path: coverage.xml}
```

---

# Débogage : les erreurs les plus fréquentes

| Symptôme | Cause habituelle |
|---|---|
| `ModuleNotFoundError` sur votre propre package | pas d'installation ; il faut `uv sync` ou `pip install -e .` |
| Les tests passent en local, pas en CI | dépendance non déclarée, ou état partagé entre tests |
| `Permission denied` sur le cache | `UV_LINK_MODE: copy` manquant |
| Job vert alors que la commande a échoué | commandes chaînées par `;` au lieu de `&&` |
| `uv.lock` en conflit à chaque merge | verrou non régénéré après modification des dépendances |
| Pipeline très lente | pas de cache, ou un seul job qui fait tout |

> **⚠️ Le quatrième** est le plus insidieux. GitLab n'échoue que si la
> **dernière** commande d'un `script` renvoie un code non nul — sauf si vous
> les séparez par des lignes distinctes, ce que fait la syntaxe YAML en liste.
> Utilisez toujours une commande par ligne.

---

# Valider son `.gitlab-ci.yml` avant de pousser

Trois moyens, du plus rapide au plus fidèle :

```bash
# 1. Syntaxe YAML seule — instantané
python -c "import yaml, pathlib; yaml.safe_load(pathlib.Path('.gitlab-ci.yml').read_text())"

# 2. Validation par GitLab — sans pousser
#    Interface : CI/CD → Editor → onglet « Validate »
#    Ou l'API  : POST /api/v4/projects/:id/ci/lint

# 3. Exécuter localement les mêmes commandes que les jobs
uv run ruff check . && uv run mypy src && uv run pytest
```

> **🎯 En pratique** : le troisième moyen est le plus utile au quotidien.
> Une pipeline ne doit contenir **aucune commande** que vous ne puissiez lancer
> sur votre poste — sinon vous déboguez à l'aveugle, une poussée à la fois.

---

# À retenir

> **1.** Commencez par six lignes qui lancent `pytest`. Une pipeline qui existe
> s'améliore ; celle qu'on prévoit d'écrire parfaitement n'arrive jamais.

> **2.** `uv sync --frozen` garantit que la CI installe exactement ce que
> décrit `uv.lock` — sans quoi vous ne testez pas la même chose que vos
> consommateurs installeront.

> **3.** Toute commande de la pipeline doit être exécutable sur votre poste.
> C'est la seule façon de déboguer autrement qu'en poussant des commits.
