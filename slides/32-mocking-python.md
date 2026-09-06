---
marp: true
theme: your-theme
paginate: true
header: "Jour 3 — Mocking en Python"
---

<!-- _class: lead -->

# 2. Mocking en Python

*`unittest.mock`, et la règle qui évite 80 % des erreurs*

---

# `Mock` : un objet qui accepte tout

```python
from unittest.mock import Mock

source = Mock()
source.lire(projet="site-web")
source.n_importe_quoi.encore_autre_chose()      # ne lève rien
```

Un `Mock` crée ses attributs et méthodes **à la demande**, et enregistre tous
les appels.

```python
source.lire.return_value = [Tache("Déployer")]  # ce qu'il renverra
source.lire.assert_called_once_with(projet="site-web")
```

| | |
|---|---|
| `Mock` | attributs et méthodes à la demande |
| `MagicMock` | idem, **plus** les méthodes spéciales (`__len__`, `__iter__`, `__enter__`…) |

> `MagicMock` est nécessaire dès que le code fait `len(obj)`, `for x in obj`,
> ou `with obj:`. En cas de doute, `MagicMock` — c'est le défaut de `patch`.

---

# Valeurs de retour et effets de bord

<div class="cols">
<div>

**`return_value`** — toujours la même

```python
client = Mock()
client.get.return_value = {"statut": "ok"}

client.get("/a")    # {'statut': 'ok'}
client.get("/b")    # {'statut': 'ok'}
```

**`side_effect` = liste** — une par appel

```python
client.get.side_effect = [
    {"page": 1},
    {"page": 2},
    StopIteration,
]
```

</div>
<div>

**`side_effect` = exception** — simuler une panne

```python
client.get.side_effect = TimeoutError(
    "délai dépassé"
)

with pytest.raises(ServiceIndisponible):
    recuperer_taches(client)
```

**`side_effect` = fonction** — réponse calculée

```python
def repondre(chemin):
    if chemin.startswith("/projets"):
        return {"taches": []}
    raise KeyError(chemin)

client.get.side_effect = repondre
```

</div>
</div>

---

# Vérifier les appels

```python
notif = Mock()
rappeler(taches_en_retard, notif)
```

| Assertion | Vérifie |
|---|---|
| `notif.envoyer.assert_called()` | au moins un appel |
| `notif.envoyer.assert_called_once()` | exactement un appel |
| `notif.envoyer.assert_called_with("Déployer")` | le **dernier** appel |
| `notif.envoyer.assert_called_once_with("Déployer")` | un seul appel, avec ces arguments |
| `notif.envoyer.assert_any_call("Déployer")` | au moins un appel avec ces arguments |
| `notif.envoyer.assert_not_called()` | aucun appel |

Et pour les cas plus fins :

```python
assert notif.envoyer.call_count == 2
assert notif.envoyer.call_args.args == ("Déployer",)
assert notif.envoyer.call_args_list == [call("Relire"), call("Déployer")]
```

---

<!-- _class: dense -->

# ⚠️ Le piège n°1 : un `Mock` nu accepte tout

Python protège les fautes de frappe sur les assertions — `assert_calle_once()`
lève bien une `AttributeError` depuis la 3.5. Le vrai danger est ailleurs :

```python
notif = Mock()
notif.envoyerr("Déployer")                   # méthode qui n'existe pas
notif.envoyer("a", "b", "c", 42)             # signature fantaisiste
notif.envoyerr.assert_called_once_with("Déployer")  # ✓ vert
```

Ces trois lignes passent. Conséquence concrète : le jour où quelqu'un renomme
`envoyer` en `notifier` dans le code de production, **vos tests restent verts**.

| Objet | Méthode inexistante | Mauvaise signature |
|---|---|---|
| `Mock()` | acceptée | acceptée |
| `Mock(spec=Notificateur)` | `AttributeError` | acceptée |
| `create_autospec(Notificateur)` | `AttributeError` | **`TypeError`** |

> **🎯 En pratique** : `create_autospec` par défaut. C'est le seul qui vérifie
> aussi les signatures — donc le seul qui rougit quand l'interface réelle change.

---

# `patch` : remplacer temporairement

Quand la dépendance n'est **pas injectée**, il faut la remplacer là où elle vit.

<div class="cols">
<div>

**Gestionnaire de contexte**

```python
def test_appel_reseau():
    with patch("todo.api.requests.get") as get:
        get.return_value.json.return_value = {"v": 1}
        assert recuperer() == 1
```

**Décorateur**

```python
@patch("todo.api.requests.get")
def test_appel_reseau(get):
    get.return_value.json.return_value = {"v": 1}
    assert recuperer() == 1
```

</div>
<div>

**`patch.object`** — plus sûr

```python
def test_appel_reseau():
    with patch.object(api, "recuperer") as r:
        r.return_value = 1
        ...
```

Pas de chaîne de caractères : une
faute de frappe devient une erreur
d'attribut immédiate.

</div>
</div>

Le décorateur injecte le mock **en premier paramètre**. Avec plusieurs `@patch`,
l'ordre est **de bas en haut**.

---

# ⚠️ Le piège n°2 : patcher là où c'est **utilisé**

C'est l'erreur la plus fréquente, et la plus déroutante.

```python
# todo/api.py
from requests import get          # ← import direct

def recuperer(url):
    return get(url).json()
```

