# TP j2-05 — Transformer un bug en test de non-régression

**Durée : 30 min**

## Contexte

`depart/temps/durees.py` formate des durées en secondes sous une forme lisible
(`3725 → "1 h 02 min 05 s"`) et sait relire cette forme. C'est ce module qui
alimente la colonne « Durée » du **tableau de bord des traitements par lots**.

Il a huit tests. Ils passent tous :

```bash
uv run pytest j2-05-test-de-non-regression/depart
```

## Le ticket

> **Bug #2291 — Le job `consolidation` est affiché en 2 h 15 min**
>
> Le job nocturne `consolidation` a tourné 26 h 15 min la nuit du 12. Le
> tableau de bord affichait « 2 h 15 min ». Il a fallu trois semaines pour
> comprendre pourquoi les traitements du matin démarraient en retard : la
> colonne Durée n'a jamais montré le dépassement.
>
> Aucune erreur dans les journaux. Aucun message.
>
> Reproduit à la main :
> ```python
> >>> formater(94500)
> '2 h 15 min'
> ```

Trois semaines de retards inexpliqués, un tableau de bord vert. C'est un bug
silencieux typique — et les huit tests existants passaient pendant tout ce temps.

## Objectif

Reproduire, corriger, et **empêcher le retour** — pas seulement de ce bug, mais
de toute sa famille.

## Étapes

1. **Reproduire avant de corriger** (5 min). Écrivez le test qui échoue,
   dans `depart/tests/test_durees.py` :

   ```python
   def test_26_heures_ne_deviennent_pas_2_heures():
       """Bug #2291 — les heures repassaient à zéro toutes les 24 h."""
       assert formater(94500) == "26 h 15 min"
   ```

   Lancez-le. **Vous devez le voir rouge.** S'il passe, vous n'avez pas
   reproduit le bug signalé.

2. **Diagnostiquer** (5 min). Lisez `formater`. Que fait `time.gmtime` d'un
   nombre de secondes ? Quel est le plus grand `tm_hour` possible ?

   > Indice : `gmtime` répond à la question « quelle heure est-il, tant de
   > secondes après le 1er janvier 1970 ? ». Ce n'est pas la question posée.

3. **Corriger au minimum** (5 min). Faites passer votre test, sans casser les
   huit tests d'origine. Deux `divmod` suffisent.

4. **Élargir à la famille** (10 min). Le bug n'est pas « 26 h ». C'est « **tout
   ce qui atteint 24 h** ». Paramétrez :

   | Cas | Pourquoi |
   |---|---|
   | `86400` | exactement un jour — la frontière |
   | `86401` | un jour et une seconde |
   | `172800` | deux jours : le bug donnait `0 s` |
   | `360000` | cent heures — trois chiffres |

   Puis écrivez la **propriété** qui aurait attrapé le bug dès le départ :
   `analyser(formater(n)) == n`, paramétrée sur une dizaine de valeurs de part
   et d'autre de 86 400.

5. **Le bug qu'on découvre en élargissant** (5 min). En écrivant les cas
   voisins, testez `formater(-1)`.

   Que renvoie le code de départ ? Que **devrait**-il renvoyer ? Vous venez de
   trouver un second bug silencieux, que personne n'avait signalé. Décidez du
   comportement, écrivez le test, corrigez.

## Critères de réussite

- Le test de non-régression a été **vu rouge** avant la correction.
- Les huit tests d'origine passent toujours, **sans avoir été modifiés**.
- Le test porte le numéro du ticket dans sa docstring.
- Au moins six cas couvrent la famille du bug, dont la frontière exacte.
- Le second bug (`formater(-1)`) est identifié et couvert.

## Discussion (5 min)

Pourquoi les huit tests existants ne détectaient-ils rien ? Regardez leurs
données : `0`, `5`, `65`, `3600`, `3725`, `86399`.

**Toutes sont inférieures à 86 400.** Le dernier cas, « presque un jour »,
donne même l'impression que la frontière a été pensée — elle ne l'a jamais été
franchie. La suite était verte, la couverture excellente, et le bug en
production. C'est l'illustration la plus directe du chapitre 2 : une couverture
élevée ne dit rien de la qualité des **cas** choisis.

## Corrigé

`corrige/` — 56 cas de test.

```bash
uv run pytest j2-05-test-de-non-regression/corrige -v
```
