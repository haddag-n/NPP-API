# Spécification API Nomenclature Produits Pharmaceutiques (FastAPI)

## 1. Contexte

Cette API expose la **nomenclature nationale des produits pharmaceutiques à usage humain** (version Juillet 2025) à partir du fichier Excel officiel.  
Elle doit permettre la **consultation**, la **recherche avancée**, la **gestion** (pour les administrateurs) et l'**import automatisé** des nouvelles versions de la nomenclature.

---

## 2. Objectifs fonctionnels

1. Centraliser la nomenclature dans une base de données relationnelle.
2. Exposer des endpoints REST pour :
   - Rechercher des médicaments par DCI, marque, code, laboratoire, pays, etc.
   - Consulter le détail d'un médicament.
   - Gérer les spécialités (création, mise à jour, suppression logique) côté administrateur.
   - Importer une nouvelle version de la nomenclature à partir d'un fichier Excel.
3. Gérer des **rôles** utilisateurs :
   - Admin : toutes opérations (CRUD + import + gestion des utilisateurs).
   - Lecteur : lecture seule.
4. Garantir une API sécurisée (authentification JWT, contrôle des rôles) et documentée (OpenAPI/Swagger).

---

## 3. Stack technique cible

- **Framework** : FastAPI (Python 3.11+)
- **Base de données** : PostgreSQL
- **ORM** : SQLAlchemy / SQLModel
- **Auth** : JWT (Bearer) + rôles
- **Migrations** : Alembic
- **Serveur** : Uvicorn (développement), Gunicorn + Uvicorn workers (prod)
- **Format d'échange** : JSON

---

## 4. Modèle de données (conceptuel)

### 4.1 Entité `Medicament`

Champs principaux (issus de la nomenclature) :

