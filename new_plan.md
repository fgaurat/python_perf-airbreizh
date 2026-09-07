# Formation Python avancé : qualité logicielle, TDD, design patterns et CI/CD

**Public concerné**
Ingénieurs, développeurs, profils scientifiques et techniques développant ou maintenant des librairies Python internes.
Cette formation s’adresse particulièrement à des équipes produisant des packages Python orientés objet, utilisés par plusieurs projets ou plusieurs codes métier, avec un enjeu de fiabilité, de maintenabilité et de non-régression.
**Prérequis**
Les participants doivent disposer d’une pratique régulière de Python.
Ils doivent connaître les bases du langage : fonctions, classes, modules, packages, environnements virtuels et usage courant de Git.
Une première expérience de GitLab est souhaitable. La formation ne reviendra pas sur les bases de Git, des commits ou des branches, sauf lorsque cela est nécessaire pour comprendre l’intégration des tests dans le workflow de développement.
**Durée**
5 jours, soit 35 heures.
**Objectifs pédagogiques**
À l’issue de la formation, les participants seront capables de :
concevoir des librairies Python plus testables et maintenables ;
identifier les parties du code qui doivent être testées en priorité ;
écrire des tests unitaires et des tests de non-régression avec pytest ;
utiliser les fixtures, la paramétrisation et les doubles de test ;
comprendre quand utiliser un mock, un stub, un fake ou un monkeypatch ;
refactoriser progressivement du code existant sans casser le comportement métier ;
réduire les dépendances fortes et les dépendances circulaires entre classes ou modules ;
appliquer certains principes SOLID de manière pragmatique en Python ;
utiliser les design patterns comme outils de découplage et de testabilité ;
mettre en place une démarche TDD réaliste, adaptée à des projets scientifiques ;
intégrer l’exécution des tests dans une pipeline GitLab CI/CD ;
produire des rapports de tests exploitables lors des fusions de branches.
**Positionnement de la formation**
Cette formation n’est pas une formation généraliste Python perfectionnement.
Elle est orientée développement logiciel professionnel en Python, avec un fil conducteur : rendre des librairies Python internes plus robustes, plus testables et plus faciles à faire évoluer.
La formation adopte une logique guidée par les tests : les tests ne sont pas seulement abordés comme un outil de vérification en fin de développement, mais comme un moyen d’analyser le besoin, de clarifier les comportements attendus, de sécuriser les évolutions et de guider progressivement la conception du code.
La formation alterne rappels conceptuels, démonstrations, exercices courts et refactoring progressif d’un mini-projet inspiré de problématiques réelles : préparation de fichiers, calculs métier, accès à des sources externes, dépendances entre packages, évolution du code sans régression.

**Programme détaillé**

## Jour 1 — Qualité du code Python, architecture testable et rappels POO utiles
Objectifs de la journée
Poser les bases d’une architecture Python testable.
Revoir uniquement les notions de POO utiles pour la suite.
Comprendre pourquoi certains codes sont difficiles à tester.
Introduire le TDD comme démarche d’analyse et de conception.
Présenter les design patterns comme outils de conception orientée objet.
Identifier les dépendances fortes, les responsabilités mélangées et les points de fragilité.

### 1. Qualité logicielle appliquée aux librairies Python
Différence entre script, notebook, module et librairie réutilisable.
Problèmes classiques dans les librairies internes :
code difficile à comprendre ;
effets de bord ;
fonctions ou méthodes trop longues ;
dépendances implicites ;
erreurs silencieuses ;
absence de contrat clair ;
modifications qui cassent d’autres codes.
Définir ce que l’on veut sécuriser :
comportement métier ;
format de données ;
calculs ;
compatibilité entre packages ;
intégration avec des sources externes.

### 2. Introduction à une démarche guidée par les tests
Pourquoi parler des tests dès la conception du code.
Différence entre tester après coup et développer avec une intention de testabilité.
Le TDD comme outil d’analyse du comportement attendu.
Présentation du cycle Red / Green / Refactor.
Lien entre TDD, qualité du code, refactoring et non-régression.
Cas où le TDD est pertinent dans une librairie Python métier.
Cas où une approche plus souple que le TDD strict est préférable.

### 3. Rappels POO Python orientés testabilité
Classes, objets et responsabilités.
Agrégation et composition.
Couplage entre objets.
Encapsulation pragmatique en Python.
Interfaces implicites et duck typing.
Classes abstraites et protocoles : quand les utiliser, quand les éviter.
Exceptions métier et gestion explicite des erreurs.

