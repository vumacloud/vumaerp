#!/bin/bash
# List all client databases in VumaERP
# Usage: ./list-clients.sh

# Configuration - UPDATE THESE
DB_HOST="YOUR_DB_HOST.db.ondigitalocean.com"
DB_PORT="25060"
DB_USER="doadmin"
DB_PASSWORD="YOUR_DB_PASSWORD"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}VumaERP Client Databases${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres --set=sslmode=require << EOF
SELECT
    datname AS "Database",
    pg_size_pretty(pg_database_size(datname)) AS "Size",
    (SELECT count(*) FROM pg_stat_activity WHERE datname = d.datname) AS "Connections"
FROM pg_database d
WHERE datistemplate = false
  AND datname NOT IN ('postgres', '_dodb')
ORDER BY datname;
EOF

echo ""
echo -e "${CYAN}URLs: https://<database>.erp.vumacloud.com${NC}"
