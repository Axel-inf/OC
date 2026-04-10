# Historique d'Utilisation de l'IA Générative

Ce document liste toutes les utilisations d'IA générative détectées dans le projet, selon les consignes du cours.

Dernière mise à jour du registre : 10.04.2026

## Format de documentation
Chaque utilisation d'IA générative est documentée directement dans le code source avec le format suivant :
```python
# Aide IA: [Description courte]
# Contexte: [Fichier et ligne mentionnés ici]
```

---

## Résumé des utilisations

### 1. Exécution multi-plateforme (__mp_main__)
- **Fichier** : [run.py](run.py)
- **Ligne** : 4
- **Date** : 15.01.2026
- **Description** : Aide de l'IA concernant le `__mp_main__` pour garantir la compatibilité multi-plateforme lors du lancement avec debugger
- **Détail** : Gère les environnements de debugging cross-platform (Windows, Linux, Mac)

---

### 2. Modèles de données et historisation
- **Fichier** : [app/database/models.py](app/database/models.py)
- **Ligne** : 48
- **Date** : 26.02.2026
- **Description** : Aide IA pour historisation des changements de classe d'un élève
- **Détail** : Table `EleveChangementClasse` permet de tracer les modifications de classe avec date

- **Fichier** : [app/database/models.py](app/database/models.py)
- **Ligne** : 142
- **Date** : 23.02.2026
- **Description** : Aide IA pour métadonnées d'examen pour affichage élève/professeur
- **Détail** : Champs d'examen pour affichage contextualisé selon le rôle utilisateur

---

### 3. Gestion de base de données
- **Fichier** : [app/database/database.py](app/database/database.py)
- **Ligne** : 16
- **Date** : 26.02.2026
- **Description** : Aide IA pour migrations légères de colonnes sans outil externe de migration
- **Détail** : Fonction `_ensure_calendar_event_columns()` ajoute dynamiquement les colonnes manquantes

---

### 4. Backend FastAPI - Sécurité et APIs
- **Fichier** : [app/main.py](app/main.py)
- **Ligne** : 1
- **Date** : 19.02.2026
- **Description** : Aide de l'IA (document global)

- **Fichier** : [app/main.py](app/main.py)
- **Ligne** : 79
- **Date** : 26.02.2026
- **Description** : Aide IA pour sécurisation de la suppression via identité de session
- **Détail** : Vérification que l'utilisateur supprime uniquement ses propres événements (pas d'identifiant client)

- **Fichier** : [app/main.py](app/main.py)
- **Ligne** : 121
- **Date** : 26.02.2026
- **Description** : Aide IA pour sécurisation de la mise à jour du temps passé via identité de session
- **Détail** : Validation serveur du temps passé avec authentification de session

---

### 5. Calendrier - Synchronisation et données
- **Fichier** : [app/database/calendar_repository.py](app/database/calendar_repository.py)
- **Ligne** : 82
- **Date** : 26.02.2026
- **Description** : Aide IA pour synchronisation automatique des événements liés lors d'un changement de classe
- **Détail** : Mise à jour automatique des événements quand un élève change de classe

- **Fichier** : [app/database/calendar_repository.py](app/database/calendar_repository.py)
- **Ligne** : 379
- **Date** : 23.02.2026
- **Description** : Aide IA pour extension des événements calendrier avec classe cible + métadonnées d'examen
- **Détail** : Enrichissement des données calendrier pour affichage détaillé

- **Fichier** : [app/database/calendar_repository.py](app/database/calendar_repository.py)
- **Ligne** : 551
- **Date** : 26.02.2026
- **Description** : Aide IA pour propagation des modifications vers événements liés (élèves)
- **Détail** : Synchronisation bidirectionnelle prof ↔ élèves

---

