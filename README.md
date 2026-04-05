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
pip install -r requirements.txt
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

```bash
python -c "from database.database import init_database; init_database()"
```

Cette étape est optionnelle si vous lancez directement `python main.py`, car le démarrage de l'application initialise déjà la base de données automatiquement.

## 🎯 Lancement de l'application

```bash
python main.py
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
pip install -r requirements.txt  # Installer les dépendances Sphinx si nécessaire
make html                        # Linux/Mac
# ou sur Windows:
make.bat html
```
Puis ouvrez `docs/build/html/index.html` dans votre navigateur.

**Option 3 : Consultation directe des sources**
- Les fichiers source se trouvent dans `docs/source/`

## �📁 Structure du projet

```
planification_devoirs/
│
├── run.py                         # Point d'entrée racine
├── README.md
├── AI_USAGE.md
├── app/
│   ├── main.py                    # Application NiceGUI
│   ├── requirements.txt           # Dépendances Python
│   ├── config/
│   │   └── settings.py            # Paramètres de l'app
│   ├── components/
│   │   ├── navbar.py              # Barre de navigation
│   │   ├── header.py              # En-tête
│   │   └── cards.py               # Composants réutilisables
│   ├── database/
│   │   ├── database.py            # Connexion BD + init
│   │   ├── models.py              # Modèles SQLAlchemy
│   │   ├── calendar_repository.py # Accès événements calendrier
│   │   ├── init_db.py             # Script d'initialisation BD
│   │   └── seed_demo_data.py      # Données de démonstration
│   ├── pages/
│   │   ├── login.py
│   │   ├── inscription.py
│   │   ├── accueil.py
│   │   ├── calendrier.py
│   │   ├── formulaire.py
│   │   ├── charge_eleve.py
│   │   ├── profil_eleve.py
│   │   ├── profil_professeur.py
│   │   ├── reset_password.py
│   │   └── statistiques.py
│   ├── utils/
│   │   ├── auth.py
│   │   ├── date_helpers.py
│   │   ├── school.py
│   │   ├── teacher_assignments.py
│   │   └── validators.py
│   ├── static/
│   │   ├── css/
│   │   ├── images/
│   │   └── js/
│   ├── templates/
│   └── tests/
└── docs/                          # Documentation Sphinx
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
1. **Connexion réelle à la base de données**
   - Remplacer les données simulées par des requêtes SQL
   - Implémenter l'authentification complète

2. **CRUD des devoirs et examens**
   - Créer, lire, modifier, supprimer des devoirs
   - Créer, lire, modifier, supprimer des examens
   - Filtrage par classe, matière, options

3. **Calcul de charge de travail**
   - Somme des temps estimés par jour/semaine
   - Répartition du temps de révision
   - Indicateur de surcharge (>3h/jour)

4. **Statistiques avancées**
   - Précision des estimations (temps estimé vs réel)
   - Charge de travail par matière
   - Périodes les plus chargées
   - Comparaison entre enseignants

5. **Fonctionnalités additionnelles**
   - Réinitialisation mot de passe
   - Modification du profil
   - Notifications
   - Export des données

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
python main.py
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

**Base de données :**
```bash
# Réinitialiser la base de données
rm app.db
python -c "from database.database import init_database; init_database()"
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