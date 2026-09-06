---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — Premiers cycles TDD avec pytest"
---

<!-- _class: lead -->

# 5. Premiers cycles TDD avec pytest

*Le cycle, appliqué pas à pas sur une fonction métier*

---

# Le cas de travail

Une règle de gestion réelle, énoncée par le métier :

> « Le tarif horaire d'une intervention est de 65 €. Au-delà de 8 heures dans la
> même journée, les heures supplémentaires sont majorées de 25 %. À partir de la
> 11ᵉ heure, la majoration passe à 50 %. »

Ce que nous **ne** faisons pas : ouvrir un fichier et commencer par
`def calculer_tarif(...)`.

Ce que nous faisons : écrire le premier test, et laisser les questions arriver.

> Combien de temps faut-il pour se rendre compte, en codant directement, que
> l'énoncé ne dit rien de ce qui se passe à **exactement** 8 heures ?

---

# Red — décrire le comportement le plus simple

```python
# tests/test_tarification.py
from facturation.tarifs import cout_intervention

def test_journee_standard():
    assert cout_intervention(heures=6) == 390.0
```

Trois décisions viennent d'être prises, et elles sont **les bonnes questions** :

| Décision | Alternative écartée |
|---|---|
| Le nom : `cout_intervention` | `calculer`, `tarif`, `process` |
| Le paramètre : `heures`, nommé | un positionnel, un objet `Intervention` |
| Le retour : un `float` en euros | un dict, un objet `Facture` |

Nous venons de concevoir une interface. Aucune implémentation n'existe encore.

---

# Red — voir l'échec, et vérifier sa raison

```bash
$ pytest tests/test_tarification.py
ImportError: cannot import name 'cout_intervention' from 'facturation.tarifs'
```

C'est un rouge **valide** : il dit exactement ce qui manque.

```python
# facturation/tarifs.py
def cout_intervention(heures: float) -> float:
    raise NotImplementedError
```

```bash
$ pytest
E   NotImplementedError
```

Encore mieux : le test atteint désormais la fonction. Nous savons que le test
**sait échouer**.

> **⚠️ Piège** : sauter cette étape est l'erreur la plus fréquente. Un test
> jamais vu rouge peut ne rien vérifier du tout — et vous ne le saurez jamais.

---

# Green — le minimum qui fait passer

```python
TAUX_HORAIRE = 65.0

def cout_intervention(heures: float) -> float:
    return heures * TAUX_HORAIRE
```

```bash
$ pytest
1 passed in 0.01s
```

C'est volontairement incomplet : les majorations ne sont pas gérées. Et c'est
**correct à ce stade** — aucun test ne les demande encore.

> **🎯 En pratique** : écrire ici la règle complète des majorations, c'est
> écrire du code que rien ne vérifie. C'est précisément ce que le TDD cherche à
> éviter : du code dont personne ne sait s'il est juste.

---

# Red — le deuxième cas fait apparaître la règle

```python
def test_heures_supplementaires_majorees_de_25_pourcent():
    # 8 h à 65 € + 2 h à 81,25 €
    assert cout_intervention(heures=10) == 682.5
```

```bash
$ pytest
E   assert 650.0 == 682.5
```

Rouge, pour la bonne raison. On implémente :

```python
SEUIL_MAJORATION_25 = 8

def cout_intervention(heures: float) -> float:
    normales = min(heures, SEUIL_MAJORATION_25)
    sup = max(0.0, heures - SEUIL_MAJORATION_25)
    return normales * TAUX_HORAIRE + sup * TAUX_HORAIRE * 1.25
```

---

# Red — la question que le métier n'avait pas tranchée

```python
def test_a_exactement_huit_heures_aucune_majoration():
    """Le seuil est exclusif : la 8ᵉ heure n'est pas majorée."""
    assert cout_intervention(heures=8) == 520.0
```

Cette question **n'était pas dans l'énoncé**. Elle est apparue en écrivant les
tests, avant que le code parte en production.

Trois cas de ce type sur cette seule règle :

