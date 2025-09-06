"""
Service de conformité RGPD
ProctoFlex AI - Université de Monastir - ESPRIM
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import json
import hashlib
import uuid
from pathlib import Path
import shutil
import os

logger = logging.getLogger(__name__)

class DataCategory(Enum):
    """Catégories de données personnelles"""
    IDENTIFICATION = "identification"  # Nom, email, ID étudiant
    BIOMETRIC = "biometric"  # Photos, enregistrements faciaux
    BEHAVIORAL = "behavioral"  # Données de surveillance, comportement
    TECHNICAL = "technical"  # Logs, métadonnées techniques
    ACADEMIC = "academic"  # Résultats d'examens, notes

class ProcessingPurpose(Enum):
    """Finalités du traitement"""
    IDENTITY_VERIFICATION = "identity_verification"
    EXAM_SURVEILLANCE = "exam_surveillance"
    FRAUD_DETECTION = "fraud_detection"
    ACADEMIC_ASSESSMENT = "academic_assessment"
    SYSTEM_MAINTENANCE = "system_maintenance"

class LegalBasis(Enum):
    """Base légale du traitement"""
    CONSENT = "consent"
    LEGITIMATE_INTEREST = "legitimate_interest"
    CONTRACT = "contract"
    LEGAL_OBLIGATION = "legal_obligation"
    VITAL_INTERESTS = "vital_interests"

class DataSubjectRights(Enum):
    """Droits des personnes concernées"""
    ACCESS = "access"
    RECTIFICATION = "rectification"
    ERASURE = "erasure"
    RESTRICTION = "restriction"
    PORTABILITY = "portability"
    OBJECTION = "objection"

@dataclass
class ConsentRecord:
    """Enregistrement de consentement"""
    id: str
    student_id: str
    data_categories: List[DataCategory]
    processing_purposes: List[ProcessingPurpose]
    legal_basis: LegalBasis
    consent_given: bool
    consent_date: datetime
    consent_method: str  # "explicit", "implicit", "opt_in"
    withdrawal_date: Optional[datetime] = None
    consent_text: str = ""
    ip_address: str = ""
    user_agent: str = ""

@dataclass
class DataRetentionPolicy:
    """Politique de rétention des données"""
    data_category: DataCategory
    retention_period_days: int
    auto_delete: bool
    anonymization_after: Optional[int] = None  # jours avant anonymisation
    archiving_after: Optional[int] = None  # jours avant archivage

@datacart
class DataProcessingRecord:
    """Enregistrement de traitement de données"""
    id: str
    student_id: str
    data_categories: List[DataCategory]
    processing_purpose: ProcessingPurpose
    legal_basis: LegalBasis
    processing_date: datetime
    data_controller: str
    data_processor: str
    retention_until: datetime
    location: str  # "EU", "US", "Other"
    security_measures: List[str]

@dataclass
class DataSubjectRequest:
    """Demande d'un sujet de données"""
    id: str
    student_id: str
    request_type: DataSubjectRights
    request_date: datetime
    status: str  # "pending", "in_progress", "completed", "rejected"
    description: str
    response_date: Optional[datetime] = None
    response_text: str = ""
    documents_provided: List[str] = None

@dataclass
class DataBreach:
    """Incident de violation de données"""
    id: str
    breach_date: datetime
    discovery_date: datetime
    notification_date: Optional[datetime] = None
    data_categories: List[DataCategory]
    affected_subjects: int
    severity: str  # "low", "medium", "high", "critical"
    description: str
    measures_taken: List[str]
    authorities_notified: bool = False
    subjects_notified: bool = False

