---
marp: true
theme: your-theme
paginate: true
header: "Jour 4 — Travaux pratiques"
---

<!-- _class: lead -->

# Travaux pratiques du Jour 4

*Quatre exercices indépendants — 4 h 15*

---

# Le programme

| TP | Ce que vous allez faire | Durée |
|---|---|---|
| **j4-01** | Ajouter un historique avec annulation à une calculatrice de 115 lignes **en TDD**, par bourgeon — sans réécrire le moteur. | 60 min |
| **j4-02** | Mettre sous test un générateur de bulletin scolaire de 190 lignes par un test d'équivalence, puis l'extraire bloc par bloc. Le TP le plus long, et le plus proche du quotidien. | 90 min |
| **j4-03** | Faire émerger Strategy, injection et Factory dans un module de rappels par une suite de petites transformations, chacune validée par les tests. | 60 min |
| **j4-04** | Diagnostiquer et casser le cycle `taches ↔ projets ↔ affichage` d'une todo-list, puis verrouiller l'architecture avec `import-linter`. | 45 min |

---

# La discipline de la journée

> **Tests verts → une transformation → tests verts → commit.**

Sur les TPs 02 et 03, engagez-vous vraiment à committer à chaque étape. Vous
mesurerez la différence quand une transformation tournera mal — et il y en aura
une.

> **🎯 Si vous êtes rouge depuis plus de 10 minutes**, ne cherchez pas la
> cause : revenez au dernier commit et recommencez avec un pas plus petit.
> C'est contre-intuitif, et c'est plus rapide.

Sur `j4-02`, résistez à la tentation de corriger les bugs que vous allez trouver.
Notez-les dans un fichier `BUGS.md` — nous en discuterons en fin de séance.
Un refactoring qui corrige des bugs en même temps n'est plus vérifiable.
