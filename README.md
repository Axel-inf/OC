# Application de Planification des Devoirs - Collège du Sud

Application mobile développée avec NiceGUI pour la gestion des devoirs et examens.

## 📋 Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Visual Studio Code (recommandé)

## 🚀 Installation

### 1. Cloner ou créer le projet

Créez un nouveau dossier pour votre projet :

```bash
mkdir planification_devoirs
cd planification_devoirs
```

### 2. Créer un environnement virtuel

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install -r app/requirements.txt
```

### 4. Configuration

Créez un fichier `.env` à la racine du projet :

```env
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=votre-clé-secrète-très-longue-et-complexe
DEBUG=True
SEED_DEMO_DATA_ON_STARTUP=False

# Email (réinitialisation mot de passe)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=True
SMTP_USERNAME=votre.adresse@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_application_gmail
SMTP_FROM_EMAIL=votre.adresse@gmail.com
```

`SEED_DEMO_DATA_ON_STARTUP=False` garde les données entre redémarrages. Mettez `True` seulement pour réinitialiser et repeupler les données de démonstration au démarrage.

Pour une première prise en main sur une machine inconnue, le plus simple est de mettre temporairement `SEED_DEMO_DATA_ON_STARTUP=True` au premier lancement. L'application créera alors une base avec des comptes de démonstration et des devoirs/examens déjà enregistrés. Vous pourrez ensuite remettre la valeur à `False` pour conserver vos données lors des prochains redémarrages.

### Configuration Gmail (obligatoire pour l'envoi d'email)

1. Activez la validation en 2 étapes sur votre compte Google.
2. Créez un **mot de passe d'application** (Google Account > Sécurité > Mots de passe des applications).
3. Utilisez ce mot de passe d'application dans `SMTP_PASSWORD` (pas votre mot de passe Google principal).
4. Vérifiez que `SMTP_USERNAME` et `SMTP_FROM_EMAIL` correspondent à l'adresse Gmail utilisée.

### 5. Initialiser la base de données

Cette étape est optionnelle: le démarrage de l'application initialise déjà la base de données automatiquement.

## 🎯 Lancement de l'application

```bash
python run.py
```

L'application sera accessible sur : [http://localhost:8080](http://localhost:8080)

En local, l'URL utilise `http` (sans `s`) par défaut. `https` nécessite une configuration TLS/certificat supplémentaire.

## 🔐 Comptes de démonstration

La base de données de démonstration contient déjà des comptes de professeurs et d'élèves, ainsi que des événements de test. Cela permet de se connecter immédiatement sans devoir créer manuellement les premiers comptes.

Dans la version actuelle du seed, les identifiants sont les suivants :

- Professeurs : `0@example.com` à `9@example.com`
- Élèves : `a@example.com` à `z@example.com`
- Mot de passe pour tous les comptes de démonstration : `12345678`

Exemples de connexion rapides :

- Professeur : `1@example.com` / `12345678`
- Élève : `a@example.com` / `12345678`

Si vous recevez une version du projet où les comptes de démonstration sont numérotés différemment, gardez la même logique : ouvrez la page de connexion, saisissez l'email correspondant au compte existant, puis utilisez le mot de passe de démonstration indiqué dans le seed.

## � Documentation

La documentation complète du projet se trouve dans le dossier `docs/`. 

### Accès à la documentation

**Option 1 : Ouvrir le Readme de la documentation (recommandé)**
```bash
code docs/Readme.md
```
Ou naviguez vers `docs/Readme.md` dans l'explorateur VS Code.

**Option 2 : Construire la documentation Sphinx (HTML)**
```bash
cd docs
python -m pip install -r requirements.txt  # Installer les dépendances Sphinx si nécessaire
make html                        # Linux/Mac
# ou, sur Windows si vous n'avez pas GNU Make:
python -m sphinx -M html source build
```
Puis ouvrez `docs/build/html/index.html` dans votre navigateur.

Si vous obtenez encore `sphinx-build: not found`, lancez directement la génération via Python :
```bash
python -m sphinx -M html source build
```
depuis le dossier `docs/`.

**Option 3 : Consultation directe des sources**
- Les fichiers source se trouvent dans `docs/source/`

**Option 4 : Ouvrir la doc en localhost (recommandé)**
1. Générez d'abord la doc HTML :
```bash
cd docs
make html
```
2. Lancez un serveur local depuis le dossier HTML généré :
```bash
# WSL / Linux / Mac
cd docs/build/html
python3 -m http.server 8000

