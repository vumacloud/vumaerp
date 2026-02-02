#!/bin/bash
# Create a new client database for VumaERP
# Usage: ./create-client.sh <client-name> <admin-email> <admin-password>

set -e

# Configuration - UPDATE THESE
ODOO_BIN="/opt/odoo/odoo-bin"
ODOO_CONF="/etc/odoo/odoo.conf"

# Database connection (DigitalOcean Managed PostgreSQL)
DB_HOST="YOUR_DB_HOST.db.ondigitalocean.com"
DB_PORT="25060"
DB_USER="doadmin"
DB_PASSWORD="YOUR_DB_PASSWORD"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check arguments
if [ $# -lt 3 ]; then
    echo -e "${YELLOW}Usage: $0 <client-name> <admin-email> <admin-password>${NC}"
    echo ""
    echo "Example: $0 acme admin@acme.com SecurePass123"
    echo ""
    echo "This will create:"
    echo "  - Database: acme"
    echo "  - URL: https://acme.erp.vumacloud.com"
    exit 1
fi

DB_NAME="$1"
ADMIN_EMAIL="$2"
ADMIN_PASSWORD="$3"

# Validate database name (subdomain-safe)
if [[ ! "$DB_NAME" =~ ^[a-z0-9][a-z0-9-]*[a-z0-9]$ ]] && [[ ! "$DB_NAME" =~ ^[a-z0-9]$ ]]; then
    echo -e "${RED}Error: Database name must be lowercase alphanumeric (hyphens allowed in middle)${NC}"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Creating VumaERP Client: $DB_NAME${NC}"
echo -e "${GREEN}========================================${NC}"

# Step 1: Create database with base module and English UK
echo -e "\n${YELLOW}Step 1/3: Creating database with base modules...${NC}"
$ODOO_BIN \
    --db_host="$DB_HOST" \
    --db_port="$DB_PORT" \
    -r "$DB_USER" \
    -w "$DB_PASSWORD" \
    --database="$DB_NAME" \
    --init=base \
    --load-language=en_GB \
    --without-demo=all \
    --stop-after-init \
    --no-http \
    2>&1 | tail -20

# Step 2: Set admin credentials
echo -e "\n${YELLOW}Step 2/3: Setting admin credentials...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --set=sslmode=require << EOF
UPDATE res_users
SET login = '$ADMIN_EMAIL',
    password = '$ADMIN_PASSWORD'
WHERE id = 2;
EOF

# Step 3: Set default language to English UK
echo -e "\n${YELLOW}Step 3/3: Setting default language to English UK...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" --set=sslmode=require << EOF
UPDATE res_lang SET active = true WHERE code = 'en_GB';
UPDATE ir_default SET json_value = '"en_GB"' WHERE field_id = (SELECT id FROM ir_model_fields WHERE model = 'res.partner' AND name = 'lang');
INSERT INTO ir_default (field_id, json_value, user_id, company_id)
SELECT id, '"en_GB"', NULL, NULL FROM ir_model_fields WHERE model = 'res.partner' AND name = 'lang'
ON CONFLICT DO NOTHING;
EOF

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Client created successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "URL:      ${YELLOW}https://$DB_NAME.erp.vumacloud.com${NC}"
echo -e "Email:    ${YELLOW}$ADMIN_EMAIL${NC}"
echo -e "Password: ${YELLOW}$ADMIN_PASSWORD${NC}"
echo ""
echo -e "${GREEN}DNS: Ensure wildcard *.erp.vumacloud.com points to this server${NC}"
