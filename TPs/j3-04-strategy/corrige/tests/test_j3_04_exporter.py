"""Tests de l'export.

Section 1 : le filet de sécurité, écrit avant le refactoring — ces tests n'ont
pas bougé. Sections 2 à 4 : ce que la Strategy rend possible.
"""

import json

import pytest
from export.exporter import (
    FORMATS,
    FormatInconnu,
    Tache,
    en_csv,
    en_json,
    en_json_compact,
    en_markdown,
    en_texte,
    exporter,
    exporter_avec,
)

TACHES = [
    Tache("Relire le rapport", "haute"),
    Tache("Déployer", "normale", terminee=True),
    Tache("Ranger le bureau", "basse"),
]

# --- 1. Fixer le comportement actuel -------------------------------------------------------


def test_texte():
    assert exporter(TACHES, "texte") == (
        "3 tâches\n[ ] Relire le rapport (haute)\n[x] Déployer (normale)\n"
        "[ ] Ranger le bureau (basse)\n"
    )


def test_texte_est_le_format_par_defaut():
    assert exporter(TACHES) == exporter(TACHES, "texte")


def test_csv():
    assert exporter(TACHES, "csv") == (
        "titre;priorite;terminee\nRelire le rapport;haute;0\nDéployer;normale;1\n"
        "Ranger le bureau;basse;0\n"
    )


def test_json():
    assert json.loads(exporter(TACHES, "json")) == [
        {"titre": "Relire le rapport", "priorite": "haute", "terminee": False},
        {"titre": "Déployer", "priorite": "normale", "terminee": True},
        {"titre": "Ranger le bureau", "priorite": "basse", "terminee": False},
    ]


def test_json_conserve_les_accents():
    assert "Déployer" in exporter(TACHES, "json")


def test_json_compact():
    assert exporter(TACHES[:1], "json-compact") == (
        '[{"titre":"Relire le rapport","priorite":"haute","terminee":false}]\n'
    )


def test_markdown():
    assert exporter(TACHES, "markdown") == (
        "| Titre | Priorité | Fait |\n|---|---|---|\n"
        "| Relire le rapport | haute |  |\n| Déployer | normale | ✓ |\n"
        "| Ranger le bureau | basse |  |\n"
    )


def test_format_inconnu_liste_les_formats_disponibles():
    with pytest.raises(FormatInconnu, match=r"'xml' — formats disponibles : \['csv', 'json'"):
        exporter(TACHES, "xml")


# --- 2. Tester une stratégie seule, sans passer par le dispatch -----------------------------------


def test_en_texte_directement():
    assert en_texte([Tache("A")]) == "1 tâches\n[ ] A (normale)"


def test_en_csv_directement():
    assert en_csv([]) == "titre;priorite;terminee"


def test_en_json_directement():
    assert en_json([]) == "[]"


def test_en_json_compact_directement():
    assert en_json_compact([Tache("A")]) == '[{"titre":"A","priorite":"normale","terminee":false}]'


def test_en_markdown_directement():
    assert en_markdown([]).splitlines() == ["| Titre | Priorité | Fait |", "|---|---|---|"]


# --- 3. Paramétrer sur le registre : les futurs formats seront couverts automatiquement --------


@pytest.mark.parametrize("format", FORMATS)
def test_tout_format_se_termine_par_un_seul_saut_de_ligne(format):
    sortie = exporter(TACHES, format)
    assert sortie.endswith("\n") and not sortie.endswith("\n\n")


@pytest.mark.parametrize("format", FORMATS)
def test_tout_format_contient_tous_les_titres(format):
    sortie = exporter(TACHES, format)
    assert all(t.titre in sortie for t in TACHES)


@pytest.mark.parametrize("format", FORMATS)
def test_tout_format_accepte_une_liste_vide(format):
    assert isinstance(exporter([], format), str)


@pytest.mark.parametrize("format", FORMATS)
def test_tout_format_est_deterministe(format):
    assert exporter(TACHES, format) == exporter(TACHES, format)


# --- 4. Injecter une stratégie externe : le principe ouvert/fermé, vérifié ---------------------


def test_un_consommateur_peut_fournir_son_propre_format():
    def en_html(taches):
        return "<ul>" + "".join(f"<li>{t.titre}</li>" for t in taches) + "</ul>"

    assert (
        exporter_avec(TACHES[:2], en_html)
        == "<ul><li>Relire le rapport</li><li>Déployer</li></ul>\n"
    )


def test_le_registre_est_extensible_sans_modifier_le_module():
    FORMATS["compte"] = lambda taches: str(len(taches))
    try:
        assert exporter(TACHES, "compte") == "3\n"
    finally:
        del FORMATS["compte"]


# --- 5. Les bornes que le code d'origine ne gérait pas ------------------------------------------


def test_csv_protege_le_separateur_dans_un_titre():
    """Le code de départ produisait « Relire;corriger;normale;0 » : quatre colonnes."""
    sortie = exporter([Tache("Relire;corriger")], "csv")
    assert sortie.splitlines()[1] == '"Relire;corriger";normale;0'


def test_csv_protege_les_guillemets():
    sortie = exporter([Tache('Lire "Python avancé"')], "csv")
    assert sortie.splitlines()[1] == '"Lire ""Python avancé""";normale;0'


def test_markdown_echappe_la_barre_verticale():
    """Le code de départ cassait le tableau : « | A | B | normale |  | »."""
    sortie = exporter([Tache("A | B")], "markdown")
    assert sortie.splitlines()[2] == "| A \\| B | normale |  |"


def test_json_echappe_les_guillemets():
    assert json.loads(exporter([Tache('Lire "Python"')], "json"))[0]["titre"] == 'Lire "Python"'


def test_liste_vide_en_texte():
    assert exporter([], "texte") == "0 tâches\n"
