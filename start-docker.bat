@echo off
echo ============================================================
echo  ProctoFlex AI - Démarrage avec Docker
echo ============================================================

echo.
echo [1/4] Arrêt des services existants...
docker-compose down

echo.
echo [2/4] Nettoyage des volumes...
docker volume prune -f

echo.
echo [3/4] Build des images...
docker-compose build --no-cache

echo.
echo [4/4] Démarrage des services...
docker-compose up -d

echo.
echo ============================================================
echo  Services démarrés avec succès !
echo ============================================================
echo.
echo Backend API: http://localhost:8000
echo Frontend Web: http://localhost:3000
echo Base de données: localhost:5432
echo.
echo Pour voir les logs: docker-compose logs -f
echo Pour arrêter: docker-compose down
echo.

pause