### 6. Pages Frontend - Calendrier
- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 1
- **Date** : 18.01.2026
- **Description** : Aide de l'IA (document global)

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 148
- **Date** : 23.02.2026
- **Description** : Aide IA pour normalisation des événements avec champs supplémentaires
- **Détail** : Extension avec classe, examen et lien source pour affichage unifié

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 431
- **Date** : 19.02.2026
- **Description** : Aide IA pour appel API sans identifiant utilisateur côté client
- **Détail** : Suppression pilotée côté serveur avec contrôle d'autorisation

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 469
- **Date** : 19.02.2026
- **Description** : Aide IA pour suppression pilotée serveur avec contrôle d'autorisation

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 647
- **Date** : 23.02.2026
- **Description** : Aide IA pour affichage prof (classe, branche, moyenne élève, méta examen)
- **Détail** : Affichage contextualisé des événements selon le rôle et les permissions

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 701
- **Date** : 26.02.2026
- **Description** : Aide IA pour protections UI élève pour devoirs partagés
- **Détail** : Masquage des boutons supprimer/modifier pour événements partagés

---

### 7. Pages Frontend - Accueil
- **Fichier** : [app/pages/accueil.py](app/pages/accueil.py)
- **Ligne** : 1
- **Date** : 15.01.2026
- **Description** : Aide de l'IA (document global)

---

### 8. Pages Frontend - Partage des devoirs d'élèves
- **Fichier** : [app/pages/formulaire.py](app/pages/formulaire.py)
- **Ligne** : 861+
- **Date** : 01.04.2026
- **Description** : Aide IA pour partage des devoirs d'élèves avec les autres élèves de leur classe
- **Détail** : Quand un élève crée un devoir, celui-ci est automatiquement partagé avec les autres élèves de la même classe via un événement source et des événements liés

---

### 9. Pages Frontend - Propagation des mises à jour
- **Fichier** : [app/pages/formulaire.py](app/pages/formulaire.py)
- **Ligne** : 830
- **Date** : 01.04.2026
- **Description** : Aide IA pour propagation des mises à jour des devoirs d'élèves à tous les élèves de la classe
- **Détail** : Quand un élève modifie un devoir, les modifications sont propagées à tous les autres élèves de sa classe (propagate_to_linked=True)

---

### 10. Enregistrement de l'historique des changements de classe
- **Fichier** : [app/pages/profil_eleve.py](app/pages/profil_eleve.py)
- **Ligne** : 318
- **Date** : 01.04.2026
- **Description** : Aide IA pour enregistrement du changement de classe dans la BD pour traçabilité historique
- **Détail** : Chaque changement de classe d'un élève est enregistré dans la table `EleveChangementClasse` avec date pour une traçabilité complète

---

### 11. Validation stricte du temps passé (heures/minutes)
- **Fichier** : [app/database/calendar_repository.py](app/database/calendar_repository.py)
- **Ligne** : 481
- **Date** : 01.04.2026
- **Description** : Aide IA pour normalisation stricte du temps passé (`normalize_time_spent_strict`)
- **Détail** : Le backend n'accepte plus que les formats `min`, `h`, `h+min` et normalise le stockage

- **Fichier** : [app/main.py](app/main.py)
- **Ligne** : 133
- **Date** : 01.04.2026
- **Description** : Aide IA pour validation API du champ temps passé
- **Détail** : Rejet HTTP 400 des valeurs invalides avant écriture en base

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 397
- **Date** : 01.04.2026
- **Description** : Aide IA pour validation côté client du champ "Temps passé"
- **Détail** : Contrôle du format à la saisie + restauration de la dernière valeur valide

---

### 12. Synchronisation automatique avant affichage calendrier
- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 216
- **Date** : 01.04.2026
- **Description** : Aide IA pour synchroniser les devoirs de classe avant rendu du calendrier élève
- **Détail** : Vérification immédiate des devoirs liés à la classe actuelle à l'ouverture de la page

---

