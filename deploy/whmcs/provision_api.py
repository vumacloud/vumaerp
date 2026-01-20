#!/usr/bin/env python3
"""
VumaERP Provisioning API for WHMCS

This Flask API handles provisioning requests from WHMCS:
- CreateAccount: Create new Odoo database for customer
- SuspendAccount: Deactivate database
- UnsuspendAccount: Reactivate database
- TerminateAccount: Delete database (with backup)

Run with: python3 provision_api.py
Or use gunicorn: gunicorn -w 2 -b 0.0.0.0:5000 provision_api:app

Configure WHMCS to call these endpoints via the Custom Server module
or use the provided WHMCS module.
"""

import os
import subprocess
import secrets
import string
import logging
from datetime import datetime
from functools import wraps

from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment
load_dotenv('/opt/vumaerp/deploy/.env')

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('PROVISION_API_SECRET', secrets.token_hex(32))

# Configuration
POSTGRES_USER = os.getenv('POSTGRES_USER', 'odoo')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
API_TOKEN = os.getenv('WHMCS_API_TOKEN', 'change_me_in_production')

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('vumaerp_provision')

# Country module mapping
COUNTRY_MODULES = {
    'ke': 'l10n_ke,l10n_ke_etims,l10n_ke_payroll',
    'ng': 'l10n_ng,l10n_ng_tax,l10n_ng_payroll',
    'gh': 'l10n_gh,l10n_gh_evat,l10n_gh_payroll',
    'ug': 'l10n_ug,l10n_ug_efris,l10n_ug_payroll',
}

COUNTRY_NAMES = {
    'ke': 'Kenya',
    'ng': 'Nigeria',
    'gh': 'Ghana',
    'ug': 'Uganda',
}


