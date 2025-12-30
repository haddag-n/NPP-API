# API Nomenclature Produits Pharmaceutiques

API FastAPI pour la gestion de la nomenclature nationale des produits pharmaceutiques à usage humain (version Juillet 2025).

## 🚀 Fonctionnalités

- ✅ **Authentification JWT** avec gestion des rôles (Admin/Lecteur)
- ✅ **CRUD complet** pour la gestion des médicaments
- ✅ **Recherche avancée** avec filtres multiples et pagination
- ✅ **Import Excel** automatisé de nouvelles versions de nomenclature
- ✅ **Suppression logique** des enregistrements
- ✅ **Statistiques** par laboratoire, pays et type
- ✅ **Documentation automatique** (Swagger/ReDoc)
- ✅ **Base de données PostgreSQL** avec SQLAlchemy async
- ✅ **Migrations Alembic** pour la gestion du schéma

## 📋 Prérequis

- Python 3.11+
- PostgreSQL 12+
- pip ou poetry pour la gestion des dépendances

## 🛠️ Installation

### 1. Cloner le dépôt

```bash
cd "API NPP"
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# ou
venv\Scripts\activate  # Sur Windows
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer la base de données

Créer une base de données PostgreSQL :

```bash
createdb nomenclature_db
```

### 5. Configurer les variables d'environnement

Copier le fichier `.env.example` vers `.env` et modifier les valeurs :

```bash
cp .env.example .env
```

Éditer `.env` :

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/nomenclature_db

# JWT
SECRET_KEY=votre-cle-secrete-tres-forte-ici
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=Nomenclature API
APP_VERSION=1.0.0
DEBUG=True

# Admin (initial user)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=votre-mot-de-passe-admin
```

### 6. Créer les migrations initiales (optionnel)

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

Note : L'application crée automatiquement les tables au démarrage si elles n'existent pas.

## 🚀 Démarrage

### Mode développement

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Ou directement avec Python :

```bash
python -m app.main
```

### Mode production

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

L'API sera accessible sur : **http://localhost:8000**

## 📚 Documentation

- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

## 🔐 Authentification

### 1. Se connecter

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "votre-mot-de-passe"}'
```

Réponse :
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 2. Utiliser le token

Pour toutes les requêtes protégées, ajouter l'en-tête :

```
Authorization: Bearer <votre_token>
```

## 📖 Endpoints principaux

### Santé
- `GET /health` - Vérifier l'état de l'API

### Authentification
- `POST /auth/login` - Se connecter (public)
- `GET /auth/me` - Obtenir les infos utilisateur (authentifié)
- `POST /auth/signup` - Créer un utilisateur (admin uniquement)

### Médicaments
- `GET /medicaments` - Lister/rechercher des médicaments (authentifié)
- `GET /medicaments/{id}` - Détails d'un médicament (authentifié)
- `GET /medicaments/statistiques` - Statistiques (authentifié)
- `POST /medicaments` - Créer un médicament (admin)
- `PUT /medicaments/{id}` - Modifier un médicament (admin)
- `DELETE /medicaments/{id}` - Supprimer un médicament (admin)

### Import
- `POST /import/nomenclature` - Importer un fichier Excel (admin)

## 🔍 Exemples d'utilisation

### Rechercher des médicaments

```bash
curl -X GET "http://localhost:8000/medicaments?page=1&page_size=10&q=CETIRIZINE" \
  -H "Authorization: Bearer <token>"
```

Avec filtres multiples :

```bash
curl -X GET "http://localhost:8000/medicaments?laboratoire=SAIDAL&pays_laboratoire=ALGERIE&type=GE" \
  -H "Authorization: Bearer <token>"
```

### Créer un médicament

```bash
curl -X POST "http://localhost:8000/medicaments" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "01 A 999",
    "dci": "PARACETAMOL",
    "nom_marque": "DOLIPRANE",
    "forme": "COMPRIME",
    "dosage": "500MG",
    "conditionnement": "B/20",
    "laboratoire": "SANOFI",
    "pays_laboratoire": "FRANCE",
    "type_medicament": "PRINCEPS",
    "statut": "F",
    "version_nomenclature": "2025-07-31"
  }'
```

### Importer un fichier Excel

```bash
curl -X POST "http://localhost:8000/import/nomenclature" \
  -H "Authorization: Bearer <token>" \
  -F "file=@nomenclature.xlsx" \
  -F "version=2025-07-31" \
  -F "remplacer_version=false"
```

## 🧪 Tests

Les tests seront ajoutés dans le dossier `tests/`.

```bash
# Installer les dépendances de test
pip install pytest pytest-asyncio httpx

# Exécuter les tests
pytest
```

## 📁 Structure du projet

```
API NPP/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   └── security.py         # Sécurité JWT
│   ├── auth/
│   │   ├── models.py           # Modèle User
│   │   ├── schemas.py          # Schémas Pydantic
│   │   ├── routes.py           # Routes auth
│   │   └── jwt.py              # Gestion JWT
│   ├── medicaments/
│   │   ├── models.py           # Modèle Medicament
│   │   ├── schemas.py          # Schémas Pydantic
│   │   ├── crud.py             # Opérations CRUD
│   │   └── routes.py           # Routes médicaments
│   ├── importer/
│   │   ├── excel_parser.py     # Parser Excel
│   │   └── routes.py           # Routes import
│   ├── db/
│   │   ├── base.py             # Base SQLAlchemy
│   │   └── session.py          # Sessions DB
│   └── models/
│       └── import_log.py       # Modèle ImportLog
├── alembic/
│   ├── versions/               # Migrations
│   └── env.py                  # Config Alembic
├── tests/                      # Tests
├── requirements.txt            # Dépendances
├── .env.example               # Exemple config
├── .gitignore
├── alembic.ini                # Config Alembic
├── API_Specification.md       # Spécification complète
└── README.md                  # Ce fichier
```

## 🔒 Sécurité

- Tous les endpoints sensibles sont protégés par JWT
- Hachage des mots de passe avec bcrypt
- Gestion des rôles (Admin/Lecteur)
- Validation des entrées avec Pydantic
- Suppression logique des enregistrements

## 🐛 Dépannage

### Erreur de connexion à la base de données

Vérifier que PostgreSQL est en cours d'exécution et que la chaîne de connexion dans `.env` est correcte.

### Erreur d'import de modules

S'assurer que l'environnement virtuel est activé et que toutes les dépendances sont installées :

```bash
pip install -r requirements.txt
```

### Problème avec Alembic

Recréer les migrations :

```bash
alembic revision --autogenerate -m "Initial"
alembic upgrade head
```

## 📝 Licence

Ce projet est développé pour la gestion de la nomenclature nationale des produits pharmaceutiques.

## 👥 Contact

Pour toute question ou suggestion, veuillez contacter l'équipe de développement.

---

**Version** : 1.0.0  
**Dernière mise à jour** : Décembre 2025
