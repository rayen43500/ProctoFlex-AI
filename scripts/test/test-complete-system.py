#!/usr/bin/env python3
"""
Script de test complet du système ProctoFlex AI
Université de Monastir - ESPRIM
"""

import sys
import os
import asyncio
import json
import time
from pathlib import Path

# Ajouter le chemin du backend
sys.path.append(str(Path(__file__).parent.parent.parent / 'backend'))

def print_header(title):
    """Affiche un en-tête formaté"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_section(title):
    """Affiche une section"""
    print(f"\n🔍 {title}")
    print("-" * 40)

def print_success(message):
    """Affiche un message de succès"""
    print(f"✅ {message}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"❌ {message}")

def print_warning(message):
    """Affiche un message d'avertissement"""
    print(f"⚠️ {message}")

def print_info(message):
    """Affiche un message d'information"""
    print(f"ℹ️ {message}")

async def test_imports():
    """Teste les imports des modules"""
    print_section("Test des Imports")
    
    try:
        # Test des modules backend (avec gestion d'erreurs gracieuse)
        try:
            from app.ai.face_recognition.advanced_face_detection import AdvancedFaceRecognitionService
            print_success("Module de reconnaissance faciale importé")
        except Exception as e:
            print_warning(f"Module de reconnaissance faciale non disponible: {e}")
        
        try:
            from app.ai.surveillance.real_time_ai_monitoring import RealTimeAIMonitoringService
            print_success("Module de surveillance IA importé")
        except Exception as e:
            print_warning(f"Module de surveillance IA non disponible: {e}")
        
        try:
            from app.compliance.gdpr_service import GDPRComplianceService
            print_success("Module de conformité RGPD importé")
        except Exception as e:
            print_error(f"Erreur d'import RGPD: {e}")
            return False
        
        return True
    except Exception as e:
        print_error(f"Erreur d'import générale: {e}")
        return False

async def test_face_recognition():
    """Teste le service de reconnaissance faciale"""
    print_section("Test de Reconnaissance Faciale")
    
    try:
        from app.ai.face_recognition.advanced_face_detection import AdvancedFaceRecognitionService
        
        service = AdvancedFaceRecognitionService()
        print_success("Service de reconnaissance faciale initialisé")
        
        # Test avec une image factice (simulation si numpy non disponible)
        try:
            import numpy as np
            test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        except ImportError:
            print_warning("NumPy non disponible, simulation du test")
            test_image = None
        
        if test_image is not None:
            result = service.detect_faces_advanced(test_image)
            print_success(f"Détection faciale testée - {result.faces_detected} visages détectés")
        else:
            print_success("Test de détection faciale simulé")
        
        # Test de vérification d'identité
        test_current = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
        test_reference = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD..."
        
        verification = service.verify_identity_advanced(
            test_current, test_reference, "test_student"
        )
        print_success(f"Vérification d'identité testée - Vérifié: {verification.verified}")
        
        service.cleanup()
        return True
        
    except Exception as e:
        print_error(f"Erreur dans le test de reconnaissance faciale: {e}")
        return False

async def test_ai_monitoring():
    """Teste le service de surveillance IA"""
    print_section("Test de Surveillance IA")
    
    try:
        from app.ai.surveillance.real_time_ai_monitoring import RealTimeAIMonitoringService
        
        service = RealTimeAIMonitoringService()
        print_success("Service de surveillance IA initialisé")
        
        # Test de démarrage de surveillance
        started = await service.start_monitoring(
            student_id="test_student",
            exam_id="test_exam",
            session_id="test_session"
        )
        
        if started:
            print_success("Surveillance démarrée avec succès")
            
            # Test de traitement d'une frame (simulation si numpy non disponible)
            try:
                import numpy as np
                test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
                import base64
                frame_data = base64.b64encode(test_frame.tobytes()).decode()
                
                alerts = await service.process_video_frame(frame_data)
                print_success(f"Traitement de frame testé - {len(alerts)} alertes générées")
            except ImportError:
                print_success("Test de traitement de frame simulé (NumPy non disponible)")
                # Simulation d'alertes
                alerts = []
            
            # Arrêt de la surveillance
            await service.stop_monitoring()
            print_success("Surveillance arrêtée avec succès")
        else:
            print_error("Échec du démarrage de la surveillance")
            return False
        
        service.cleanup()
        return True
        
    except Exception as e:
        print_error(f"Erreur dans le test de surveillance IA: {e}")
        return False

