# 📘 Guide d'Utilisation - API NPP (Nomenclature Produits Pharmaceutiques)

## 🚀 Démarrage Rapide

### Démarrer le Serveur

```bash
cd "/Users/dell/API NPP"
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Le serveur sera accessible sur : `http://localhost:8000`

Documentation interactive : 
- **Swagger UI** : http://localhost:8000/docs
- **ReDoc** : http://localhost:8000/redoc

---

## 🔐 Authentification

### Configuration par Défaut

L'administrateur par défaut est créé au démarrage :
- **Email** : `admin@nomenclature.dz`
- **Mot de passe** : `Admin2025!`
- **Rôle** : `ADMIN`

### Se Connecter

```bash
curl -X POST 'http://localhost:8000/auth/login' \
  --data-urlencode 'username=admin@nomenclature.dz' \
  --data-urlencode 'password=Admin2025!'
```

**Réponse** :
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

### Utiliser le Token

Pour toutes les requêtes authentifiées, ajoutez le header :
```
Authorization: Bearer <access_token>
```

### Vérifier l'Utilisateur Connecté

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/auth/me
```

---

## 📊 Gestion des Médicaments

### Lister les Médicaments (avec pagination)

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  'http://localhost:8000/medicaments?page=1&page_size=20'
```

**Filtres disponibles** :
- `code` : Code du médicament
- `dci` : Dénomination Commune Internationale
- `nom_marque` : Nom de marque
- `laboratoire` : Nom du laboratoire
- `pays_laboratoire` : Pays du laboratoire
- `type_medicament` : Type (PRINCEPS, GENERIQUE, etc.)
- `statut` : ACTIF ou INACTIF
- `liste` : Liste (A, B, C)
- `version_nomenclature` : Version de la nomenclature

**Exemple avec filtres** :
```bash
curl -H "Authorization: Bearer <TOKEN>" \
  'http://localhost:8000/medicaments?pays_laboratoire=FRANCE&type_medicament=PRINCEPS&page=1&page_size=10'
```

### Obtenir un Médicament par ID

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/medicaments/1
```

### Créer un Médicament (ADMIN uniquement)

```bash
curl -X POST http://localhost:8000/medicaments \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "MED001",
    "dci": "PARACETAMOL",
    "nom_marque": "DOLIPRANE",
    "forme": "Comprimé",
    "dosage": "500mg",
    "conditionnement": "Boîte de 20",
    "laboratoire": "SANOFI",
    "pays_laboratoire": "FRANCE",
    "type_medicament": "PRINCEPS",
    "statut": "ACTIF",
    "version_nomenclature": "2025.1"
  }'
```

### Mettre à Jour un Médicament (ADMIN uniquement)

```bash
curl -X PUT http://localhost:8000/medicaments/1 \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "MED001",
    "dci": "PARACETAMOL",
    "nom_marque": "DOLIPRANE",
    "forme": "Comprimé",
    "dosage": "1000mg",
    "conditionnement": "Boîte de 30",
    "laboratoire": "SANOFI",
    "pays_laboratoire": "FRANCE",
    "type_medicament": "PRINCEPS",
    "statut": "ACTIF",
    "version_nomenclature": "2025.1"
  }'
```

### Supprimer un Médicament (ADMIN uniquement - Soft Delete)

```bash
curl -X DELETE http://localhost:8000/medicaments/1 \
  -H "Authorization: Bearer <TOKEN>"
```

### Statistiques

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  http://localhost:8000/medicaments/stats
```

**Réponse** :
```json
{
  "total": 1500,
  "actifs": 1450,
  "inactifs": 50,
  "par_type": {
    "PRINCEPS": 800,
    "GENERIQUE": 700
  },
  "par_pays": {
    "FRANCE": 600,
    "ALGERIE": 500,
    "ESPAGNE": 400
  }
}
```

---

## 📥 Import de Nomenclature Excel

### 1. Prévisualiser les Feuilles d'un Fichier

Avant d'importer, visualisez les feuilles disponibles :

```bash
curl -X POST http://localhost:8000/import/sheets/preview \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@nomenclature.xlsx"
```

