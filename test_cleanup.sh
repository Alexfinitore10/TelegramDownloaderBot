#!/bin/bash
# 1. Create dummy containers
docker run -d --name bot_v020_dummy alpine sleep 1000
docker run -d --name telegramdownloaderbot_dummy alpine sleep 1000

echo "Before cleanup:"
docker ps -a --format "{{.Names}}" | grep -E "bot_v|telegramdownloaderbot"

# 2. Cleanup logic
patterns=("bot_v" "telegramdownloaderbot" "tg_downloader")
for pattern in "${patterns[@]}"; do
    IDS=$(docker ps -aq --filter "name=$pattern")
    if [ -n "$IDS" ]; then
        echo "Killing $pattern..."
        docker rm -f $IDS
    fi
done

echo "After cleanup:"
docker ps -a --format "{{.Names}}" | grep -E "bot_v|telegramdownloaderbot" || echo "All gone!"