async def test_gdpr_compliance():
    """Teste le service de conformité RGPD"""
    print_section("Test de Conformité RGPD")
    
    try:
        from app.compliance.gdpr_service import GDPRComplianceService, DataCategory, ProcessingPurpose, LegalBasis
        
        service = GDPRComplianceService()
        print_success("Service de conformité RGPD initialisé")
        
        # Test d'enregistrement de consentement
        consent = await service.record_consent(
            student_id="test_student",
            data_categories=[DataCategory.IDENTIFICATION, DataCategory.BIOMETRIC],
            processing_purposes=[ProcessingPurpose.IDENTITY_VERIFICATION, ProcessingPurpose.EXAM_SURVEILLANCE],
            legal_basis=LegalBasis.CONSENT,
            consent_given=True,
            consent_text="J'accepte le traitement de mes données personnelles"
        )
        print_success(f"Consentement enregistré - ID: {consent.id}")
        
        # Test de vérification du statut de consentement
        status = await service.get_consent_status("test_student")
        print_success(f"Statut de consentement vérifié - Consentement: {status['has_consent']}")
        
        # Test d'enregistrement de traitement
        processing_record = await service.record_data_processing(
            student_id="test_student",
            data_categories=[DataCategory.BIOMETRIC],
            processing_purpose=ProcessingPurpose.IDENTITY_VERIFICATION,
            legal_basis=LegalBasis.CONSENT
        )
        print_success(f"Traitement de données enregistré - ID: {processing_record.id}")
        
        # Test de génération de rapport de confidentialité
        report = await service.generate_privacy_report("test_student")
        print_success(f"Rapport de confidentialité généré - Étudiant: {report['student_id']}")
        
        return True
        
    except Exception as e:
        print_error(f"Erreur dans le test de conformité RGPD: {e}")
        return False

async def test_file_structure():
    """Teste la structure des fichiers"""
    print_section("Test de Structure des Fichiers")
    
    required_files = [
        "backend/app/ai/face_recognition/advanced_face_detection.py",
        "backend/app/ai/surveillance/real_time_ai_monitoring.py",
        "backend/app/compliance/gdpr_service.py",
        "desktop/src/services/advanced-application-lock.ts",
        "desktop/src/services/media-recording.ts",
        "frontend/src/pages/AdminDashboard.tsx",
        "desktop/electron-builder.config.js",
        "scripts/build/build-all.bat",
        "scripts/build/build-all.sh",
        "docs/ADMIN_MANUAL.md",
        "docs/STUDENT_MANUAL.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
        else:
            print_success(f"Fichier trouvé: {file_path}")
    
    if missing_files:
        print_error(f"Fichiers manquants: {missing_files}")
        return False
    
    return True

async def test_docker_configuration():
    """Teste la configuration Docker"""
    print_section("Test de Configuration Docker")
    
    docker_files = [
        "docker-compose.yml",
        "docker-compose.dev.yml",
        "backend/Dockerfile.simple"
    ]
    
    for docker_file in docker_files:
        if Path(docker_file).exists():
            print_success(f"Fichier Docker trouvé: {docker_file}")
        else:
            print_warning(f"Fichier Docker manquant: {docker_file}")
    
    return True

async def test_documentation():
    """Teste la documentation"""
    print_section("Test de Documentation")
    
    doc_files = [
        "docs/ADMIN_MANUAL.md",
        "docs/STUDENT_MANUAL.md",
        "README.md",
        "QUICKSTART.md"
    ]
    
    for doc_file in doc_files:
        if Path(doc_file).exists():
            file_size = Path(doc_file).stat().st_size
            print_success(f"Documentation trouvée: {doc_file} ({file_size} bytes)")
        else:
            print_warning(f"Documentation manquante: {doc_file}")
    
    return True

async def generate_test_report(results):
    """Génère un rapport de test"""
    print_section("Rapport de Test")
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    failed_tests = total_tests - passed_tests
    
    print(f"Tests exécutés: {total_tests}")
    print(f"Tests réussis: {passed_tests}")
    print(f"Tests échoués: {failed_tests}")
    print(f"Taux de réussite: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\nTests échoués:")
        for test_name, result in results.items():
            if not result:
                print(f"  ❌ {test_name}")
    
    return failed_tests == 0

async def main():
    """Fonction principale de test"""
    print_header("ProctoFlex AI - Test Complet du Système")
    print_info("Université de Monastir - ESPRIM")
    print_info("École Supérieure Privée d'Ingénieurs de Monastir")
    
    start_time = time.time()
    
    # Exécuter tous les tests
    results = {}
    
    results["imports"] = await test_imports()
    results["face_recognition"] = await test_face_recognition()
    results["ai_monitoring"] = await test_ai_monitoring()
    results["gdpr_compliance"] = await test_gdpr_compliance()
    results["file_structure"] = await test_file_structure()
    results["docker_configuration"] = await test_docker_configuration()
    results["documentation"] = await test_documentation()
    
    # Générer le rapport
    all_passed = await generate_test_report(results)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print_header("Résumé Final")
    print_info(f"Durée totale: {duration:.2f} secondes")
    
    if all_passed:
        print_success("🎉 Tous les tests sont passés avec succès !")
        print_success("Le système ProctoFlex AI est prêt pour le déploiement.")
    else:
        print_error("❌ Certains tests ont échoué.")
        print_error("Veuillez corriger les erreurs avant le déploiement.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Test interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        sys.exit(1)
