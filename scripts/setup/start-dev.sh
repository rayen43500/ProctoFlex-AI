#!/bin/bash

# Script de démarrage pour ProctoFlex AI - Mode Développement
# Université de Monastir - ESPRIM

set -e

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${BLUE}[ProctoFlex AI]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Fonction pour vérifier si Docker est installé
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé. Veuillez installer Docker avant de continuer."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé. Veuillez installer Docker Compose avant de continuer."
        exit 1
    fi
    
    print_success "Docker et Docker Compose sont installés"
}

# Fonction pour vérifier si Node.js est installé
check_nodejs() {
    if ! command -v node &> /dev/null; then
        print_warning "Node.js n'est pas installé. L'application desktop ne pourra pas être démarrée."
        return 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION est installé"
    return 0
}

# Fonction pour vérifier si Python est installé
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_warning "Python 3 n'est pas installé. Le backend ne pourra pas être démarré localement."
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    print_success "$PYTHON_VERSION est installé"
    return 0
}

# Fonction pour créer les répertoires nécessaires
create_directories() {
    print_message "Création des répertoires nécessaires..."
    
    mkdir -p logs
    mkdir -p uploads
    mkdir -p backend/logs
    mkdir -p backend/uploads
    
    print_success "Répertoires créés"
}

# Fonction pour démarrer les services Docker
start_docker_services() {
    print_message "Démarrage des services Docker..."
    
    # Vérifier si docker-compose.dev.yml existe
    if [ ! -f "docker-compose.dev.yml" ]; then
        print_error "Fichier docker-compose.dev.yml non trouvé"
        exit 1
    fi
    
    # Démarrer les services
    docker-compose -f docker-compose.dev.yml up -d
    
    print_success "Services Docker démarrés"
}

# Fonction pour attendre que les services soient prêts
wait_for_services() {
    print_message "Attente du démarrage des services..."
    
    # Attendre PostgreSQL
    print_message "Vérification de PostgreSQL..."
    for i in {1..30}; do
    if docker exec proctoflex-postgres-dev pg_isready -U postgres -d proctoflex &> /dev/null; then
            print_success "PostgreSQL est prêt"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "PostgreSQL n'est pas prêt après 30 secondes"
            exit 1
        fi
        sleep 1
    done
    
    # Attendre Redis
    print_message "Vérification de Redis..."
    for i in {1..30}; do
        if docker exec proctoflex-redis-dev redis-cli ping &> /dev/null; then
            print_success "Redis est prêt"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Redis n'est pas prêt après 30 secondes"
            exit 1
        fi
        sleep 1
    done
    
    # Attendre le backend
    print_message "Vérification du backend..."
    for i in {1..60}; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_success "Backend est prêt"
            break
        fi
        if [ $i -eq 60 ]; then
            print_warning "Backend n'est pas prêt après 60 secondes (peut être normal si en cours de démarrage)"
        fi
        sleep 2
    done
}

# Fonction pour installer les dépendances du frontend
install_frontend_dependencies() {
    if [ -d "frontend" ]; then
        print_message "Installation des dépendances du frontend..."
        cd frontend
        npm install
        cd ..
        print_success "Dépendances du frontend installées"
    fi
}

# Fonction pour installer les dépendances du desktop
install_desktop_dependencies() {
    if [ -d "desktop" ]; then
        print_message "Installation des dépendances du desktop..."
        cd desktop
        npm install
        cd ..
        print_success "Dépendances du desktop installées"
    fi
}

# Fonction pour installer les dépendances du backend
install_backend_dependencies() {
    if [ -d "backend" ]; then
        print_message "Installation des dépendances du backend..."
        cd backend
        
        # Créer un environnement virtuel s'il n'existe pas
        if [ ! -d "venv" ]; then
            python3 -m venv venv
        fi
        
        # Activer l'environnement virtuel
        source venv/bin/activate
        
        # Installer les dépendances
        pip install -r requirements.txt
        
        cd ..
        print_success "Dépendances du backend installées"
    fi
}

# Fonction pour afficher les informations de connexion
show_connection_info() {
    echo ""
    echo "=========================================="
    echo "🎯 ProctoFlex AI - Services Démarrés"
    echo "=========================================="
    echo ""
    echo "📊 Services disponibles:"
    echo "  • Backend API:     http://localhost:8000"
    echo "  • Documentation:   http://localhost:8000/docs"
    echo "  • Frontend Admin:  http://localhost:3000"
    echo "  • PostgreSQL:      localhost:5432"
    echo "  • Redis:           localhost:6379"
    echo ""
    echo "🔐 Identifiants par défaut:"
    echo "  • PostgreSQL:      postgres / ${POSTGRES_PASSWORD:-secure_password}"
    echo "  • Admin:           admin@proctoflex.ai / admin123"
    echo "  • Étudiant Test:   student@test.com / student123"
    echo ""
    echo "📱 Application Desktop:"
    echo "  • Aller dans le dossier 'desktop'"
    echo "  • Exécuter: npm run dev"
    echo ""
    echo "🛠️ Commandes utiles:"
    echo "  • Arrêter:         ./scripts/setup/stop-dev.sh"
    echo "  • Logs:            docker-compose -f docker-compose.dev.yml logs -f"
    echo "  • Redémarrer:      docker-compose -f docker-compose.dev.yml restart"
    echo ""
    echo "=========================================="
}

# Fonction principale
main() {
    echo "🚀 Démarrage de ProctoFlex AI - Mode Développement"
    echo "Université de Monastir - ESPRIM"
    echo "=========================================="
    echo ""
    
    # Vérifications préliminaires
    check_docker
    
    # Créer les répertoires
    create_directories
    
    # Démarrer les services Docker
    start_docker_services
    
    # Attendre que les services soient prêts
    wait_for_services
    
    # Installer les dépendances si Node.js est disponible
    if check_nodejs; then
        install_frontend_dependencies
        install_desktop_dependencies
    fi
    
    # Installer les dépendances si Python est disponible
    if check_python; then
        install_backend_dependencies
    fi
    
    # Afficher les informations de connexion
    show_connection_info
    
    print_success "ProctoFlex AI est prêt ! 🎉"
}

# Exécuter la fonction principale
main "$@"
