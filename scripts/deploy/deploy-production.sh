#!/bin/bash
# Script de déploiement en production
# ProctoFlex AI - Université de Monastir - ESPRIM

set -e  # Arrêter en cas d'erreur

echo "========================================"
echo "   ProctoFlex AI - Déploiement Production"
echo "   Université de Monastir - ESPRIM"
echo "========================================"
echo

# Configuration
PROJECT_NAME="proctoflex-ai"
VERSION="1.0.0"
ENVIRONMENT="production"
BACKUP_DIR="/backup/proctoflex-ai"
LOG_DIR="/var/log/proctoflex-ai"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier les permissions
    if ! docker info &> /dev/null; then
        log_error "Permissions Docker insuffisantes"
        exit 1
    fi
    
    log_success "Prérequis vérifiés"
}

# Sauvegarde des données existantes
backup_existing_data() {
    log_info "Sauvegarde des données existantes..."
    
    # Créer le répertoire de sauvegarde
    mkdir -p "$BACKUP_DIR"
    
    # Sauvegarder la base de données
    if docker ps | grep -q "proctoflex-postgres"; then
        log_info "Sauvegarde de la base de données..."
    docker exec proctoflex-postgres pg_dump -U postgres proctoflex > "$BACKUP_DIR/database_backup_$(date +%Y%m%d_%H%M%S).sql"
        log_success "Base de données sauvegardée"
    fi
    
    # Sauvegarder les fichiers de configuration
    if [ -d "config" ]; then
        cp -r config "$BACKUP_DIR/config_backup_$(date +%Y%m%d_%H%M%S)"
        log_success "Configuration sauvegardée"
    fi
    
    # Sauvegarder les logs
    if [ -d "logs" ]; then
        cp -r logs "$BACKUP_DIR/logs_backup_$(date +%Y%m%d_%H%M%S)"
        log_success "Logs sauvegardés"
    fi
}

# Arrêt des services existants
stop_existing_services() {
    log_info "Arrêt des services existants..."
    
    # Arrêter Docker Compose
    if [ -f "docker-compose.yml" ]; then
        docker-compose down --remove-orphans
        log_success "Services Docker arrêtés"
    fi
    
    # Arrêter les processus Python
    pkill -f "python.*main_simple.py" || true
    pkill -f "uvicorn.*main_simple" || true
    log_success "Processus Python arrêtés"
}

# Construction des images Docker
build_docker_images() {
    log_info "Construction des images Docker..."
    
    # Construire l'image backend
    docker build -f backend/Dockerfile.simple -t proctoflex-backend:latest backend/
    log_success "Image backend construite"
    
    # Construire l'image frontend
    docker build -f frontend/Dockerfile -t proctoflex-frontend:latest frontend/
    log_success "Image frontend construite"
    
    # Construire l'image desktop (si nécessaire)
    if [ -f "desktop/Dockerfile" ]; then
        docker build -f desktop/Dockerfile -t proctoflex-desktop:latest desktop/
        log_success "Image desktop construite"
    fi
}

# Configuration de l'environnement de production
configure_production() {
    log_info "Configuration de l'environnement de production..."
    
    # Créer le fichier .env de production
    cat > .env.production << EOF
# Configuration de production
NODE_ENV=production
ENVIRONMENT=production

# Base de données
DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD:-secure_password}@postgres:5432/proctoflex
DATABASE_TEST_URL=postgresql://postgres:${POSTGRES_PASSWORD:-secure_password}@postgres:5432/proctoflex_test

# Redis
REDIS_URL=redis://redis:6379

# Sécurité
SECRET_KEY=${SECRET_KEY:-$(openssl rand -hex 32)}
JWT_SECRET=${JWT_SECRET:-$(openssl rand -hex 32)}

# CORS
CORS_ORIGINS=["https://proctoflex.ai", "https://admin.proctoflex.ai"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/proctoflex-ai/app.log

# Surveillance IA
AI_MODEL_PATH=/app/models
FACE_DETECTION_CONFIDENCE=0.7
GAZE_TRACKING_SENSITIVITY=0.8

# RGPD
GDPR_ENABLED=true
DATA_RETENTION_DAYS=90
AUTO_DELETE_ENABLED=true

# Monitoring
HEALTH_CHECK_INTERVAL=30
METRICS_ENABLED=true
EOF

    log_success "Configuration de production créée"
}

# Déploiement des services
deploy_services() {
    log_info "Déploiement des services..."
    
    # Créer les répertoires nécessaires
    mkdir -p "$LOG_DIR"
    mkdir -p "data/gdpr"
    mkdir -p "uploads"
    
    # Déployer avec Docker Compose
    docker-compose -f docker-compose.yml up -d
    
    # Attendre que les services soient prêts
    log_info "Attente du démarrage des services..."
    sleep 30
    
    # Vérifier le statut des services
    if docker-compose ps | grep -q "Up"; then
        log_success "Services déployés avec succès"
    else
        log_error "Échec du déploiement des services"
        exit 1
    fi
}

