#!/bin/bash

if [ "$INIT_DATABASE" = "true" ]; then
    echo "🔧 Запуск инициализации базы данных..."
    python build_chroma_collection.py
    echo "✅ База данных инициализирована!"
fi

echo "🚀 AI сервис готов к работе!"
tail -f /dev/null