# Windows (PowerShell / CMD)
cd docs\\build\\html
python -m http.server 8000
```
3. Ouvrez ensuite : http://localhost:8000

Cette méthode évite toute publication externe et reste idéale pour les tests locaux.

## �📁 Structure du projet

```
projet_info/
│
├── run.py                          # Point d'entrée racine
├── README.md
├── AI_USAGE.md
├── app/
│   ├── __init__.py
│   ├── main.py                     # Application NiceGUI
│   ├── requirements.txt            # Dépendances Python de l'app
│   ├── components/                 # Composants UI réutilisables
│   │   ├── __init__.py
│   │   ├── navbar.py
│   │   ├── header.py
│   │   └── cards.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py             # Paramètres globaux
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py             # Session/engine SQLAlchemy + init
│   │   ├── models.py               # Modèles ORM
│   │   ├── calendar_repository.py  # Requêtes calendrier
│   │   ├── init_db.py
│   │   └── seed_demo_data.py
│   ├── pages/                      # Pages NiceGUI
│   │   ├── __init__.py
│   │   ├── accueil.py
│   │   ├── calendrier.py
│   │   ├── charge_eleve.py
│   │   ├── formulaire.py
│   │   ├── inscription.py
│   │   ├── login.py
│   │   ├── profil_eleve.py
│   │   ├── profil_professeur.py
│   │   ├── reset_password.py
│   │   └── statistiques.py
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── js/
│   ├── templates/
│   │   └── base.html
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_pages.py
│   └── utils/
│       ├── __init__.py
│       ├── auth.py
│       ├── date_helpers.py
│       ├── school.py
│       ├── teacher_assignments.py
│       └── validators.py
└── docs/                           # Documentation Sphinx
   ├── Makefile                    # Cibles de build Sphinx (si make est installé)
   ├── Readme.md                   # Guide spécifique à la documentation
   ├── requirements.txt            # Dépendances doc
   ├── packages                    # Métadonnées/template de packaging doc
   ├── source/                     # Sources .rst/.md
   ├── latex-templates/            # Templates LaTeX pour génération PDF
   └── build/html/                 # Sortie HTML générée
```

## 🎨 Fonctionnalités implémentées

### ✅ Pages principales
- [x] Page de connexion
- [x] Page d'inscription (élève/enseignant)
- [x] Page d'accueil
- [x] Page calendrier avec devoirs/examens
- [x] Formulaire d'ajout devoir/examen
- [x] Profil élève
- [x] Profil enseignant
- [x] Page statistiques

### ✅ Composants
- [x] Navbar de navigation
- [x] Header réutilisable
- [x] Cartes d'événements

### ✅ Base de données
- [x] Modèles ORM (Utilisateur, Élève, Enseignant, Devoir, Examen)
- [x] Système d'authentification
- [x] Gestion des options spécifiques (OS, OC, langues)

## 🔄 Prochaines étapes (Backend)

### À implémenter
1. **Sécuriser l'authentification et les sessions**
   - Renforcer la gestion des sessions (expiration, invalidation à la déconnexion)
   - Uniformiser les vérifications d'accès selon le rôle (élève/enseignant)

2. **Finaliser le CRUD complet des événements**
   - Ajouter les routes/actions de modification et suppression avec validations métier
   - Journaliser les opérations critiques (création, édition, suppression)

3. **Améliorer la couche repository et les transactions**
   - Centraliser les requêtes SQLAlchemy dans les repositories
   - Encadrer les opérations sensibles par des transactions atomiques

4. **Renforcer la qualité logicielle**
   - Étendre les tests unitaires sur `database/`, `utils/` et `pages/`
   - Ajouter des tests d'intégration pour les scénarios complets (login -> création -> consultation)

5. **Préparer le déploiement et l'exploitation**
   - Ajouter une configuration de logs structurés (niveau, fichier, contexte utilisateur)
   - Documenter les variables d'environnement de production et le mode debug

## 📝 Utilisation

### Connexion avec un compte existant

Si vous avez activé les données de démonstration, vous pouvez vous connecter directement avec un compte déjà présent en base au lieu de créer un nouvel utilisateur.

1. Ouvrez la page de connexion.
2. Saisissez l'email d'un compte de démonstration.
3. Entrez le mot de passe `12345678`.
4. Connectez-vous et vous accédez à un profil qui possède déjà des devoirs et examens de test.

### Création d'un nouveau compte

Si vous voulez créer votre propre utilisateur, choisissez le rôle correspondant lors de l'inscription :

**Élève :**
- Sélectionner "Élève" lors de l'inscription
- Remplir les informations (classe, langues, options)

**Enseignant :**
- Sélectionner "Enseignant" lors de l'inscription
- Remplir les branches et classes enseignées

### Navigation

- **Accueil** : Page de bienvenue avec accès rapide
- **Calendrier** : Vue des devoirs et examens avec charge de travail
- **Statistiques** : Graphiques de suivi (à améliorer avec vraies données)
- **Profil** : Gestion des informations personnelles

## 🛠️ Développement

### Lancer en mode développement

```bash
python run.py
```

Le mode rechargement automatique est activé par défaut.

### Modifier le design

Les styles CSS sont intégrés dans chaque page via `ui.add_head_html()`.
Pour des styles globaux, utilisez `static/css/custom.css`.

### Ajouter une nouvelle page

1. Créer un fichier dans `pages/`
2. Définir une fonction `create()`
3. Ajouter la route dans `main.py`
4. Ajouter l'import dans `pages/__init__.py`

## 🐛 Débogage

### Problèmes courants

**Erreur d'import :**
```bash
# Vérifier que tous les __init__.py existent
# Vérifier l'activation de l'environnement virtuel
```

**ImportError `Sentinel` (typing_extensions) :**
```bash
# Depuis la racine du projet
python -m pip install -U typing_extensions
python -m pip install -r app/requirements.txt
```

Si l'erreur persiste, réinstallez les dépendances dans un environnement virtuel propre.

**Base de données :**
```bash
# Réinitialiser la base de données
rm app.db
python run.py
```

**Port déjà utilisé :**
```python
# Dans main.py, changer le port
ui.run(port=8081)  # Au lieu de 8080
```

## 📚 Documentation

- [NiceGUI](https://nicegui.io/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Quasar Components](https://quasar.dev/vue-components/)

## 🤝 Contribution

1. Créer une branche pour chaque fonctionnalité
2. Tester avant de commiter
3. Documenter les changements majeurs

## 📄 License

Projet développé pour le Collège du Sud.

---