# Configuration de la base de données
setup_database() {
    log_info "Configuration de la base de données..."
    
    # Attendre que PostgreSQL soit prêt
    until docker exec proctoflex-postgres pg_isready -U postgres; do
        log_info "Attente de PostgreSQL..."
        sleep 5
    done
    
    # Exécuter les migrations
    if [ -f "backend/init.sql" ]; then
    docker exec -i proctoflex-postgres psql -U postgres -d proctoflex < backend/init.sql
        log_success "Base de données initialisée"
    fi
    
    # Créer les utilisateurs de test
    docker exec proctoflex-postgres psql -U postgres -d proctoflex -c "
        INSERT INTO users (email, username, full_name, hashed_password, role) 
        VALUES ('admin@esprim.tn', 'admin', 'Administrateur', '\$2b\$12\$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.8K2', 'admin')
        ON CONFLICT (email) DO NOTHING;
    "
    log_success "Utilisateurs de test créés"
}

# Configuration du monitoring
setup_monitoring() {
    log_info "Configuration du monitoring..."
    
    # Créer le script de monitoring
    cat > /usr/local/bin/proctoflex-monitor.sh << 'EOF'
#!/bin/bash
# Script de monitoring ProctoFlex AI

LOG_FILE="/var/log/proctoflex-ai/monitor.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

# Vérifier les services Docker
if ! docker ps | grep -q "proctoflex-postgres"; then
    echo "[$DATE] ERREUR: PostgreSQL n'est pas en cours d'exécution" >> $LOG_FILE
fi

if ! docker ps | grep -q "proctoflex-redis"; then
    echo "[$DATE] ERREUR: Redis n'est pas en cours d'exécution" >> $LOG_FILE
fi

if ! docker ps | grep -q "proctoflex-backend"; then
    echo "[$DATE] ERREUR: Backend n'est pas en cours d'exécution" >> $LOG_FILE
fi

# Vérifier l'espace disque
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "[$DATE] ATTENTION: Utilisation disque élevée: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Vérifier la mémoire
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEM_USAGE -gt 80 ]; then
    echo "[$DATE] ATTENTION: Utilisation mémoire élevée: ${MEM_USAGE}%" >> $LOG_FILE
fi
EOF

    chmod +x /usr/local/bin/proctoflex-monitor.sh
    
    # Ajouter au crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/proctoflex-monitor.sh") | crontab -
    
    log_success "Monitoring configuré"
}

# Tests de validation
run_validation_tests() {
    log_info "Exécution des tests de validation..."
    
    # Test de connectivité
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "API backend accessible"
    else
        log_error "API backend non accessible"
        return 1
    fi
    
    # Test de la base de données
    if docker exec proctoflex-postgres psql -U postgres -d proctoflex -c "SELECT 1;" > /dev/null 2>&1; then
        log_success "Base de données accessible"
    else
        log_error "Base de données non accessible"
        return 1
    fi
    
    # Test de Redis
    if docker exec proctoflex-redis redis-cli ping | grep -q "PONG"; then
        log_success "Redis accessible"
    else
        log_error "Redis non accessible"
        return 1
    fi
    
    log_success "Tous les tests de validation sont passés"
}

# Configuration du pare-feu
configure_firewall() {
    log_info "Configuration du pare-feu..."
    
    # Ouvrir les ports nécessaires
    if command -v ufw &> /dev/null; then
        ufw allow 80/tcp   # HTTP
        ufw allow 443/tcp  # HTTPS
        ufw allow 8000/tcp # API Backend
        ufw allow 5432/tcp # PostgreSQL
        ufw allow 6379/tcp # Redis
        log_success "Pare-feu configuré"
    else
        log_warning "UFW non disponible, configuration manuelle requise"
    fi
}

# Configuration SSL/TLS
setup_ssl() {
    log_info "Configuration SSL/TLS..."
    
    # Créer le répertoire pour les certificats
    mkdir -p /etc/ssl/proctoflex-ai
    
    # Générer un certificat auto-signé (pour le développement)
    if [ ! -f "/etc/ssl/proctoflex-ai/cert.pem" ]; then
        openssl req -x509 -newkey rsa:4096 -keyout /etc/ssl/proctoflex-ai/key.pem -out /etc/ssl/proctoflex-ai/cert.pem -days 365 -nodes -subj "/C=TN/ST=Monastir/L=Monastir/O=ESPRIM/OU=IT/CN=proctoflex.ai"
        log_success "Certificat SSL généré"
    else
        log_info "Certificat SSL existant trouvé"
    fi
}

# Fonction principale
main() {
    log_info "Début du déploiement ProctoFlex AI v$VERSION"
    
    # Vérifications préliminaires
    check_prerequisites
    
    # Sauvegarde
    backup_existing_data
    
    # Arrêt des services existants
    stop_existing_services
    
    # Construction des images
    build_docker_images
    
    # Configuration
    configure_production
    setup_ssl
    configure_firewall
    
    # Déploiement
    deploy_services
    setup_database
    setup_monitoring
    
    # Validation
    if run_validation_tests; then
        log_success "🎉 Déploiement réussi !"
        log_info "Services disponibles :"
        log_info "  - API Backend: http://localhost:8000"
        log_info "  - Documentation: http://localhost:8000/docs"
        log_info "  - Frontend: http://localhost:3000"
        log_info "  - Base de données: localhost:5432"
        log_info "  - Redis: localhost:6379"
        echo
        log_info "Logs disponibles dans: $LOG_DIR"
        log_info "Sauvegardes dans: $BACKUP_DIR"
    else
        log_error "❌ Déploiement échoué"
        log_error "Vérifiez les logs pour plus de détails"
        exit 1
    fi
}

# Gestion des erreurs
trap 'log_error "Déploiement interrompu par l'\''utilisateur"; exit 1' INT
trap 'log_error "Erreur fatale lors du déploiement"; exit 1' ERR

# Exécution
main "$@"
