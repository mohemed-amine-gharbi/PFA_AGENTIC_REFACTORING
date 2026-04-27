@echo off
echo 🚀 Démarrage des services...

:: Démarrer le serveur Python
start "Refactoring API" cmd /k "cd pfe_agentic_refactoring && pip install -r requirements_api.txt && python api_server.py"

:: Attendre 5 secondes
timeout /t 5 /nobreak

:: Démarrer Next.js
start "Next.js App" cmd /k "cd Coach_Advisor-main\Coach_Advisor-main && npm run dev"

echo ✅ Services démarrés !
echo 📍 API Refactoring: http://localhost:8000
echo 📍 Next.js App: http://localhost:3000
echo 📍 API Docs: http://localhost:8000/docs