### 13. Règles pédagogiques par année (enseignants/élèves)
- **Fichier** : [app/utils/teacher_assignments.py](app/utils/teacher_assignments.py)
- **Ligne** : 50+
- **Date** : 04.04.2026
- **Description** : Aide IA pour appliquer les branches autorisées selon l'année
- **Détail** : 1ère sans OS/OC, 2ème avec OS, 3ème/4ème avec OS+OC+philosophie selon les règles définies

- **Fichier** : [app/pages/profil_professeur.py](app/pages/profil_professeur.py)
- **Ligne** : 250+
- **Date** : 04.04.2026
- **Description** : Aide IA pour rendre l'UI des branches cohérente avec les règles par classe
- **Détail** : affichage conditionnel OS/OC, validation par classe et correction des faux négatifs de sélection

- **Fichier** : [app/pages/formulaire.py](app/pages/formulaire.py)
- **Ligne** : 374+
- **Date** : 04.04.2026
- **Description** : Aide IA pour restreindre les matières élève selon la classe
- **Détail** : blocage des matières non autorisées côté UI et côté validation serveur

---

### 14. Robustesse des classes (normalisation casse) et propagation transverse
- **Fichier** : [app/pages/profil_professeur.py](app/pages/profil_professeur.py)
- **Ligne** : 33+
- **Date** : 04.04.2026
- **Description** : Aide IA pour normaliser les codes classes (`2gy1`/`2GY1`)
- **Détail** : pré-cochage fiable des classes et stockage cohérent des sélections

- **Fichier** : [app/pages/statistiques.py](app/pages/statistiques.py)
- **Ligne** : 78+
- **Date** : 04.04.2026
- **Description** : Aide IA pour attribution professeur robuste
- **Détail** : matching classes/matières insensible à la casse et suppression du bucket `Non attribué`

- **Fichier** : [app/pages/charge_eleve.py](app/pages/charge_eleve.py)
- **Ligne** : 38+
- **Date** : 04.04.2026
- **Description** : Aide IA pour prise en compte des classes prof mises à jour
- **Détail** : filtrage élèves/classes robuste après modifications du profil enseignant

---

### 15. Persistance de l'état "fait" des devoirs
- **Fichier** : [app/database/models.py](app/database/models.py)
- **Ligne** : 146
- **Date** : 04.04.2026
- **Description** : Aide IA pour ajout du champ `is_done` sur les événements calendrier
- **Détail** : persistance base de données de la coche "devoir fait"

- **Fichier** : [app/database/database.py](app/database/database.py)
- **Ligne** : 29+
- **Date** : 04.04.2026
- **Description** : Aide IA pour migration légère de la colonne `is_done`
- **Détail** : ajout automatique de la colonne si absente

- **Fichier** : [app/main.py](app/main.py)
- **Ligne** : 142+
- **Date** : 04.04.2026
- **Description** : Aide IA pour API de persistance de la coche
- **Détail** : endpoint sécurisé `/api/calendar-events/done`

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 349+
- **Date** : 04.04.2026
- **Description** : Aide IA pour branchement UI ↔ API de l'état "fait"
- **Détail** : restauration de la coche au chargement et sauvegarde au clic

---

### 16. Synchronisation avancée du calendrier lors des changements de profil
- **Fichier** : [app/database/calendar_repository.py](app/database/calendar_repository.py)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour synchronisation fiable des événements liés (classe/options)
- **Détail** : normalisation des classes, dédoublonnage par source, règles OS/OC par niveau, et maintien des événements partagés après redémarrage

- **Fichier** : [app/pages/profil_eleve.py](app/pages/profil_eleve.py)
- **Ligne** : 281+
- **Date** : 04.04.2026
- **Description** : Aide IA pour déclencher la synchronisation aussi sur changement d'options
- **Détail** : synchro non limitée au changement de classe (langues, OS, OC, Basic English)

