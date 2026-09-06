# TP j1-02 — Extraire une fonction pure, isoler les I/O

**Durée : 45 min**

## Contexte

`depart/salutations.py` affiche le message d'accueil de la console interne :
« Bonjour fgaurat ! », « Good evening, ada. Welcome. », avec un « Bon week-end ! »
le vendredi. Il lit la langue et le registre dans `config.json`, prend le nom de
l'utilisateur système et l'heure courante, écrit une ligne dans un journal, et
affiche le résultat.

Tout tient dans une fonction de 30 lignes. Elle marche. C'est un *hello world*.

L'équipe vous annonce trois évolutions :

1. une troisième langue, l'espagnol ;
2. une sortie JSON pour l'interface web, en plus du texte ;
3. la correction d'un doute : « Bonsoir » devrait commencer à 18 h, pas 19 h.

Aucune des trois ne peut être menée en confiance aujourd'hui : il n'existe
**aucun moyen de vérifier le message produit sans changer l'heure de la
machine, le nom de l'utilisateur ou le contenu de `config.json`**.

## Objectif

Séparer les trois couches — calcul, I/O, orchestration — et écrire les tests
du calcul. Sans changer un seul message.

## Étapes

1. **Fixer le comportement actuel** (5 min). Lancez le module tel quel :

   ```bash
   cd depart && python salutations.py
   ```

   Notez le message affiché et la ligne écrite dans `accueil.log`. C'est votre
   référence : ils devront être identiques à la fin.

2. **Extraire la première fonction pure** (10 min).
   `moment_de_la_journee(heure: int) -> Moment`, où `Moment` est un `Enum` à
   trois valeurs. Écrivez-la, puis appelez-la depuis le code existant.

   > Regardez au passage `HEURE_SOIR` dans le code de départ, et comparez avec
   > le commentaire qui l'accompagne. Il y a un écart d'une heure. Combien de
   > temps aurait-il fallu pour le repérer sans lire cette ligne ?

3. **Extraire le calcul** (15 min). Faites émerger :

   - `formuler(nom, moment, langue, formel, veille_de_weekend) -> str` —
     construit le message, et rien d'autre ;
   - `Config`, une `@dataclass(frozen=True)` avec des valeurs par défaut,
     plutôt qu'un dictionnaire dont on fait des `.get(...)` un peu partout.

   `formuler` ne doit connaître ni `datetime`, ni `getpass`, ni `json`.

4. **Isoler les I/O** (10 min). Il doit rester :

   - `lire_config(chemin) -> Config` — lit, et rien d'autre ;
   - `journaliser(chemin, ...)` — écrit une ligne, et rien d'autre ;
   - `saluer(...) -> str` — orchestre les précédentes en quatre ou cinq
     lignes, et **retourne** le texte au lieu de l'afficher. Le `print` remonte
     dans le `if __name__ == "__main__"`.

5. **Tester** (5 min). Écrivez au moins trois tests dans
   `depart/test_salutations.py` :

   ```python
   def test_les_bornes_du_soir():
       assert moment_de_la_journee(17) is Moment.JOUR
       assert moment_de_la_journee(18) is Moment.SOIR
   ```

   Relancez `python salutations.py` : le message et la ligne de journal de
   l'étape 1 doivent être inchangés.

   > Ils le sont — **alors même que vous avez corrigé le bug de l'étape 2**.
   > À moins que vous ne fassiez ce TP entre 18 h et 19 h, aucune exécution ne
   > peut révéler l'écart. Un test de bout en bout lancé par la CI toutes les
   > nuits serait resté vert pendant des années. C'est très exactement
   > l'argument en faveur des tests unitaires ciblés.

## Critères de réussite

- `moment_de_la_journee` et `formuler` **n'appellent ni `datetime.now`, ni
  `getpass`, ni `open`**.
- Vos tests du calcul s'exécutent sans créer le moindre fichier et sans
  `monkeypatch`.
- Le message et la ligne de journal de l'étape 1 sont identiques.
- `saluer` tient en cinq lignes ou moins.

## Pour aller plus loin

Que se passe-t-il aujourd'hui si `config.json` contient `"langue": "es"` ?
Un `KeyError` sur une ligne au milieu de `saluer`, sans indication de ce qui
était attendu. Faites de `formuler` une fonction qui refuse explicitement une
langue inconnue, avec un message qui liste les langues disponibles — c'est le
sujet du TP suivant.

## Corrigé

`corrige/` — module découpé et 26 tests.

```bash
uv run pytest j1-02-decoupage-responsabilites/corrige
```
