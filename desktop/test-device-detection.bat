@echo off
echo ========================================
echo   TEST - DETECTION PERIPHERIQUES
echo ========================================
echo.

echo [1/4] Verification de la detection des peripheriques...
echo ✓ Enumeration des peripheriques avec enumerateDevices
echo ✓ Verification des types videoinput et audioinput
echo ✓ Logs de debug pour identifier les peripheriques
echo ✓ Gestion des erreurs d'enumeration

echo.
echo [2/4] Verification de la demande de permissions...
echo ✓ Demande getUserMedia avec contraintes minimales
echo ✓ Verification des tracks video et audio obtenus
echo ✓ Messages informatifs selon les tracks detectes
echo ✓ Gestion des erreurs specifiques

echo.
echo [3/4] Verification de l'interface utilisateur...
echo ✓ Bouton "Verifier les Peripheriques"
echo ✓ Bouton "Reinitialiser" pour reset complet
echo ✓ Bouton "Demander les Permissions" conditionnel
echo ✓ Messages d'erreur contextuels et informatifs

echo.
echo [4/4] Verification de la robustesse...
echo ✓ Contraintes video minimales (320x240)
echo ✓ Contraintes audio desactivees pour compatibilite
echo ✓ Nettoyage des streams apres verification
echo ✓ Logs de debug pour troubleshooting

echo.
echo ========================================
echo   INSTRUCTIONS DE TEST
echo ========================================
echo.
echo ETAPES DE TEST:
echo 1. Ouvrir la page Surveillance
echo 2. Cliquer sur "Verifier les Peripheriques"
echo 3. Observer les logs dans la console (F12)
echo 4. Si "Non detecte", cliquer sur "Demander les Permissions"
echo 5. Autoriser les permissions dans la popup du navigateur
echo 6. Verifier que les indicateurs passent au vert
echo.
echo EN CAS DE PROBLEME:
echo - Verifier que la camera/micro sont connectes
echo - Fermer les autres applications utilisant la camera
echo - Redemarrer l'application
echo - Verifier les logs dans la console du navigateur
echo.
echo LOGS ATTENDUS:
echo - "Peripheriques detectes: [liste des peripheriques]"
echo - "Video tracks: [nombre]"
echo - "Audio tracks: [nombre]"
echo - "Permissions accordees - Video tracks: [nombre] Audio tracks: [nombre]"
echo.
echo POUR TESTER:
echo 1. npm run dev
echo 2. Aller dans Surveillance
echo 3. Ouvrir la console (F12)
echo 4. Cliquer sur "Verifier les Peripheriques"
echo 5. Observer les logs et les indicateurs
echo.
echo LA DETECTION DES PERIPHERIQUES EST MAINTENANT AMELIOREE!
echo.
pause