| Question | Réponse à obtenir du métier |
|---|---|
| À exactement 8 h, majoration ? | Non — le seuil est exclusif |
| À exactement 11 h, quel taux ? | 25 %, la 11ᵉ heure n'est pas encore à 50 % |
| Heures négatives ou nulles ? | Erreur métier explicite |

> C'est cela, « le TDD comme outil d'analyse ». Le bénéfice principal n'est pas
> le test : c'est la **conversation** qu'il déclenche.

---

# Refactor — la phase qu'on saute

Après le troisième palier, la fonction accumule les `min` et les `max` :

<div class="cols">
<div>

**Avant**

```python
def cout_intervention(heures):
    n = min(heures, 8)
    s25 = max(0.0, min(heures, 11) - 8)
    s50 = max(0.0, heures - 11)
    return (n * 65.0 + s25 * 65.0 * 1.25
            + s50 * 65.0 * 1.5)
```

</div>
<div>

**Après**

```python
PALIERS = [(8, 1.00), (11, 1.25), (float("inf"), 1.50)]

def cout_intervention(heures: float) -> float:
    total, precedent = 0.0, 0
    for borne, coef in PALIERS:
        tranche = max(0.0, min(heures, borne) - precedent)
        total += tranche * TAUX_HORAIRE * coef
        precedent = borne
    return total
```

</div>
</div>

Les tests ne changent pas d'une ligne — c'est ce qui prouve que le comportement
est préservé. Et un quatrième palier ne coûte plus qu'une entrée dans `PALIERS`.

---

# Ajouter les cas limites, un par un

Une fois la règle nominale en place, le cycle continue sur les bords :

```python
@pytest.mark.parametrize(
    ("heures", "attendu"),
    [
        (0,    0.0),         # aucune intervention
        (0.5,  32.5),        # demi-heure
        (8,    520.0),       # borne du premier palier
        (11,   763.75),      # borne du second palier
        (24,   2031.25),     # journée maximale
    ],
)
def test_paliers(heures, attendu):
    assert cout_intervention(heures) == pytest.approx(attendu)


def test_duree_negative_refusee():
    with pytest.raises(DureeInvalide):
        cout_intervention(heures=-1)
```

Chaque ligne ajoutée a suivi le même cycle : rouge, vert, refactor éventuel.

---

# Ce que le TDD a produit, au-delà des tests

| Livrable | Comment il est apparu |
|---|---|
| Une interface nommée et typée | Écrite dans le premier test, avant tout code |
| Trois ambiguïtés métier levées | Découvertes en écrivant les cas limites |
| Une table de paliers extensible | Sortie de la phase Refactor |
| Une exception métier explicite | Exigée par un test de cas invalide |
| 8 tests qui documentent la règle | Sous-produit |

> La dernière ligne est celle dont on parle toujours. Les quatre premières sont
> celles qui font gagner du temps.

---

# TDD strict ou pragmatique : la règle de décision

| Question | Si oui → TDD strict | Si non → approche souple |
|---|---|---|
| Sais-je énoncer le résultat attendu avant de coder ? | ✓ | écrire un prototype, puis tester ce qui survit |
| Le comportement est-il une règle métier ? | ✓ | tester les propriétés (bornes, monotonie) |
| Le code existe-t-il déjà ? | — | tests de caractérisation d'abord (Jour 4) |
| Suis-je en train d'explorer une bibliothèque ? | — | un test d'intégration pour apprendre |

Une variante intermédiaire, très utile en pratique :

> **« Test-first sur l'interface, code-first sur l'algorithme »** — écrivez le
> test qui fixe la signature et le cas nominal, puis implémentez librement, et
> revenez ajouter les cas limites en TDD.

---

# À retenir

> **1.** Le premier test conçoit l'**interface**. C'est le moment le moins cher
> pour changer d'avis sur un nom, un paramètre ou un type de retour.

> **2.** Voir le rouge n'est pas une formalité : c'est la seule preuve que votre
> test sait détecter l'absence du comportement.

> **3.** Les cas limites écrits en TDD révèlent les **ambiguïtés du besoin**
> avant la production. C'est le bénéfice principal, et il n'est pas technique.
