#!/bin/bash
# ===========================================
# VumaERP SSL Setup Script
# ===========================================
# Run after DNS is pointing to your server

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[VUMA]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

cd /opt/vumaerp/deploy

# Load environment
source .env

DOMAIN=${DOMAIN:-vuma.cloud}
EMAIL=${LETSENCRYPT_EMAIL:-admin@$DOMAIN}

log "Setting up SSL for $DOMAIN..."

# Check DNS
log "Checking DNS resolution..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | tail -1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    warn "DNS may not be configured yet."
    warn "Server IP: $SERVER_IP"
    warn "Domain resolves to: $DOMAIN_IP"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop nginx temporarily
log "Stopping nginx for certificate generation..."
docker compose stop nginx

# Get certificate
log "Requesting SSL certificate from Let's Encrypt..."
docker compose run --rm certbot certonly \
    --standalone \
    --preferred-challenges http \
    --email "$EMAIL" \
    --agree-tos \
    --no-eff-email \
    -d "$DOMAIN" \
    -d "*.$DOMAIN"

# If wildcard fails, try without it
if [ $? -ne 0 ]; then
    warn "Wildcard cert failed, trying single domain..."
    docker compose run --rm certbot certonly \
        --standalone \
        --preferred-challenges http \
        --email "$EMAIL" \
        --agree-tos \
        --no-eff-email \
        -d "$DOMAIN"
fi

# Restart nginx
log "Starting nginx with new certificate..."
docker compose up -d nginx

# Set up auto-renewal cron
log "Setting up certificate auto-renewal..."
(crontab -l 2>/dev/null; echo "0 3 * * * cd /opt/vumaerp/deploy && docker compose run --rm certbot renew --quiet && docker compose exec nginx nginx -s reload") | crontab -

log "SSL setup complete!"
echo ""
echo "Your site is now available at: https://$DOMAIN"
echo "Certificate will auto-renew via cron."
