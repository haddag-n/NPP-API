# Render Deployment Guide

## ✅ Fichiers de Configuration Créés

- ✅ `Procfile` - Configuration de démarrage pour Render
- ✅ `runtime.txt` - Version Python 3.12.0
- ✅ `requirements.txt` - Mis à jour avec gunicorn
- ✅ `app/core/config.py` - Support PostgreSQL + SQLite
- ✅ `.env.example` - Configuration d'exemple

## 📋 Étapes de Déploiement sur Render

### 1️⃣ Initialiser le Repository GitHub

```bash
cd "/Users/dell/API NPP"

# Initialiser Git
git init

# Ajouter les fichiers
git add .

# Commit initial
git commit -m "Initial commit: API Nomenclature Pharmaceutiques - Ready for Render deployment"
```

### 2️⃣ Créer un Repository GitHub

1. Allez sur [github.com/new](https://github.com/new)
2. **Repository name** : `api-nomenclature-pharmaceutiques`
3. **Description** : "API REST FastAPI pour la nomenclature nationale des produits pharmaceutiques"
4. **Visibility** : Public
5. Cliquez "Create repository"

### 3️⃣ Connecter et Pousser le Code

```bash
git remote add origin https://github.com/VOTRE_USERNAME/api-nomenclature-pharmaceutiques.git
git branch -M main
git push -u origin main
```

### 4️⃣ Créer un Compte Render

1. Allez sur [render.com](https://render.com)
2. Inscrivez-vous avec GitHub
3. Autorisez Render à accéder à vos repositories

### 5️⃣ Créer une Base de Données PostgreSQL sur Render

1. Cliquez **"New +"** en haut à droite
2. Sélectionnez **"PostgreSQL"**
3. **Name** : `nomenclature-db`
4. **Region** : `Frankfurt (EU Central)` (ou votre région)
5. **PostgreSQL Version** : 15
6. **Pricing Plan** : `Free` 
7. Cliquez **"Create Database"**
8. ⏳ Attendez la création (2-3 minutes)
9. **IMPORTANT** : Copiez l'`Internal Database URL` (vous en aurez besoin)

**Format attendu** :
```
postgresql+asyncpg://username:password@hostname.c.render.com/database
```

### 6️⃣ Créer un Service Web sur Render

1. Cliquez **"New +"** → **"Web Service"**
2. Connectez votre repository GitHub :
   - Sélectionnez `api-nomenclature-pharmaceutiques`
3. Configurez le service :
   - **Name** : `api-nomenclature`
   - **Region** : `Frankfurt (EU Central)` (même que la DB)
   - **Branch** : `main`
   - **Runtime** : `Python 3`
   - **Build Command** : 
     ```
     pip install --upgrade pip && pip install -r requirements.txt
     ```
   - **Start Command** :
     ```
     gunicorn -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} app.main:app
     ```
   - **Pricing Plan** : `Free`

4. Cliquez **"Create Web Service"**
5. ⏳ Attendez le déploiement initial (3-5 minutes)

### 7️⃣ Configurer les Variables d'Environnement

Dans le tableau de bord Render, allez dans **"Environment"** du service web :

```
DATABASE_URL=postgresql+asyncpg://COPIEZ_DEPUIS_LA_DB
SECRET_KEY=votre-secret-key-très-sécurisé-2025
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
APP_NAME=Nomenclature API
APP_VERSION=1.0.0
DEBUG=False
ADMIN_EMAIL=admin@nomenclature.dz
ADMIN_PASSWORD=VotreMotDePasse123!
```

> Cliquez "Save" après chaque ajout

### 8️⃣ Vérifier le Déploiement

Une fois les variables d'environnement configurées :

1. Allez sur l'onglet **"Logs"** pour voir l'état du déploiement
2. Attendez que le service soit **"Live"** (vert)
3. Accédez à votre API :
   - **URL** : `https://api-nomenclature.onrender.com`
   - **Swagger UI** : `https://api-nomenclature.onrender.com/docs`
   - **Health** : `https://api-nomenclature.onrender.com/health`

## 🧪 Tester l'API en Production

```bash
# Test du health endpoint
curl https://api-nomenclature.onrender.com/health

# Résultat attendu
{
  "status": "ok",
  "version": "1.0.0",
  "derniere_mise_a_jour": null
}
```

## 📊 Logs et Monitoring

Dans le tableau de bord Render :
- **Logs** : Onglet "Logs" pour voir les logs en temps réel
- **Metrics** : Onglet "Metrics" pour le CPU, mémoire, etc.
- **Deployments** : Historique des déploiements

## 🚀 Mise à Jour Automatique

À chaque `git push` sur `main` :
1. Render détecte automatiquement les modifications
2. Lance un nouveau déploiement
3. L'API est mise à jour sans downtime

```bash
# Pour déclencher un déploiement
git add .
git commit -m "Mise à jour de l'API"
git push origin main
```

## 💾 Limites Gratuites Render

- **Temps de compute** : 750 heures/mois (24h x 31 jours = 744h)
- **PostgreSQL** : 90 jours gratuits, puis payant (~$10/mois)
- **Bande passante** : Illimitée
- **Uptime** : ~99.9%

## ⚠️ Notes Importantes

1. **PostgreSQL gratuit expire après 90 jours** - Passer en plan payant (~$10/mois)
2. **SQLite n'est pas adapté à Render** - Utiliser PostgreSQL
3. **Les fichiers uploadés ne persistent pas** - Utiliser S3 ou stockage Render
4. **Redémarrage automatique chaque 30 minutes** pour les plans gratuits

## 📚 Ressources

- [Render Documentation](https://render.com/docs)
- [Render PostgreSQL Guide](https://render.com/docs/databases)
- [FastAPI on Render](https://render.com/docs/deploy-fastapi)

---

✅ **Ton API est prête pour la production sur Render !**