class GDPRComplianceService:
    """Service de conformité RGPD"""
    
    def __init__(self, data_dir: str = "data/gdpr"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration RGPD
        self.config = {
            'data_controller': 'Université de Monastir - ESPRIM',
            'data_protection_officer': 'dpo@esprim.tn',
            'supervisory_authority': 'Instance Nationale de Protection des Données Personnelles (INPDP)',
            'retention_policies': self._load_retention_policies(),
            'consent_required': True,
            'explicit_consent_required': True,
            'data_minimization': True,
            'purpose_limitation': True,
            'storage_limitation': True,
            'accuracy_requirement': True,
            'security_measures': [
                'Chiffrement des données au repos',
                'Chiffrement des données en transit',
                'Contrôle d\'accès basé sur les rôles',
                'Audit des accès',
                'Sauvegarde sécurisée',
                'Suppression sécurisée'
            ]
        }
        
        # Initialiser les fichiers de données
        self._initialize_data_files()
        
        logger.info("Service de conformité RGPD initialisé")
    
    def _load_retention_policies(self) -> List[DataRetentionPolicy]:
        """Charge les politiques de rétention par défaut"""
        return [
            DataRetentionPolicy(
                data_category=DataCategory.IDENTIFICATION,
                retention_period_days=365 * 3,  # 3 ans
                auto_delete=True,
                anonymization_after=365 * 2  # Anonymisation après 2 ans
            ),
            DataRetentionPolicy(
                data_category=DataCategory.BIOMETRIC,
                retention_period_days=90,  # 90 jours
                auto_delete=True
            ),
            DataRetentionPolicy(
                data_category=DataCategory.BEHAVIORAL,
                retention_period_days=90,  # 90 jours
                auto_delete=True
            ),
            DataRetentionPolicy(
                data_category=DataCategory.TECHNICAL,
                retention_period_days=365,  # 1 an
                auto_delete=True
            ),
            DataRetentionPolicy(
                data_category=DataCategory.ACADEMIC,
                retention_period_days=365 * 5,  # 5 ans
                auto_delete=False,  # Conservation pour obligations légales
                archiving_after=365 * 2
            )
        ]
    
    def _initialize_data_files(self):
        """Initialise les fichiers de données RGPD"""
        files = [
            'consents.json',
            'processing_records.json',
            'data_subject_requests.json',
            'data_breaches.json',
            'audit_log.json'
        ]
        
        for file in files:
            file_path = self.data_dir / file
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
    
    async def record_consent(
        self,
        student_id: str,
        data_categories: List[DataCategory],
        processing_purposes: List[ProcessingPurpose],
        legal_basis: LegalBasis,
        consent_given: bool,
        consent_method: str = "explicit",
        consent_text: str = "",
        ip_address: str = "",
        user_agent: str = ""
    ) -> ConsentRecord:
        """
        Enregistre un consentement RGPD
        
        Args:
            student_id: ID de l'étudiant
            data_categories: Catégories de données concernées
            processing_purposes: Finalités du traitement
            legal_basis: Base légale
            consent_given: Consentement donné ou non
            consent_method: Méthode de consentement
            consent_text: Texte du consentement
            ip_address: Adresse IP
            user_agent: User agent
            
        Returns:
            ConsentRecord: Enregistrement de consentement
        """
        try:
            consent_record = ConsentRecord(
                id=str(uuid.uuid4()),
                student_id=student_id,
                data_categories=data_categories,
                processing_purposes=processing_purposes,
                legal_basis=legal_basis,
                consent_given=consent_given,
                consent_date=datetime.utcnow(),
                consent_method=consent_method,
                consent_text=consent_text,
                ip_address=ip_address,
                user_agent=user_agent
            )
            
            # Sauvegarder le consentement
            await self._save_consent_record(consent_record)
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="consent_recorded",
                student_id=student_id,
                details={
                    "consent_id": consent_record.id,
                    "consent_given": consent_given,
                    "data_categories": [cat.value for cat in data_categories],
                    "purposes": [purpose.value for purpose in processing_purposes]
                }
            )
            
            logger.info(f"Consentement enregistré pour l'étudiant {student_id}")
            return consent_record
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du consentement: {e}")
            raise
    
    async def withdraw_consent(self, student_id: str, consent_id: str) -> bool:
        """
        Retire un consentement
        
        Args:
            student_id: ID de l'étudiant
            consent_id: ID du consentement
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Charger les consentements
            consents = await self._load_consent_records()
            
            # Trouver et modifier le consentement
            for consent in consents:
                if consent['id'] == consent_id and consent['student_id'] == student_id:
                    consent['withdrawal_date'] = datetime.utcnow().isoformat()
                    consent['consent_given'] = False
                    break
            else:
                logger.warning(f"Consentement {consent_id} non trouvé pour l'étudiant {student_id}")
                return False
            
            # Sauvegarder
            await self._save_consent_records(consents)
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="consent_withdrawn",
                student_id=student_id,
                details={"consent_id": consent_id}
            )
            
            logger.info(f"Consentement {consent_id} retiré pour l'étudiant {student_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du retrait du consentement: {e}")
            return False
    
    async def get_consent_status(self, student_id: str) -> Dict[str, Any]:
        """
        Obtient le statut de consentement d'un étudiant
        
        Args:
            student_id: ID de l'étudiant
            
        Returns:
            Dict: Statut de consentement
        """
        try:
            consents = await self._load_consent_records()
            student_consents = [c for c in consents if c['student_id'] == student_id]
            
            if not student_consents:
                return {
                    "has_consent": False,
                    "consent_date": None,
                    "data_categories": [],
                    "purposes": [],
                    "can_withdraw": False
                }
            
            # Prendre le consentement le plus récent
            latest_consent = max(student_consents, key=lambda x: x['consent_date'])
            
            return {
                "has_consent": latest_consent['consent_given'],
                "consent_date": latest_consent['consent_date'],
                "data_categories": latest_consent['data_categories'],
                "purposes": latest_consent['processing_purposes'],
                "can_withdraw": latest_consent['consent_given'] and not latest_consent.get('withdrawal_date'),
                "consent_id": latest_consent['id']
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du statut de consentement: {e}")
            return {"has_consent": False, "error": str(e)}
    
    async def record_data_processing(
        self,
        student_id: str,
        data_categories: List[DataCategory],
        processing_purpose: ProcessingPurpose,
        legal_basis: LegalBasis,
        data_controller: str = None,
        data_processor: str = None,
        location: str = "EU"
    ) -> DataProcessingRecord:
        """
        Enregistre un traitement de données
        
        Args:
            student_id: ID de l'étudiant
            data_categories: Catégories de données traitées
            processing_purpose: Finalité du traitement
            legal_basis: Base légale
            data_controller: Responsable du traitement
            data_processor: Sous-traitant
            location: Localisation des données
            
        Returns:
            DataProcessingRecord: Enregistrement de traitement
        """
        try:
            # Calculer la date de rétention
            retention_policy = self._get_retention_policy(data_categories[0])
            retention_until = datetime.utcnow() + timedelta(days=retention_policy.retention_period_days)
            
            processing_record = DataProcessingRecord(
                id=str(uuid.uuid4()),
                student_id=student_id,
                data_categories=data_categories,
                processing_purpose=processing_purpose,
                legal_basis=legal_basis,
                processing_date=datetime.utcnow(),
                data_controller=data_controller or self.config['data_controller'],
                data_processor=data_processor or "ProctoFlex AI System",
                retention_until=retention_until,
                location=location,
                security_measures=self.config['security_measures']
            )
            
            # Sauvegarder
            await self._save_processing_record(processing_record)
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="data_processing_recorded",
                student_id=student_id,
                details={
                    "processing_id": processing_record.id,
                    "data_categories": [cat.value for cat in data_categories],
                    "purpose": processing_purpose.value
                }
            )
            
            logger.info(f"Traitement de données enregistré pour l'étudiant {student_id}")
            return processing_record
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du traitement: {e}")
            raise
    
    async def handle_data_subject_request(
        self,
        student_id: str,
        request_type: DataSubjectRights,
        description: str,
        documents: List[str] = None
    ) -> DataSubjectRequest:
        """
        Traite une demande d'un sujet de données
        
        Args:
            student_id: ID de l'étudiant
            request_type: Type de demande
            description: Description de la demande
            documents: Documents fournis
            
        Returns:
            DataSubjectRequest: Demande enregistrée
        """
        try:
            request = DataSubjectRequest(
                id=str(uuid.uuid4()),
                student_id=student_id,
                request_type=request_type,
                request_date=datetime.utcnow(),
                status="pending",
                description=description,
                documents_provided=documents or []
            )
            
            # Sauvegarder
            await self._save_data_subject_request(request)
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="data_subject_request_received",
                student_id=student_id,
                details={
                    "request_id": request.id,
                    "request_type": request_type.value,
                    "description": description
                }
            )
            
            logger.info(f"Demande de sujet de données enregistrée: {request.id}")
            return request
            
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement de la demande: {e}")
            raise
    
    async def process_data_subject_request(
        self,
        request_id: str,
        status: str,
        response_text: str = "",
        documents_provided: List[str] = None
    ) -> bool:
        """
        Traite une demande de sujet de données
        
        Args:
            request_id: ID de la demande
            status: Nouveau statut
            response_text: Texte de réponse
            documents_provided: Documents fournis
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Charger les demandes
            requests = await self._load_data_subject_requests()
            
            # Trouver et modifier la demande
            for request in requests:
                if request['id'] == request_id:
                    request['status'] = status
                    request['response_date'] = datetime.utcnow().isoformat()
                    request['response_text'] = response_text
                    if documents_provided:
                        request['documents_provided'] = documents_provided
                    break
            else:
                logger.warning(f"Demande {request_id} non trouvée")
                return False
            
            # Sauvegarder
            await self._save_data_subject_requests(requests)
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="data_subject_request_processed",
                student_id=request['student_id'],
                details={
                    "request_id": request_id,
                    "status": status,
                    "response_text": response_text
                }
            )
            
            logger.info(f"Demande {request_id} traitée avec le statut: {status}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la demande: {e}")
            return False
    
    async def report_data_breach(
        self,
        breach_date: datetime,
        data_categories: List[DataCategory],
        affected_subjects: int,
        severity: str,
        description: str,
        measures_taken: List[str]
    ) -> DataBreach:
        """
        Signale une violation de données
        
        Args:
            breach_date: Date de la violation
            data_categories: Catégories de données concernées
            affected_subjects: Nombre de sujets affectés
            severity: Gravité de la violation
            description: Description de la violation
            measures_taken: Mesures prises
            
        Returns:
            DataBreach: Violation enregistrée
        """
        try:
            breach = DataBreach(
                id=str(uuid.uuid4()),
                breach_date=breach_date,
                discovery_date=datetime.utcnow(),
                data_categories=data_categories,
                affected_subjects=affected_subjects,
                severity=severity,
                description=description,
                measures_taken=measures_taken
            )
            
            # Sauvegarder
            await self._save_data_breach(breach)
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="data_breach_reported",
                student_id="system",
                details={
                    "breach_id": breach.id,
                    "severity": severity,
                    "affected_subjects": affected_subjects
                }
            )
            
            # Notifier les autorités si nécessaire
            if severity in ["high", "critical"]:
                await self._notify_supervisory_authority(breach)
            
            logger.warning(f"Violation de données signalée: {breach.id}")
            return breach
            
        except Exception as e:
            logger.error(f"Erreur lors du signalement de la violation: {e}")
            raise
    
    async def cleanup_expired_data(self) -> Dict[str, int]:
        """
        Nettoie les données expirées selon les politiques de rétention
        
        Returns:
            Dict: Nombre de données supprimées par catégorie
        """
        try:
            cleanup_stats = {}
            
            for policy in self.config['retention_policies']:
                category = policy.data_category.value
                cutoff_date = datetime.utcnow() - timedelta(days=policy.retention_period_days)
                
                # Supprimer les données expirées
                deleted_count = await self._delete_expired_data(category, cutoff_date)
                cleanup_stats[category] = deleted_count
                
                logger.info(f"Données {category} supprimées: {deleted_count}")
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="data_cleanup",
                student_id="system",
                details={"cleanup_stats": cleanup_stats}
            )
            
            return cleanup_stats
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des données: {e}")
            return {}
    
    async def anonymize_data(self, student_id: str, data_categories: List[DataCategory]) -> bool:
        """
        Anonymise les données d'un étudiant
        
        Args:
            student_id: ID de l'étudiant
            data_categories: Catégories à anonymiser
            
        Returns:
            bool: Succès de l'opération
        """
        try:
            # Générer un hash anonyme
            anonymous_id = hashlib.sha256(f"{student_id}_{datetime.utcnow()}".encode()).hexdigest()[:16]
            
            # Anonymiser les données
            for category in data_categories:
                await self._anonymize_category_data(student_id, category, anonymous_id)
            
            # Enregistrer l'audit
            await self._log_audit_event(
                event_type="data_anonymized",
                student_id=student_id,
                details={
                    "anonymous_id": anonymous_id,
                    "data_categories": [cat.value for cat in data_categories]
                }
            )
            
            logger.info(f"Données anonymisées pour l'étudiant {student_id}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'anonymisation: {e}")
            return False
    
    async def generate_privacy_report(self, student_id: str) -> Dict[str, Any]:
        """
        Génère un rapport de confidentialité pour un étudiant
        
        Args:
            student_id: ID de l'étudiant
            
        Returns:
            Dict: Rapport de confidentialité
        """
        try:
            # Récupérer les données de l'étudiant
            consents = await self._load_consent_records()
            processing_records = await self._load_processing_records()
            requests = await self._load_data_subject_requests()
            
            student_consents = [c for c in consents if c['student_id'] == student_id]
            student_processing = [p for p in processing_records if p['student_id'] == student_id]
            student_requests = [r for r in requests if r['student_id'] == student_id]
            
            return {
                "student_id": student_id,
                "report_date": datetime.utcnow().isoformat(),
                "consent_status": await self.get_consent_status(student_id),
                "data_processing_history": student_processing,
                "data_subject_requests": student_requests,
                "data_categories_processed": list(set([
                    cat for record in student_processing 
                    for cat in record['data_categories']
                ])),
                "retention_policies": [
                    {
                        "category": policy.data_category.value,
                        "retention_days": policy.retention_period_days,
                        "auto_delete": policy.auto_delete
                    }
                    for policy in self.config['retention_policies']
                ],
                "rights": {
                    "access": True,
                    "rectification": True,
                    "erasure": True,
                    "restriction": True,
                    "portability": True,
                    "objection": True
                },
                "contact_info": {
                    "data_controller": self.config['data_controller'],
                    "dpo_email": self.config['data_protection_officer'],
                    "supervisory_authority": self.config['supervisory_authority']
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération du rapport: {e}")
            return {"error": str(e)}
    
    def _get_retention_policy(self, data_category: DataCategory) -> DataRetentionPolicy:
        """Obtient la politique de rétention pour une catégorie"""
        for policy in self.config['retention_policies']:
            if policy.data_category == data_category:
                return policy
        # Politique par défaut
        return DataRetentionPolicy(
            data_category=data_category,
            retention_period_days=365,
            auto_delete=True
        )
    
    async def _save_consent_record(self, consent: ConsentRecord):
        """Sauvegarde un enregistrement de consentement"""
        consents = await self._load_consent_records()
        consents.append(asdict(consent))
        await self._save_consent_records(consents)
    
    async def _load_consent_records(self) -> List[Dict]:
        """Charge les enregistrements de consentement"""
        file_path = self.data_dir / 'consents.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _save_consent_records(self, consents: List[Dict]):
        """Sauvegarde les enregistrements de consentement"""
        file_path = self.data_dir / 'consents.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(consents, f, ensure_ascii=False, indent=2, default=str)
    
    async def _save_processing_record(self, record: DataProcessingRecord):
        """Sauvegarde un enregistrement de traitement"""
        records = await self._load_processing_records()
        records.append(asdict(record))
        await self._save_processing_records(records)
    
    async def _load_processing_records(self) -> List[Dict]:
        """Charge les enregistrements de traitement"""
        file_path = self.data_dir / 'processing_records.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _save_processing_records(self, records: List[Dict]):
        """Sauvegarde les enregistrements de traitement"""
        file_path = self.data_dir / 'processing_records.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(records, f, ensure_ascii=False, indent=2, default=str)
    
    async def _save_data_subject_request(self, request: DataSubjectRequest):
        """Sauvegarde une demande de sujet de données"""
        requests = await self._load_data_subject_requests()
        requests.append(asdict(request))
        await self._save_data_subject_requests(requests)
    
    async def _load_data_subject_requests(self) -> List[Dict]:
        """Charge les demandes de sujets de données"""
        file_path = self.data_dir / 'data_subject_requests.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _save_data_subject_requests(self, requests: List[Dict]):
        """Sauvegarde les demandes de sujets de données"""
        file_path = self.data_dir / 'data_subject_requests.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(requests, f, ensure_ascii=False, indent=2, default=str)
    
    async def _save_data_breach(self, breach: DataBreach):
        """Sauvegarde une violation de données"""
        breaches = await self._load_data_breaches()
        breaches.append(asdict(breach))
        await self._save_data_breaches(breaches)
    
    async def _load_data_breaches(self) -> List[Dict]:
        """Charge les violations de données"""
        file_path = self.data_dir / 'data_breaches.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    async def _save_data_breaches(self, breaches: List[Dict]):
        """Sauvegarde les violations de données"""
        file_path = self.data_dir / 'data_breaches.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(breaches, f, ensure_ascii=False, indent=2, default=str)
    
    async def _log_audit_event(self, event_type: str, student_id: str, details: Dict[str, Any]):
        """Enregistre un événement d'audit"""
        audit_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "student_id": student_id,
            "details": details
        }
        
        file_path = self.data_dir / 'audit_log.json'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except FileNotFoundError:
            logs = []
        
        logs.append(audit_log)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2, default=str)
    
    async def _delete_expired_data(self, category: str, cutoff_date: datetime) -> int:
        """Supprime les données expirées d'une catégorie"""
        # En production, implémenter la suppression réelle des données
        # Pour l'instant, simulation
        return 0
    
    async def _anonymize_category_data(self, student_id: str, category: DataCategory, anonymous_id: str):
        """Anonymise les données d'une catégorie"""
        # En production, implémenter l'anonymisation réelle
        pass
    
    async def _notify_supervisory_authority(self, breach: DataBreach):
        """Notifie l'autorité de contrôle"""
        # En production, envoyer la notification
        logger.warning(f"Notification à l'autorité de contrôle requise pour la violation {breach.id}")

# Instance globale du service
gdpr_compliance_service = GDPRComplianceService()