### 4. Introduction aux design patterns comme outils de conception
Pourquoi les design patterns ne sont pas des recettes à appliquer systématiquement.
Les design patterns comme réponses à des problèmes récurrents de conception objet.
Lien entre design patterns, responsabilités, couplage et dépendances.
Différence entre connaître un pattern et reconnaître le problème qu’il résout.
Exemples de problèmes rencontrés dans des librairies Python :
création d’objets complexe ;
dépendance à une source externe ;
choix d’un algorithme selon le contexte ;
code difficile à tester car trop couplé ;
workflow métier difficile à faire évoluer.
Présentation rapide des patterns qui seront réutilisés dans la formation :
Adapter ;
Strategy ;
Factory ;
Repository ;
Facade ;
Dependency Injection ;
Template Method.

### 5. Identifier le code difficile à tester
Méthodes trop longues.
Mélange entre calcul, accès aux données et écriture de fichiers.
Dépendances circulaires.
Accès directs à des ressources externes.
Utilisation excessive de variables globales.
Objets qui construisent eux-mêmes toutes leurs dépendances.
Fonctions qui font plusieurs choses à la fois.

### 6. Principes SOLID utiles en Python
Single Responsibility Principle : découper sans sur-architecturer.
Open/Closed Principle : permettre l’évolution sans casser l’existant.
Dependency Inversion : injecter les dépendances pour faciliter les tests.
Interface Segregation : éviter les objets trop gros.
Limites d’une application trop rigide des principes SOLID en Python.
Travaux pratiques
Analyse d’un code Python volontairement difficile à tester.
Identification des responsabilités mélangées.
Repérage des dépendances circulaires ou implicites.
Premier découpage en composants plus simples.
Ajout d’exceptions explicites pour remplacer certains comportements silencieux.
Discussion sur la manière dont les tests et les design patterns peuvent guider l’amélioration du code.

## Jour 2 — Tests unitaires avec pytest, stratégie de test et premiers cycles TDD
Objectifs de la journée
Savoir écrire des tests unitaires utiles avec pytest.
Comprendre quoi tester et quoi ne pas tester.
Structurer les tests d’une librairie Python.
Mettre en pratique les premiers cycles Red / Green / Refactor.
Utiliser les tests comme support de conception et de sécurisation du code.

### 1. Rôle des tests dans une librairie partagée
Pourquoi tester une librairie interne.
Différence entre bug visible, bug silencieux et régression.
Tests unitaires, tests d’intégration, tests fonctionnels : périmètre et usage.
Tester le comportement plutôt que l’implémentation.
Cas limites, entrées invalides et erreurs attendues.
La notion de contrat logiciel.

### 2. Prioriser ce qui doit être testé
Fonctions critiques métier.
Calculs sensibles.
Transformations de données.
Formats d’entrée et de sortie.
Règles de validation.
Bugs déjà rencontrés.
Parties utilisées par plusieurs packages.
Ce qu’il est inutile ou peu rentable de tester :
getters simples ;
détails internes instables ;
duplication de tests ;
tests trop liés à l’implémentation.

### 3. Organisation d’un projet de tests
Structure recommandée d’un package Python.
Dossier tests.
Convention de nommage.
Séparation entre tests unitaires et tests d’intégration.
Données de test.
Tests lisibles et maintenables.
Arrange / Act / Assert.
Notion de fixture de test.

### 4. Pytest en pratique
Écriture de tests simples.
Assertions.
Test des exceptions.
Fixtures.
Fixtures partagées.
Paramétrisation des tests.
Tests sur fichiers temporaires.
Tests de cas limites.
Marqueurs de tests.
Exécution ciblée de tests.
Bonnes pratiques d’écriture.

### 5. Premiers cycles TDD avec pytest
Écrire un test avant le code.
Décrire un comportement attendu sous forme de test.
Observer l’échec initial du test.
Implémenter le minimum de code nécessaire.
Refactoriser sans modifier le comportement.
Ajouter progressivement des cas limites.
Utiliser le TDD pour clarifier l’interface d’une fonction ou d’une classe.
Savoir quand appliquer le TDD strictement et quand adopter une démarche plus pragmatique.

