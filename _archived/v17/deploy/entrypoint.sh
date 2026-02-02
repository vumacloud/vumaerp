#!/bin/bash
set -e

# Set database connection from environment
: "${HOST:=db}"
: "${PORT:=5432}"
: "${USER:=odoo}"
: "${PASSWORD:=odoo}"

DB_ARGS=("--db_host" "$HOST" "--db_port" "$PORT" "--db_user" "$USER" "--db_password" "$PASSWORD")

case "$1" in
    -- | odoo)
        shift
        exec /opt/odoo/odoo-bin "$@" "${DB_ARGS[@]}"
        ;;
    -*)
        exec /opt/odoo/odoo-bin "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac
