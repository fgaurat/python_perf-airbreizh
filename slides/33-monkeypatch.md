---
marp: true
theme: your-theme
paginate: true
header: "Jour 3 — Monkeypatch avec pytest"
---

<!-- _class: lead -->

# 3. Monkeypatch avec pytest

*La fixture native, et quand la préférer à `patch`*

---

# `monkeypatch` : modifier, et défaire automatiquement

C'est une fixture native de pytest. Toute modification est **annulée à la fin du
test**, y compris s'il échoue.

```python
def test_titre_du_rapport(monkeypatch):
    monkeypatch.setattr(rapport, "aujourdhui", lambda: date(2026, 1, 5))
    assert titre() == "Rapport du 2026-01-05"
```

| Méthode | Usage |
|---|---|
| `setattr(objet, "nom", valeur)` | remplacer un attribut ou une fonction |
| `delattr(objet, "nom")` | simuler l'absence d'un attribut |
| `setitem(dict, clé, valeur)` | modifier une entrée de dictionnaire |
| `delitem(dict, clé)` | simuler une clé manquante |
| `setenv` / `delenv` | variables d'environnement |
| `chdir(chemin)` | changer de répertoire courant |
| `syspath_prepend(chemin)` | ajouter un chemin d'import |

---

# Variables d'environnement

C'est l'usage le plus fréquent, et celui où `monkeypatch` est nettement le plus
pratique que `patch`.

```python
def test_configuration_par_defaut(monkeypatch):
    monkeypatch.delenv("MESURES_API_URL", raising=False)
    assert url_api() == "https://api.interne/v1"


def test_url_surchargee(monkeypatch):
    monkeypatch.setenv("MESURES_API_URL", "http://localhost:8000")
    assert url_api() == "http://localhost:8000"


def test_url_invalide_est_refusee(monkeypatch):
    monkeypatch.setenv("MESURES_API_URL", "pas-une-url")
    with pytest.raises(ConfigurationInvalide):
        url_api()
```

> `raising=False` évite l'erreur quand la variable n'était pas définie —
> indispensable pour que le test passe aussi bien sur votre poste qu'en CI.

---

# Remplacer une fonction ou une méthode

<div class="cols">
<div>

**Une fonction de module**

```python
def test_sans_reseau(monkeypatch):
    def faux_get(url, timeout=None):
        return Reponse({"mesures": [12.4]})

    monkeypatch.setattr(
        "mesures.api.requests.get", faux_get
    )
    assert recuperer("35A") == [12.4]
```

</div>
<div>

**Une méthode de classe**

```python
def test_lecture_figee(monkeypatch):
    monkeypatch.setattr(
        SourceAPI, "lire",
        lambda self, jour: [Mesure(8, 12.4)],
    )
    assert Analyse(SourceAPI()).moyenne(JOUR) == 12.4
```

</div>
</div>

> **⚠️ Piège** : la règle du chapitre 2 s'applique à l'identique —
> `monkeypatch.setattr` cible **là où l'objet est utilisé**. `monkeypatch` ne
> résout pas ce problème, il le partage.

---

# Simuler l'absence d'une dépendance

Cas réel : votre librairie doit fonctionner même quand un paquet optionnel n'est
pas installé.

```python
def test_repli_quand_le_paquet_optionnel_est_absent(monkeypatch):
    monkeypatch.setitem(sys.modules, "accelerateur", None)

    resultat = calculer_rapide([1, 2, 3])

    assert resultat == [1, 4, 9]        # même résultat, chemin lent
```

Et pour vérifier qu'une clé de configuration manquante est bien signalée :

```python
def test_cle_manquante(monkeypatch):
    monkeypatch.delitem(CONFIG, "seuil", raising=False)
    with pytest.raises(SeuilNonConfigure):
        appliquer_seuil(12.4)
```

Ces deux situations arrivent en production et ne se testent pas autrement.

---

# `chdir` et `syspath_prepend`

```python
def test_chemin_relatif(monkeypatch, tmp_path):
    (tmp_path / "config.json").write_text('{"seuil": 10}')
    monkeypatch.chdir(tmp_path)

    assert charger_config_locale()["seuil"] == 10
```

`chdir` est restauré automatiquement — contrairement à un `os.chdir` manuel, qui
laisserait tous les tests suivants dans le mauvais répertoire.

> **🎯 En pratique** : `monkeypatch.chdir` est la bonne réponse à du code
> existant qui utilise des chemins relatifs. La bonne réponse à long terme est
> de faire du chemin un **paramètre** de la fonction.

---

# `patch` ou `monkeypatch` ?

| | `unittest.mock.patch` | `monkeypatch` |
|---|---|---|
| Origine | bibliothèque standard | fixture pytest |
| Portée | bloc `with` ou décorateur | le test entier |
| Restauration | fin du bloc | fin du test, automatique |
| Crée un `Mock` | **oui**, par défaut | non — vous fournissez la valeur |
| Vérifie les appels | oui (`assert_called_*`) | non |
| Variables d'environnement | `patch.dict(os.environ, …)` | `setenv` / `delenv` |
| Vérification d'interface | `create_autospec` | aucune |

**La règle de choix, en une ligne :**

> Vous voulez **vérifier un appel** → `patch` (avec `create_autospec`).
> Vous voulez **remplacer une valeur** → `monkeypatch`.

Et dans les deux cas : si la dépendance peut être **injectée**, ni l'un ni l'autre.

---

# Les trois niveaux, sur le même besoin

Tester une fonction qui lit une URL dans l'environnement et appelle un service :

<div class="cols">
<div>

**1. `monkeypatch` — code existant**

```python
def test_recuperer(monkeypatch):
    monkeypatch.setenv("API_URL", "http://x")
    monkeypatch.setattr(
        "mesures.api.requests.get", faux_get
    )
    assert recuperer("35A") == [12.4]
```

**2. `patch` + autospec — vérifier l'appel**

```python
def test_appel_unique():
    client = create_autospec(ClientHTTP)
    recuperer("35A", client=client)
    client.get.assert_called_once()
```

</div>
<div>

**3. Injection — aucun outil**

```python
class ClientFactice:
    def get(self, url):
        return {"mesures": [12.4]}


def test_recuperer():
    assert recuperer(
        "35A",
        client=ClientFactice(),
        url_base="http://x",
    ) == [12.4]
```

Lisible, rapide, sans chaîne magique.

</div>
</div>

C'est le chemin que suit le chapitre suivant : rendre le niveau 3 possible.

---

# À retenir

> **1.** `monkeypatch` est la fixture pytest pour **remplacer une valeur** :
> variables d'environnement, attributs, entrées de dictionnaire, répertoire
> courant. Tout est restauré automatiquement.

> **2.** `patch` reste préférable quand vous voulez **vérifier un appel**, avec
> `create_autospec` pour rester fidèle à l'interface réelle.

> **3.** Les deux souffrent du même défaut : ils dépendent d'un **chemin en
> chaîne de caractères** que rien ne vérifie. Une dépendance injectée n'en a
> pas besoin.
