#!/bin/bash

echo "🧹 Cleaning bot cache & sessions..."

# Hapus semua __pycache__
find . -type d -name "__pycache__" -exec rm -rf {} +

# Hapus file .pyc dan .pyo
find . -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete

# Hapus folder session dan session-journal (jika ada)
if [ -d "session" ]; then
    rm -rf session
    echo "🗑️ Removed session/"
fi

if [ -d "session-journal" ]; then
    rm -rf session-journal
    echo "🗑️ Removed session-journal/"
fi

echo "✅ Clean complete!"
