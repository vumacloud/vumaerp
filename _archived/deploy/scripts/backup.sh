#!/bin/bash
# ===========================================
# VumaERP Backup Script
# ===========================================
# Creates database dumps and uploads to DO Spaces
# Run manually or via cron

set -e

cd /opt/vumaerp/deploy
source .env

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=${BACKUP_RETENTION_DAYS:-30}

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"; }

log "Starting backup..."

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Get list of databases (excluding templates)
DATABASES=$(docker compose exec -T db psql -U "$POSTGRES_USER" -t -c \
    "SELECT datname FROM pg_database WHERE datistemplate = false AND datname NOT IN ('postgres');" | tr -d ' ')

# Backup each database
for DB in $DATABASES; do
    if [ -n "$DB" ]; then
        BACKUP_FILE="$BACKUP_DIR/${DB}_${DATE}.sql.gz"
        log "Backing up database: $DB"

        docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$DB" | gzip > "$BACKUP_FILE"

        if [ -f "$BACKUP_FILE" ]; then
            SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
            log "Created: $BACKUP_FILE ($SIZE)"
        fi
    fi
done

# Backup filestore
log "Backing up filestore..."
FILESTORE_BACKUP="$BACKUP_DIR/filestore_${DATE}.tar.gz"
docker compose exec -T odoo tar czf - /var/lib/odoo/filestore 2>/dev/null > "$FILESTORE_BACKUP" || true

if [ -f "$FILESTORE_BACKUP" ] && [ -s "$FILESTORE_BACKUP" ]; then
    SIZE=$(du -h "$FILESTORE_BACKUP" | cut -f1)
    log "Created: $FILESTORE_BACKUP ($SIZE)"
fi

# Upload to DO Spaces (if configured)
if [ -n "$DO_SPACES_KEY" ] && [ -n "$DO_SPACES_SECRET" ]; then
    log "Uploading to DigitalOcean Spaces..."

    # Install s3cmd if not present
    if ! command -v s3cmd &> /dev/null; then
        apt-get install -y -qq s3cmd
    fi

    # Configure s3cmd
    cat > ~/.s3cfg << EOF
[default]
access_key = $DO_SPACES_KEY
secret_key = $DO_SPACES_SECRET
host_base = ${DO_SPACES_REGION}.digitaloceanspaces.com
host_bucket = %(bucket)s.${DO_SPACES_REGION}.digitaloceanspaces.com
EOF

    # Upload today's backups
    for FILE in $BACKUP_DIR/*_${DATE}*; do
        if [ -f "$FILE" ]; then
            s3cmd put "$FILE" "s3://${DO_SPACES_BUCKET}/$(basename $FILE)" --acl-private
            log "Uploaded: $(basename $FILE)"
        fi
    done
fi

# Clean old local backups
log "Cleaning backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

log "Backup complete!"