<div class="cols">
<div>

**Ne marche pas** ❌

```python
patch("requests.get")
```

`todo.api` détient déjà **sa propre
référence** vers la fonction. Remplacer
l'attribut du module `requests`
ne change rien pour lui.

</div>
<div>

**Marche** ✓

```python
patch("todo.api.get")
```

On remplace la référence **là où elle
est consultée**.

</div>
</div>

> **La règle** : on patche le chemin par lequel le code **cherche** l'objet au
> moment de l'appel, pas celui où l'objet est défini.

---

# Le corollaire de la règle

Le style d'import détermine le chemin à patcher :

| Dans le module testé | À patcher |
|---|---|
| `from requests import get` | `mon_module.get` |
| `import requests` puis `requests.get(...)` | `mon_module.requests.get` ou `requests.get` |
| `from .client import Client` puis `Client()` | `mon_module.Client` |

> **🎯 En pratique** : préférer `import requests` puis `requests.get(...)` rend
> le code **plus facile à patcher**, parce que la résolution se fait à l'appel.

Et surtout : une dépendance **injectée** ne demande aucun patch.

```python
def recuperer(url, client=requests):    # ← paramètre avec défaut
    return client.get(url).json()

def test_recuperer():
    assert recuperer("/x", client=ClientFactice()) == 1
```

---

# Mocker une méthode, une propriété, un module

<div class="cols">
<div>

**Une méthode d'instance**

```python
with patch.object(Rapport, "charger") as c:
    c.return_value = [Tache("A"), Tache("B")]
    Rapport().avancement()
```

**Une propriété**

```python
from unittest.mock import PropertyMock

with patch.object(
    Tache, "est_en_retard", new_callable=PropertyMock
) as en_retard:
    en_retard.return_value = True
    ...
```

</div>
<div>

**Une constante de module**

```python
with patch("todo.rappels.SEUIL_JOURS", 3):
    assert doit_rappeler(retard_jours=5)
```

**Un module entier absent**

```python
import sys
with patch.dict(sys.modules, {"lib_proprio": Mock()}):
    import mon_module
```

</div>
</div>

> **⚠️ Piège** : `patch.object(Classe, "methode")` remplace la méthode pour
> **toutes** les instances, pendant toute la durée du bloc. Préférez patcher
> l'instance quand c'est possible.

---

# Simuler une panne externe

C'est l'usage le plus rentable du mocking : produire à la demande une erreur
qu'on ne sait pas provoquer autrement.

```python
def test_un_timeout_est_traduit_en_erreur_metier():
    client = create_autospec(ClientHTTP)
    client.get.side_effect = TimeoutError("délai dépassé")

    with pytest.raises(ServiceIndisponible, match="délai"):
        recuperer_taches(client, projet="site-web")


def test_une_reponse_incomplete_est_signalee():
    client = create_autospec(ClientHTTP)
    client.get.return_value = {"projet": "site-web"}   # clé « taches » absente

    with pytest.raises(ReponseInvalide):
        recuperer_taches(client, projet="site-web")
```

Ces deux cas se produiront en production. Sans double de test, ils ne seront
jamais vérifiés — et c'est précisément là que le code est le plus fragile.

---

# Mocker l'horloge et l'aléatoire

Deux dépendances invisibles, sources de tests instables.

<div class="cols">
<div>

**Par patch** — fonctionne partout

```python
with patch("todo.rapport.datetime") as dt:
    dt.now.return_value = datetime(2026, 1, 5)
    assert titre_rapport() == "Rapport 2026-01-05"
```

Fragile : dépend du style d'import.

</div>
<div>

**Par injection** — préférable

```python
def titre_rapport(horloge=datetime.now) -> str:
    return f"Rapport {horloge():%Y-%m-%d}"


def test_titre():
    fige = lambda: datetime(2026, 1, 5)
    assert titre_rapport(fige) == "Rapport 2026-01-05"
```

Aucun patch, aucune chaîne de
caractères, aucun effet global.

</div>
</div>

> Le même raisonnement vaut pour `random`, `uuid4`, `time.time` et les variables
> d'environnement : ce sont des **entrées** du système, pas des détails internes.

---

# Récapitulatif : quel outil pour quoi

| Besoin | Outil |
|---|---|
| Une réponse figée | `Mock(return_value=…)` ou une classe stub de 3 lignes |
| Des réponses successives | `side_effect=[…]` |
| Simuler une panne | `side_effect=Exception(…)` |
| Vérifier qu'un envoi a eu lieu | `assert_called_once_with` |
| Vérifier qu'un envoi **n'a pas** eu lieu | `assert_not_called` |
| Rester fidèle à l'interface réelle | `create_autospec` |
| Remplacer une dépendance non injectée | `patch("module_qui_utilise.nom")` |
| Remplacer une dépendance injectée | **rien** — passez un fake en paramètre |

---

# À retenir

> **1.** `create_autospec` par défaut : sans lui, un mock accepte des méthodes
> et des signatures qui n'existent pas — et vos tests survivent au renommage
> qu'ils auraient dû détecter.

> **2.** On patche **là où l'objet est utilisé**, pas là où il est défini. Le
> style d'import du module testé détermine le chemin.

> **3.** Le meilleur `patch` est celui qu'on n'écrit pas : une dépendance
> injectée se remplace par un paramètre.
