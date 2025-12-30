#!/bin/bash

# 🚀 Script de Démarrage Rapide - API NPP
# Usage: ./start.sh

echo "🏥 API Nomenclature Produits Pharmaceutiques"
echo "=============================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Environnement virtuel non trouvé !${NC}"
    echo "Créez-le avec : python3 -m venv venv"
    exit 1
fi

# Activer l'environnement virtuel
echo -e "${BLUE}📦 Activation de l'environnement virtuel...${NC}"
source venv/bin/activate

# Vérifier si les dépendances sont installées
if ! python -c "import fastapi" 2>/dev/null; then
    echo -e "${RED}❌ Dépendances non installées !${NC}"
    echo "Installez-les avec : pip install -r requirements.txt"
    exit 1
fi

# Démarrer le serveur
echo -e "${GREEN}✅ Démarrage du serveur...${NC}"
echo ""
echo -e "${BLUE}📍 API accessible sur:${NC}"
echo "   • http://localhost:8000"
echo "   • Documentation: http://localhost:8000/docs"
echo "   • ReDoc: http://localhost:8000/redoc"
echo ""
echo -e "${BLUE}🔐 Compte admin par défaut:${NC}"
echo "   • Email: admin@nomenclature.dz"
echo "   • Password: Admin2025!"
echo ""
echo -e "${GREEN}Press CTRL+C to stop${NC}"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