### 6. Tests de non-régression
Transformer un bug trouvé en test.
Capturer un comportement attendu.
Stabiliser progressivement une base de code existante.
Construire un filet de sécurité avant refactoring.
Tests de caractérisation sur code legacy.

### Travaux pratiques
Mise en place d’une suite de tests pytest.
Écriture de tests unitaires sur fonctions métier.
Paramétrisation de cas de calcul.
Test des erreurs attendues.
Réalisation d’un premier cycle Red / Green / Refactor sur une fonction métier simple.
Ajout progressif de cas limites à partir de tests.
Discussion sur l’évolution de l’interface produite par les tests.
Ajout d’un test de non-régression après correction d’un bug.
Structuration du dossier de tests.

## Jour 3 — Mocking, dépendances externes et application des design patterns à la testabilité

### Objectifs de la journée
Objectifs de la journée
Comprendre le rôle du mocking.
Tester du code dépendant de bases de données, fichiers, services ou flux externes.
Réduire le couplage entre classes.
Appliquer certains design patterns pour améliorer la testabilité.

### 1. Comprendre les doubles de test
Dummy, stub, fake, mock et spy.
Différence entre vérifier un résultat et vérifier une interaction.
Quand utiliser un mock.
Quand éviter les mocks.
Risques des tests trop mockés.
Tester les frontières du système.

### 2. Mocking en Python
unittest.mock.
Mock et MagicMock.
patch.
Vérification des appels.
Valeurs de retour.
Effets de bord.
Simulation d’exceptions.
Mocks de fonctions, classes, modules et objets.
Mocking de méthodes et de propriétés.
Mocking hors classes : fonctions, appels réseau, variables d’environnement.

### 3. Monkeypatch avec pytest
Modifier temporairement une fonction.
Modifier une variable d’environnement.
Remplacer un attribut.
Simuler un module ou une dépendance.
Tester sans accéder réellement à une base de données ou à un service externe.
Comparaison entre patch et monkeypatch.

### 4. Tester les accès externes
Bases de données.
Fichiers.
APIs.
Flux externes.
Données IGN ou autres sources distantes.
Stratégies possibles :
adapter ;
repository ;
service ;
fake en mémoire ;
fichier de test ;
injection de dépendance ;
séparation entre logique métier et I/O.

### 5. Application des design patterns à la testabilité
Utiliser Adapter pour isoler une API, une base de données ou une source externe.
Utiliser Strategy pour rendre un algorithme interchangeable et testable.
Utiliser Factory pour centraliser la création d’objets.
Utiliser Repository pour isoler l’accès aux données.
Utiliser Facade pour simplifier l’accès à un sous-système complexe.
Utiliser l’injection de dépendance pour remplacer une dépendance réelle par un fake ou un mock.
Utiliser Template Method pour structurer un workflow métier.
Identifier les cas où un design pattern améliore réellement le code.
Identifier les cas où un design pattern ajoute de la complexité inutile.

### 6. Design patterns, SOLID et mocking
Comment un pattern peut faciliter les tests.
Comment un pattern peut compliquer inutilement le code.
Choisir un pattern pour résoudre un problème concret.
Éviter le sur-design.
Relier design patterns, SOLID et mocking.
Comprendre comment une meilleure conception réduit le besoin de mocks complexes.

### Travaux pratiques
Refactoring d’un composant dépendant d’une source externe.
Extraction d’un adapter.
Injection d’une dépendance.
Écriture de tests avec fake ou mock.
Simulation d’une erreur externe.
Test d’une classe sans connexion réelle à la source externe.
Application d’un pattern Strategy ou Repository sur un cas simple.
Suppression progressive d’une dépendance circulaire.


### Jour 4 — TDD avancé, refactoring sécurisé et code legacy

### Objectifs de la journée
Approfondir le TDD sur du code existant.
Appliquer le TDD sans dogmatisme.
Refactoriser du code existant sous protection des tests.
Découper progressivement des méthodes longues.
Utiliser les design patterns comme outils de refactoring lorsque cela est pertinent.

### 1. Approfondir le TDD sur du code existant
Rappel du cycle Red / Green / Refactor.
Utiliser le TDD pour ajouter une fonctionnalité à une base existante.
Utiliser les tests de caractérisation avant de modifier du code legacy.
Transformer un bug en test de non-régression.
Sécuriser un refactoring avec une suite de tests.
Identifier les zones où le TDD est difficile à appliquer directement.
Adapter la démarche TDD à des calculs scientifiques, traitements de données ou workflows complexes.
Combiner tests unitaires, tests de non-régression et tests d’intégration.

