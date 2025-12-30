# 📊 Analyse de l'Import Nomenclature Juillet 2025

## Résumé de l'Import

**Fichier** : `920346269-NOMENCLATURE-VERSION-JUILLET-2025-2.xlsx`  
**Version** : `2025-06-30`  
**Feuille** : `Nomenclature JUIN 2025`

### Statistiques Globales

| Métrique | Valeur |
|----------|--------|
| ✅ Lignes insérées | **4 923** |
| 🔄 Lignes mises à jour | **20** |
| ⚠️ Lignes ignorées | **151** |
| ❌ Erreurs | **151** |
| **Total traité** | **5 094** |

### Taux de Succès

- **Succès** : 97.0% (4 943 / 5 094)
- **Échec** : 3.0% (151 / 5 094)

---

## 🔍 Analyse des Erreurs

### Types d'Erreurs Rencontrées

#### 1. **Doublons (Multiple rows found)** - 95 occurrences (62.9%)

**Symptôme** : `Error processing row: Multiple rows were found when one or none was required`

**Cause** : Plusieurs médicaments avec le même code existent déjà dans la base de données.

**Lignes affectées** :
- 204-208, 610, 821-823, 925-927, 1029-1041, 1142-1146, 1247-1253, 1454-1455
- 1556-1561, 1763-1764, 1966, 2067-2071, 2172-2173, 2274-2275, 2699-2700
- 3204, 3620-3630, 3933-3934, 4035-4038, 4139

**Solution proposée** :
1. Détecter les doublons avec : `python manage_duplicates.py detect --version 2025-06-30`
2. Nettoyer avec : `python manage_duplicates.py clean --strategy latest --no-dry-run`

**Impact** : Ces lignes sont ignorées lors de l'import pour éviter les conflits.

---

#### 2. **Champ `type_medicament` manquant** - 40 occurrences (26.5%)

**Symptôme** : `Missing required field: type_medicament`

**Lignes affectées** :
- 189, 198, 582, 611, 673, 698, 706, 720, 721, 723, 782, 788, 838, 978
- 1910, 2406, 2407, 2420, 2424, 2428, 2432, 2436, 2447, 2448, 2467, 2468
- 2507, 2553-2562, 2641, 2664, 3154, 3155, 3311, 3312, 3829, 4172, 4768, 4865, 5083, 5085, 5091, 5092

**Cause** : La colonne `type_medicament` (PRINCEPS, GENERIQUE, etc.) n'est pas renseignée dans l'Excel.

**Solution recommandée** :
1. Vérifier la colonne dans Excel (possiblement mal nommée ou vide)
2. Ou définir une valeur par défaut : `type_medicament = "NON_SPECIFIE"`

**Impact Métier** : Ces médicaments ne peuvent pas être importés car le type est essentiel pour la classification.

---

#### 3. **Champ `dosage` manquant** - 19 occurrences (12.6%)

**Symptôme** : `Missing required field: dosage`

**Lignes affectées** :
- 1626, 3159, 3379, 3458, 3479, 3514-3523, 4618, 4619, 4622, 4952, 4953

**Cause** : Le dosage n'est pas renseigné dans l'Excel.

**Solution recommandée** :
1. Vérifier si la colonne existe mais est vide
2. Ou autoriser un dosage "NON SPECIFIE" pour certains produits (ex: dispositifs médicaux)

**Impact Métier** : Le dosage est critique pour l'identification des médicaments.

---

#### 4. **Champ `conditionnement` manquant** - 2 occurrences (1.3%)

**Symptôme** : `Missing required field: conditionnement`

**Lignes affectées** : 174, 791

**Cause** : Conditionnement non renseigné.

**Solution** : Vérifier ces lignes dans l'Excel source.

---

#### 5. **Champ `forme` manquant** - 1 occurrence (0.7%)

**Symptôme** : `Missing required field: forme`

**Lignes affectées** : 3826

**Cause** : Forme pharmaceutique non renseignée.

