---
marp: true
theme: your-theme
paginate: true
header: "Jour 1 — Une démarche guidée par les tests"
---

<!-- _class: lead -->

# 2. Introduction à une démarche guidée par les tests

*Le test comme outil d'analyse, pas comme corvée finale*

---

# Pourquoi parler des tests dès la conception

Le test est le **premier consommateur** de votre code.

Il l'utilise exactement comme le fera un autre projet : de l'extérieur, sans
connaître les détails internes, en fournissant des entrées et en observant des
sorties.

Conséquence directe :

> Si votre code est pénible à tester, il sera pénible à utiliser.
> La difficulté à écrire le test n'est pas un problème de test.
> C'est un **retour d'information sur la conception**.

C'est pour cela que nous ne traitons pas les tests en fin de formation.

---

# Tester après coup vs concevoir testable

<div class="cols">
<div>

**Tester après coup**

Le code existe, il faut « le couvrir ».

- On subit la structure existante
- On mocke beaucoup pour contourner
- Les tests deviennent fragiles
- On teste ce qui est facile, pas ce qui est risqué
- La couverture monte, la confiance non

</div>
<div>

**Concevoir testable**

On se demande, avant d'écrire : *comment saurai-je que c'est juste ?*

- Les dépendances deviennent des paramètres
- Le calcul se sépare des I/O
- Les fonctions rétrécissent naturellement
- Les tests sont courts et stables

</div>
</div>

La deuxième colonne ne demande pas plus de temps. Elle demande de se poser la
question **avant** plutôt qu'après.

---

# Le TDD n'est pas une technique de test

C'est une technique d'**analyse et de conception** qui produit des tests
comme sous-produit.

Écrire le test d'abord vous force à répondre, avant d'écrire une ligne
d'implémentation :

- Comment cette fonction s'appelle-t-elle ?
- Que reçoit-elle exactement, et sous quelle forme ?
- Que retourne-t-elle ? Dans quelle unité ?
- Que fait-elle quand l'entrée est invalide ?

> Ce sont les questions qu'on ne se pose habituellement **qu'après** avoir
> écrit le code — c'est-à-dire trop tard pour changer d'avis sans coût.

---

# Le cycle Red / Green / Refactor

```
        ┌──────────────────────────────────────────┐
        │                                          │
        ▼                                          │
   ┌─────────┐        ┌─────────┐         ┌────────────┐
   │  RED    │───────▶│  GREEN  │────────▶│  REFACTOR  │
   └─────────┘        └─────────┘         └────────────┘
   Écrire un test     Le faire passer     Améliorer le code
   qui échoue         le plus simplement  sans changer le
   pour la bonne      possible            comportement
   raison
     ~1 min             ~2 min                ~2 min
```

L'unité de temps est la **minute**, pas la journée. Un cycle qui dure une
demi-journée n'est pas un cycle TDD : c'est un développement classique avec un
test écrit en premier.

---

# Ce que chaque phase apporte réellement

| Phase | Ce qu'on croit y faire | Ce qu'on y fait vraiment |
|---|---|---|
| **Red** | écrire un test | **définir le comportement attendu et l'interface** |
| **Green** | écrire du code | prouver que le test sait détecter l'absence de code |
| **Refactor** | faire joli | **concevoir**, sous protection du test qui vient de passer |

La phase la plus souvent sautée est **Refactor**. C'est pourtant la seule où
la conception s'améliore : sans elle, le TDD ne produit que des tests.

> **⚠️ Piège** : un test qui passe *du premier coup* n'a rien prouvé. Vous
> ignorez s'il est capable d'échouer. Voir le rouge fait partie du test.

---

<!-- _class: dense -->

# Un cycle complet en 3 minutes

<div class="cols">
<div>

**Red** — le test décrit l'intention

```python
def test_moyenne_horaire_simple():
    mesures = [10.0, 20.0, 30.0]
    assert moyenne_horaire(mesures) == 20.0
```

`ImportError` → rouge, pour la bonne raison.

**Green** — le minimum

```python
def moyenne_horaire(mesures):
    return sum(mesures) / len(mesures)
```

</div>
<div>

**Red** — le cas limite découvert en écrivant

```python
def test_moyenne_horaire_sans_mesure():
    with pytest.raises(SérieVide):
        moyenne_horaire([])
```

**Green + Refactor**

```python
def moyenne_horaire(mesures: Sequence[float]) -> float:
    """Moyenne arithmétique d'une série non vide."""
    if not mesures:
        raise SérieVide("série de mesures vide")
    return sum(mesures) / len(mesures)
```

</div>
</div>

Le cas `[]` a été trouvé **en écrivant le test**, pas en production.

---

# Où le TDD est clairement pertinent

Dans une librairie métier, le TDD fonctionne très bien sur :

- **les règles de gestion** — seuils, validations, conditions d'éligibilité ;
- **les transformations de données** — un format d'entrée vers un format de sortie ;
- **le parsing** — lire un fichier, une chaîne, un identifiant ;
- **les calculs à résultat connu** — une formule dont on peut écrire un cas de référence à la main ;
- **la correction de bugs** — le bug fournit le test rouge, gratuitement ;
- **la conception d'une API publique** — le test est le premier utilisateur.

Point commun : **on sait énoncer le résultat attendu avant de coder**.

---

# Où une approche plus souple s'impose

Quand on ne connaît pas le résultat attendu à l'avance :

| Situation | Pourquoi le TDD strict coince | Démarche adaptée |
|---|---|---|
| Exploration, prototype | On cherche encore le problème | Coder puis jeter, tester ce qui survit |
| Calcul numérique complexe | Le résultat exact est inconnu | Tester les **propriétés** : bornes, monotonie, symétrie, conservation |
| Portage d'un code existant | La référence, c'est l'ancien code | Tests de **caractérisation** (Jour 4) |
| Visualisation, rendu | Le résultat est visuel | Test de non-plantage + relecture humaine |
| Intégration d'un outil tiers | Le comportement réel est incertain | Un test d'intégration d'abord, pour apprendre |

> **🎯 En pratique** : TDD strict sur le cœur métier, approche souple sur les
> bords. Personne ne fait du TDD à 100 %, et ce n'est pas le but.

---

# À retenir

> **1.** Le test est le premier consommateur de votre code : une difficulté à
> tester est un signal de conception, pas une contrainte de test.

> **2.** Le TDD est une démarche d'analyse. Son produit principal est une
> meilleure interface ; les tests ne sont qu'un bénéfice secondaire.

> **3.** Red / Green / **Refactor** — la troisième phase est celle qu'on saute
> et c'est la seule où la conception progresse.
