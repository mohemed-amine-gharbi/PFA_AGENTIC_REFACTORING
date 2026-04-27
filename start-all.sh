#!/bin/bash

echo "🚀 Démarrage des services..."

# Démarrer le serveur Python
cd pfe_agentic_refactoring
pip install -r requirements_api.txt
python api_server.py &
API_PID=$!

# Attendre 5 secondes
sleep 5

# Démarrer Next.js
cd ../Coach_Advisor-main/Coach_Advisor-main
npm run dev &
NEXT_PID=$!

echo "✅ Services démarrés !"
echo "📍 API Refactoring: http://localhost:8000"
echo "📍 Next.js App: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"

# Attendre les processus
wait $API_PID $NEXT_PID