**Réponse** :
```json
{
  "sheets": [
    {
      "sheet_name": "PRINCEPS",
      "sheet_type": "medicaments",
      "row_count": 850,
      "header_row": 1,
      "column_count": 20,
      "columns": ["Code", "DCI", "Nom Marque", ...],
      "sample_data": [
        ["MED001", "PARACETAMOL", "DOLIPRANE", ...]
      ]
    },
    {
      "sheet_name": "GENERIQUES",
      "sheet_type": "medicaments",
      "row_count": 700,
      "header_row": 1,
      "column_count": 20,
      "columns": ["Code", "DCI", "Nom Marque", ...],
      "sample_data": [...]
    }
  ]
}
```

### 2. Importer une ou Plusieurs Feuilles

**Import de toutes les feuilles** :
```bash
curl -X POST http://localhost:8000/import/nomenclature \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@nomenclature.xlsx" \
  -F "version=2025.1"
```

**Import de feuilles spécifiques** :
```bash
curl -X POST http://localhost:8000/import/nomenclature \
  -H "Authorization: Bearer <TOKEN>" \
  -F "file=@nomenclature.xlsx" \
  -F "version=2025.1" \
  -F "sheet_names=PRINCEPS" \
  -F "sheet_names=GENERIQUES"
```

**Réponse** :
```json
{
  "version_nomenclature": "2025-06-30",
  "source_fichier": "nomenclature.xlsx",
  "sheets_processed": {
    "Nomenclature JUIN 2025": {
      "rows_inserted": 6278,
      "rows_updated": 906,
      "rows_ignored": 2111,
      "errors": [
        {
          "row": 10,
          "message": "Duplicate code '01 A 003' found in database (11 entries). Skipping to avoid conflicts."
        }
      ]
    }
  },
  "total_rows_inserted": 6278,
  "total_rows_updated": 906,
  "available_sheets": ["Nomenclature JUIN 2025", "Non Renouvelés", "Retraits"]
}
```

**Exemples de Lignes avec Champs Manquants (importées avec "ND")** :
```
Code: 02 D 047 | Nom: RETALEX | Dosage: 50MG/5ML | Type: ND
Code: 03 A 102 | Nom: ASPRO ACCEL | Conditionnement: ND | Type: ND
Code: 05 A 094 | Nom: ONGECIN 200 | Conditionnement: ND | Type: ND
```

### Structure Excel Attendue

L'importateur détecte automatiquement :
- La ligne d'en-tête (première ligne avec des données textuelles)
- Le type de feuille (médicaments, génériques, princeps, etc.)
- Les colonnes importantes même si mal nommées

**Colonnes reconnues** (ordre flexible, noms flexibles) :
- `n`, `N°`, `numero` → Numéro
- `num_enr*`, `enregistrement` → Numéro d'enregistrement
- `code`, `Code` → Code médicament ***(seul champ obligatoire)***
- `dci`, `DCI`, `denomination` → DCI
- `nom*`, `marque`, `produit` → Nom marque
- `forme`, `forme*` → Forme pharmaceutique
- `dosage`, `dose` → Dosage
- `condition*`, `cond*` → Conditionnement
- `liste`, `Liste` → Liste (A, B, C)
- `p1`, `P1`, `prix*1` → Prix 1
- `p2`, `P2`, `prix*2` → Prix 2
- `obs*`, `remarque` → Observations
- `labo*`, `fabricant` → Laboratoire
- `pays*`, `origine` → Pays laboratoire
- `date*initial`, `date*enr*` → Date enregistrement initial
- `date*final`, `expir*` → Date expiration/final
- `duree*stabilite*` → Durée de stabilité
- `type*`, `type*medicament` → Type de médicament
- `statut`, `état` → Statut (ACTIF/INACTIF)

**Gestion des Champs Manquants** :
- 🔴 **Code manquant** → Ligne rejetée (identifiant unique obligatoire)
- 🟢 **Autres champs manquants** → Valeur par défaut "ND" (Non Disponible)
- 🔶 **Doublons** → Première occurrence conservée, suivantes ignorées
- 🔶 **Dépassement de longueur** → Ligne rejetée avec message d'erreur

**Limites de Longueur** :
- Code : 50 caractères max
- DCI, Nom marque, Forme, Laboratoire : 255 caractères max
- Pays laboratoire : 100 caractères max

