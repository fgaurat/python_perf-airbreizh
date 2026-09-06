# TP j3-02 — Extraire un Adapter

**Durée : 60 min**

## Contexte

`depart/devises/convertisseur.py` interroge l'API de taux de change d'un
fournisseur pour répondre à trois questions : combien vaut ce montant dans
telle devise, combien vaut-il dans chacune de ces devises, laquelle est la plus
avantageuse.

Regardez les trois méthodes. Elles partagent :

- le **même appel réseau**, recopié trois fois ;
- le **vocabulaire du fournisseur** (`rates`, `base`, `apikey`) mêlé aux
  règles métier ;
- un `except Exception: return 0.0` — donc **une panne réseau est
  indiscernable d'un montant nul**, et une devise inconnue vaut zéro.

Ce dernier point est un bug silencieux en production : si l'API tombe, le
devis annonce 0,00 USD, sans la moindre alerte. Et une faute de frappe dans un
code de devise donne le même résultat.

## Objectif

Extraire un Adapter, rendre le métier testable sans réseau, et faire apparaître
la panne au lieu de la masquer.

## Étapes

### 1. Le modèle métier (10 min)

Créez `devises/modele.py` avec une `@dataclass(frozen=True) Montant` portant
**votre** vocabulaire : `valeur`, `devise`. Validez le code de devise à la
construction (trois lettres majuscules).

Ajoutez une hiérarchie d'exceptions : `ErreurDevises`, et trois filles
`SourceIndisponible`, `DonneesInvalides`, `DeviseInconnue`.

### 2. Le contrat (5 min)

Créez `devises/ports.py` avec un `Protocol` :

```python
class SourceTaux(Protocol):
    def taux(self, base: str) -> dict[str, float]: ...
```

Une seule méthode. C'est le principe ISP : le métier n'a besoin de rien d'autre.

### 3. L'adaptateur (15 min)

Créez `devises/adaptateur_api.py`. Il concentre **tout** ce qui concerne le
fournisseur : l'URL, la clé d'API, le vocabulaire, la traduction.

Rendez le transport injectable :

```python
def __init__(self, cle_api: str, transport: Transport = transport_http):
```

Et remplacez le `except Exception: return 0.0` par des exceptions explicites :
panne réseau d'un côté, réponse mal formée de l'autre (clé `rates` absente,
taux qui n'est pas un nombre, taux nul ou négatif).

### 4. Le métier (10 min)

`Convertisseur` reçoit une `SourceTaux` et n'appelle plus jamais le réseau.
Les trois méthodes deviennent des transformations de dictionnaires. L'arrondi
au centime se fait **à un seul endroit**.

> En les réécrivant, vous rencontrerez une question que le code d'origine ne
> tranchait pas : que renvoie `la_plus_avantageuse` quand **deux devises
> donnent la même valeur** ? Le résultat dépendait de l'ordre de la liste.
> Décidez, et écrivez le test.

### 5. Les fakes (5 min)

Créez `devises/fakes.py` avec deux classes :

- `SourceEnMemoire` — un dictionnaire de taux par devise de base ;
- `SourceEnPanne` — lève systématiquement `SourceIndisponible`.

Ce sont des **fakes**, pas des mocks : ils fonctionnent, on peut les interroger
plusieurs fois. Faites compter les appels à `SourceEnMemoire` : cela permettra
de vérifier que `equivalents` n'interroge la source **qu'une fois**.

### 6. Les tests (15 min)

Trois familles :

| Famille | Double utilisé | Ce qu'on vérifie |
|---|---|---|
| Métier | `SourceEnMemoire` | les règles, l'arrondi, les cas vides, l'égalité |
| Adaptateur | un transport factice (`lambda url: {...}`) | la traduction, l'URL, les réponses mal formées |
| Pannes | `SourceEnPanne` | l'erreur remonte au lieu d'être avalée |

Écrivez en particulier le test qui **distingue** une devise inconnue d'une
panne de la source. C'était impossible avant : les deux donnaient `0.0`.

## Critères de réussite

- `Convertisseur` ne contient plus ni `urllib`, ni `json`, ni URL.
- Le mot `rates` n'apparaît **que** dans `adaptateur_api.py` — écrivez le test
  qui le vérifie.
- Un test vérifie que convertir vers la **même** devise ne consulte pas la source.
- Un test distingue « devise inconnue » de « source en panne ».
- Aucun test du métier n'utilise `Mock`, `patch` ou `monkeypatch`.

## Pour aller plus loin

Le fournisseur annonce une v4 de son API : `rates` devient `data`, chaque taux
devient un objet `{"value": 1.08}`, et le paramètre `base` s'appelle désormais
`base_currency`. Combien de fichiers devez-vous modifier ? Combien de tests
devez-vous réécrire ?

Écrivez `AdaptateurApiTauxV4` et vérifiez que **tous les tests métier passent
sans modification**.

## Corrigé

`corrige/` — 5 modules et 29 tests.

```bash
uv run pytest j3-02-extraire-un-adapter/corrige -v
```
