# TP j3-04 — Remplacer une cascade de `if` par une Strategy

**Durée : 45 min**

## Contexte

`depart/export/exporter.py` exporte la todo-list. Une seule fonction, quatre
formats, une cascade de `if` — et son histoire est lisible dans le code :

> le format texte au départ, puis CSV pour le tableur du service, puis JSON
> pour l'interface web, puis Markdown pour le wiki, puis les options `entete`
> et `compact` réclamées par deux équipes.

À chaque nouveau format, quelqu'un a rouvert la fonction. Et à chaque
réouverture, il a pu casser les formats existants sans s'en apercevoir.

Deux formats de plus sont annoncés pour le trimestre : HTML pour l'intranet,
et iCal pour les échéances.

## Objectif

Rendre chaque format indépendant, testable seul, et faire en sorte que
`exporter` **n'ait plus jamais à être rouverte**.

## Étapes

### 1. Fixer le comportement actuel (10 min)

Avant tout refactoring, un filet de sécurité. Écrivez au moins huit tests
couvrant les quatre formats, les deux options et le format inconnu.

> Écrivez la sortie attendue **à la main**, puis vérifiez avec le code. Pour le
> JSON, comparez avec `json.loads` plutôt qu'avec la chaîne brute : l'indentation
> n'est pas ce que vous voulez figer.

### 2. Une fonction par format (10 min)

Extrayez `en_texte`, `en_csv`, `en_json`, `en_markdown`. Chacune prend une
`list[Tache]` et retourne une `str`. Décidez d'une convention et tenez-la :
**sans** saut de ligne final, il sera ajouté à un seul endroit.

Nommez le type au passage :

```python
Formateur = Callable[[list[Tache]], str]
```

Que deviennent les drapeaux `entete` et `compact` ? Un drapeau booléen qui
change la sortie est une stratégie qui ne dit pas son nom : `compact` devient
`en_json_compact`, une entrée de plus dans le registre. Quant à `entete=False`,
regardez qui l'utilise vraiment.

### 3. Le registre (5 min)

```python
FORMATS: dict[str, Formateur] = {
    "texte": en_texte,
    "csv": en_csv,
    "json": en_json,
    "json-compact": en_json_compact,
    "markdown": en_markdown,
}


def exporter(taches: list[Tache], format: str = "texte") -> str:
    try:
        formateur = FORMATS[format]
    except KeyError:
        raise FormatInconnu(f"{format!r} — formats disponibles : {sorted(FORMATS)}") from None
    return exporter_avec(taches, formateur)
```

Remplacez le `ValueError` par une exception métier dérivée d'une racine
commune : un format inconnu n'est pas une erreur de programmation, c'est une
demande qu'on ne sait pas servir.

### 4. Les tests qui deviennent possibles (10 min)

Trois choses que vous ne pouviez pas faire avant :

**Tester une stratégie seule**, sans passer par le dispatch :

```python
def test_en_csv_directement():
    assert en_csv([]) == "titre;priorite;terminee"
```

**Paramétrer sur le registre** — les futurs formats seront couverts automatiquement :

```python
@pytest.mark.parametrize("format", FORMATS)
def test_tout_format_se_termine_par_un_seul_saut_de_ligne(format):
    sortie = exporter(TACHES, format)
    assert sortie.endswith("\n") and not sortie.endswith("\n\n")
```

**Injecter une stratégie externe** — le principe ouvert/fermé, vérifié :

```python
def test_un_consommateur_peut_fournir_son_propre_format():
    def en_html(taches):
        return "<ul>" + "".join(f"<li>{t.titre}</li>" for t in taches) + "</ul>"

    assert exporter_avec(TACHES, en_html) == "<ul>...</ul>\n"
```

### 5. Les bornes (10 min)

Que produit le code d'origine pour un titre contenant un `;` en CSV ? Un `|`
en Markdown ? Des guillemets en JSON ? Écrivez les trois tests, puis corrigez
les stratégies concernées — le module `csv` de la bibliothèque standard fait
le travail pour le premier cas.

## Critères de réussite

- `exporter` tient en cinq lignes et ne contient plus aucun `elif`.
- Chaque format est testé **sans passer par** `exporter`.
- Au moins un test est paramétré sur `FORMATS`.
- Un test prouve qu'un consommateur peut ajouter un format sans modifier le module.
- Un titre contenant `;` produit un CSV à trois colonnes.

## Discussion (5 min)

Nous avons utilisé des **fonctions**, pas des classes. Quand faudrait-il passer
à des classes ?

> Pistes : si une stratégie avait besoin d'une **configuration** (le séparateur
> CSV, le niveau d'indentation JSON), ou de **plusieurs méthodes** (`formater`
> et `extension_de_fichier`). Tant qu'une fonction suffit, elle est plus simple
> à écrire, à lire et à tester.

## Corrigé

`corrige/` — 40 tests.

```bash
uv run pytest j3-04-strategy/corrige -v
```
