#!/bin/bash
# ===========================================
# VumaERP Deploy Script
# ===========================================
# Run this on a fresh Ubuntu 22.04 droplet
# Usage: curl -sSL https://raw.githubusercontent.com/vumacloud/vumaerp/main/deploy/scripts/deploy.sh | bash

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[VUMA]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# ===========================================
# Prerequisites
# ===========================================
log "Checking prerequisites..."

if [ "$EUID" -ne 0 ]; then
    error "Please run as root (sudo)"
fi

# ===========================================
# System Updates
# ===========================================
log "Updating system packages..."
apt-get update -qq
apt-get upgrade -y -qq

# ===========================================
# Install Docker
# ===========================================
log "Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
fi

if ! command -v docker-compose &> /dev/null; then
    apt-get install -y -qq docker-compose-plugin
fi

# ===========================================
# Install additional tools
# ===========================================
log "Installing tools..."
apt-get install -y -qq git curl wget htop vim ufw fail2ban

# ===========================================
# Configure Firewall
# ===========================================
log "Configuring firewall..."
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

# ===========================================
# Configure Fail2ban
# ===========================================
log "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# ===========================================
# Clone VumaERP
# ===========================================
log "Cloning VumaERP..."
INSTALL_DIR="/opt/vumaerp"

if [ -d "$INSTALL_DIR" ]; then
    warn "Directory exists, pulling latest..."
    cd "$INSTALL_DIR"
    git pull origin main || true
else
    git clone https://github.com/vumacloud/vumaerp.git "$INSTALL_DIR"
    cd "$INSTALL_DIR"
fi

# ===========================================
# Setup Environment
# ===========================================
log "Setting up environment..."
cd "$INSTALL_DIR/deploy"

if [ ! -f .env ]; then
    cp .env.example .env

    # Generate secure passwords
    POSTGRES_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    ODOO_PASS=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)
    WHMCS_TOKEN=$(openssl rand -base64 32 | tr -dc 'a-zA-Z0-9' | head -c 32)

    sed -i "s/CHANGE_ME_STRONG_PASSWORD_HERE/$POSTGRES_PASS/" .env
    sed -i "s/CHANGE_ME_MASTER_PASSWORD/$ODOO_PASS/" .env
    sed -i "s/generate_a_secure_token_here/$WHMCS_TOKEN/" .env

    log "Generated secure passwords in .env"
    warn "IMPORTANT: Save these passwords!"
    echo ""
    echo "PostgreSQL Password: $POSTGRES_PASS"
    echo "Odoo Master Password: $ODOO_PASS"
    echo "WHMCS API Token: $WHMCS_TOKEN"
    echo ""
fi

# ===========================================
# Create directories
# ===========================================
log "Creating directories..."
mkdir -p backups
mkdir -p nginx/ssl

# ===========================================
# Initial SSL (self-signed for startup)
# ===========================================
log "Creating initial self-signed certificate..."
if [ ! -f nginx/ssl/selfsigned.crt ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/selfsigned.key \
        -out nginx/ssl/selfsigned.crt \
        -subj "/C=US/ST=State/L=City/O=VumaCloud/CN=vumaerp.com"
fi

# Create dummy Let's Encrypt directory structure for initial startup
mkdir -p /etc/letsencrypt/live/vumaerp.com
if [ ! -f /etc/letsencrypt/live/vumaerp.com/fullchain.pem ]; then
    cp nginx/ssl/selfsigned.crt /etc/letsencrypt/live/vumaerp.com/fullchain.pem
    cp nginx/ssl/selfsigned.key /etc/letsencrypt/live/vumaerp.com/privkey.pem
fi

# ===========================================
# Start Services
# ===========================================
log "Starting services..."
docker compose pull
docker compose up -d

# ===========================================
# Wait for Odoo
# ===========================================
log "Waiting for Odoo to start (this may take a minute)..."
sleep 30

# Check health
for i in {1..30}; do
    if curl -s http://localhost:8069/web/health > /dev/null 2>&1; then
        log "Odoo is running!"
        break
    fi
    sleep 5
done

# ===========================================
# Done
# ===========================================
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "YOUR_SERVER_IP")

echo ""
echo "=========================================="
echo -e "${GREEN}VumaERP Deployment Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Register vumaerp.com and point DNS:"
echo "   A    vumaerp.com     → $SERVER_IP"
echo "   A    *.vumaerp.com   → $SERVER_IP"
echo ""
echo "2. Run SSL setup: cd /opt/vumaerp/deploy && ./scripts/setup-ssl.sh"
echo ""
echo "3. Create first customer:"
echo "   ./scripts/new-customer.sh mycompany ke admin@example.com"
echo ""
echo "Useful commands:"
echo "  Logs:    docker compose logs -f odoo"
echo "  Restart: docker compose restart"
echo "  Stop:    docker compose down"
echo "  Backup:  ./scripts/backup.sh"
echo ""
echo "Passwords saved in: /opt/vumaerp/deploy/.env"
echo ""
