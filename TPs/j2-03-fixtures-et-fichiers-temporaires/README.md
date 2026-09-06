# TP j2-03 — Fixtures et fichiers temporaires

**Durée : 45 min**

## Contexte

`depart/carnet/stockage.py` gère un carnet d'adresses au format JSON :
lecture, écriture, ajout d'un contact avec e-mail unique, **sauvegarde
tournante** (`carnet.json` → `.1` → `.2` → …) et **purge** des copies les plus
anciennes.

Tout y touche au système de fichiers. C'est exactement le genre de module qu'on
renonce à tester — et exactement celui où les bugs coûtent cher : une rotation
ratée, et on écrase la seule bonne copie du carnet.

Il n'a aucun test.

## Objectif

Écrire une suite complète **sans jamais écrire hors d'un dossier temporaire**,
en factorisant la préparation dans des fixtures.

## Étapes

1. **Le premier test avec `tmp_path`** (5 min).

   ```python
   def test_ecrire_puis_lire(tmp_path):
       chemin = tmp_path / "carnet.json"
       contacts = [Contact("Ada Lovelace", "ada@exemple.org")]
       ecrire(chemin, contacts)
       assert lire(chemin) == contacts
   ```

   `tmp_path` est un dossier vide, **unique à ce test**, supprimé ensuite.

2. **Extraire les fixtures** (10 min). Écrivez trois tests de plus, et vous
   aurez recopié quatre fois les deux mêmes lignes. Créez
   `depart/tests/conftest.py` avec :

   - `carnet` — le chemin, construit à partir de `tmp_path`, fichier pas encore
     créé ;
   - `contacts` — un jeu de trois contacts, dont un sans téléphone ;
   - `carnet_rempli` — **composée** des deux précédentes, déjà écrite sur disque.

   > Une fixture peut en demander une autre. C'est ce qui évite d'écrire une
   > seule grosse fixture qui prépare tout.

3. **Les cas limites de lecture** (10 min). Que se passe-t-il pour :
   un fichier absent ? un fichier vide ? une liste vide ? un JSON invalide ?
   un JSON valide qui n'est pas une liste ? un contact sans `email` ?

   Trois de ces six situations doivent lever `FichierCorrompu`. Pour le JSON
   invalide, le message contient le **numéro de ligne** ; pour le contact
   incomplet, sa **position** dans la liste. Vérifiez-le avec `match=`.

4. **La rotation** (10 min). Écrivez une fixture `sauvegardes_numerotees` qui
   fabrique un carnet accompagné de `.1`, `.2` et `.3`, puis testez la cascade :
   après `sauvegarder`, `.3` doit être devenu `.4`, et `.1` doit être une copie
   exacte du carnet courant.

   > Comment vérifier qu'une copie est bien celle qu'on croit ? Écrivez des
   > contenus différents dans chacune.

5. **La purge** (5 min). Paramétrez sur la valeur de `garder` : combien de
   copies restent pour `garder = 0, 1, 2, 3, 5` ?

   Vérifiez aussi que le carnet **courant** n'est jamais supprimé, même avec
   `garder=0`.

6. **Prouver l'isolation** (5 min). Écrivez un test qui vérifie que son propre
   `tmp_path` est vide — alors que les tests précédents ont écrit des carnets.

## Critères de réussite

- `uv run pytest j2-03-fixtures-et-fichiers-temporaires/depart` est vert.
- Aucun fichier n'est créé ailleurs que dans `tmp_path` — après exécution,
  `git status` doit être propre.
- Au moins une fixture est **composée** d'une autre.
- La suite passe deux fois de suite sans nettoyage manuel, et dans le désordre.

## Pour aller plus loin

`lire` sur un fichier **absent** retourne `[]`, et `lire` sur un carnet
**vide** retourne aussi `[]`. Deux situations différentes, un résultat
identique. Est-ce le comportement souhaitable pour une librairie partagée ?
Écrivez le test qui documente la situation actuelle — puis discutez de ce qu'il
faudrait changer.

Autre piste : `sauvegardes` trie-t-il `carnet.json.10` après `carnet.json.2` ?
Un tri alphabétique dirait le contraire.

## Corrigé

`corrige/` — 4 fixtures et 32 tests.

```bash
uv run pytest j2-03-fixtures-et-fichiers-temporaires/corrige -v
uv run pytest j2-03-fixtures-et-fichiers-temporaires/corrige --fixtures | head -30
```
