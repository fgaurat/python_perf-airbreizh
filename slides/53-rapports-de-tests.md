---
marp: true
theme: your-theme
paginate: true
header: "Jour 5 — Rapports de tests"
---

<!-- _class: lead -->

# 3. Rapports de tests

*Passer des journaux bruts à une information exploitable*

---

# Journal brut ou rapport structuré

<div class="cols">
<div>

**Le journal du job**

```
============ FAILURES ============
___ test_seuil_inclusif ___
    def test_seuil_inclusif():
>       assert est_eligible(...) is True
E       assert False is True
=== 1 failed, 632 passed in 0.9s ===
```

Il faut ouvrir le job, dérouler
2 000 lignes, et chercher.

</div>
<div>

**Le rapport JUnit dans la MR**

GitLab affiche directement, en tête
de la merge request :

> ❌ **1 test en échec**
> `test_seuil_inclusif`
> *nouvel échec*

Un clic donne la trace complète.

</div>
</div>

Le rapport structuré apporte trois choses que le journal ne donne pas : la
**visibilité** sans ouvrir le job, la distinction **nouvel échec / échec
existant**, et l'historique d'un test dans le temps.

---

# Produire un rapport JUnit

```bash
pytest --junitxml=rapport.xml
```

```yaml
tests:
  stage: test
  script:
    - uv run pytest --junitxml=rapport.xml
  artifacts:
    when: always              # ← indispensable : sinon rien en cas d'échec
    reports:
      junit: rapport.xml
    expire_in: 30 days
```

> **⚠️ Le piège classique** : sans `when: always`, GitLab ne récupère les
> artifacts que si le job réussit. Or c'est **précisément quand il échoue** que
> vous avez besoin du rapport. Cette ligne est la plus importante de la slide.

Enrichir le rapport avec des propriétés utiles :

```bash
pytest --junitxml=rapport.xml -o junit_family=xunit2 -o junit_logging=all
```

---

# La couverture dans la merge request

```bash
pytest --cov=src --cov-report=xml --cov-report=term
```

```yaml
tests:
  script:
    - uv run pytest --cov=src --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'        # extrait le pourcentage du journal
  artifacts:
    when: always
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

Deux affichages distincts en résultent :

| Où | Quoi |
|---|---|
| Badge de la MR | le pourcentage global, et son évolution |
| **Diff de la MR** | chaque ligne ajoutée est marquée couverte ou non |

> Le second est le seul vraiment utile : il montre **si le code de cette MR**
> est testé, indépendamment du passif du projet.

---

# Conserver et transmettre les artifacts

```yaml
tests:
  artifacts:
    when: always
    expire_in: 30 days
    paths:
      - rapport.xml
      - htmlcov/            # rapport HTML de couverture, navigable
    reports:
      junit: rapport.xml

analyse:
  stage: rapport
  needs: [tests]            # récupère automatiquement les artifacts de `tests`
  script:
    - python outils/comparer_couverture.py coverage.xml
```

| Réglage | Effet |
|---|---|
| `expire_in` | durée de conservation — au-delà, GitLab supprime |
| `paths` | fichiers téléchargeables depuis l'interface |
| `reports` | fichiers **interprétés** par GitLab (JUnit, couverture) |
| `needs` | dépendance explicite entre jobs, et transfert d'artifacts |

---

# Lire un échec de pipeline efficacement

L'ordre qui fait gagner du temps :

```
   1. L'onglet « Tests » de la MR        quel test, et est-il nouveau ?
              ↓
   2. Le nom du test                     quelle règle métier est en cause ?
              ↓
   3. L'assertion                        quelle valeur, quel écart ?
              ↓
   4. Reproduire en local                pytest tests/…::test_… -x
              ↓
   5. Le journal complet du job          seulement si les 4 précédents ne suffisent pas
```

> **🎯 En pratique** : si vous devez systématiquement aller jusqu'à l'étape 5,
> vos noms de tests ou vos assertions sont trop pauvres. C'est un défaut de
> **vos tests**, que la CI rend simplement visible.

C'est le retour direct des conventions du Jour 2 : un test = un comportement,
un nom qui décrit ce comportement, une assertion sur une valeur.

---

# Ce qu'il ne faut pas attendre d'un rapport

| Attente | Réalité |
|---|---|
| « Le rapport nous dira si le code est bon » | il dit si **vos tests** passent |
| « 100 % de couverture = pas de bug » | la couverture ne juge aucune assertion |
| « Le badge motivera l'équipe » | il motive surtout à écrire des tests faciles |
| « On archivera tous les rapports » | `expire_in` existe pour une raison : le stockage |

Ce que le rapport apporte réellement, et qui est déjà beaucoup :

- une **preuve** partagée que la suite a tourné, sur un environnement neutre ;
- la distinction entre un échec **nouveau** et un échec **connu** ;
- une trace consultable **sans relancer** quoi que ce soit ;
- un point d'appui factuel en revue, à la place d'une discussion d'opinion.

---

# À retenir

> **1.** `when: always` sur les artifacts. Sans cette ligne, vous perdez le
> rapport exactement quand vous en avez besoin.

> **2.** La couverture qui compte est celle du **diff**, affichée ligne à ligne
> dans la merge request — pas le pourcentage global.

> **3.** Si lire un échec exige d'ouvrir le journal complet, le problème est
> dans le nommage de vos tests, pas dans l'outil.
