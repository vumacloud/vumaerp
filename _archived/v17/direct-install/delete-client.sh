#!/bin/bash
# Delete a client database from VumaERP
# Usage: ./delete-client.sh <client-name>

set -e

# Configuration - UPDATE THESE
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
if [ $# -lt 1 ]; then
    echo -e "${YELLOW}Usage: $0 <client-name>${NC}"
    echo ""
    echo "Example: $0 acme"
    exit 1
fi

DB_NAME="$1"

# Safety check - don't delete postgres or template databases
if [[ "$DB_NAME" == "postgres" ]] || [[ "$DB_NAME" == "template"* ]]; then
    echo -e "${RED}Error: Cannot delete system database${NC}"
    exit 1
fi

# Check if database exists
DB_EXISTS=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres --set=sslmode=require -tAc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'")

if [ "$DB_EXISTS" != "1" ]; then
    echo -e "${RED}Error: Database '$DB_NAME' does not exist${NC}"
    exit 1
fi

echo -e "${RED}========================================${NC}"
echo -e "${RED}WARNING: About to DELETE client: $DB_NAME${NC}"
echo -e "${RED}========================================${NC}"
echo ""
echo -e "This will permanently delete:"
echo -e "  - Database: $DB_NAME"
echo -e "  - All client data, users, and files"
echo ""
read -p "Type the database name to confirm deletion: " CONFIRM

if [ "$CONFIRM" != "$DB_NAME" ]; then
    echo -e "${YELLOW}Deletion cancelled${NC}"
    exit 1
fi

echo -e "\n${YELLOW}Terminating active connections...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres --set=sslmode=require << EOF
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
EOF

echo -e "${YELLOW}Dropping database...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres --set=sslmode=require -c "DROP DATABASE \"$DB_NAME\";"

# Also remove filestore
FILESTORE_PATH="/var/lib/odoo/filestore/$DB_NAME"
if [ -d "$FILESTORE_PATH" ]; then
    echo -e "${YELLOW}Removing filestore...${NC}"
    rm -rf "$FILESTORE_PATH"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Client '$DB_NAME' deleted successfully${NC}"
echo -e "${GREEN}========================================${NC}"