def require_auth(f):
    """Decorator to require API token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('X-API-Token') or request.form.get('api_token')
        if not token or token != API_TOKEN:
            logger.warning(f"Unauthorized access attempt from {request.remote_addr}")
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


def generate_password(length=16):
    """Generate a secure random password."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def run_docker_command(cmd, timeout=300):
    """Run a docker compose command and return output."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd='/opt/vumaerp/deploy',
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, '', 'Command timed out'
    except Exception as e:
        return False, '', str(e)


def database_exists(db_name):
    """Check if database exists."""
    cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -t -c \"SELECT 1 FROM pg_database WHERE datname = '{db_name}';\""
    success, stdout, _ = run_docker_command(cmd)
    return success and '1' in stdout


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({'status': 'ok', 'service': 'vumaerp-provision'})


@app.route('/api/v1/provision', methods=['POST'])
@require_auth
def create_account():
    """
    Create a new Odoo database for a customer.

    Required params:
        - db_name: Database name (e.g., acme_ltd)
        - country: Country code (ke, ng, gh, ug)
        - admin_email: Admin user email
        - company_name: Company name

    Optional params:
        - admin_password: If not provided, one will be generated

    Returns:
        - success: boolean
        - db_name: Database name
        - url: Login URL
        - admin_email: Admin email
        - admin_password: Admin password (only on creation)
    """
    data = request.form or request.json or {}

    # Validate required fields
    db_name = data.get('db_name', '').strip().lower()
    country = data.get('country', '').strip().lower()
    admin_email = data.get('admin_email', '').strip()
    company_name = data.get('company_name', '').strip()

    if not all([db_name, country, admin_email]):
        return jsonify({
            'success': False,
            'error': 'Missing required fields: db_name, country, admin_email'
        }), 400

    if country not in COUNTRY_MODULES:
        return jsonify({
            'success': False,
            'error': f'Invalid country code. Supported: {", ".join(COUNTRY_MODULES.keys())}'
        }), 400

    # Sanitize database name (only alphanumeric and underscore)
    db_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in db_name)

    # Check if database exists
    if database_exists(db_name):
        return jsonify({
            'success': False,
            'error': f'Database {db_name} already exists'
        }), 409

    # Generate password if not provided
    admin_password = data.get('admin_password') or generate_password()

    logger.info(f"Creating database: {db_name} for {country.upper()}")

    # Create database
    create_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -c \"CREATE DATABASE \\\"{db_name}\\\" ENCODING 'UTF8' TEMPLATE template0;\""
    success, _, stderr = run_docker_command(create_cmd)

    if not success:
        logger.error(f"Failed to create database: {stderr}")
        return jsonify({'success': False, 'error': 'Failed to create database'}), 500

    # Install modules
    country_modules = COUNTRY_MODULES[country]
    base_modules = "base,web,mail,contacts,sale_management,purchase,account,hr,om_hr_payroll,muk_web_theme,vumaerp_branding"
    all_modules = f"{base_modules},{country_modules}"

    init_cmd = f"docker compose exec -T odoo odoo --database=\"{db_name}\" --init=\"{all_modules}\" --stop-after-init --without-demo=all --load-language=en_US"

    logger.info(f"Initializing database with modules: {all_modules}")
    success, stdout, stderr = run_docker_command(init_cmd, timeout=600)

    if not success:
        logger.error(f"Failed to initialize database: {stderr}")
        # Cleanup: drop the database
        run_docker_command(f"docker compose exec -T db psql -U {POSTGRES_USER} -c \"DROP DATABASE IF EXISTS \\\"{db_name}\\\";\"")
        return jsonify({'success': False, 'error': 'Failed to initialize database'}), 500

    # Set admin credentials
    update_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -d \"{db_name}\" -c \"UPDATE res_users SET login='{admin_email}', password='{admin_password}' WHERE id=2;\""
    run_docker_command(update_cmd)

    # Set company name if provided
    if company_name:
        company_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -d \"{db_name}\" -c \"UPDATE res_company SET name='{company_name}' WHERE id=1;\""
        run_docker_command(company_cmd)

    # Generate subdomain
    subdomain = db_name.replace('_', '-')
    url = f"https://{subdomain}.vumacloud.com"

    logger.info(f"Successfully created database: {db_name}")

    return jsonify({
        'success': True,
        'db_name': db_name,
        'url': url,
        'admin_email': admin_email,
        'admin_password': admin_password,
        'country': COUNTRY_NAMES.get(country, country.upper()),
        'modules': all_modules.split(','),
    })


@app.route('/api/v1/suspend', methods=['POST'])
@require_auth
def suspend_account():
    """
    Suspend a customer's database by revoking connect permissions.
    """
    data = request.form or request.json or {}
    db_name = data.get('db_name', '').strip()

    if not db_name:
        return jsonify({'success': False, 'error': 'Missing db_name'}), 400

    if not database_exists(db_name):
        return jsonify({'success': False, 'error': 'Database not found'}), 404

    logger.info(f"Suspending database: {db_name}")

    # Revoke connect permissions
    cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -c \"REVOKE CONNECT ON DATABASE \\\"{db_name}\\\" FROM PUBLIC;\""
    success, _, stderr = run_docker_command(cmd)

    if not success:
        logger.error(f"Failed to suspend: {stderr}")
        return jsonify({'success': False, 'error': 'Failed to suspend'}), 500

    # Terminate existing connections
    term_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}';\""
    run_docker_command(term_cmd)

    return jsonify({'success': True, 'db_name': db_name, 'status': 'suspended'})


@app.route('/api/v1/unsuspend', methods=['POST'])
@require_auth
def unsuspend_account():
    """
    Unsuspend a customer's database by granting connect permissions.
    """
    data = request.form or request.json or {}
    db_name = data.get('db_name', '').strip()

    if not db_name:
        return jsonify({'success': False, 'error': 'Missing db_name'}), 400

    if not database_exists(db_name):
        return jsonify({'success': False, 'error': 'Database not found'}), 404

    logger.info(f"Unsuspending database: {db_name}")

    cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -c \"GRANT CONNECT ON DATABASE \\\"{db_name}\\\" TO PUBLIC;\""
    success, _, stderr = run_docker_command(cmd)

    if not success:
        logger.error(f"Failed to unsuspend: {stderr}")
        return jsonify({'success': False, 'error': 'Failed to unsuspend'}), 500

    return jsonify({'success': True, 'db_name': db_name, 'status': 'active'})


@app.route('/api/v1/terminate', methods=['POST'])
@require_auth
def terminate_account():
    """
    Terminate (delete) a customer's database.
    Creates a backup before deletion.
    """
    data = request.form or request.json or {}
    db_name = data.get('db_name', '').strip()
    skip_backup = data.get('skip_backup', False)

    if not db_name:
        return jsonify({'success': False, 'error': 'Missing db_name'}), 400

    if not database_exists(db_name):
        return jsonify({'success': False, 'error': 'Database not found'}), 404

    logger.info(f"Terminating database: {db_name}")

    # Create backup unless skipped
    backup_file = None
    if not skip_backup:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{db_name}_terminated_{timestamp}.sql.gz"
        backup_cmd = f"docker compose exec -T db pg_dump -U {POSTGRES_USER} \"{db_name}\" | gzip > /opt/vumaerp/deploy/backups/{backup_file}"
        run_docker_command(backup_cmd)
        logger.info(f"Created backup: {backup_file}")

    # Terminate connections
    term_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{db_name}';\""
    run_docker_command(term_cmd)

    # Drop database
    drop_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -c \"DROP DATABASE IF EXISTS \\\"{db_name}\\\";\""
    success, _, stderr = run_docker_command(drop_cmd)

    if not success:
        logger.error(f"Failed to terminate: {stderr}")
        return jsonify({'success': False, 'error': 'Failed to terminate'}), 500

    result = {
        'success': True,
        'db_name': db_name,
        'status': 'terminated'
    }
    if backup_file:
        result['backup'] = backup_file

    return jsonify(result)


@app.route('/api/v1/status', methods=['GET', 'POST'])
@require_auth
def get_status():
    """
    Get status of a customer's database.
    """
    data = request.form or request.json or request.args or {}
    db_name = data.get('db_name', '').strip()

    if not db_name:
        return jsonify({'success': False, 'error': 'Missing db_name'}), 400

    if not database_exists(db_name):
        return jsonify({'success': False, 'error': 'Database not found'}), 404

    # Check if suspended (no connect permission)
    check_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -t -c \"SELECT has_database_privilege('PUBLIC', '{db_name}', 'CONNECT');\""
    success, stdout, _ = run_docker_command(check_cmd)

    status = 'active' if 't' in stdout.lower() else 'suspended'

    # Get database size
    size_cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -t -c \"SELECT pg_size_pretty(pg_database_size('{db_name}'));\""
    _, size_out, _ = run_docker_command(size_cmd)
    size = size_out.strip()

    return jsonify({
        'success': True,
        'db_name': db_name,
        'status': status,
        'size': size,
    })


@app.route('/api/v1/list', methods=['GET'])
@require_auth
def list_databases():
    """
    List all customer databases.
    """
    cmd = f"docker compose exec -T db psql -U {POSTGRES_USER} -t -c \"SELECT datname FROM pg_database WHERE datistemplate = false AND datname NOT IN ('postgres');\""
    success, stdout, _ = run_docker_command(cmd)

    if not success:
        return jsonify({'success': False, 'error': 'Failed to list databases'}), 500

    databases = [db.strip() for db in stdout.strip().split('\n') if db.strip()]

    return jsonify({
        'success': True,
        'databases': databases,
        'count': len(databases)
    })


if __name__ == '__main__':
    port = int(os.getenv('PROVISION_API_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

    print(f"""
╔═══════════════════════════════════════════════════╗
║         VumaERP Provisioning API                   ║
╠═══════════════════════════════════════════════════╣
║  Endpoints:                                        ║
║    POST /api/v1/provision   - Create database     ║
║    POST /api/v1/suspend     - Suspend database    ║
║    POST /api/v1/unsuspend   - Unsuspend database  ║
║    POST /api/v1/terminate   - Delete database     ║
║    GET  /api/v1/status      - Check status        ║
║    GET  /api/v1/list        - List databases      ║
╚═══════════════════════════════════════════════════╝
    """)

    app.run(host='0.0.0.0', port=port, debug=debug)
