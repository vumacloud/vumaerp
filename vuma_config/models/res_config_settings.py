# -*- coding: utf-8 -*-
import os
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    # Environment info (read-only display)
    env_smtp_configured = fields.Boolean(
        string='SMTP from Environment',
        compute='_compute_env_status',
    )
    env_db_configured = fields.Boolean(
        string='Database from Environment',
        compute='_compute_env_status',
    )
    env_file_loaded = fields.Boolean(
        string='.env File Loaded',
        compute='_compute_env_status',
    )
    env_info = fields.Text(
        string='Environment Info',
        compute='_compute_env_status',
    )

    @api.depends_context('uid')
    def _compute_env_status(self):
        for record in self:
            record.env_smtp_configured = bool(os.environ.get('ODOO_SMTP_HOST'))
            record.env_db_configured = bool(os.environ.get('ODOO_DB_HOST'))

            # Check if .env was loaded
            env_paths = [
                '/etc/odoo/.env',
                os.path.expanduser('~/.odoo/.env'),
                os.path.join(os.getcwd(), '.env'),
            ]
            record.env_file_loaded = any(os.path.isfile(p) for p in env_paths)

            # Build info text
            info_lines = []
            if record.env_smtp_configured:
                info_lines.append(f"SMTP: {os.environ.get('ODOO_SMTP_HOST')}:{os.environ.get('ODOO_SMTP_PORT', '587')}")
            if record.env_db_configured:
                info_lines.append(f"DB: {os.environ.get('ODOO_DB_HOST')}:{os.environ.get('ODOO_DB_PORT', '5432')}")
            record.env_info = '\n'.join(info_lines) if info_lines else 'No environment variables configured'