- `id` (PK technique)
- `n` : numéro de ligne (N)
- `num_enregistrement` : N° d'enregistrement
- `code` : code produit
- `dci` : dénomination commune internationale
- `nom_marque`
- `forme`
- `dosage`
- `conditionnement`
- `liste`
- `p1`
- `p2`
- `obs`
- `laboratoire`
- `pays_laboratoire`
- `date_enregistrement_initial`
- `date_enregistrement_final`
- `type_medicament` (ex. GE)
- `statut` (ex. F, I)
- `duree_stabilite`
- `version_nomenclature` (ex. `2025-07-31`)
- `source_fichier` (nom de l'Excel)
- `deleted` (suppression logique)
- `created_at`
- `updated_at`

### 4.2 Entité `User`

- `id`
- `email`
- `hashed_password`
- `role` : `ADMIN` ou `LECTEUR`
- `is_active`
- `created_at`
- `updated_at`

### 4.3 Entité `ImportLog` (optionnelle)

- `id`
- `version_nomenclature`
- `source_fichier`
- `start_time`
- `end_time`
- `rows_inserted`
- `rows_updated`
- `rows_ignored`
- `errors` (JSON texte)

---

## 5. Authentification et autorisation

### 5.1 Authentification

- JWT Bearer dans l'en-tête HTTP :
  - `Authorization: Bearer <token>`
- Flux :
  - L'utilisateur se connecte avec email + mot de passe.
  - L'API renvoie un `access_token` (JWT) avec un temps d'expiration.
  - Le token est utilisé pour toutes les requêtes protégées.

### 5.2 Rôles et autorisation

- **Lecteur** :
  - Accès lecture aux endpoints `/medicaments` (GET).
- **Admin** :
  - Tous les endpoints `/medicaments` (GET, POST, PUT, DELETE).
  - Endpoints d'import `/import/...`
  - Endpoints de gestion utilisateurs (si exposés).

---

## 6. Liste des endpoints

### 6.1 Santé & métadonnées

#### `GET /health`

- **Description** : Vérifier que l'API est opérationnelle.
- **Auth** : Aucune (public ou restreint selon besoin).
- **Réponse (200)** :
  ```json
  {
    "status": "ok",
    "version": "1.0.0"
  }
  ```

---

### 6.2 Authentification

#### `POST /auth/login`

- **Description** : Authentification par email + mot de passe, renvoie un JWT.
- **Auth** : Public.
- **Body (JSON)** :
  ```json
  {
    "email": "user@example.com",
    "password": "string"
  }
  ```
- **Réponse (200)** :
  ```json
  {
    "access_token": "jwt_token_here",
    "token_type": "bearer"
  }
  ```
- **Erreurs** :
  - 401 : identifiants invalides.

#### `GET /auth/me`

- **Description** : Récupérer les informations de l'utilisateur connecté.
- **Auth** : JWT requis.
- **Réponse (200)** :
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "role": "ADMIN",
    "is_active": true
  }
  ```

*(Optionnel : `/auth/signup` RESTREINT aux admins pour créer des comptes.)*

---

### 6.3 Médicaments – Lecture (Lecteur + Admin)

#### `GET /medicaments`

- **Description** : Rechercher et lister les médicaments.
- **Auth** : JWT, rôle `LECTEUR` ou `ADMIN`.
- **Query params** (tous optionnels) :
  - `page` (int, défaut 1)
  - `page_size` (int, défaut 50, max 200)
  - `q` (string) : recherche plein texte sur DCI + nom_marque
  - `dci` (string)
  - `nom_marque` (string)
  - `code` (string)
  - `laboratoire` (string)
  - `pays_laboratoire` (string)
  - `liste` (string)
  - `type` (string)
  - `statut` (string)
  - `date_initial_min` (date ISO)
  - `date_initial_max` (date ISO)
  - `version` (string, référence de la version_nomenclature)
- **Réponse (200)** :
  ```json
  {
    "items": [
      {
        "id": 1,
        "n": 1,
        "num_enregistrement": "352/01 A 003/06/22",
        "code": "01 A 003",
        "dci": "CETIRIZINE DICHLORHYDRATE",
        "nom_marque": "ARTIZ",
        "forme": "COMPRIME PELLICULE SECABLE",
        "dosage": "10MG",
        "conditionnement": "B/10",
        "liste": "LISTE II",
        "p1": "HOP",
        "p2": "OFF",
        "obs": null,
        "laboratoire": "EL KENDI INDUSTRIE DU MEDICAMENT",
        "pays_laboratoire": "ALGERIE",
        "date_enregistrement_initial": "2006-07-31",
        "date_enregistrement_final": "2025-06-10",
        "type_medicament": "GE",
        "statut": "F",
        "duree_stabilite": "60 MOIS",
        "version_nomenclature": "2025-07-31",
        "source_fichier": "NOMENCLATURE-VERSION-JUILLET-2025-2.xlsx"
      }
    ],
    "total": 5094,
    "page": 1,
    "page_size": 50
  }
  ```

#### `GET /medicaments/{id}`

- **Description** : Obtenir le détail complet d'un médicament.
- **Auth** : JWT.
- **Réponse (200)** : Objet `Medicament` complet (mêmes champs que ci-dessus).
- **Erreurs** :
  - 404 : id inexistant ou marqué supprimé.

#### `GET /medicaments/statistiques`

- **Description** : Fournir des statistiques globales (optionnel).
- **Auth** : JWT.
- **Réponse (200)** : exemple
  ```json
  {
    "par_laboratoire": {
      "EL KENDI INDUSTRIE DU MEDICAMENT": 20,
      "GROUPE SAIDAL": 35
    },
    "par_pays": {
      "ALGERIE": 3000,
      "FRANCE": 200
    },
    "par_type": {
      "GE": 4500,
      "PRINCEPS": 594
    }
  }
  ```

---

### 6.4 Médicaments – Écriture (Admin)

#### `POST /medicaments`

- **Description** : Créer un nouveau médicament.
- **Auth** : JWT, rôle `ADMIN`.
- **Body (JSON)** :
  ```json
  {
    "n": 5095,
    "num_enregistrement": "XXX/...",
    "code": "01 A 999",
    "dci": "NOUVELLE DCI",
    "nom_marque": "NOM MARQUE",
    "forme": "FORME",
    "dosage": "DOSAGE",
    "conditionnement": "COND",
    "liste": "LISTE II",
    "p1": "HOP",
    "p2": "OFF",
    "obs": null,
    "laboratoire": "LABO",
    "pays_laboratoire": "ALGERIE",
    "date_enregistrement_initial": "2025-01-01",
    "date_enregistrement_final": "2030-01-01",
    "type_medicament": "GE",
    "statut": "F",
    "duree_stabilite": "24 MOIS",
    "version_nomenclature": "2025-07-31"
  }
  ```
- **Réponse (201)** : Objet `Medicament` créé.

#### `PUT /medicaments/{id}`

- **Description** : Mettre à jour un médicament existant.
- **Auth** : JWT, rôle `ADMIN`.
- **Body (JSON)** : même structure que `POST` mais champs partiellement obligatoires (schéma Update).
- **Réponse (200)** : Objet `Medicament` mis à jour.

#### `DELETE /medicaments/{id}`

- **Description** : Suppression logique (marque `deleted = true`).
- **Auth** : JWT, rôle `ADMIN`.
- **Réponse (204)** : Pas de corps.
- **Effet** : l'élément ne doit plus apparaître dans les listes standard.

---

### 6.5 Import de nomenclature (Admin)

#### `POST /import/nomenclature`

- **Description** : Importer une nouvelle version de la nomenclature à partir d'un fichier Excel.
- **Auth** : JWT, rôle `ADMIN`.
- **Content-Type** : `multipart/form-data`
- **Paramètres** :
  - Fichier : `file` (champ binaire, Excel).
  - Query ou form fields :
    - `version` (string, ex. `2025-07-31`)
    - `remplacer_version` (bool, défaut false) :
      - true : supprimer logique les entrées de cette version avant import
      - false : fusion (update/insert) selon logique définie
- **Traitement attendu** :
  1. Lire la feuille principale du fichier Excel.
  2. Mapper les colonnes du fichier aux champs de la table `medicaments`.
  3. Pour chaque ligne :
     - Créer ou mettre à jour l'entrée correspondante.
  4. Enregistrer un `ImportLog`.
- **Réponse (200)** :
  ```json
  {
    "version_nomenclature": "2025-07-31",
    "source_fichier": "NOMENCLATURE-VERSION-JUILLET-2025-2.xlsx",
    "rows_inserted": 100,
    "rows_updated": 50,
    "rows_ignored": 10,
    "errors": [
      {
        "row": 123,
        "message": "Date invalide"
      }
    ]
  }
  ```

---

## 7. Comportements et règles métier

1. **Suppression logique** :  
   - `/medicaments` n'affiche jamais les enregistrements `deleted = true`.
2. **Versions de nomenclature** :
   - Chaque ligne est associée à une `version_nomenclature`.
   - Les recherches peuvent être filtrées par `version`.
3. **Données obligatoires minimales** :
   - Pour créer un médicament : `code`, `dci`, `nom_marque`, `forme`, `dosage`, `conditionnement`, `laboratoire`, `pays_laboratoire`, `type_medicament`, `statut`, `version_nomenclature`.
4. **Validation** :
   - Dates valides (format ISO).
   - Longueur maximale de champs texte (ex. 255).
   - Valeurs contrôlées pour certains champs (type, statut, rôle…).

---

## 8. Contraintes non fonctionnelles

- **Performance** :
  - Pagination obligatoire côté `/medicaments`.
  - Index sur colonnes de filtre (dci, nom_marque, code, laboratoire, pays_laboratoire, type_medicament, statut, version_nomenclature).
- **Sécurité** :
  - All endpoints sensibles protégés par JWT + rôle.
  - Logs des actions d'admin (création/mise à jour/suppression/import).
- **Disponibilité** :
  - L'API doit être capable de gérer les mises à jour régulières de la nomenclature (import de nouveaux fichiers).
- **Logs** :
  - Journalisation des requêtes et des erreurs.
  - Historique des imports.

---

## 9. Structure du projet (répertoires)

```
nomenclature-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Point d'entrée FastAPI
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Paramètres (DB, JWT, secrets)
│   │   └── security.py         # Sécurité, JWT, dépendances auth
│   ├── auth/
│   │   ├── __init__.py
│   │   ├── models.py           # Modèle User (SQLAlchemy)
│   │   ├── schemas.py          # Pydantic UserCreate, UserOut, Login
│   │   ├── routes.py           # /auth/* endpoints
│   │   └── jwt.py              # Création/vérification JWT
│   ├── medicaments/
│   │   ├── __init__.py
│   │   ├── models.py           # Modèle Medicament (SQLAlchemy)
│   │   ├── schemas.py          # Pydantic MedicamentCreate/Update/Out
│   │   ├── crud.py             # Fonctions CRUD (SQLAlchemy)
│   │   └── routes.py           # /medicaments/* endpoints
│   ├── importer/
│   │   ├── __init__.py
│   │   ├── excel_parser.py     # Lecture Excel, mapping
│   │   └── routes.py           # /import/* endpoints
│   ├── db/
│   │   ├── __init__.py
│   │   ├── session.py          # SessionLocal, engine (async)
│   │   └── base.py             # Base déclarative
│   └── models/
│       └── import_log.py        # Modèle ImportLog
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
│   ├── test_auth.py
│   ├── test_medicaments.py
│   └── test_import.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
└── SPECIFICATION_API.md
```

---

## 10. Dépendances Python (requirements.txt)

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
pydantic==2.5.0
pydantic-settings==2.1.0
openpyxl==3.11.0
pandas==2.1.3
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
python-dotenv==1.0.0
```

