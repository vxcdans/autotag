#!/bin/bash

echo "🤖 Starting LiveGram Bot..."

# Masuk ke folder script
cd "$(dirname "$0")"

# Aktifkan venv kalau ada
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "🐍 Virtualenv activated"
fi

# Jalankan clean dulu kalau ada
if [ -f "clean.sh" ]; then
    echo "🧹 Running clean.sh"
    bash clean.sh
fi

# Auto-restart loop
while true; do
    echo "🚀 Bot starting..."
    python3 bot.py

    echo "⚠️ Bot stopped! Restarting in 5 seconds..."
    sleep 5
done
