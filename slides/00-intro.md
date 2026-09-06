---
marp: true
theme: your-theme
paginate: true
header: "Introduction"
---

# Python avancé
<center>

![width:400px](logo_python.png)

</center>

Qualité logicielle, TDD, design patterns et CI/CD

---

# Frédéric Gaurat
## Formateur et développeur

---

# Horaires

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
<div>

  - 9h00
  - pause
  - 12h30


</div>
<div>

  - 13h30
  - pause
  - 17h00
</div>
</div>


---

# Ce que cette formation n'est pas

Ce n'est **pas** un « Python perfectionnement » généraliste.

Nous ne parlerons pas de :

- métaclasses, descripteurs et magie du langage pour eux-mêmes ;
- `asyncio`, multiprocessing, optimisation de performance ;
- Django, Flask, FastAPI ;
- data science et notebooks.

> Ces sujets sont utiles. Ils ne sont pas ce qui rend une librairie interne
> fiable et durable.

---

# Ce que cette formation est

Du **développement logiciel professionnel en Python**, avec un seul fil directeur :

> Rendre des librairies Python internes plus robustes,
> plus testables et plus faciles à faire évoluer.

Le problème que nous traitons pendant 5 jours :

**« Je dois modifier ce code, et je ne sais pas ce que je vais casser. »**

---

# La logique de la formation : guidée par les tests

Les tests ne sont pas un contrôle qualité de fin de chaîne.

Ce sont, dans l'ordre :

1. un **outil d'analyse** — écrire le test force à définir le comportement attendu ;
2. un **outil de conception** — un code difficile à tester est un code mal découpé ;
3. un **filet de sécurité** — ils autorisent le refactoring ;
4. un **contrat** — ils documentent ce que la librairie promet à ses consommateurs.

La vérification des régressions n'arrive qu'en cinquième position.

---

# À la fin des 5 jours, vous saurez

<div class="cols">
<div>

**Concevoir**

- Découper un code pour le rendre testable
- Réduire le couplage et les dépendances circulaires
- Appliquer SOLID sans sur-architecturer
- Choisir un design pattern quand il résout un vrai problème

</div>
<div>

**Tester et industrialiser**

- Écrire des tests pytest utiles (et savoir lesquels ne pas écrire)
- Utiliser fixtures, paramétrisation, doubles de test
- Distinguer mock, stub, fake et monkeypatch
- Refactoriser du code existant sans régression
- Automatiser tout cela dans GitLab CI/CD

</div>
</div>

---

# Déroulé des 5 jours

| Jour | Thème | Question centrale |
|---|---|---|
| **1** | Qualité, POO testable, SOLID | *Pourquoi ce code est-il si dur à tester ?* |
| **2** | pytest, stratégie de test, TDD | *Que faut-il tester, et comment ?* |
| **3** | Mocking et design patterns | *Comment tester ce qui dépend de l'extérieur ?* |
| **4** | Refactoring et code legacy | *Comment améliorer sans casser ?* |
| **5** | GitLab CI/CD et qualité automatisée | *Comment rendre tout cela systématique ?* |

Chaque journée : environ **la moitié du temps en pratique**, le reste en apport et discussion.

---

# Prérequis et outillage

**Ce qui est supposé acquis** : fonctions, classes, modules, packages,
environnements virtuels, usage courant de Git.

**Outillage de la formation** :

| Outil | Rôle |
|---|---|
| Python 3.12 | Le langage |
| `uv` | Environnement et dépendances |
| `pytest` + `pytest-cov` | Tests et couverture |
| `ruff` | Lint et formatage |
| `mypy` | Typage statique |
| GitLab CI/CD | Automatisation |

Tout ce qui est montré avec `uv` reste faisable avec `python -m venv` + `pip`.

---

# Conventions du support

Trois types de slides reviennent régulièrement :

> **⚠️ Piège** — l'erreur classique sur le sujet qui vient d'être présenté.

> **🎯 En pratique** — la règle de décision utilisable dès lundi prochain.

> **À retenir** — trois points maximum en clôture de chaque section.

Les exemples de code sont volontairement courts et souvent présentés
**avant / après**. Le mauvais exemple n'est jamais laissé sans sa correction.

---

# Comment nous allons travailler

- **19 travaux pratiques indépendants.** Chacun a son propre contexte : pas de
  projet fil rouge à suivre de bout en bout.
- Chaque TP contient un `README.md`, un dossier `depart/` et un dossier
  `corrige/` que vous pouvez consulter.
- Les questions sont bienvenues à tout moment, en particulier
  **« chez nous, on a exactement ce problème »** — ce sont les meilleurs
  moments de la formation.

Un conseil pour ces 5 jours : gardez en tête **un** code de votre équipe qui
vous pose problème. Nous y reviendrons.