---

## 11. Configuration (.env.example)

```
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost/nomenclature_db

# JWT
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# App
APP_NAME=Nomenclature API
APP_VERSION=1.0.0
DEBUG=False

# Admin (initial user)
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change-me-in-production
```

---

## 12. Documentation & tests

- **Documentation auto** :  
  - Swagger UI : `http://localhost:8000/docs`
  - ReDoc : `http://localhost:8000/redoc`
- **Tests** :
  - Tests unitaires : fonctions CRUD, parsing Excel.
  - Tests d'intégration : endpoints principaux (`/auth/login`, `/medicaments`, `/import/nomenclature`).
- **Exemples** :
  - Fournir quelques exemples de requêtes dans la doc OpenAPI (exemples de filtres, d'import).

---

## 13. Déploiement recommandé

- **Développement** :
  ```bash
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
  ```
- **Production** :
  ```bash
  gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
  ```
- **Docker** (optional) :
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install -r requirements.txt
  COPY app .
  CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker"]
  ```

---

## 14. Notes pour GitHub Copilot

Pour une productivité maximale avec GitHub Copilot :

1. **Commentaires TODO explicites** :
   ```python
   # TODO: Implémenter l'import Excel
   # TODO: Ajouter la validation de dates
   # TODO: Implémenter le tri par colonnes
   ```

2. **Type hints complets** :
   ```python
   def get_medicaments(
       page: int = 1,
       page_size: int = 50,
       q: Optional[str] = None,
       db: Session = Depends(get_db)
   ) -> PaginatedResponse[MedicamentOut]:
       pass
   ```

3. **Tests écrits en premier** :
   - Aide Copilot à générer du code conforme aux attentes.

4. **Docstrings détaillées** :
   ```python
   def create_medicament(
       medicament: MedicamentCreate,
       current_user: User = Depends(get_current_admin),
       db: Session = Depends(get_db)
   ) -> MedicamentOut:
       """
       Créer un nouveau médicament.
       - Vérifie que l'utilisateur est admin.
       - Valide les champs obligatoires.
       - Insère dans la base de données.
       """
       pass
   ```

---

**Fin de la spécification API.**

Ce document constitue une base solide pour commencer le développement avec FastAPI et GitHub Copilot.