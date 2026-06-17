#!/bin/bash

# Script di verifica post-aggiornamento per TelegramDownloaderBot
# Da eseguire sul server remoto (.99)

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "🔍 Avvio verifica integrità v0.2.1..."

# 1. Verifica Versione
if [ -f "version.txt" ]; then
    VERSION=$(cat version.txt)
    if [ "$VERSION" == "0.2.1" ]; then
        echo -e "${GREEN}✅ Versione corretta: $VERSION${NC}"
    else
        echo -e "${RED}❌ Versione errata: $VERSION (attesa 0.2.1)${NC}"
    fi
else
    echo -e "${RED}❌ File version.txt non trovato!${NC}"
fi

# 2. Verifica Docker
echo "🐳 Verifica container Docker..."
CONTAINER_INFO=$(docker ps -a --filter "name=tg_downloader_bot" --format "{{.Names}}|{{.Status}}")

if [[ "$CONTAINER_INFO" == *"tg_downloader_bot"* ]] && [[ "$CONTAINER_INFO" == *"Up"* ]]; then
    echo -e "${GREEN}✅ Container 'tg_downloader_bot' in esecuzione${NC}"
else
    echo -e "${RED}❌ Container 'tg_downloader_bot' non è in esecuzione!${NC}"
fi

# 3. Verifica implementazione Codice (Grep chirurgico)
echo "💻 Verifica modifiche critiche..."

# Verifica Fallback TikTok
if grep -q "async def _tiktok_fallback" core/downloader.py; then
    echo -e "${GREEN}✅ Metodo Fallback TikTok presente${NC}"
else
    echo -e "${RED}❌ Metodo Fallback TikTok mancante in core/downloader.py${NC}"
fi

# Verifica Requests in requirements
if grep -q "requests" requirements.txt; then
    echo -e "${GREEN}✅ Dipendenza 'requests' presente${NC}"
else
    echo -e "${RED}❌ Dipendenza 'requests' mancante in requirements.txt${NC}"
fi

# Verifica Countdown Deltarune (nuova logica oraria)
if grep -q "current_hour != last_sent_hour" main.py; then
    echo -e "${GREEN}✅ Logica Countdown orario (Deltarune) presente${NC}"
else
    echo -e "${RED}❌ Logica Countdown orario mancante in main.py${NC}"
fi

# 4. Verifica Log
echo "📝 Controllo log per errori di avvio..."
docker logs --tail=20 tg_downloader_bot