- **Fichier** : [app/pages/profil_eleve.py](app/pages/profil_eleve.py)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour masquer les options en 1ère année
- **Détail** : section options cachée en 1ère et nettoyage des valeurs OS/OC/flags à la sauvegarde

---

### 17. Ajustements UX et navigation
- **Fichier** : [app/pages/accueil.py](app/pages/accueil.py)
- **Ligne** : 210+
- **Date** : 04.04.2026
- **Description** : Aide IA pour ajouter l'accès calendrier côté enseignant
- **Détail** : carte dédiée vers `/calendrier` sur l'accueil professeur

- **Fichier** : [app/pages/calendrier.py](app/pages/calendrier.py)
- **Ligne** : 30+
- **Date** : 04.04.2026
- **Description** : Aide IA pour clarifier "Classe concernée"
- **Détail** : affichage explicite (classe réelle, ou libellé option par niveau, ou "Classe non définie")

- **Fichier** : [app/pages/profil_professeur.py](app/pages/profil_professeur.py)
- **Ligne** : 430+
- **Date** : 04.04.2026
- **Description** : Aide IA pour retrait d'une classe professeur
- **Détail** : masquage des devoirs source et événements liés des classes retirées

---

### 18. Rédaction et structuration de la documentation Sphinx
- **Fichier** : [docs/source/presentation.md](docs/source/presentation.md)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour reformuler la motivation du projet et préciser la répartition du travail entre Figma, CSS et base de données
- **Détail** : présentation du projet réécrite avec une formulation plus claire et plus adaptée au rendu final

- **Fichier** : [docs/source/manuel.md](docs/source/manuel.md)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour rédiger le manuel utilisateur, les étapes d'installation et les conseils d'utilisation
- **Détail** : parcours utilisateur, commandes d'installation et consignes de consultation de la documentation

- **Fichier** : [docs/source/code.md](docs/source/code.md)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour documenter l'architecture, le point d'entrée, les concepts techniques et les parties complexes du code
- **Détail** : création d'un chapitre technique séparé pour expliquer le fonctionnement du projet

- **Fichier** : [docs/source/critique.md](docs/source/critique.md)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour rédiger le regard critique, les limites et les améliorations possibles
- **Détail** : séparation du bilan, des limites et des pistes d'amélioration dans un chapitre dédié

- **Fichier** : [docs/source/apprentissages.md](docs/source/apprentissages.md)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour créer un chapitre distinct sur ce qui a été appris pendant le projet
- **Détail** : mise en page d'une section finale dédiée aux acquis techniques, conceptuels et de gestion de projet

- **Fichier** : [docs/source/index.rst](docs/source/index.rst)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour organiser la toctree et placer les chapitres dans le bon ordre
- **Détail** : insertion du chapitre apprentissages à la fin et maintien de la structure générale de la documentation

- **Fichier** : [docs/source/conf.py](docs/source/conf.py)
- **Ligne** : 1+
- **Date** : 04.04.2026
- **Description** : Aide IA pour stabiliser l'affichage de la navigation Sphinx
- **Détail** : réglage des options du thème pour garder une table des matières cohérente entre les pages

---

### 19. Mise à jour du registre d'utilisation de l'IA
- **Fichier** : [AI_USAGE.md](AI_USAGE.md)
- **Ligne** : 1+
- **Date** : 05.04.2026
- **Description** : Aide IA pour mise à jour du registre des usages (références, lignes, date de révision)
- **Détail** : harmonisation des entrées existantes avec l'état actuel du code et ajout de la date de mise à jour du document

---

### 20. Références IA et harmonisation du rendu technique dans la documentation
- **Fichier** : [docs/source/online.bib](docs/source/online.bib)
- **Ligne** : fin de fichier
- **Date** : 06.04.2026
- **Description** : Aide IA pour ajouter les références d'outils IA selon le format bibliographique en place
- **Détail** : ajout d'entrées `@online` pour ChatGPT et GitHub Copilot

