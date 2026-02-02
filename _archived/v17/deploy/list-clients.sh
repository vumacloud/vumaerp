#!/bin/bash
# ===========================================
# VumaERP - List All Client Databases
# ===========================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

echo ""
echo "============================================"
echo "VumaERP - Client Databases"
echo "============================================"
echo ""

# List databases using psql via docker
docker compose exec -T odoo python3 <<EOF
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
cur = conn.cursor()
cur.execute("""
    SELECT datname, pg_size_pretty(pg_database_size(datname)) as size
    FROM pg_database
    WHERE datistemplate = false
    AND datname NOT IN ('postgres', '_dodb')
    ORDER BY datname
""")
rows = cur.fetchall()
cur.close()
conn.close()

if rows:
    print(f"{'Database Name':<30} {'Size':<15} {'URL'}")
    print("-" * 80)
    for row in rows:
        db_name = row[0]
        size = row[1]
        url = f"https://{db_name}.erp.vumacloud.com"
        print(f"{db_name:<30} {size:<15} {url}")
    print("-" * 80)
    print(f"Total: {len(rows)} database(s)")
else:
    print("No client databases found.")
EOF

echo ""
