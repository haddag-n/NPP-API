#!/bin/bash

# 🧪 Script de Test - API NPP
# Teste tous les endpoints principaux

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "🧪 Tests API NPP"
echo "================"
echo ""

# Test 1: Health Check
echo -e "${BLUE}Test 1: Health Check${NC}"
HEALTH=$(curl -s "$BASE_URL/health")
if echo "$HEALTH" | grep -q "ok"; then
    echo -e "${GREEN}✅ Health check OK${NC}"
    echo "$HEALTH" | python3 -m json.tool
else
    echo -e "${RED}❌ Health check FAILED${NC}"
    exit 1
fi
echo ""

# Test 2: Login
echo -e "${BLUE}Test 2: Login Admin${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  --data-urlencode 'username=admin@nomenclature.dz' \
  --data-urlencode 'password=Admin2025!')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✅ Login réussi${NC}"
    echo "Token: ${TOKEN:0:30}..."
else
    echo -e "${RED}❌ Login FAILED${NC}"
    echo "$LOGIN_RESPONSE"
    exit 1
fi
echo ""

# Test 3: Get Current User
echo -e "${BLUE}Test 3: Get Current User (/auth/me)${NC}"
ME_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/auth/me")
if echo "$ME_RESPONSE" | grep -q "admin@nomenclature.dz"; then
    echo -e "${GREEN}✅ Current user OK${NC}"
    echo "$ME_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Current user FAILED${NC}"
    echo "$ME_RESPONSE"
fi
echo ""

# Test 4: List Medicaments
echo -e "${BLUE}Test 4: List Medicaments (empty)${NC}"
MEDS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/medicaments?page=1&page_size=5")
if echo "$MEDS_RESPONSE" | grep -q "items"; then
    echo -e "${GREEN}✅ List medicaments OK${NC}"
    echo "$MEDS_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ List medicaments FAILED${NC}"
    echo "$MEDS_RESPONSE"
fi
echo ""

# Test 5: Create Medicament
echo -e "${BLUE}Test 5: Create Medicament${NC}"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/medicaments" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "TEST001",
    "dci": "PARACETAMOL",
    "nom_marque": "DOLIPRANE TEST",
    "forme": "Comprimé",
    "dosage": "500mg",
    "conditionnement": "Boîte de 20",
    "laboratoire": "SANOFI",
    "pays_laboratoire": "FRANCE",
    "type_medicament": "PRINCEPS",
    "statut": "ACTIF",
    "version_nomenclature": "TEST-2025"
  }')

MED_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)

if [ -n "$MED_ID" ]; then
    echo -e "${GREEN}✅ Create medicament OK (ID: $MED_ID)${NC}"
    echo "$CREATE_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Create medicament FAILED${NC}"
    echo "$CREATE_RESPONSE"
fi
echo ""

# Test 6: Get Medicament by ID
if [ -n "$MED_ID" ]; then
    echo -e "${BLUE}Test 6: Get Medicament by ID${NC}"
    GET_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/medicaments/$MED_ID")
    if echo "$GET_RESPONSE" | grep -q "TEST001"; then
        echo -e "${GREEN}✅ Get medicament OK${NC}"
        echo "$GET_RESPONSE" | python3 -m json.tool
    else
        echo -e "${RED}❌ Get medicament FAILED${NC}"
        echo "$GET_RESPONSE"
    fi
    echo ""
fi

# Test 7: Update Medicament
if [ -n "$MED_ID" ]; then
    echo -e "${BLUE}Test 7: Update Medicament${NC}"
    UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/medicaments/$MED_ID" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "code": "TEST001",
        "dci": "PARACETAMOL",
        "nom_marque": "DOLIPRANE TEST UPDATED",
        "forme": "Comprimé",
        "dosage": "1000mg",
        "conditionnement": "Boîte de 30",
        "laboratoire": "SANOFI",
        "pays_laboratoire": "FRANCE",
        "type_medicament": "PRINCEPS",
        "statut": "ACTIF",
        "version_nomenclature": "TEST-2025"
      }')
    
    if echo "$UPDATE_RESPONSE" | grep -q "UPDATED"; then
        echo -e "${GREEN}✅ Update medicament OK${NC}"
        echo "$UPDATE_RESPONSE" | python3 -m json.tool
    else
        echo -e "${RED}❌ Update medicament FAILED${NC}"
        echo "$UPDATE_RESPONSE"
    fi
    echo ""
fi

# Test 8: Statistics
echo -e "${BLUE}Test 8: Statistics${NC}"
STATS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/medicaments/stats")
if echo "$STATS_RESPONSE" | grep -q "total"; then
    echo -e "${GREEN}✅ Statistics OK${NC}"
    echo "$STATS_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Statistics FAILED${NC}"
    echo "$STATS_RESPONSE"
fi
echo ""

# Test 9: Search with Filters
echo -e "${BLUE}Test 9: Search with Filters${NC}"
SEARCH_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" \
  "$BASE_URL/medicaments?pays_laboratoire=FRANCE&type_medicament=PRINCEPS&page=1&page_size=10")
if echo "$SEARCH_RESPONSE" | grep -q "items"; then
    echo -e "${GREEN}✅ Search with filters OK${NC}"
    echo "$SEARCH_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Search FAILED${NC}"
    echo "$SEARCH_RESPONSE"
fi
echo ""

# Test 10: Delete Medicament (Soft Delete)
if [ -n "$MED_ID" ]; then
    echo -e "${BLUE}Test 10: Delete Medicament (Soft Delete)${NC}"
    DELETE_RESPONSE=$(curl -s -X DELETE "$BASE_URL/medicaments/$MED_ID" \
      -H "Authorization: Bearer $TOKEN")
    
    if echo "$DELETE_RESPONSE" | grep -q "deleted"; then
        echo -e "${GREEN}✅ Delete medicament OK${NC}"
        echo "$DELETE_RESPONSE" | python3 -m json.tool
    else
        echo -e "${RED}❌ Delete FAILED${NC}"
        echo "$DELETE_RESPONSE"
    fi
    echo ""
fi

# Test 11: Import Logs
echo -e "${BLUE}Test 11: Import Logs${NC}"
LOGS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/import/logs?page=1&page_size=5")
if echo "$LOGS_RESPONSE" | grep -q "items"; then
    echo -e "${GREEN}✅ Import logs OK${NC}"
    echo "$LOGS_RESPONSE" | python3 -m json.tool
else
    echo -e "${RED}❌ Import logs FAILED${NC}"
    echo "$LOGS_RESPONSE"
fi
echo ""

echo ""
echo "================================"
echo -e "${GREEN}✅ Tests terminés avec succès !${NC}"
echo "================================"
