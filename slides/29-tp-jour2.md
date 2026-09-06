---
marp: true
theme: your-theme
paginate: true
header: "Jour 2 — Travaux pratiques"
---

<!-- _class: lead -->

# Travaux pratiques du Jour 2

*Cinq exercices indépendants — 3 h 45*

---

# Le programme

| TP | Ce que vous allez faire | Durée |
|---|---|---|
| **j2-01** | Construire une suite de tests de zéro sur une todo-list : structure, `conftest.py`, fixtures, jeu de données, erreurs attendues. | 45 min |
| **j2-02** | Transformer 8 tests répétitifs en tests paramétrés, puis couvrir les cas limites et les propriétés des opérations d'une calculatrice — et attraper `round()` en flagrant délit. | 45 min |
| **j2-03** | Tester un carnet d'adresses qui écrit sur disque — `tmp_path`, fixtures composées, sauvegardes tournantes — sans jamais polluer le dépôt. | 45 min |
| **j2-04** | Écrire un convertisseur en chiffres romains **entièrement en TDD**, du premier test rouge aux propriétés invariantes. | 60 min |
| **j2-05** | Reproduire par un test un bug de production (« 26 h » affichées « 2 h »), le corriger, et couvrir toute sa famille. | 30 min |

---

# Le TP central : j2-04

Une seule règle, et elle est stricte :

> **Aucune ligne de code de production ne s'écrit sans un test rouge qui la réclame.**

L'énoncé métier que vous recevrez tient en deux phrases — comme dans la vraie vie.
Le livrable le plus important n'est pas le code : c'est le fichier où vous notez
**les questions que l'écriture des tests fait apparaître** et que l'énoncé ne
tranchait pas.

Il y en a au moins quatre. Nous les comparerons en fin de séance.

---

# Deux conseils pour la séance

> **🎯 Voyez le rouge.** Sur j2-04 et j2-05, ne corrigez jamais avant d'avoir vu
> le test échouer. Un test qui n'a jamais échoué ne prouve rien.

> **🎯 Lisez la liste de vos tests.** À la fin de chaque TP, lancez
> `uv run pytest --collect-only -q`. Si la liste ne se lit pas comme une
> spécification du module, vos noms de tests sont à revoir.

Rappel de mise en place :

```bash
cd TPs
uv sync
uv run pytest j2-01-suite-pytest-de-zero/depart
```

Les corrigés sont dans `corrige/` — à consulter **après** avoir cherché.
