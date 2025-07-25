#!/bin/bash

echo "🤖 KI Song-Agent wird gestartet..."
echo ""

# Prüfe ob Ollama läuft
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ Ollama ist nicht erreichbar!"
    echo "Bitte starte Ollama mit: ollama serve"
    echo "Und lade das Modell: ollama pull gemma3n:e4b"
    exit 1
fi

echo "✅ Ollama ist erreichbar"

# Prüfe ob secrets.toml existiert
if [ ! -f ".streamlit/secrets.toml" ]; then
    echo "❌ secrets.toml nicht gefunden!"
    echo "Bitte kopiere .streamlit/secrets.toml.example zu .streamlit/secrets.toml"
    echo "und füge deinen Suno API-Key ein."
    exit 1
fi

echo "✅ Konfiguration gefunden"
echo ""
echo "🚀 Starte KI Song-Agent..."
echo "Öffne http://localhost:8501 in deinem Browser"
echo ""

streamlit run song_agent.py

