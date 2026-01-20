#!/bin/bash
# ===========================================
# VumaERP New Customer Provisioning
# ===========================================
# Creates a new database with country-specific modules

set -e

cd /opt/vumaerp/deploy
source .env

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[VUMA]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

usage() {
    echo "Usage: $0 <database_name> <country_code> [admin_email]"
    echo ""
    echo "Arguments:"
    echo "  database_name  Unique name for the customer database (e.g., acme_ltd)"
    echo "  country_code   Country code: ke (Kenya), ng (Nigeria), gh (Ghana)"
    echo "  admin_email    Optional admin email (default: admin@example.com)"
    echo ""
    echo "Examples:"
    echo "  $0 acme_ltd ke admin@acme.co.ke"
    echo "  $0 widgets_ng ng"
    exit 1
}

# Check arguments
if [ -z "$1" ] || [ -z "$2" ]; then
    usage
fi

DB_NAME="$1"
COUNTRY="$2"
ADMIN_EMAIL="${3:-admin@example.com}"
ADMIN_PASSWORD=$(openssl rand -base64 12 | tr -dc 'a-zA-Z0-9' | head -c 12)

# Validate country
case "$COUNTRY" in
    ke|KE)
        COUNTRY_NAME="Kenya"
        MODULES="l10n_ke,l10n_ke_etims,l10n_ke_payroll"
        CURRENCY="KES"
        ;;
    ng|NG)
        COUNTRY_NAME="Nigeria"
        MODULES="l10n_ng,l10n_ng_tax,l10n_ng_payroll"
        CURRENCY="NGN"
        ;;
    gh|GH)
        COUNTRY_NAME="Ghana"
        MODULES="l10n_gh,l10n_gh_evat,l10n_gh_payroll"
        CURRENCY="GHS"
        ;;
    ug|UG)
        COUNTRY_NAME="Uganda"
        MODULES="l10n_ug,l10n_ug_efris,l10n_ug_payroll"
        CURRENCY="UGX"
        ;;
    *)
        error "Unknown country code: $COUNTRY. Use: ke, ng, gh, ug"
        ;;
esac

log "Creating new customer database..."
echo "  Database: $DB_NAME"
echo "  Country:  $COUNTRY_NAME"
echo "  Email:    $ADMIN_EMAIL"
echo ""

# Check if database exists (connect to postgres db, which always exists)
EXISTING=$(docker compose exec -T db psql -U "$POSTGRES_USER" -d postgres -t -c \
    "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME';" | tr -d ' ')

if [ "$EXISTING" == "1" ]; then
    error "Database '$DB_NAME' already exists!"
fi

# Create database
log "Creating PostgreSQL database..."
docker compose exec -T db psql -U "$POSTGRES_USER" -d postgres -c "CREATE DATABASE \"$DB_NAME\" ENCODING 'UTF8' TEMPLATE template0;"

# Initialize Odoo database with modules
log "Initializing Odoo database with $COUNTRY_NAME modules..."
log "This may take 2-5 minutes..."

# Base modules + country modules + common apps
ALL_MODULES="base,web,mail,contacts,sale_management,purchase,account,hr,om_hr_payroll,muk_web_theme,$MODULES"

docker compose exec -T odoo odoo \
    --database="$DB_NAME" \
    --init="$ALL_MODULES" \
    --stop-after-init \
    --without-demo=all \
    --load-language=en_US \
    2>&1 | tail -20

# Set admin password
log "Setting admin credentials..."
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$DB_NAME" -c \
    "UPDATE res_users SET login='$ADMIN_EMAIL', password='$ADMIN_PASSWORD' WHERE id=2;"

# Create the company with correct country/currency would require more Odoo API calls
# For now, admin can set this in the UI

# Generate subdomain (replace underscores with dashes)
SUBDOMAIN=$(echo "$DB_NAME" | tr '_' '-')

echo ""
echo "=========================================="
echo -e "${GREEN}Customer Database Created!${NC}"
echo "=========================================="
echo ""
echo "Database:     $DB_NAME"
echo "Country:      $COUNTRY_NAME"
echo "Currency:     $CURRENCY"
echo ""

echo "Admin Login:"
echo "  URL:      https://${SUBDOMAIN}.vumaerp.com"
echo "  Email:    $ADMIN_EMAIL"
echo "  Password: $ADMIN_PASSWORD"
echo ""
echo "Installed modules: $ALL_MODULES"
echo ""
warn "IMPORTANT: Share credentials securely with customer!"
warn "Customer should change password on first login."
echo ""