- **Fichier** : [docs/source/code.md](docs/source/code.md)
- **Ligne** : 1+
- **Date** : 06.04.2026
- **Description** : Aide IA pour uniformiser la mise en évidence des éléments techniques
- **Détail** : mise au format code de noms techniques (`is_done`, endpoints API, chemins `.py`) pour une lecture cohérente

- **Fichier** : [docs/source/critique.md](docs/source/critique.md)
- **Ligne** : 1+
- **Date** : 06.04.2026
- **Description** : Aide IA pour clarifier les limites, solutions et risques d'usage abusif
- **Détail** : reformulation des objectifs non finalisés et ajout de contre-mesures côté sécurité

---

### 21. Mise à jour du registre avec cette conversation
- **Fichier** : [AI_USAGE.md](AI_USAGE.md)
- **Ligne** : 1+
- **Date** : 10.04.2026
- **Description** : Aide IA pour inclure explicitement cette conversation dans le registre d'utilisation
- **Détail** : ajout d'une entrée de traçabilité liée à la demande utilisateur de mise à jour du document

---

## Statistiques
- **Nombre total d'utilisations d'IA documentées** : ~58 références
- **Fichiers concernés** : 18
- **Domaines** : Backend sécurité, Modèles de données, Synchronisation calendrier, Frontend UI, Documentation
- **Période** : 15.01.2026 - 10.04.2026

---

## Chronologie des utilisations

| Date | Activité | Fichiers |
|------|----------|----------|
| **15.01.2026** | Création structure + pages accueil et calendrier | `run.py`, `accueil.py`, `calendrier.py` |
| **18-19.01.2026** | Frontend calendrier et pages | `calendrier.py`, `main.py` |
| **23.02.2026** | Métadonnées examen + normalisation calendrier + affichage prof | `models.py`, `calendar_repository.py`, `calendrier.py` |
| **19.02.2026** | Sécurité API et suppression serveur | `main.py`, `calendrier.py` |
| **26.02.2026** | Synchronisation complète + sécurité complete + migrations | `database.py`, `calendar_repository.py`, `models.py`, `main.py`, `calendrier.py` |
| **01.04.2026** | Synchronisation élève-classe, validation stricte du temps passé, anti-doublons | `calendrier.py`, `calendar_repository.py`, `main.py`, `formulaire.py`, `profil_eleve.py` |
| **04.04.2026** | Règles pédagogiques par année, robustesse classes (casse), persistance coche "fait", suppression de `Non attribué`, sync options/OS/OC, UX accueil/calendrier | `teacher_assignments.py`, `profil_professeur.py`, `formulaire.py`, `statistiques.py`, `charge_eleve.py`, `models.py`, `database.py`, `main.py`, `calendrier.py`, `calendar_repository.py`, `profil_eleve.py`, `accueil.py` |
| **04.04.2026** | Rédaction de la documentation Sphinx, séparation des chapitres, réglage de la navigation et du plan | `presentation.md`, `manuel.md`, `code.md`, `critique.md`, `apprentissages.md`, `index.rst`, `conf.py` |
| **05.04.2026** | Mise à jour du registre des usages IA (références + date de révision) | `AI_USAGE.md` |
| **06.04.2026** | Ajout des références IA, clarification critique et harmonisation du rendu technique dans la documentation | `online.bib`, `code.md`, `critique.md`, `AI_USAGE.md` |
| **10.04.2026** | Mise à jour du registre pour inclure cette conversation | `AI_USAGE.md` |

---

## Remarques
- Toutes les utilisations documentées concernent des améliorations de sécurité, de synchronisation de données ou d'optimisation d'UX
- Aucune section du code ne semble générée automatiquement sans documentation
- Les améliorations apportées par IA se concentrent sur les aspects avancés du système (migrations, synchronisation, sécurité des sessions)
- Les phases de sécurité et synchronisation (19-26.02.2026) correspondent au développement des fonctionnalités avancées après le frontend initial
