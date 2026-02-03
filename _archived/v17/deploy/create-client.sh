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

# Validate required env vars
if [ -z "$DB_HOST" ] || [ -z "$DB_PORT" ] || [ -z "$DB_USER" ] || [ -z "$DB_PASSWORD" ]; then
    echo "Error: Missing database configuration in .env file"
    echo "Required: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD"
    exit 1
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

# Default language: English (UK)
DEFAULT_LANG="en_GB"

echo ""
echo "============================================"
echo "Creating VumaERP Client Database"
echo "============================================"
echo "Database:  $DB_NAME"
echo "Admin:     $ADMIN_EMAIL"
echo "Language:  English (UK)"
echo "============================================"
echo ""

# Check if container is running
if ! docker compose ps --status running | grep -q "odoo"; then
    if ! docker ps | grep -q "odoo17"; then
        echo "Error: Odoo container is not running."
        echo "Start it with: docker compose up -d"
        exit 1
    fi
fi

# Database connection flags for odoo CLI
DB_FLAGS="--db_host=$DB_HOST --db_port=$DB_PORT -r $DB_USER -w $DB_PASSWORD"

echo "Step 1/4: Creating database with English (UK)..."
docker compose exec -T odoo odoo \
    $DB_FLAGS \
    --no-http \
    --stop-after-init \
    -d "$DB_NAME" \
    -i base \
    --load-language=$DEFAULT_LANG \
    --without-demo=all

echo ""
echo "Step 2/4: Setting admin credentials and language..."
docker compose exec -T odoo odoo shell \
    $DB_FLAGS \
    -d "$DB_NAME" \
    --no-http \
    --stop-after-init <<EOF
# Set English UK as default language for the system
lang = env['res.lang'].search([('code', '=', '$DEFAULT_LANG')], limit=1)
if not lang:
    env['res.lang']._activate_lang('$DEFAULT_LANG')
    lang = env['res.lang'].search([('code', '=', '$DEFAULT_LANG')], limit=1)

# Update admin user
user = env['res.users'].browse(2)
user.write({
    'login': '$ADMIN_EMAIL',
    'password': '$ADMIN_PASSWORD',
    'lang': '$DEFAULT_LANG',
})

# Set company default language
company = env['res.company'].browse(1)
if company:
    company.write({})  # Trigger any defaults

# Set default language in system parameters
env['ir.default'].set('res.partner', 'lang', '$DEFAULT_LANG')

env.cr.commit()
print('Admin credentials and language configured successfully')
EOF

echo ""
echo "Step 3/4: Installing VumaERP White Label..."
docker compose exec -T odoo odoo \
    $DB_FLAGS \
    --no-http \
    --stop-after-init \
    -d "$DB_NAME" \
    -i vumaerp_whitelabel \
    --without-demo=all 2>/dev/null || echo "Note: White label module will need manual installation"

echo ""
echo "Step 4/4: Final configuration..."
docker compose exec -T odoo odoo shell \
    $DB_FLAGS \
    -d "$DB_NAME" \
    --no-http \
    --stop-after-init <<EOF
# Ensure all partners default to English UK
env['ir.default'].set('res.partner', 'lang', '$DEFAULT_LANG')
env.cr.commit()
print('Configuration complete')
EOF

echo ""
echo "============================================"
echo "CLIENT DATABASE CREATED SUCCESSFULLY!"
echo "============================================"
echo ""
echo "URL:      https://${DB_NAME}.erp.vumacloud.com"
echo "Email:    $ADMIN_EMAIL"
echo "Password: $ADMIN_PASSWORD"
echo "Language: English (UK)"
echo ""
echo "IMPORTANT: Save these credentials securely!"
echo "Send them to the client via secure channel."
echo "============================================"
echo ""
