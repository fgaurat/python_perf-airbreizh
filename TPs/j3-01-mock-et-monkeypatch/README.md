# TP j3-01 — `monkeypatch`, `patch`, ou injection ?

**Durée : 45 min**

## Contexte

`depart/todo/service.py` interroge le service todo interne pour lister les
tâches en retard d'un projet :

```python
def taches_en_retard(projet: str) -> list[str]:
    charge = get(f"{url_base()}/projets/{projet}/taches")  # ← appel réseau
    return interpreter(charge, aujourd_hui())
```

Trois dépendances, **aucune injectée** :

1. `url_base()` lit la variable d'environnement `TODO_API_URL` ;
2. `get` est importé depuis `todo.transport` et appelé directement ;
3. `aujourd_hui()` demande la date à l'horloge de la machine.

Aucun test. En l'état, tester « quelles tâches sont en retard » exige un
service qui répond **et** de lancer le test à la bonne date.

## Objectif

Écrire **le même comportement testé de trois façons**, puis comparer. C'est la
comparaison qui est le livrable, pas les tests.

## Étapes

### 1. Le noyau pur, d'abord (10 min)

Avant tout double de test, regardez `interpreter`. Elle est **pure** : elle
prend un dictionnaire et une date, elle rend une liste de titres.

Écrivez ses tests — la règle du retard, le tri, la borne (une échéance **au
jour même** n'est pas en retard), et **six façons** dont le service peut
renvoyer n'importe quoi (clé absente, réponse qui n'est pas un objet, tâche
qui n'est pas un objet, tâche sans échéance, échéance illisible, échéance qui
n'est pas du texte).

> Six cas d'erreur réseau testés sans une ligne de mock. Retenez la proportion :
> c'est ce que « séparer le métier des I/O » veut dire concrètement.

### 2. Version 1 — `monkeypatch` (10 min)

```python
def test_v1_taches_en_retard(monkeypatch):
    monkeypatch.setenv("TODO_API_URL", "http://x")
    monkeypatch.setattr(service, "get", lambda url: CHARGE_VALIDE)
    monkeypatch.setattr(service, "aujourd_hui", lambda: JOUR)
    assert service.taches_en_retard("site-web") == [...]
```

Testez aussi `url_base` : valeur par défaut, surcharge, URL invalide.

> **Attention** : `monkeypatch.setattr("todo.transport.get", ...)` ne
> fonctionne **pas**. Pourquoi ? Regardez comment `service.py` importe `get`.
> C'est le piège n°2 du chapitre 2. Écrivez le test qui le prouve.

> **Pourquoi `aujourd_hui()` existe-t-il ?** Essayez
> `monkeypatch.setattr(date, "today", ...)` : `date` est un type écrit en C,
> ses attributs sont en lecture seule. La petite fonction d'indirection est là
> pour ça — et c'est déjà une forme d'injection déguisée.

### 3. Version 2 — `patch` + `create_autospec` (10 min)

Écrivez les tests qui vérifient une **interaction** :

- une panne réseau est traduite en `ServiceIndisponible` ;
- la cause d'origine est conservée (`__cause__`) ;
- il n'y a **qu'un seul** appel réseau par projet, avec la bonne URL.

Puis vérifiez ce que `create_autospec` apporte : appelez le transport avec
quatre arguments. Que se passe-t-il avec `Mock()` ? avec `create_autospec(get)` ?

### 4. Version 3 — l'injection (10 min)

Écrivez `todo/service_injecte.py` : les trois dépendances deviennent des
**paramètres avec des valeurs par défaut**, de sorte que le comportement en
production est inchangé.

```python
def taches_en_retard(projet, transport=get_reel, url=None, horloge=date.today): ...
```

Réécrivez les tests. Comptez les lignes.

### 5. Comparaison (5 min)

Remplissez ce tableau :

| | v1 `monkeypatch` | v2 `patch` | v3 injection |
|---|---|---|---|
| Lignes par test | | | |
| Chaînes de caractères magiques | | | |
| Casse si on renomme `get` | | | |
| Casse si on réorganise les modules | | | |
| Lisible sans connaître le module | | | |

## Critères de réussite

- `interpreter` est testée sans aucun double.
- Vous savez expliquer pourquoi `monkeypatch.setattr("todo.transport.get", …)`
  échoue là où `monkeypatch.setattr(service, "get", …)` fonctionne.
- La version 3 ne contient **ni `patch`, ni `monkeypatch`, ni chaîne de module**.
- `service_injecte.taches_en_retard("site-web")` fonctionne toujours en
  production, sans argument supplémentaire.

## Discussion (5 min)

La version 3 est plus courte et plus robuste. Pourquoi ne pas l'appliquer
partout, tout de suite ?

> Piste : que se passe-t-il pour les **appelants existants** de
> `taches_en_retard` ? Et si la fonction avait sept dépendances au lieu de
> trois ? À quel moment l'injection par paramètre doit-elle céder la place à
> l'injection par constructeur ?

## Corrigé

`corrige/` — 23 tests, les trois versions côte à côte dans un seul fichier.

```bash
uv run pytest j3-01-mock-et-monkeypatch/corrige -v
```
