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
```

### 5. Initialiser la base de données

```bash
python -c "from database.database import init_database; init_database()"
```

## 🎯 Lancement de l'application

```bash
python main.py
```

L'application sera accessible sur : **http://localhost:8080**

## 📁 Structure du projet

```
planification_devoirs/
│
├── main.py                      # Point d'entrée
├── requirements.txt             # Dépendances
├── .env                         # Configuration (à créer)
│
├── config/
│   └── settings.py             # Paramètres de l'app
│
├── database/
│   ├── models.py               # Modèles SQLAlchemy
│   ├── database.py             # Connexion BD
│   └── init_db.py              # Init BD
│
├── pages/
│   ├── login.py                # Connexion
│   ├── inscription.py          # Inscription
│   ├── accueil.py              # Accueil
│   ├── calendrier.py           # Calendrier
│   ├── formulaire.py           # Ajout devoir/examen
│   ├── profil_eleve.py         # Profil élève
│   ├── profil_professeur.py   # Profil professeur
│   └── statistiques.py         # Statistiques
│
├── components/
│   ├── navbar.py               # Barre de navigation
│   ├── header.py               # En-tête
│   └── cards.py                # Composants réutilisables
│
├── utils/
│   ├── auth.py                 # Authentification
│   ├── validators.py           # Validation
│   └── date_helpers.py         # Utilitaires dates
│
└── static/
    ├── css/
    ├── images/
    └── js/
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

### Compte de test (à créer via inscription)

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

**Bon développement ! 🎓**