# TP j2-02 — Paramétrisation et cas limites

**Durée : 45 min**

## Contexte

`depart/calcul/operations.py` fournit les opérations d'une calculatrice :
addition, soustraction, multiplication, division, puissance, racine,
pourcentage, arrondi commercial, moyenne. Sa docstring pose un contrat en trois
points, dont : **le résultat est toujours un `float`**, et l'arrondi est
commercial : 2,675 → 2,68.

`depart/tests/test_operations.py` contient huit tests. Ils passent tous :

```bash
uv run pytest j2-02-parametrize-et-cas-limites/depart
```

Regardez-les. Trois tests pour l'addition, nommés `test_additionner_1`, `_2`,
`_3`, tous sur des entiers positifs. Aucun ne couvre la division par zéro, la
racine d'un négatif, la moyenne d'une liste vide — alors que le module déclare
**trois exceptions**. Et aucun ne vérifie ce que la docstring promet.

## Objectif

Transformer cette suite en une suite qui documente le comportement réel, en
utilisant la paramétrisation, et en couvrant les bords.

## Étapes

1. **Fusionner par paramétrisation** (10 min). Les trois `test_additionner_*`
   deviennent un seul test paramétré. Donnez à chaque cas un `id=` lisible :

   ```python
   @pytest.mark.parametrize(
       ("a", "b", "attendu"),
       [
           pytest.param(2, 3, 5, id="petits_entiers"),
           pytest.param(-2, 3, 1, id="un_negatif"),
           pytest.param(0.1, 0.2, 0.3, id="flottants"),
       ],
   )
   def test_additionner(a, b, attendu):
       assert additionner(a, b) == pytest.approx(attendu)
   ```

   Vérifiez le rendu : `uv run pytest ... --collect-only -q`

   > Le cas `flottants` échoue sans `pytest.approx`. Essayez.

2. **Ajouter les cas limites** (10 min). Pour chaque fonction, cherchez :
   **zéro**, les **négatifs**, les **flottants**, les **très grands** et
   **très petits** nombres, l'exposant **nul** ou **négatif**.

   Pour `arrondir`, testez ce que la docstring annonce : `2.5 → 3` et
   `2.675 → 2.68`. **Les deux échouent.** Pourquoi ? Lisez la documentation de
   `round()`, puis corrigez le module (piste : `decimal.Decimal(str(x))` et
   `ROUND_HALF_UP`).

3. **Couvrir les erreurs attendues** (10 min). Le module déclare
   `DivisionParZero`, `HorsDomaine` et `SerieVide`. Écrivez un test par
   exception, avec `match=` sur le message.

   La frontière du domaine de `racine` est zéro : testez `0`, `-1e-9` et `-1`.
   Quelle borne faut-il tester en priorité ?

4. **Écrire des tests de propriété** (10 min). Certains comportements se
   vérifient **sans valeur de référence** :

   ```python
   @pytest.mark.parametrize(("a", "b"), [(2, 3), (-4, 7), (0.1, 0.2)])
   def test_l_addition_est_commutative(a, b):
       assert additionner(a, b) == additionner(b, a)
   ```

   Trouvez-en trois autres. Pistes : que donne `multiplier(diviser(a, b), b)` ?
   `puissance(racine(x), 2)` ? Arrondir deux fois ? La moyenne peut-elle sortir
   de `[min, max]` ?

5. **Vérifier le contrat de type** (5 min). La docstring dit : *le résultat est
   toujours un `float`*. Écrivez le test paramétré sur les neuf fonctions, avec
   `type(resultat) is float`. Que renvoie `additionner(2, 3)` ? Corrigez le
   module.

## Critères de réussite

- Plus aucun test nommé `test_xxx_1`, `_2`, `_3`.
- Les trois exceptions du module sont couvertes, message compris.
- Au moins trois tests de propriété, sans valeur de référence en dur.
- Tous les flottants sont comparés avec `pytest.approx`.
- `arrondir(2.5, 0) == 3.0` et `type(additionner(2, 3)) is float` sont verts.
- `uv run pytest ... --collect-only -q` se lit comme une spécification.

## Pour aller plus loin

Que renvoie `puissance(-8, 1 / 3)` ? Tapez-le dans un interpréteur. Ce n'est
pas un `float`, et ce n'est pas une exception non plus. Décidez de ce que le
module **devrait** faire, écrivez le test, corrigez.

## Corrigé

`corrige/` — les 8 tests de départ sont devenus **94 cas** répartis sur
23 fonctions de test. Le module corrigé règle les trois écarts au contrat
(arrondi, type de retour, puissance complexe).

```bash
uv run pytest j2-02-parametrize-et-cas-limites/corrige -v
```
