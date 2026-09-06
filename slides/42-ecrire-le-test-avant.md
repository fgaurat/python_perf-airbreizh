---
marp: true
theme: your-theme
paginate: true
header: "Jour 4 — Écrire le test avant le code"
---

<!-- _class: lead -->

# 2. Écrire le test avant le code

*Six règles pour que le test reste utile dans deux ans*

---

# 1. Partir du comportement, pas de la fonction

<div class="cols">
<div>

**Partir du code** ❌

*« Je dois écrire une méthode
`calculer_majoration` dans la classe
`Tarif`. »*

Le test suit la structure imaginée.
Si la structure change, il casse.

</div>
<div>

**Partir du comportement** ✓

*« Au-delà de 8 heures, les heures
supplémentaires sont majorées. »*

Le test énonce la règle. La structure
qui la porte peut évoluer librement.

</div>
</div>

Formulation qui marche bien, en trois temps :

```
Étant donné   un colis de 35 kg
Quand         on calcule les frais en mode standard
Alors         la majoration de surpoids s'applique
```

→ `def test_surpoids_majore_les_frais_en_standard():`

---

# 2. Commencer par le cas le plus simple

Le premier test ne doit pas être le plus représentatif. Il doit être **celui
qui vous fait écrire le moins de code**.

| Ordre | Test | Ce qu'il force à décider |
|---|---|---|
| 1 | `repartir(100, [1, 1]) == [50, 50]` | le nom, les paramètres, l'unité, le type de retour |
| 2 | `repartir(100, [3, 1]) == [75, 25]` | la proportionnalité |
| 3 | `repartir(100, [1, 1, 1])` | **la règle d'arrondi** — le vrai sujet |
| 4 | `repartir(0, [1, 1])` | le cas dégénéré |
| 5 | `repartir(100, [])` | l'erreur métier |

> Commencer par le cas 3 est tentant, puisque c'est le difficile. C'est aussi le
> meilleur moyen de mélanger quatre décisions et de ne plus savoir laquelle a
> causé l'échec.

---

# 3. Faire émerger l'interface, ne pas la décréter

Le test est le **premier code appelant**. Ce qui est pénible à écrire dans un
test sera pénible pour vos consommateurs.

<div class="cols">
<div>

**Ce que le test révèle**

```python
def test_frais():
    frais = calculer(
        2.0, 100.0, True, False, "std", None, 3
    )
```

Sept paramètres, dont trois booléens
et un `None`. Personne ne relira cet
appel.

</div>
<div>

**Ce que le test suggère**

```python
def test_frais():
    frais = frais_livraison(
        Colis(poids_kg=2.0, distance_km=100.0),
        mode="standard",
    )
```

</div>
</div>

> **🎯 En pratique** : quand un appel devient pénible à écrire dans un test,
> ne cherchez pas à rendre le test plus court. **Changez la signature.**

---

# 4. Ajouter les cas limites un par un

Pas cinq d'un coup. Un seul, en rouge, puis vert, puis le suivant.

```python
def test_serie_vide():          # rouge → implémentation → vert
    with pytest.raises(SerieVide):
        mediane([])
```

À chaque cas limite ajouté, posez-vous la question :

> **Est-ce que ce cas est possible chez le consommateur ?**

| Cas | Verdict |
|---|---|
| Liste vide | oui — une journée sans aucune vente |
| Valeur négative | oui — un avoir, un remboursement |
| Liste d'un milliard d'éléments | non — inutile de le gérer |
| Chaîne au lieu d'un nombre | selon vos consommateurs : à décider explicitement |

Ajouter des cas impossibles produit du code défensif que personne n'exécutera —
et qui restera non testé en pratique.

---

# 5. Garder les tests lisibles

Un test se lit **cent fois** et s'écrit une fois. C'est le seul code où
l'optimisation pour la lecture prime sur tout le reste.

<div class="cols">
<div>

**Compact mais opaque** ❌

```python
@pytest.mark.parametrize("d", DATA)
def test_all(d):
    r = process(**d["in"])
    for k, v in d["exp"].items():
        assert getattr(r, k) == v
```

Un échec affiche `d = {...}`.
Bon courage.

</div>
<div>

**Explicite** ✓

```python
def test_surpoids_majore_de_12_euros():
    frais = standard(Colis(35.0, 100.0))
    assert frais == pytest.approx(31.15)
```

Un échec affiche la règle, l'entrée
et l'écart.

</div>
</div>

Trois règles concrètes : **pas de boucle**, **pas de `if`**, **pas d'héritage
de test** — sauf pour un test de contrat, où c'est justement le but.

---

# 6. Ne pas tester les détails d'implémentation

| Ce qu'on teste | Verdict |
|---|---|
| La valeur retournée | ✓ toujours |
| L'exception levée et son message | ✓ toujours |
| L'état observable après l'appel | ✓ si public |
| Un effet hors du système (envoi, écriture) | ✓ avec un mock ou un spy |
| Un attribut préfixé `_` | ✗ |
| L'ordre des appels internes | ✗ sauf si l'ordre **est** la règle |
| Le nombre d'itérations d'une boucle | ✗ |
| Le type concret d'un objet interne | ✗ |

> **Le test décisif** : *si je réécris entièrement l'intérieur de cette fonction
> en gardant le même contrat, mon test doit-il rester vert ?*
> Si non, il teste l'implémentation.

---

# À retenir

> **1.** Le test énonce un **comportement**, pas une structure. C'est ce qui lui
> permet de survivre au refactoring qu'il est censé protéger.

> **2.** Le test est votre premier consommateur : ce qui est pénible à écrire
> dans un test doit être corrigé dans la **signature**, pas dans le test.

> **3.** Un cas limite ne mérite un test que s'il peut réellement se produire
> chez vos consommateurs.
