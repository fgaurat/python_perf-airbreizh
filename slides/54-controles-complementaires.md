---
marp: true
theme: your-theme
paginate: true
header: "Jour 5 — Contrôles complémentaires"
---

<!-- _class: lead -->

# 4. Contrôles complémentaires

*Ce qu'on automatise à côté des tests*

---

# Les cinq contrôles, et ce qu'ils attrapent

| Contrôle | Attrape | Coût |
|---|---|---|
| `ruff format` | débats de mise en forme en revue | quelques secondes |
| `ruff check` | imports inutilisés, variables mortes, pièges courants | quelques secondes |
| `mypy` | incohérences de types, `None` non géré | dizaines de secondes |
| `pytest-cov` | code neuf jamais exécuté | +20 % sur la suite |
| `import-linter` | cycles et violations d'architecture | quelques secondes |

Aucun ne remplace un test. Tous attrapent des défauts qu'un test ne verrait
qu'indirectement — et pour un coût très inférieur.

> **🎯 L'ordre d'adoption qui fonctionne** : formatage, puis lint, puis
> architecture, puis typage, puis couverture. Du moins discutable au plus
> discutable.

---

# `ruff` — formatage et lint

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py312"
extend-exclude = ["**/migrations"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]
```

| Famille | Ce qu'elle apporte |
|---|---|
| `E`, `F` | erreurs et avertissements de base (ex-`pycodestyle`, `pyflakes`) |
| `I` | tri automatique des imports (ex-`isort`) |
| `UP` | modernisation de la syntaxe selon la version cible |
| `B` | pièges réels — dont l'argument par défaut mutable |
| `SIM` | simplifications de code lisibles |

```bash
uv run ruff format .          # applique
uv run ruff format --check .  # vérifie, pour la CI
uv run ruff check --fix .     # corrige ce qui est corrigeable
```

> Un seul outil remplace `black`, `isort`, `flake8` et une partie de `pylint` —
> pour un temps d'exécution de l'ordre de la centaine de millisecondes.

---

# `mypy` — l'adoption progressive

Activer `strict` sur une base existante produit des milliers d'erreurs et une
équipe démotivée. L'adoption se fait **module par module**.

```toml
[tool.mypy]
python_version = "3.12"
ignore_missing_imports = true      # les dépendances non typées ne bloquent pas

# Le socle, écrit récemment : exigeant
[[tool.mypy.overrides]]
module = ["mesures.modele", "mesures.calculs"]
strict = true

# Le legacy : on vérifie ce qui est déjà annoté, sans plus
[[tool.mypy.overrides]]
module = ["mesures.ancien_moteur"]
ignore_errors = true
```

> **🎯 En pratique** : commencez par les modules du bas de l'architecture —
> `modele`, `calculs`. Ce sont les mieux découpés, les plus faciles à typer, et
> ceux dont tout le reste dépend.

---

# `pytest-cov` — mesurer sans se mentir

```toml
[tool.coverage.run]
source = ["src"]
branch = true                     # couvre aussi les branches, pas que les lignes

[tool.coverage.report]
exclude_also = [
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
```

```bash
uv run pytest --cov=src --cov-report=term-missing
```

```
Name                     Stmts   Miss Branch BrPart  Cover   Missing
------------------------------------------------------------------------
src/mesures/calculs.py      42      2     14      1    95%   58, 71->74
```

> La colonne **Missing** est la seule vraiment exploitable : elle donne les
> lignes et les branches à regarder. Le pourcentage, lui, ne dit rien
> d'actionnable.

---

# Le seuil de couverture : sur le diff, pas sur le projet

<div class="cols">
<div>

**Seuil global** ❌

```bash
pytest --cov=src --cov-fail-under=80
```

Sur du legacy à 12 %, la pipeline est
rouge dès le premier jour. L'équipe
désactive le contrôle — ou écrit des
tests sans assertion.

</div>
<div>

**Seuil sur le diff** ✓

Dans GitLab : *Settings → Merge requests →
Merge checks*, ou via l'affichage
ligne à ligne du diff.

On n'exige rien du passé. On exige que
le **code neuf** soit testé.

</div>
</div>

> **🎯 En pratique** : `--cov-fail-under` reste utile avec un seuil réglé
> **juste en dessous** de la valeur actuelle. Il n'impose pas de progresser, il
> empêche de **régresser** — c'est un cliquet, pas un objectif.

---

# `pre-commit` — attraper avant de pousser

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.16.5
    hooks:
      - id: ruff-format
      - id: ruff
        args: [--fix]
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

```bash
uv run pre-commit install        # une fois par poste
```

Le formatage et le lint sont corrigés **avant** le commit : la pipeline ne
rougit plus jamais pour une virgule.

> **⚠️ Piège** : `pre-commit` ne remplace pas la CI. Il s'installe poste par
> poste et peut être contourné (`--no-verify`). Les mêmes contrôles doivent
> rester dans la pipeline.

---

# Choisir des indicateurs utiles

| Indicateur utile | Ce qu'il pilote |
|---|---|
| Le code neuf est-il testé ? | couverture du diff |
| Un bug corrigé peut-il revenir ? | présence d'un test de non-régression dans la MR |
| La suite reste-t-elle lançable en local ? | durée des tests unitaires |
| L'architecture tient-elle ? | `lint-imports` en CI |
| Les tests sont-ils fiables ? | nombre de tests instables sur un mois |

| Métrique cosmétique | Ce qu'elle produit |
|---|---|
| Couverture globale imposée | des tests sans assertion |
| Nombre de tests | des tests dupliqués |
| Nombre de lignes par fonction, en dur | des fonctions découpées arbitrairement |
| Zéro avertissement, tous outils confondus | des `# noqa` partout |

> Chaque ligne du second tableau a été observée dans des équipes réelles, à qui
> l'on avait fixé la métrique comme objectif.

---

# À retenir

> **1.** Adoptez dans cet ordre : formatage, lint, architecture, typage,
> couverture. Chaque contrôle n'est rendu bloquant qu'après résorption du passif.

> **2.** `mypy` s'active **module par module**, en commençant par le bas de
> l'architecture — jamais en `strict` global sur du legacy.

> **3.** Le seuil de couverture est un **cliquet** contre la régression, réglé
> juste sous la valeur actuelle. Ce n'est pas un objectif à atteindre.