### 2. Écrire un test avant le code
Définir un comportement attendu.
Commencer par un cas simple.
Ajouter progressivement les cas limites.
Faire émerger l’interface.
Garder les tests lisibles.
Ne pas tester les détails d’implémentation.

### 3. Refactoring sécurisé
Pourquoi refactoriser.
Différence entre refactoring et réécriture.
Préserver le comportement.
Refactoring sous couverture de tests.
Petits pas.
Extraction de fonctions.
Extraction de classes.
Réduction de paramètres.
Suppression de duplication.
Clarification des erreurs.
Réduction des effets de bord.
Introduire progressivement un design pattern pendant un refactoring lorsque cela permet de réduire le couplage, d’isoler une dépendance ou de rendre un composant plus testable.

### 4. Traiter les méthodes longues
Méthodes de 100, 300 ou 600 lignes : pourquoi c’est un problème.
Identifier les blocs cohérents.
Séparer calcul, validation, accès aux données et écriture.
Extraire des fonctions pures.
Introduire des objets de configuration.
Ajouter des tests de caractérisation avant transformation.
Vérifier la non-régression après chaque étape.

### 5. Dépendances circulaires et architecture
Causes fréquentes des dépendances circulaires.
Modules trop gros.
Classes qui se connaissent mutuellement.
Imports croisés.
Objets métier et services mélangés.
Techniques de résolution :
extraction d’interface ;
inversion de dépendance ;
module commun ;
événements simples ;
services applicatifs ;
passage explicite des dépendances.

### 6. Stratégie de reprise d’une base existante
Cartographier les zones critiques.
Ajouter des tests là où le risque est fort.
Prioriser les bugs silencieux.
Construire progressivement une couverture utile.
Ne pas viser 100 % de couverture sans discernement.
Mettre en place une politique réaliste d’amélioration continue.

### Travaux pratiques
Écriture d’un test avant ajout d’une fonctionnalité.
Implémentation minimale.
Refactoring après passage du test.
Mise sous test d’une méthode longue.
Extraction progressive de fonctions.
Ajout d’un test de non-régression.
Introduction d’un design pattern simple pour réduire le couplage.
Réduction d’une dépendance circulaire dans un mini-package.

## Jour 5 — CI/CD GitLab, qualité automatisée et synthèse projet

### Objectifs de la journée
Intégrer les tests dans GitLab CI/CD.
Automatiser les contrôles à chaque branche ou merge request.
Produire des rapports exploitables.

### 1. Rôle de la CI/CD dans la qualité logicielle
Pourquoi automatiser les tests.
Détection précoce des régressions.
Validation avant fusion de branches.
Différence entre test local et test en pipeline.
Politique d’équipe : quand la pipeline doit bloquer.
Gestion des tests rapides et des tests lents.

### 2. GitLab CI/CD pour un projet Python
Structure d’un fichier .gitlab-ci.yml.
Image Docker Python.
Installation des dépendances.
Environnement virtuel ou installation isolée.
Lancement de pytest.
Organisation en stages :
installation ;
qualité ;
tests ;
rapport ;
packaging éventuel.
Cache des dépendances.
Artifacts.
Variables d’environnement.

### 3. Rapports de tests
Publication du rapport dans GitLab.
Lecture des résultats dans la pipeline.
Exploitation dans les merge requests.
Conservation des artifacts.
Différence entre logs bruts et rapport structuré.

### 4. Contrôles complémentaires
formatage avec black ou ruff format ;
linting avec ruff ;
typage statique avec mypy ;
mesure de couverture avec pytest-cov ;
rapport de couverture ;
seuil minimal de couverture ;
choix d’indicateurs utiles plutôt que métriques artificielles.

### 5. Tests et workflow d’équipe
Quand écrire un test.
Comment ajouter un test lors d’une correction de bug.
Comment relire une merge request orientée qualité.
Comment éviter de casser une librairie utilisée par d’autres packages.
Politique de non-régression.
Documentation minimale des tests.
Standards d’équipe.

### Travaux pratiques
Création d’un fichier .gitlab-ci.yml.
Exécution automatique de pytest.
Génération d’un rapport JUnit.
Ajout éventuel d’un rapport de couverture.
Simulation d’une merge request avec test cassé.
Correction et validation.
Bilan des bonnes pratiques applicables aux librairies internes.

