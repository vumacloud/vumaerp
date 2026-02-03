#!/bin/bash
# ===========================================
# VumaERP - Delete Client Database
# ===========================================
# Usage: ./delete-client.sh <database_name>
# WARNING: This permanently deletes the database!

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

if [ -z "$1" ]; then
    echo "============================================"
    echo "VumaERP - Delete Client Database"
    echo "============================================"
    echo ""
    echo "Usage: ./delete-client.sh <database_name>"
    echo ""
    echo "WARNING: This permanently deletes the database!"
    echo "============================================"
    exit 1
fi

DB_NAME=$1

echo ""
echo "============================================"
echo "WARNING: DATABASE DELETION"
echo "============================================"
echo ""
echo "You are about to permanently delete:"
echo "  Database: $DB_NAME"
echo "  URL: https://${DB_NAME}.erp.vumacloud.com"
echo ""
echo "This action CANNOT be undone!"
echo ""
read -p "Type the database name to confirm deletion: " CONFIRM

if [ "$CONFIRM" != "$DB_NAME" ]; then
    echo ""
    echo "Confirmation failed. Aborting."
    exit 1
fi

echo ""
read -p "Are you ABSOLUTELY sure? (yes/no): " FINAL_CONFIRM

if [ "$FINAL_CONFIRM" != "yes" ]; then
    echo ""
    echo "Aborted."
    exit 1
fi

echo ""
echo "Deleting database '$DB_NAME'..."

# Drop the database using psql via docker
docker compose exec -T odoo python3 <<EOF
import odoo
from odoo.service import db
from odoo.tools import config

# Initialize Odoo configuration
config.parse_config([])

try:
    db.exp_drop('$DB_NAME')
    print("Database '$DB_NAME' deleted successfully.")
except Exception as e:
    print(f"Error deleting database: {e}")
    # Try alternative method
    import psycopg2
    import os
    conn = psycopg2.connect(
        host=os.environ.get('HOST'),
        port=os.environ.get('PORT'),
        user=os.environ.get('USER'),
        password=os.environ.get('PASSWORD'),
        dbname='postgres',
        sslmode='require'
    )
    conn.autocommit = True
    cur = conn.cursor()
    # Terminate existing connections
    cur.execute("""
        SELECT pg_terminate_backend(pid)
        FROM pg_stat_activity
        WHERE datname = %s AND pid <> pg_backend_pid()
    """, ('$DB_NAME',))
    # Drop database
    cur.execute('DROP DATABASE IF EXISTS "$DB_NAME"')
    cur.close()
    conn.close()
    print("Database '$DB_NAME' deleted successfully (via psql).")
EOF

echo ""
echo "============================================"
echo "DATABASE DELETED"
echo "============================================"
echo "Database '$DB_NAME' has been permanently deleted."
echo "============================================"
echo ""