**Solution** : Compléter dans l'Excel source.

---

## 🛠️ Actions Correctives Recommandées

### Priorité 1 : Nettoyer les Doublons (95 erreurs)

```bash
# 1. Détecter les doublons
cd "/Users/dell/API NPP"
source venv/bin/activate
python manage_duplicates.py detect --version 2025-06-30

# 2. Simulation de nettoyage (dry-run)
python manage_duplicates.py clean --version 2025-06-30 --strategy latest

# 3. Appliquer le nettoyage
python manage_duplicates.py clean --version 2025-06-30 --strategy latest --no-dry-run
```

**Ou via l'API** :
```bash
TOKEN=$(curl -s -X POST 'http://localhost:8000/auth/login' \
  --data-urlencode 'username=admin@nomenclature.dz' \
  --data-urlencode 'password=Admin2025!' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# Détecter
curl -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/import/duplicates?version=2025-06-30'

# Nettoyer (dry-run)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/import/clean-duplicates?version=2025-06-30&keep_strategy=latest&dry_run=true'

# Nettoyer (réel)
curl -X POST -H "Authorization: Bearer $TOKEN" \
  'http://localhost:8000/import/clean-duplicates?version=2025-06-30&keep_strategy=latest&dry_run=false'
```

### Priorité 2 : Corriger les Champs Manquants

#### Option A : Corriger dans Excel et Ré-importer

1. Ouvrir le fichier Excel source
2. Identifier les lignes avec erreurs (voir liste ci-dessus)
3. Compléter les champs manquants :
   - `type_medicament` : Déterminer si PRINCEPS, GENERIQUE, etc.
   - `dosage` : Ajouter le dosage ou mettre "NON SPECIFIE"
   - `conditionnement` : Compléter le conditionnement
   - `forme` : Ajouter la forme pharmaceutique

4. Ré-importer avec `remplacer_version=true` :
```bash
curl -X POST http://localhost:8000/import/nomenclature \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@nomenclature_corrige.xlsx" \
  -F "version=2025-06-30" \
  -F "remplacer_version=true"
```

#### Option B : Assouplir les Validations (pour certains cas)

Modifier le modèle pour accepter des valeurs par défaut :
- `dosage` : Autoriser `"NON SPECIFIE"` pour dispositifs médicaux
- `type_medicament` : Utiliser `"A_DETERMINER"` temporairement

**⚠️ Non recommandé** : Compromet la qualité des données.

### Priorité 3 : Prévention Future

1. **Validation Excel en amont** : Créer un outil de validation avant import
2. **Contrainte d'unicité** : Ajouter un index unique sur `(code, version)` en base
3. **Améliorer le mapping des colonnes** : Détecter mieux les colonnes mal nommées

---

## 📈 Améliorations Implémentées

### ✅ Gestion des Doublons

**Avant** : L'import crashait avec `scalar_one_or_none()` quand plusieurs résultats existaient.

**Après** : 
- Détection automatique des doublons
- Skip gracieux avec message d'erreur détaillé
- Endpoints dédiés pour analyse et nettoyage

### ✅ Meilleure Gestion des Erreurs

- Chaque erreur est loggée avec le numéro de ligne
- Distinction claire entre types d'erreurs
- L'import continue même en cas d'erreur sur une ligne

---

## 📋 Prochaines Étapes

1. **Immédiat** : Nettoyer les 95 doublons
2. **Court terme** : Corriger les 56 champs manquants dans Excel
3. **Moyen terme** : Ajouter contrainte unique sur (code, version)
4. **Long terme** : Outil de validation pré-import

---

## 📞 Support

Pour toute question sur cette analyse :
- Consulter [GUIDE_UTILISATION.md](GUIDE_UTILISATION.md)
- Utiliser l'endpoint `/import/logs` pour l'historique détaillé
- Exécuter `python manage_duplicates.py --help`

---

**Généré le** : 30 décembre 2025  
**Version API** : 1.0.0