---

## 📝 Historique des Imports

### Lister les Logs d'Import

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  'http://localhost:8000/import/logs?page=1&page_size=10'
```

### Filtrer par Version

```bash
curl -H "Authorization: Bearer <TOKEN>" \
  'http://localhost:8000/import/logs?version=2025.1'
```

---

## 👥 Gestion des Utilisateurs (ADMIN uniquement)

### Créer un Nouvel Utilisateur

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "lecteur@nomenclature.dz",
    "password": "Pass123!",
    "role": "LECTEUR"
  }'
```

**Rôles disponibles** :
- `ADMIN` : Toutes les permissions (CRUD + import)
- `LECTEUR` : Lecture seule

---

## 🏥 Endpoint de Santé

```bash
curl http://localhost:8000/health
```

**Réponse** :
```json
{
  "status": "ok",
  "version": "1.0.0",
  "derniere_mise_a_jour": "2025-06-30"
}
```

> La date `derniere_mise_a_jour` provient de la dernière importation effectuée (champ `version_nomenclature`)

---

## 📚 Exemples de Workflows Complets

### Workflow 1 : Importer une Nouvelle Nomenclature

```bash
# 1. Se connecter
TOKEN=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  --data-urlencode 'username=admin@nomenclature.dz' \
  --data-urlencode 'password=Admin2025!' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Prévisualiser le fichier Excel
curl -X POST http://localhost:8000/import/sheets/preview \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@nomenclature_2025.xlsx"

# 3. Importer les feuilles sélectionnées
curl -X POST http://localhost:8000/import/nomenclature \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@nomenclature_2025.xlsx" \
  -F "version=2025-06-30" \
  -F "sheet_names=PRINCEPS" \
  -F "sheet_names=GENERIQUES"

# 4. Vérifier les statistiques
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/medicaments/stats

# 5. Vérifier le health pour voir la dernière mise à jour
curl http://localhost:8000/health
```

### Workflow 2 : Rechercher et Mettre à Jour un Médicament

```bash
# 1. Se connecter
TOKEN=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  --data-urlencode 'username=admin@nomenclature.dz' \
  --data-urlencode 'password=Admin2025!' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Rechercher un médicament
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/medicaments?nom_marque=DOLIPRANE'

# 3. Mettre à jour (exemple ID=1)
curl -X PUT http://localhost:8000/medicaments/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...}'
```

---

## 🔧 Configuration

Fichier [.env](.env) :

```env
# Database
DATABASE_URL=sqlite+aiosqlite:///./nomenclature.db

# JWT
SECRET_KEY=secret-key-2025-npp-api
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 jours

# Admin par défaut
ADMIN_EMAIL=admin@nomenclature.dz
ADMIN_PASSWORD=Admin2025!

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

---

## 🛠️ Développement

### Structure du Projet

```
API NPP/
├── app/
│   ├── main.py                 # Point d'entrée
│   ├── core/
│   │   ├── config.py           # Configuration
│   │   └── security.py         # Sécurité JWT
│   ├── db/
│   │   ├── base.py             # Base SQLAlchemy
│   │   └── session.py          # Sessions DB
│   ├── auth/
│   │   ├── models.py           # Modèle User
│   │   ├── schemas.py          # Schémas Pydantic
│   │   ├── routes.py           # Routes auth
│   │   └── jwt.py              # JWT helpers
│   ├── medicaments/
│   │   ├── models.py           # Modèle Medicament
│   │   ├── schemas.py          # Schémas CRUD
│   │   ├── crud.py             # Opérations DB
│   │   └── routes.py           # Routes API
│   ├── importer/
│   │   ├── excel_parser.py     # Parser Excel
│   │   └── routes.py           # Routes import
│   └── models/
│       └── import_log.py       # Modèle ImportLog
├── requirements.txt
├── .env
└── nomenclature.db             # Base SQLite
```

### Logs

Les logs du serveur sont disponibles dans `uvicorn.log` si démarré avec nohup.

---

## 📞 Support

Pour toute question technique, consultez :
- La documentation interactive : http://localhost:8000/docs
- Le fichier [API_Specification.md](API_Specification.md)

---

**Version** : 1.0.0  
**Dernière mise à jour** : 30 décembre 2025
