#!/bin/bash
# ===========================================
# VumaERP - Create New Client Database
# ===========================================
# Usage: ./create-client.sh <database_name> [admin_email]
# Example: ./create-client.sh acme admin@acme.co.ke

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$1" ]; then
    echo "============================================"
    echo "VumaERP - Create New Client Database"
    echo "============================================"
    echo ""
    echo "Usage: ./create-client.sh <database_name> [admin_email]"
    echo ""
    echo "Examples:"
    echo "  ./create-client.sh acme"
    echo "  ./create-client.sh acme admin@acme.co.ke"
    echo ""
    echo "The database name becomes the subdomain:"
    echo "  acme -> https://acme.erp.vumacloud.com"
    echo "============================================"
    exit 1
fi

DB_NAME=$1
ADMIN_EMAIL=${2:-"admin@${DB_NAME}.com"}
ADMIN_PASSWORD=$(openssl rand -base64 12 | tr -d '/+=' | head -c 12)

echo ""
echo "============================================"
echo "Creating VumaERP Client Database"
echo "============================================"
echo "Database:  $DB_NAME"
echo "Admin:     $ADMIN_EMAIL"
echo "============================================"
echo ""

# Check if container is running
if ! docker compose ps --status running | grep -q "odoo"; then
    # Fallback check for older docker compose versions
    if ! docker ps | grep -q "odoo17"; then
        echo "Error: Odoo container is not running."
        echo "Start it with: docker compose up -d"
        exit 1
    fi
fi

echo "Step 1/3: Creating database..."
docker compose exec -T odoo odoo \
    --no-http \
    --stop-after-init \
    -d "$DB_NAME" \
    -i base \
    --without-demo=all

echo ""
echo "Step 2/3: Setting admin credentials..."
docker compose exec -T odoo odoo shell -d "$DB_NAME" --no-http --stop-after-init <<EOF
user = env['res.users'].browse(2)
user.write({
    'login': '$ADMIN_EMAIL',
    'password': '$ADMIN_PASSWORD'
})
env.cr.commit()
print('Admin credentials updated successfully')
EOF

echo ""
echo "Step 3/3: Installing VumaERP White Label..."
docker compose exec -T odoo odoo \
    --no-http \
    --stop-after-init \
    -d "$DB_NAME" \
    -i vumaerp_whitelabel \
    --without-demo=all 2>/dev/null || echo "Note: White label module will need manual installation"

echo ""
echo "============================================"
echo "CLIENT DATABASE CREATED SUCCESSFULLY!"
echo "============================================"
echo ""
echo "URL:      https://${DB_NAME}.erp.vumacloud.com"
echo "Email:    $ADMIN_EMAIL"
echo "Password: $ADMIN_PASSWORD"
echo ""
echo "IMPORTANT: Save these credentials securely!"
echo "Send them to the client via secure channel."
echo "============================================"
echo ""
