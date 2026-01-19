# -*- coding: utf-8 -*-
import os
import logging
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

from . import models


def _load_env_file():
    """Load environment variables from .env file if it exists."""
    env_paths = [
        '/etc/odoo/.env',
        os.path.expanduser('~/.odoo/.env'),
        os.path.join(os.getcwd(), '.env'),
    ]

    for env_path in env_paths:
        if os.path.isfile(env_path):
            _logger.info(f"Loading environment from {env_path}")
            try:
                with open(env_path) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if key not in os.environ:
                                os.environ[key] = value
                return True
            except Exception as e:
                _logger.warning(f"Failed to load .env file: {e}")
    return False


def post_init_hook(env):
    """Post-installation hook to configure SMTP from environment."""
    _load_env_file()

    # Configure outgoing mail server from environment
    smtp_host = os.environ.get('ODOO_SMTP_HOST')
    if smtp_host:
        _logger.info("Configuring SMTP from environment variables")
        mail_server = env['ir.mail_server'].search([], limit=1)
        vals = {
            'name': 'Environment SMTP',
            'smtp_host': smtp_host,
            'smtp_port': int(os.environ.get('ODOO_SMTP_PORT', 587)),
            'smtp_user': os.environ.get('ODOO_SMTP_USER', ''),
            'smtp_pass': os.environ.get('ODOO_SMTP_PASSWORD', ''),
            'smtp_encryption': os.environ.get('ODOO_SMTP_ENCRYPTION', 'starttls'),
        }
        if mail_server:
            mail_server.write(vals)
        else:
            env['ir.mail_server'].create(vals)


# Load .env on module import
_load_env_file()
